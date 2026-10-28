#!/bin/bash
# Regenerate the schematic and run every check. Exit non-zero on any failure.
set -e
cd "$(dirname "$0")"
/usr/bin/python3 gen_sch.py
kicad-cli sch export netlist --format kicadsexpr -o la4440.net la4440.kicad_sch >/dev/null
/usr/bin/python3 netcheck.py la4440.net ../sim/amp_full.cir
kicad-cli sch erc --format json -o erc.json la4440.kicad_sch >/dev/null
/usr/bin/python3 - <<'PY'
import json, sys
from collections import Counter
d = json.load(open("erc.json"))
c = Counter(); bad = 0
for sh in d["sheets"]:
    for v in sh["violations"]:
        c[(v["severity"], v["description"])] += 1
        if v["severity"] == "error":
            bad += 1
            print("ERC error:", v["description"], [(i.get("description"), i["pos"]) for i in v["items"]][:2])
for k, n in sorted(c.items()): print("ERC", n, k)
sys.exit(1 if bad else 0)
PY
rm -rf svg && kicad-cli sch export svg -o svg --exclude-drawing-sheet la4440.kicad_sch >/dev/null
kicad-cli sch export pdf -o la4440-schematic.pdf la4440.kicad_sch >/dev/null
/usr/bin/python3 - <<'PY'
import re
t = open("svg/la4440.svg").read()
t = re.sub(r'width="[^"]+"', 'width="3360"', t, count=1)
t = re.sub(r'height="[^"]+"', 'height="2376"', t, count=1)
open("svg/la4440-big.svg", "w").write(t)
PY
/usr/bin/google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=3360,2376 --screenshot="$PWD/sch.png" "file://$PWD/svg/la4440-big.svg" 2>/dev/null
echo "ALL CHECKS PASSED; picture at $PWD/sch.png"
