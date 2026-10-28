#!/bin/bash
# Regenerate everything: schematic + checks -> board (place, route, pour, DRC) -> renders -> fab files -> panel.
set -e
cd "$(dirname "$0")"
./run_checks.sh
./build_pcb.sh
kicad-cli pcb render -o ../docs/images/pcb_3d_iso.png --width 1600 --height 1100 --quality high --rotate "-45,0,30" --zoom 0.9 la4440.kicad_pcb >/dev/null 2>&1
kicad-cli pcb render -o ../docs/images/pcb_3d_top.png --width 1600 --height 1250 --quality high la4440.kicad_pcb >/dev/null 2>&1
cp pcb.png ../docs/images/pcb_2layer.png; cp sch.png ../docs/images/schematic.png
rm -rf gerbers la4440-gerbers.zip && mkdir gerbers
kicad-cli pcb export gerbers -o gerbers/ --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts,F.Paste,B.Paste --subtract-soldermask la4440.kicad_pcb >/dev/null
kicad-cli pcb export drill -o gerbers/ --format excellon --excellon-separate-th --generate-map --map-format gerberx2 la4440.kicad_pcb >/dev/null
(cd gerbers && zip -q ../la4440-gerbers.zip *)
cd panel
~/tools/kikit-venv/bin/python make_panel.py la4440-panel-2up.kicad_pcb ../la4440.kicad_pcb:2 2>&1 | grep -v Debug
rm -rf g la4440-panel-2up-gerbers.zip && mkdir g
kicad-cli pcb export gerbers -o g/ --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask la4440-panel-2up.kicad_pcb >/dev/null
kicad-cli pcb export drill -o g/ --format excellon --excellon-separate-th la4440-panel-2up.kicad_pcb >/dev/null
(cd g && zip -q ../la4440-panel-2up-gerbers.zip *) && rm -rf g
echo "BUILD ALL DONE"
