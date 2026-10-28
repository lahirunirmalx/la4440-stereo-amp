"""Close the one link freerouting leaves open: Q2 pad 1 (VCC, emitter) to the VCC track
that passes just below it on B.Cu. freerouting reaches the SOT-23 twin pad but cannot fit a
1.0 mm track onto the TO-92 pad next to it. Checks the target track is where it expects;
DRC in build_pcb.sh is the real check. Run with /usr/bin/python3."""
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

b = pcbnew.LoadBoard(sys.argv[1])
pad = [p for p in b.FindFootprintByReference("Q2").Pads() if p.GetNumber() == "1"][0]
px, py = pad.GetPosition().x, pad.GetPosition().y
hit = None
for t in b.GetTracks():
    if t.GetNetname() != "/VCC" or t.GetLayer() != pcbnew.B_Cu or t.GetClass() == "PCB_VIA":
        continue
    s, e = t.GetStart(), t.GetEnd()
    lo, hi = sorted((s.x, e.x))
    if lo <= px <= hi and s.x != e.x:
        y = s.y + (e.y - s.y) * (px - s.x) / (e.x - s.x)
        if 0 < y - py < FromMM(8) and (hit is None or y < hit):
            hit = int(y)
if hit is None:
    print("post_route: no VCC track below Q2 pad 1 - routing changed, link not added")
    sys.exit(0)
tr = pcbnew.PCB_TRACK(b)
tr.SetStart(VECTOR2I(px, py)); tr.SetEnd(VECTOR2I(px, hit))
tr.SetWidth(FromMM(1.0)); tr.SetLayer(pcbnew.B_Cu); tr.SetNet(pad.GetNet())
b.Add(tr)
pcbnew.SaveBoard(sys.argv[1], b)
print("post_route: Q2 pad 1 linked to VCC, %.2f mm on B.Cu" % ((hit - py) / 1e6))
