"""Add (or refresh) GND copper pours on B.Cu and F.Cu and fill them. Run with /usr/bin/python3."""
import sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

path = sys.argv[1]
b = pcbnew.LoadBoard(path)
gnd = b.FindNet(sys.argv[2] if len(sys.argv) > 2 else "/GND")
assert gnd is not None and gnd.GetNetname() == (sys.argv[2] if len(sys.argv) > 2 else "/GND"), "pour net not found"
bb = b.GetBoardEdgesBoundingBox()
PTS = [(bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
       (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())]
# remove old pours only after every board query: Remove() corrupts later SWIG returns
for z in list(b.Zones()):
    b.Remove(z)
for layer in (pcbnew.B_Cu, pcbnew.F_Cu):
  z = pcbnew.ZONE(b)
  z.SetLayer(layer)
  z.SetNet(gnd)
  z.SetAssignedPriority(0)
  z.SetLocalClearance(FromMM(0.3))
  z.SetMinThickness(FromMM(0.3))
  z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
  z.SetThermalReliefGap(FromMM(0.4))
  z.SetThermalReliefSpokeWidth(FromMM(0.5))
  z.SetIsFilled(False)
  z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)   # a GND island is a gap to bridge, not copper
  outline = z.Outline()
  outline.NewOutline()
  for x, y in PTS:
      outline.Append(x, y)
  b.Add(z)
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
pcbnew.SaveBoard(path, b)
print("GND zones on B.Cu + F.Cu filled")
