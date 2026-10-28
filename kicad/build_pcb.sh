#!/bin/bash
# Place -> autoroute -> import -> DRC (with schematic parity) -> render.
set -e
cd "$(dirname "$0")"
/usr/bin/python3 gen_pcb.py
rm -f la4440.ses
~/.local/bin/freerouting -de la4440.dsn -do la4440.ses -mp 400 -oit 0.1 2>&1 | grep -E "INFO|ERROR" | grep -v "New version" | tail -4
/usr/bin/python3 - <<'PY'
import pcbnew
b = pcbnew.LoadBoard("la4440.kicad_pcb")
assert pcbnew.ImportSpecctraSES(b, "la4440.ses")
tr = list(b.GetTracks()); vias = [t for t in tr if t.GetClass() == "PCB_VIA"]
print("routed: %d track segments, %d vias" % (len(tr) - len(vias), len(vias)))
pcbnew.SaveBoard("la4440.kicad_pcb", b)
PY
/usr/bin/python3 post_route.py la4440.kicad_pcb
/usr/bin/python3 add_gnd_zone.py la4440.kicad_pcb /GND
kicad-cli pcb drc --schematic-parity --format json -o drc.json la4440.kicad_pcb >/dev/null
/usr/bin/python3 - <<'PY'
import json, sys
from collections import Counter
d = json.load(open("drc.json")); bad = 0
for key in ["violations", "unconnected_items", "schematic_parity"]:
    items = d.get(key, [])
    for (sev, desc), n in sorted(Counter((v["severity"], v["description"]) for v in items).items()):
        print("DRC %-18s %-7s x%-2d %s" % (key, sev, n, desc))
    for v in items:
        if v["severity"] == "error":
            bad += 1
            print("   ", v["description"], [(i.get("description"), i["pos"]) for i in v["items"]][:2])
print("DRC errors:", bad)
sys.exit(1 if bad else 0)
PY
./render_pcb.sh
