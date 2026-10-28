"""Generate la4440.kicad_sch + la4440.kicad_pro: LA4440 stereo amplifier with a
volume header (B100K now, 2 x X9C104 later) and toggle / GPIO mute.
Reference designators match ../sim/amp_full.cir and docs/notes.html.
Every pin gets a short stub and a net label; blocks are grouped on the sheet.
Run with /usr/bin/python3 (or any python3).
"""
import json
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from kisch import Sch

FP_R = "Custom:R_Axial_1206"          # 0.25 W: 7.62 mm axial holes + 1206 pads
FP_R1W = "Custom:R_Axial10_2512"      # 1 W: 12.7 mm axial holes + 2512 pads
FP_FILM = "Custom:C_Rect5_1206"       # film cap 5 mm pitch + 1206 pads
FP_TO92 = "Custom:TO92_SOT23"
FP_JQ = "Custom:JQ_3x4"
FP_U1 = "Custom:SIP14H_LA4440"
FP_CP8 = "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm"     # 47 uF 50 V Nichicon UBT
FP_CP12 = "Capacitor_THT:CP_Radial_D12.5mm_P5.00mm"   # 1000 / 2200 uF 25 V Nichicon UBW / UPW
FP_H2 = "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
FP_H3 = "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical"
FP_H6 = "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"
FP_TB2 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"


def u(n):
    return round(n * 2.54, 2)


s = Sch("LA4440 stereo amplifier - volume header, toggle / GPIO mute")
U = s.lib("la4440", "LA4440", libfile=str(HERE / "la4440.kicad_sym"))
R = s.lib("Device", "R")
C = s.lib("Device", "C")
CP = s.lib("Device", "C_Polarized")
POT = s.lib("Device", "R_Potentiometer")
SPK = s.lib("Device", "Speaker")
QPNP = s.lib("Transistor_BJT", "Q_PNP_EBC")     # 2N5401 TO-92: 1=E 2=B 3=C
QNPN = s.lib("Transistor_BJT", "2N3904")        # TO-92: 1=E 2=B 3=C
SPST = s.lib("Switch", "SW_SPST")
H2 = s.lib("Connector_Generic", "Conn_01x02")
H3 = s.lib("Connector_Generic", "Conn_01x03")
H6 = s.lib("Connector_Generic", "Conn_01x06")
H12 = s.lib("Connector_Generic", "Conn_01x12")
H1 = s.lib("Connector_Generic", "Conn_01x01")
FLAG = s.lib("power", "PWR_FLAG")


def part(lib, ref, val, gx, gy, nets, rot=0, fp="", mirror=None, on_board=True, lbl=(3.2, -1.0)):
    """Place a symbol and hang a 1-grid stub + net label off every pin.
    nets: {pin number: net name}; None leaves the pin for the caller."""
    x, y = u(gx), u(gy)
    ref = s.place(lib, ref, val, x, y, rot, mirror=mirror, footprint=fp,
                  ref_at=(x + lbl[0], y + lbl[1]), val_at=(x + lbl[0], y + lbl[1] + 2.3), on_board=on_board)
    for num, net in nets.items():
        px, py = s.pin("%s.%s" % (ref, num))
        dx, dy = px - x, py - y
        if abs(dx) >= abs(dy) and dx != 0:
            q, rot_l = ((px + 2.54, py), 0) if dx > 0 else ((px - 2.54, py), 180)
        else:
            q, rot_l = ((px, py - 2.54), 90) if dy < 0 else ((px, py + 2.54), 270)
        s.wire((px, py), q)
        s.label(q, net, rot_l)
    return ref


def block(gx, gy, title):
    s.text((u(gx), u(gy)), title, 2.0)


# ------------------------------------------------------------------ input and volume
block(4, 8, "INPUT AND VOLUME (RV1/RV2 = one dual pot, off-board, plugs into J2; 2 x X9C104 later on the same pins)")
part(H3, "J1", "LINE IN L/GND/R", 8, 18, {"1": "INL", "2": "GND", "3": "INR"}, fp=FP_H3)
part(H6, "J2", "VOLUME / CONTROL", 8, 34, {"1": "INL", "2": "WL", "3": "INR", "4": "WR", "5": "GND",
                                            "6": "MUTE_CTL"}, fp=FP_H6)
part(POT, "RV1", "B100K lin gang A", 24, 18, {"1": "INL", "2": "WL", "3": "GND"}, on_board=False, lbl=(-13.0, -5.0))
part(POT, "RV2", "B100K lin gang B", 24, 34, {"1": "INR", "2": "WR", "3": "GND"}, on_board=False, lbl=(-13.0, -5.0))
part(R, "R3", "10k", 36, 18, {"1": "WL", "2": "GND"}, fp=FP_R)
part(R, "R4", "10k", 36, 34, {"1": "WR", "2": "GND"}, fp=FP_R)
part(CP, "C13", "47u 50V", 44, 18, {"1": "W1", "2": "WL"}, fp=FP_CP8)
part(CP, "C14", "47u 50V", 44, 34, {"1": "W2", "2": "WR"}, fp=FP_CP8)
part(R, "R5", "5.6k", 52, 18, {"1": "W1", "2": "IN1"}, fp=FP_R)
part(R, "R6", "5.6k", 52, 34, {"1": "W2", "2": "IN2"}, fp=FP_R)

# ------------------------------------------------------------------ mute
block(4, 48, "MUTE: SW1 (off-board, J3) or MUTE_CTL high (GPIO) - wire-OR")
part(H2, "J3", "MUTE SWITCH", 8, 58, {"1": "VCC", "2": "MV"}, fp=FP_H2)
part(SPST, "SW1", "MTS-112 MUTE", 18, 58, {"1": "VCC", "2": "MV"}, on_board=False, lbl=(-4.0, -5.0))
part(R, "R10", "47k", 28, 58, {"1": "VCC", "2": "PB"}, fp=FP_R)
part(QPNP, "Q2", "2N5401", 38, 58, {"1": "VCC", "2": "PB", "3": "MV"}, fp=FP_TO92, mirror="x")
part(R, "R11", "10k", 28, 70, {"1": "PB", "2": "Q1C"}, fp=FP_R)
part(QNPN, "Q1", "2N3904", 38, 72, {"1": "GND", "2": "Q1B", "3": "Q1C"}, fp=FP_TO92)
part(R, "R12", "4.7k", 48, 72, {"1": "MUTE_CTL", "2": "Q1B"}, fp=FP_R)
part(R, "R13", "100k", 56, 72, {"1": "Q1B", "2": "GND"}, fp=FP_R)
part(R, "R9", "1.8k", 48, 58, {"1": "MV", "2": "MUTE"}, fp=FP_R)
part(CP, "C10", "47u 50V", 56, 58, {"1": "MUTE", "2": "GND"}, fp=FP_CP8)

# ------------------------------------------------------------------ amplifier
block(70, 8, "LA4440 STEREO CORE (gain 30 dB: R7/R8 470R in the feedback legs)")
part(U, "U1", "LA4440", 88, 32, {"1": "NF1", "2": "IN1", "3": "GND", "4": "MUTE", "5": "DC", "6": "IN2",
                                 "7": "NF2", "8": "GND", "9": "BS2", "10": "OUT2", "11": "VCC",
                                 "12": "OUT1", "13": "BS1", "14": "GND"}, fp=FP_U1, lbl=(-10.0, -20.0))
part(R, "R7", "470", 72, 52, {"1": "NF1", "2": "NFC1"}, fp=FP_R)
part(CP, "C1", "47u 50V", 72, 63, {"1": "NFC1", "2": "GND"}, fp=FP_CP8)
part(R, "R8", "470", 80, 52, {"1": "NF2", "2": "NFC2"}, fp=FP_R)
part(CP, "C2", "47u 50V", 80, 63, {"1": "NFC2", "2": "GND"}, fp=FP_CP8)
part(CP, "C9", "1000u 25V", 88, 56, {"1": "DC", "2": "GND"}, fp=FP_CP12)
part(CP, "C3", "1000u 25V", 104, 52, {"1": "BS1", "2": "OUT1"}, fp=FP_CP12)
part(CP, "C4", "1000u 25V", 112, 52, {"1": "BS2", "2": "OUT2"}, fp=FP_CP12)

block(120, 8, "OUTPUTS (Zobel = 0.1u film + 2 x 10R 1W in parallel)")
part(CP, "C7", "2200u 25V", 124, 20, {"1": "OUT1", "2": "SPK1"}, fp=FP_CP12)
part(C, "C5", "0.1u film", 132, 20, {"1": "OUT1", "2": "ZB1"}, fp=FP_FILM)
part(R, "R14", "10R 1W (R1 pair)", 132, 30, {"1": "ZB1", "2": "GND"}, fp=FP_R1W)
part(R, "R15", "10R 1W (R1 pair)", 138, 30, {"1": "ZB1", "2": "GND"}, fp=FP_R1W)
part(H2, "J5", "SPEAKER L", 148, 20, {"1": "SPK1", "2": "GND"}, fp=FP_TB2)
part(SPK, "LS1", "4-8R", 158, 20, {"1": "SPK1", "2": "GND"}, on_board=False, lbl=(-2.0, -7.5))
part(CP, "C8", "2200u 25V", 124, 44, {"1": "OUT2", "2": "SPK2"}, fp=FP_CP12)
part(C, "C6", "0.1u film", 132, 44, {"1": "OUT2", "2": "ZB2"}, fp=FP_FILM)
part(R, "R16", "10R 1W (R2 pair)", 132, 54, {"1": "ZB2", "2": "GND"}, fp=FP_R1W)
part(R, "R17", "10R 1W (R2 pair)", 138, 54, {"1": "ZB2", "2": "GND"}, fp=FP_R1W)
part(H2, "J6", "SPEAKER R", 148, 44, {"1": "SPK2", "2": "GND"}, fp=FP_TB2)
part(SPK, "LS2", "4-8R", 158, 44, {"1": "SPK2", "2": "GND"}, on_board=False, lbl=(-2.0, -7.5))

# ------------------------------------------------------------------ supply
block(70, 72, "SUPPLY 12 to 15 V DC, 2 A (18 V max)")
part(H2, "J4", "DC IN +/-", 74, 82, {"1": "VCC", "2": "GND"}, fp=FP_TB2)
part(CP, "C11", "2200u 25V", 84, 82, {"1": "VCC", "2": "GND"}, fp=FP_CP12)
part(C, "C12", "0.1u", 92, 82, {"1": "VCC", "2": "GND"}, fp=FP_FILM)
part(H1, "J7", "HEATSINK GND (M3 lug)", 114, 82, {"1": "GND"}, fp="MountingHole:MountingHole_3.2mm_M3_Pad")
part(FLAG, "#FLG", "PWR_FLAG", 100, 80, {"1": "VCC"})
part(FLAG, "#FLG", "PWR_FLAG", 106, 80, {"1": "GND"})

# ------------------------------------------------------------------ pinout fields
block(4, 88, "TRANSISTOR PINOUT FIELDS: columns L E B C, rows = legs 1..3")
P = s.pin
for ref, val, gx, nets in (("JQ1", "Q1 2N3904 pinout field", 14, ("GND", "Q1B", "Q1C")),
                           ("JQ2", "Q2 2N5401 pinout field", 40, ("VCC", "PB", "MV"))):
    s.place(H12, ref, val, u(gx), u(100), 0, footprint=FP_JQ, ref_at=(u(gx) - 9.0, u(100) - 17.0),
            val_at=(u(gx) - 9.0, u(100) - 15.0))
    for pin in range(1, 13):
        px, py = P("%s.%d" % (ref, pin))
        col = (pin - 1) % 4
        if col == 0:
            s.no_connect((px, py))
            continue
        s.wire((px, py), (px - 5.08, py))
        s.label((px - 5.08, py), nets[col - 1], 180)

notes = [
    "Verified in ngspice (../sim/amp_full.cir): 30.3 dB, 20 Hz - 190 kHz, 4.4 W into 4R at 13.2 V before clipping, mute pin 6.9 mA.",
    "RV1 is a dual B100K LINEAR pot (or 2 x X9C104 on J2 later: they need 5 V and CS/INC/U-D from the ESP32). R3/R4 give it a near-log law.",
    "U1 heatsink tab to GND. Off-board: RV1/RV2 (dual pot), SW1, LS1, LS2. Not built yet - see docs/notes.html for the simulation and the unverified items.",
]
for i, t in enumerate(notes):
    s.text((u(70), u(100) + i * 4.0), t)

out = HERE / "la4440.kicad_sch"
s.write(out)
pro = {
    "board": {"design_settings": {"defaults": {}, "diff_pair_dimensions": [], "drc_exclusions": [],
                                  "rules": {}, "track_widths": [], "via_dimensions": []}},
    "boards": [], "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": "la4440.kicad_pro", "version": 1},
    "net_settings": {"classes": [], "meta": {"version": 0}},
    "pcbnew": {"page_layout_descr_file": ""},
    "sheets": [[s.uuid, "Root"]], "text_variables": {},
}
(HERE / "la4440.kicad_pro").write_text(json.dumps(pro, indent=2))
(HERE / "sym-lib-table").write_text('(sym_lib_table\n  (version 7)\n  (lib (name "la4440")(type "KiCad")(uri "${KIPRJMOD}/la4440.kicad_sym")(options "")(descr "LA4440 symbol"))\n)\n')
print("wrote", out, "symbols:", len(s.refs), "wires:", len(s.wires))
