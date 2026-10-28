"""Build la4440.kicad_pcb from the KiCad netlist (la4440.net) with the pcbnew API.

Run with /usr/bin/python3 (the PlatformIO python has no pcbnew).
90 x 70 mm 2-layer board (standard 7 x 9 cm proto-board size). Places every
on-board footprint from the PLACE table, assigns nets, links footprints to
their schematic symbols (KIID path) for DRC schematic parity, and exports a
Specctra DSN for freerouting. build_pcb.sh does the rest.
Off-board symbols (no footprint in the schematic) are skipped.
"""
import re
import sys
from pathlib import Path
import pcbnew
from pcbnew import VECTOR2I, FromMM

HERE = Path(__file__).parent
FPDIR = "/usr/share/kicad/footprints/"
BX, BY, BW, BH = 50.0, 50.0, 90.0, 70.0      # board origin and size (mm)
STEM = "la4440"
POUR_NET = "GND"
POWER_NETS = ["/GND", "/VCC", "/OUT1", "/OUT2", "/SPK1", "/SPK2"]

from place import PLACE, TEXTS, JQ_REFS


def shrink_boundary(dsn_path, margin_mm=0.6):
    txt = open(dsn_path).read()
    m = re.search(r'\(boundary\s*\(path pcb 0((?:\s+-?\d+)+)\s*\)', txt)
    nums = [int(v) for v in m.group(1).split()]
    xs, ys = nums[0::2], nums[1::2]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    d = int(margin_mm * 1000)
    out = []
    for x, y in zip(xs, ys):
        out += [x - d if x > cx else x + d, y - d if y > cy else y + d]
    txt = txt[:m.start()] + "(boundary (path pcb 0 " + " ".join(str(v) for v in out) + ")" + txt[m.end():]
    txt = txt.replace("(clearance 200)", "(clearance 250)", 1)
    open(dsn_path, "w").write(txt)


def make_jq_footprint(board, template):
    """3 x 4 field of plated holes. Pin n: row (n-1)//4, column (n-1)%4;
    column 0 = L (transistor leg, rightmost hole), columns 1..3 = E, B, C going left."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPIDAsString("Custom:JQ_3x4")
    lib, name = template.split(":")
    src = pcbnew.FootprintLoad(FPDIR + lib + ".pretty", name)
    proto = [pd for pd in src.Pads() if pd.GetNumber() == "2"][0]
    for n in range(1, 13):
        row, col = (n - 1) // 4, (n - 1) % 4
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(proto.GetAttribute())
        pad.SetShape(pcbnew.PAD_SHAPE_RECT if col == 0 else proto.GetShape())
        pad.SetSize(proto.GetSize())
        pad.SetDrillSize(proto.GetDrillSize())
        pad.SetLayerSet(proto.GetLayerSet())
        pad.SetNumber(str(n))
        pad.SetPosition(VECTOR2I(FromMM((3 - col) * 2.54), FromMM(row * 2.54)))
        fp.Add(pad)
    for layer, margin in [(pcbnew.F_CrtYd, 1.81), (pcbnew.F_SilkS, 1.5)]:
        r = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_RECT)
        r.SetStart(VECTOR2I(FromMM(-margin), FromMM(-margin)))
        r.SetEnd(VECTOR2I(FromMM(3 * 2.54 + margin), FromMM(2 * 2.54 + margin)))
        r.SetLayer(layer)
        r.SetWidth(FromMM(0.05 if layer == pcbnew.F_CrtYd else 0.12))
        fp.Add(r)
    return fp


def make_sip14(board):
    """Sanyo SIP-14H (LA4440): one straight row, 2.54 mm pitch, 1.0 mm drill. Pin 1 at the
    anchor, pins run +x. The body and heatsink tab sit on the -y side (toward the top edge)."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPIDAsString("Custom:SIP14H_LA4440")
    for n in range(1, 15):
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT if n == 1 else pcbnew.PAD_SHAPE_OVAL)
        pad.SetSize(VECTOR2I(FromMM(1.7), FromMM(2.4)))
        pad.SetDrillSize(VECTOR2I(FromMM(1.0), FromMM(1.0)))
        pad.SetLayerSet(pad.PTHMask())
        pad.SetNumber(str(n))
        pad.SetPosition(VECTOR2I(FromMM((n - 1) * 2.54), 0))
        fp.Add(pad)
    x0, x1 = 16.51 - 18.5, 16.51 + 18.5          # body 37 mm centred on the pin row
    for layer, y0, y1, w in [(pcbnew.F_SilkS, -4.6, 1.6, 0.12), (pcbnew.F_CrtYd, -4.9, 1.9, 0.05)]:
        r = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_RECT)
        r.SetStart(VECTOR2I(FromMM(x0 if layer == pcbnew.F_SilkS else x0 - 0.3), FromMM(y0)))
        r.SetEnd(VECTOR2I(FromMM(x1 if layer == pcbnew.F_SilkS else x1 + 0.3), FromMM(y1)))
        r.SetLayer(layer); r.SetWidth(FromMM(w)); fp.Add(r)
    t = pcbnew.PCB_TEXT(fp)
    t.SetText("TAB / HEATSINK SIDE"); t.SetLayer(pcbnew.F_SilkS)
    t.SetPosition(VECTOR2I(FromMM(16.51), FromMM(-3.0)))
    t.SetTextSize(VECTOR2I(FromMM(0.9), FromMM(0.9))); t.SetTextThickness(FromMM(0.15))
    fp.Add(t)
    return fp


# hybrid = through-hole pattern + the SMD twin's pads ("nS" pads share pin n's net)
HYBRIDS = {
    "Custom:R_Axial_1206": dict(tht=("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal"),
                                smd=("Resistor_SMD", "R_1206_3216Metric_Pad1.30x1.75mm_HandSolder"),
                                at=(3.81, 0), oval=4.2),
    "Custom:R_Axial10_2512": dict(tht=("Resistor_THT", "R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal"),
                                  smd=("Resistor_SMD", "R_2512_6332Metric_Pad1.40x3.35mm_HandSolder"),
                                  at=(6.35, 0), oval=8.8),     # oval reaches the 2512 pads: no bridge track needed
    "Custom:D_DO41_SMA": dict(tht=("Diode_THT", "D_DO-41_SOD81_P10.16mm_Horizontal"),
                              smd=("Diode_SMD", "D_SMA_Handsoldering"),
                              at=(5.08, 0), oval=4.4),
    "Custom:C_Rect5_1206": dict(tht=("Capacitor_THT", "C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"),
                                smd=("Capacitor_SMD", "C_1206_3216Metric_Pad1.33x1.80mm_HandSolder"),
                                at=(2.5, 0), oval=None),
    "Custom:TO92_SOT23": dict(tht=("Package_TO_SOT_THT", "TO-92_Inline"),
                              smd=("Package_TO_SOT_SMD", "SOT-23_Handsoldering"),
                              at=(1.27, 4.0), oval=None, smd_map={"1": "2", "2": "1", "3": "3"}),
}


def make_hybrid(board, name):
    spec = HYBRIDS[name]
    fp = pcbnew.FOOTPRINT(board)
    fp.SetFPIDAsString(name)
    tlib, tname = spec["tht"]
    slib, sname = spec["smd"]
    tht = pcbnew.FootprintLoad(FPDIR + tlib + ".pretty", tname)
    smd = pcbnew.FootprintLoad(FPDIR + slib + ".pretty", sname)
    for p in tht.Pads():
        q = pcbnew.PAD(fp)
        q.SetAttribute(p.GetAttribute()); q.SetShape(p.GetShape()); q.SetSize(p.GetSize())
        q.SetDrillSize(p.GetDrillSize()); q.SetLayerSet(p.GetLayerSet()); q.SetNumber(p.GetNumber())
        q.SetPosition(p.GetPosition())
        if spec["oval"]:
            q.SetShape(pcbnew.PAD_SHAPE_OVAL)
            q.SetSize(VECTOR2I(FromMM(spec["oval"]), FromMM(1.7)))
        fp.Add(q)
    ax, ay = spec["at"]
    for p in smd.Pads():
        q = pcbnew.PAD(fp)
        q.SetAttribute(pcbnew.PAD_ATTRIB_SMD); q.SetShape(p.GetShape()); q.SetSize(p.GetSize())
        q.SetLayerSet(p.GetLayerSet())
        # SOT-23 BJTs (MMBT3904, MMBT5401) are B-E-C while the TO-92 parts are E-B-C:
        # SOT pad 1 carries the base (pin 2) net, SOT pad 2 the emitter (pin 1) net
        q.SetNumber(spec.get("smd_map", {}).get(p.GetNumber(), p.GetNumber()) + "S")
        q.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        q.SetPosition(VECTOR2I(FromMM(ax + p.GetPosition().x / 1e6), FromMM(ay + p.GetPosition().y / 1e6)))
        fp.Add(q)
    xs, ys = [], []
    for q in fp.Pads():
        cx, cy = q.GetPosition().x / 1e6, q.GetPosition().y / 1e6
        hx, hy = q.GetSize().x / 2e6, q.GetSize().y / 2e6
        xs += [cx - hx, cx + hx]; ys += [cy - hy, cy + hy]
    for layer, m, w in [(pcbnew.F_CrtYd, 0.5, 0.05), (pcbnew.F_SilkS, 0.75, 0.12)]:
        r = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_RECT)
        r.SetStart(VECTOR2I(FromMM(min(xs) - m), FromMM(min(ys) - m)))
        r.SetEnd(VECTOR2I(FromMM(max(xs) + m), FromMM(max(ys) + m)))
        r.SetLayer(layer); r.SetWidth(FromMM(w)); fp.Add(r)
    return fp


def parse_netlist(path):
    txt = Path(path).read_text()
    comps = {}
    ctxt = txt[txt.find("(components"):txt.find("(libparts")]
    for chunk in ctxt.split("(comp (ref ")[1:]:
        ref = re.match(r'"([^"]+)"', chunk).group(1)
        val = re.search(r'\(value "([^"]*)"\)', chunk).group(1)
        fp = re.search(r'\(footprint "([^"]*)"\)', chunk)
        fp = fp.group(1) if fp else ""
        ts = re.findall(r'\(tstamps "([^"]+)"\)', chunk)[-1]
        comps[ref] = (val, fp, ts)
    nets = {}
    ntxt = txt[txt.find("(nets"):]
    for chunk in ntxt.split("(net (code")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', chunk).group(1)
        nets[name] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk)
    return comps, nets


def main():
    comps, nets = parse_netlist(HERE / (STEM + ".net"))
    onboard = {r: v for r, v in comps.items() if v[1]}
    offboard = sorted(r for r in comps if not comps[r][1])
    nets = {n: [p for p in pins if p[0] in onboard] for n, pins in nets.items()}
    nets = {n: pins for n, pins in nets.items() if pins}
    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetCustomTrackWidth(FromMM(0.5))
    ds.SetCustomViaSize(FromMM(0.9))
    ds.SetCustomViaDrill(FromMM(0.5))
    ds.UseCustomTrackViaSize(True)
    ds.m_MinClearance = FromMM(0.2)
    ds.m_CopperEdgeClearance = FromMM(0.5)
    dflt = ds.m_NetSettings.GetDefaultNetclass()
    dflt.SetClearance(FromMM(0.2))
    dflt.SetTrackWidth(FromMM(0.5))
    dflt.SetViaDiameter(FromMM(0.9))
    dflt.SetViaDrill(FromMM(0.5))
    # signal tracks 0.3 mm (fits between 2.54 mm header pads); supply and speaker paths 1.0 mm
    ds.SetCustomTrackWidth(FromMM(0.3))
    dflt.SetTrackWidth(FromMM(0.3))
    ns = ds.m_NetSettings
    pw = pcbnew.NETCLASS("Power")
    pw.SetClearance(FromMM(0.2))
    pw.SetTrackWidth(FromMM(1.0))
    pw.SetViaDiameter(FromMM(1.2))
    pw.SetViaDrill(FromMM(0.6))
    ns.SetNetclass("Power", pw)
    for n in POWER_NETS:
        ns.SetNetclassPatternAssignment(n, "Power")

    pts = [(BX, BY), (BX + BW, BY), (BX + BW, BY + BH), (BX, BY + BH)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(VECTOR2I(FromMM(a[0]), FromMM(a[1])))
        seg.SetEnd(VECTOR2I(FromMM(b[0]), FromMM(b[1])))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(FromMM(0.1))
        board.Add(seg)

    netitems = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netitems[name] = ni
    board.SynchronizeNetsAndNetClasses(True)
    pin_net = {(ref, pin): name for name, nodes in nets.items() for ref, pin in nodes}

    missing = [r for r in onboard if r not in PLACE]
    extra = [r for r in PLACE if r not in onboard]
    if missing or extra:
        sys.exit("placement table mismatch: missing %s extra %s" % (missing, extra))
    for ref, (val, fpname, ts) in onboard.items():
        if fpname == "Custom:SIP14H_LA4440":
            fp = make_sip14(board)
        elif fpname == "Custom:JQ_3x4":
            fp = make_jq_footprint(board, "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")
        elif fpname in HYBRIDS:
            fp = make_hybrid(board, fpname)
        else:
            lib, name = fpname.split(":")
            fp = pcbnew.FootprintLoad(FPDIR + lib + ".pretty", name)
            if fp is None:
                sys.exit("footprint not found: " + fpname)
            fp.SetFPIDAsString(fpname)
        fp.SetReference(ref)
        fp.SetValue(val)
        fp.SetPath(pcbnew.KIID_PATH("/" + ts))
        x, y, rot = PLACE[ref]
        fp.SetPosition(VECTOR2I(FromMM(BX + x), FromMM(BY + y)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            num = pad.GetNumber()
            key = (ref, num[:-1] if num.endswith("S") else num)
            if key in pin_net:
                pad.SetNet(netitems[pin_net[key]])
        fp.Reference().SetTextSize(VECTOR2I(FromMM(0.9), FromMM(0.9)))
        fp.Reference().SetTextThickness(FromMM(0.15))
        board.Add(fp)
        cy = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
        fp.Reference().SetPosition(VECTOR2I(cy.GetCenter().x, cy.GetTop() - FromMM(0.7)))
        fp.Reference().SetTextAngleDegrees(0)
        if ref.startswith("JQ"):
            fp.Reference().SetVisible(False)

    # column labels above every pinout field
    for ref in JQ_REFS:
        px, py, _ = PLACE[ref]
        for col, lbl in enumerate(["L", "E", "B", "C"]):
            t = pcbnew.PCB_TEXT(board)
            t.SetText(lbl)
            t.SetPosition(VECTOR2I(FromMM(BX + px + (3 - col) * 2.54), FromMM(BY + py - 2.4)))
            t.SetLayer(pcbnew.F_SilkS)
            t.SetTextSize(VECTOR2I(FromMM(0.8), FromMM(0.8)))
            t.SetTextThickness(FromMM(0.15))
            board.Add(t)

    # corner mounting holes (2.5 mm, 2.5 mm inset, like a 6 x 8 cm proto board)
    for i, (hx, hy) in enumerate([(BX + 2.5, BY + 2.5), (BX + BW - 2.5, BY + 2.5),
                                  (BX + 2.5, BY + BH - 2.5), (BX + BW - 2.5, BY + BH - 2.5)], start=1):
        fp = pcbnew.FOOTPRINT(board)
        fp.SetFPIDAsString("Custom:Hole_2.5mm")
        fp.SetReference("H%d" % i)
        fp.SetValue("M2.5")
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(VECTOR2I(FromMM(2.5), FromMM(2.5)))
        pad.SetDrillSize(VECTOR2I(FromMM(2.5), FromMM(2.5)))
        pad.SetNumber("")
        fp.Add(pad)
        c = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_CIRCLE)
        c.SetCenter(VECTOR2I(0, 0)); c.SetEnd(VECTOR2I(FromMM(2.0), 0))
        c.SetLayer(pcbnew.F_CrtYd); c.SetWidth(FromMM(0.05)); fp.Add(c)
        fp.Reference().SetVisible(False)
        fp.SetPosition(VECTOR2I(FromMM(hx), FromMM(hy)))
        board.Add(fp)

    for item in TEXTS:
        text, x, y, size = item[:4]
        back = len(item) > 4 and item[4] == "B"
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(VECTOR2I(FromMM(BX + x), FromMM(BY + y)))
        t.SetLayer(pcbnew.B_SilkS if back else pcbnew.F_SilkS)
        t.SetMirrored(back)
        t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size)))
        t.SetTextThickness(FromMM(0.15))
        board.Add(t)

    # courtyard overlap and edge check
    boxes = []
    for fp in board.GetFootprints():
        if hasattr(fp, "BuildCourtyardCaches"):
            fp.BuildCourtyardCaches()
        boxes.append((fp.GetReference(), fp.GetCourtyard(pcbnew.F_CrtYd).BBox()))
    bad = 0
    for i in range(len(boxes)):
        r, b = boxes[i]
        if (b.GetLeft() < FromMM(BX) or b.GetRight() > FromMM(BX + BW)
                or b.GetTop() < FromMM(BY) or b.GetBottom() > FromMM(BY + BH)):
            print("OFF BOARD:", r, [round(v / 1e6 - o, 1) for v, o in ((b.GetLeft(), BX), (b.GetTop(), BY), (b.GetRight(), BX), (b.GetBottom(), BY))]); bad += 1
        for j in range(i + 1, len(boxes)):
            r2, b2 = boxes[j]
            if b.Intersects(b2):
                print("OVERLAP:", r, r2); bad += 1
    lib = str(HERE / "Custom.pretty")
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    import os
    os.makedirs(lib, exist_ok=True)
    saved = set()
    for fp in board.GetFootprints():
        name = fp.GetFPID().GetLibItemName().wx_str() if hasattr(fp.GetFPID().GetLibItemName(), "wx_str") else str(fp.GetFPID().GetLibItemName())
        if str(fp.GetFPID().GetLibNickname()) == "Custom" and name not in saved and not name.startswith("Hole"):
            c = pcbnew.FOOTPRINT(fp)
            c.SetPosition(VECTOR2I(0, 0)); c.SetOrientationDegrees(0)
            for pad in c.Pads():
                pad.SetNetCode(0)
            io.FootprintSave(lib, c)
            saved.add(name)
    out = str(HERE / (STEM + ".kicad_pcb"))
    pcbnew.ExportSpecctraDSN(board, str(HERE / (STEM + ".dsn")))
    shrink_boundary(HERE / (STEM + ".dsn"))
    pcbnew.SaveBoard(out, board)
    print("wrote", out, "footprints:", len(onboard), "nets:", len(nets), "off-board skipped:", offboard, "placement problems:", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
