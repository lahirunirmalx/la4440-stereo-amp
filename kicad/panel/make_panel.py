"""Pack several (different) KiCad boards into one PCBWay-friendly panel.

Usage:  ~/tools/kikit-venv/bin/python make_panel.py out.kicad_pcb board1.kicad_pcb[:N] [board2.kicad_pcb[:N] ...]
        (N = copies of that board, default 1)

Layout: boards are placed row by row (shelf packing) inside MAX_W x MAX_H,
2 mm apart, joined by 4 mm tabs with mouse bites (0.5 mm holes, 0.8 mm
pitch). No frame rails, so the panel stays inside the cheap-prototype size.
PCBWay rules used: >= 1.6 mm between boards for tab routing (we use 2 mm);
stamp holes allowed; V-score would need 0 mm gaps and straight through-cuts,
which mixed designs rarely allow, so mouse bites are the default.

Run with the kikit venv (it needs KiCad's pcbnew): ~/tools/kikit-venv/bin/python
"""
import sys
from pathlib import Path
import pcbnew
from pcbnew import VECTOR2I, FromMM
from kikit import panelize
from kikit.units import mm

MAX_W, MAX_H = 100 * mm, 150 * mm     # 2-up of the 90 x 70 board stacks to 90 x 142 (outside the 100 x 100 tier - see ORDER_GUIDE)
GAP = 2 * mm
TAB_W = 4 * mm
HOLE, PITCH = 0.5 * mm, 0.8 * mm


def board_size(path):
    b = pcbnew.LoadBoard(str(path))
    bb = b.GetBoardEdgesBoundingBox()
    return bb.GetWidth(), bb.GetHeight()


def main(out, specs):
    items = []
    for s in specs:
        path, _, n = s.partition(":")
        w, h = board_size(path)
        items += [(path, w, h)] * (int(n) if n else 1)
    items.sort(key=lambda t: -t[1])          # widest first, shelf packing
    panel = panelize.Panel(out)
    x = y = row_h = 0
    placed = []
    for path, w, h in items:
        if x + w > MAX_W:
            x, y, row_h = 0, y + row_h + GAP, 0
        if y + h > MAX_H:
            sys.exit("panel full: %s does not fit in %.0f x %.0f mm" % (path, MAX_W / mm, MAX_H / mm))
        panel.appendBoard(path, VECTOR2I(x, y), origin=panelize.Origin.TopLeft, tolerance=FromMM(1))
        placed.append((path, x, y, w, h))
        x += w + GAP
        row_h = max(row_h, h)
    panel.buildPartitionLineFromBB()
    panel.buildTabAnnotationsFixed(hcount=3, vcount=2, hwidth=TAB_W, vwidth=TAB_W,
                                   minDistance=5 * mm, ghostSubstrates=[])
    cuts = panel.buildTabsFromAnnotations(fillet=0)
    panel.makeMouseBites(cuts, HOLE, PITCH, offset=int(0.2 * mm), prolongation=int(0.5 * mm))
    panel.addMillFillets(1 * mm)
    panel.save()
    # the copied pours still follow the old outlines: refill so copper keeps its
    # edge clearance from the new tab edges and mouse-bite holes
    b = pcbnew.LoadBoard(out)
    b.GetDesignSettings().m_CopperEdgeClearance = FromMM(0.5)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(out, b)
    b = pcbnew.LoadBoard(out)
    bb = b.GetBoardEdgesBoundingBox()
    npth = sum(1 for f in b.GetFootprints() for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH)
    print("panel %s: %.1f x %.1f mm, %d boards, %d tab cuts, %d mouse-bite holes"
          % (out, bb.GetWidth() / mm, bb.GetHeight() / mm, len(placed), len(cuts), npth))
    for path, px, py, w, h in placed:
        print("  %-32s at (%5.1f, %5.1f)  %.1f x %.1f mm" % (Path(path).name, px / mm, py / mm, w / mm, h / mm))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:])
