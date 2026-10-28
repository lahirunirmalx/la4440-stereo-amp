import sys
sys.path.insert(0, "/home/lahiru/.claude/skills/circuit-sim")
from schem import Schem, check, crossings

DECK = "amp_full.cir"
SUB = ("Rin1 Boac1 Rf1 Rnf1 Rc1 Cc1 Ro1 Rin2 Rf2 Rnf2 Rc2 Cc2 Ro2 Dmute Rdc Rbs1 Rbs2 "
       "Rg1 Rg2 VsL VsR Vctl Vcc").split()


def gnd(sc, x, y):
    sc.gnd_symbol(x, y)
    sc.labels.append(((x, y), "0"))


def term(sc, p, text, dx=14, dy=5, anchor=None):
    sc.terminal(p, "")
    sc.txt((p[0] + dx, p[1] + dy), text, "rail", anchor)


def cap_h(sc, ref, val, x1, x2, y, gap=7, plate=22, lbl_dy=None):
    mid = (x1 + x2) // 2
    sc.wire((x1, y), (mid - gap, y))
    sc.add(f'<path class="wire" d="M{mid - gap} {y - plate} V{y + plate}"/>')
    sc.add(f'<path class="wire" d="M{mid + gap} {y - plate} V{y + plate}"/>')
    sc.wire((mid + gap, y), (x2, y))
    sc._lbl(ref, val, mid, y - plate - 26 if lbl_dy is None else y + lbl_dy, "middle")
    sc.pins[f"{ref}.a"], sc.pins[f"{ref}.b"] = (x1, y), (x2, y)


def plus(sc, x, y):
    sc.txt((x, y), "+", "pol", "middle")


def pot_r(sc, ref, val, x, y1, y2):
    """pot with the wiper on the right and its label on the left"""
    mid = (y1 + y2) // 2
    sc.wire((x, y1), (x, mid - 36))
    sc.add(f'<path class="wire" d="M{x} {mid - 36} l-9 8 l18 14 l-18 14 l18 14 l-18 14 l9 8"/>')
    sc.wire((x, mid + 36), (x, y2))
    sc.wire((x + 44, mid), (x + 16, mid))
    sc.add(f'<polygon class="fillink" points="{x+16},{mid} {x+29},{mid-5} {x+29},{mid+5}"/>')
    sc._lbl(ref, val, x - 20, mid - 4, "end")
    sc.pins[f"{ref}.a"], sc.pins[f"{ref}.b"], sc.pins[f"{ref}.w"] = (x, y1), (x, y2), (x + 44, mid)


def switch_v(sc, ref, val, x, y1, y2):
    mid = (y1 + y2) // 2
    sc.wire((x, y1), (x, mid - 22))
    sc.wire((x, mid + 22), (x, y2))
    sc.add(f'<circle class="wire" cx="{x}" cy="{mid - 22}" r="3" fill="var(--bg)"/>')
    sc.add(f'<circle class="wire" cx="{x}" cy="{mid + 22}" r="3" fill="var(--bg)"/>')
    sc.add(f'<path class="wire" d="M{x} {mid + 19} L{x - 20} {mid - 18}"/>')
    sc._lbl(ref, val, x + 16, mid - 4)
    sc.pins[f"{ref}.a"], sc.pins[f"{ref}.b"] = (x, y1), (x, y2)


# ======================================================= Fig 1: volume + mute
f1 = Schem(1300, 690, "Input, volume and mute: each line input feeds one gang of a 100k "
           "linear pot (or an X9C104 later) whose wiper has a 10k taper resistor to ground, "
           "then 47 uF and 5.6k to the LA4440 input. Mute: toggle SW1 or a GPIO through "
           "2N3904 Q1 and 2N5401 Q2 connects VCC through 1.8k to the LA4440 mute pin, "
           "with 47 uF to ground")
for ch, y, rv, rt, cw, rs, inn, wn, wnode, cnode, out in (
        ("L", 140, "RV1A", "R3", "C13", "R5", "inl", "wl", "w1", "in1", "IN1"),
        ("R", 420, "RV1B", "R4", "C14", "R6", "inr", "wr", "w2", "in2", "IN2")):
    term(f1, (60, y), f"LINE {ch} (J2-{1 if ch == 'L' else 3})", -10, -14)
    f1.wire((60, y), (200, y))
    pot_r(f1, rv, "100k LIN", 200, y, y + 180)
    gnd(f1, 200, y + 180)
    wy = y + 90
    f1.wire((244, wy), (320, wy))
    f1.txt((252, wy + 18), f"J2-{2 if ch == 'L' else 4}", "pin")
    f1.res_v(rt, "10k", 320, wy, wy + 120, side=1)
    gnd(f1, 320, wy + 120)
    f1.dot((320, wy))
    cap_h(f1, cw, "47u", 320, 440, wy)
    plus(f1, 400, wy - 6)
    f1.res_h(rs, "5.6k", 440, 580, wy)
    term(f1, (580, wy), f"{out}: U1 pin {2 if ch == 'L' else 6}")
f1.txt((60, 676), "RV1 = dual B100K on the panel, wired to header J2 (J2-5 = GND). "
       "Swap for 2 x X9C104 later: same pins.", "tiny")

V = 100
f1.netlabel((940, V), "VCC", "up")
f1.wire((940, V), (1044, V), (1150, V))
f1.res_v("R10", "47k", 940, V, 200, side=-1)
f1.wire((940, 200), (1000, 200))
f1.dot((940, 200))
f1.bjt("Q2", "2N5401", 1020, 200, pnp=True)
f1.wire((1044, 142), (1044, V))
f1.dot((1044, V))
f1.res_v("R11", "10k", 940, 200, 330, side=-1)
f1.bjt("Q1", "2N3904", 916, 388)
gnd(f1, 940, 446)
f1.res_h("R12", "4.7k", 720, 840, 388, side=-1)
f1.wire((840, 388), (896, 388))
f1.res_v("R13", "100k", 840, 388, 500, side=-1)
gnd(f1, 840, 500)
f1.dot((840, 388))
term(f1, (690, 388), "MUTE_CTL", -10, -14)
f1.txt((560, 420), "(J2-6, GPIO high = mute)", "tiny")
f1.wire((690, 388), (720, 388))
f1.wire((1044, 258), (1044, 300), (1150, 300))
switch_v(f1, "SW1", "MTS-112 MUTE", 1150, V, 300)
f1.dot((1044, 300))
f1.res_v("R9", "1.8k", 1044, 300, 440, side=-1)
f1.wire((1044, 440), (1150, 440), (1220, 440))
f1.cap_v("C10", "47u", 1150, 440, 540)
plus(f1, 1116, 486)
gnd(f1, 1150, 540)
f1.dot((1150, 440))
term(f1, (1220, 440), "MUTE: U1 pin 4", -124, -12)

exp1 = {
    "RV1A.a": "inl", "RV1A.w": "wl", "RV1A.b": "0", "RV1B.a": "inr", "RV1B.w": "wr", "RV1B.b": "0",
    "R3.a": "wl", "R3.b": "0", "R4.a": "wr", "R4.b": "0",
    "C13.a": "wl", "C13.b": "w1", "C14.a": "wr", "C14.b": "w2",
    "R5.a": "w1", "R5.b": "in1", "R6.a": "w2", "R6.b": "in2",
    "R10.a": "vcc", "R10.b": "pb", "R11.a": "pb", "R11.b": "c1",
    "Q2.C": "mv", "Q2.B": "pb", "Q2.E": "vcc", "Q1.C": "c1", "Q1.B": "b1", "Q1.E": "0",
    "R12.a": "mctl", "R12.b": "b1", "R13.a": "b1", "R13.b": "0",
    "SW1.a": "vcc", "SW1.b": "mv", "R9.a": "mv", "R9.b": "mute", "C10.a": "mute", "C10.b": "0",
}
fig2_refs = "U1 R7 C1 R8 C2 C3 C4 C9 C7 C8 RL1 RL2 C5 R1 C6 R2 C11 C12".split()
p1 = check(f1, exp1, DECK, alias={"RV1A": ["RV1AT", "RV1AB"], "RV1B": ["RV1BT", "RV1BB"],
                                  "SW1": ["Rsw1"]},
           not_drawn=fig2_refs, ignore=SUB)

# ======================================================= Fig 2: LA4440 + outputs + supply
f2 = Schem(1360, 720, "LA4440 stereo core: pin 1 and 7 feedback legs of 470 ohm plus 47 uF "
           "to ground set 30 dB gain; 1000 uF bootstrap caps from pins 13 and 9 to the "
           "outputs; 1000 uF on pin 5; outputs on pins 12 and 10 through 2200 uF to 4 to 8 ohm "
           "speakers with 0.1 uF plus 5 ohm Zobel networks; 12 to 15 V on pin 11 with 2200 uF "
           "and 0.1 uF")
BX0, BX1, BY0, BY1 = 160, 1300, 230, 300
f2.add(f'<rect class="boxf" x="{BX0}" y="{BY0}" width="{BX1 - BX0}" height="{BY1 - BY0}" rx="4"/>')
f2.txt((BX0 + 16, BY0 + 30), "U1  LA4440 (SIP-14, heatsink tab to GND)", "ref")
names = {1: "NF1", 2: "IN1", 3: "PGND", 4: "MUTE", 5: "DC", 6: "IN2", 7: "NF2", 8: "GND2",
         9: "BS2", 10: "OUT2", 11: "VCC", 12: "OUT1", 13: "BS1", 14: "GND1"}
nodes = {1: "nf1", 2: "in1", 3: "0", 4: "mute", 5: "dc", 6: "in2", 7: "nf2", 8: "0",
         9: "bs2", 10: "out2", 11: "vcc", 12: "out1", 13: "bs1", 14: "0"}
px = {n: 140 + 80 * n for n in range(1, 15)}
for n in range(1, 15):
    f2.wire((px[n], BY1), (px[n], 340))
    f2.pins[f"U1.{n}"] = (px[n], 340)
    f2.txt((px[n], BY1 - 8), names[n], "tiny", "middle")
    f2.txt((px[n] + 4, 330), str(n), "pin")
# NF legs
for n, r, c in ((1, "R7", "C1"), (7, "R8", "C2")):
    f2.res_v(r, "470", px[n], 340, 450, side=-1)
    f2.cap_v(c, "47u", px[n], 450, 540)
    plus(f2, px[n] - 34, 486)
    gnd(f2, px[n], 540)
# inputs / mute terminals
for n, t in ((2, "IN1"), (6, "IN2"), (4, "MUTE")):
    f2.wire((px[n], 340), (px[n], 620))
    term(f2, (px[n], 620), t, -14, 28)
for n in (3, 8, 14):
    gnd(f2, px[n], 340)
f2.cap_v("C9", "1000u", px[5], 340, 450)
plus(f2, px[5] - 34, 386)
gnd(f2, px[5], 450)
# outputs
for bs, out, cb, co, rl, cz, rz in ((9, 10, "C4", "C8", "RL2", "C6", "R2"),
                                     (13, 12, "C3", "C7", "RL1", "C5", "R1")):
    xb, xo = px[bs], px[out]
    f2.wire((xb, 340), (xb, 380))
    f2.wire((xo, 340), (xo, 380))
    a, b = (xb, xo) if xb < xo else (xo, xb)
    cap_h(f2, cb, "1000u", a, b, 380, plate=16)
    plus(f2, xb + (-10 if xb < xo else 10), 372 if cb == "C4" else 372)
    f2.wire((xo, 380), (xo, 420))
    f2.dot((xo, 380))
    xz = xo - 120 if out == 10 else xo + 120
    f2.wire((xo, 420), (xz, 420))
    f2.dot((xo, 420))
    f2.cap_v(cz, "0.1u", xz, 420, 500)
    f2.res_v(rz, "5R", xz, 500, 600)
    gnd(f2, xz, 600)
    f2.cap_v(co, "2200u", xo, 420, 520)
    plus(f2, xo - 34, 466)
    f2.res_v(rl, "SPK 4-8R", xo, 520, 640)
    gnd(f2, xo, 640)
f2.wire((px[11], 340), (px[11], 360))
f2.netlabel((px[11], 360), "VCC", "down")
# supply
term(f2, (160, 90), "+12 to 15 V DC, 2 A", -10, -14)
f2.wire((160, 90), (300, 90), (420, 90), (520, 90))
f2.cap_v("C11", "2200u", 300, 90, 180)
plus(f2, 266, 132)
gnd(f2, 300, 180)
f2.cap_v("C12", "0.1u", 420, 90, 180)
gnd(f2, 420, 180)
f2.dot((300, 90)); f2.dot((420, 90))
f2.netlabel((520, 90), "VCC", "right")

exp2 = {f"U1.{n}": nodes[n] for n in range(1, 15)}
exp2.update({
    "R7.a": "nf1", "R7.b": "nfc1", "C1.a": "nfc1", "C1.b": "0",
    "R8.a": "nf2", "R8.b": "nfc2", "C2.a": "nfc2", "C2.b": "0",
    "C9.a": "dc", "C9.b": "0", "C4.a": "bs2", "C4.b": "out2", "C3.a": "out1", "C3.b": "bs1",
    "C8.a": "out2", "C8.b": "spk2", "RL2.a": "spk2", "RL2.b": "0",
    "C7.a": "out1", "C7.b": "spk1", "RL1.a": "spk1", "RL1.b": "0",
    "C6.a": "out2", "C6.b": "zb2", "R2.a": "zb2", "R2.b": "0",
    "C5.a": "out1", "C5.b": "zb1", "R1.a": "zb1", "R1.b": "0",
    "C11.a": "vcc", "C11.b": "0", "C12.a": "vcc", "C12.b": "0",
})
fig1_refs = "RV1AT RV1AB RV1BT RV1BB R3 R4 C13 C14 R5 R6 R10 R11 Q2 Q1 R12 R13 Rsw1 R9 C10".split()
p2 = check(f2, exp2, DECK, alias={"U1": []}, not_drawn=fig1_refs, ignore=SUB)

deck = open(DECK).read()
xl = next(l.split()[1:15] for l in deck.splitlines() if l.startswith("XU1"))
if xl != [nodes[n] for n in range(1, 15)]:
    p2.append(f"XU1 deck {xl} vs drawn {[nodes[n] for n in range(1, 15)]}")

print("FIG1", p1 or "OK", "crossings", crossings(f1))
print("FIG2", p2 or "OK", "crossings", crossings(f2))
open("fig1.svg.part", "w").write(f1.render(min_width=1000))
open("fig2.svg.part", "w").write(f2.render(min_width=1050))
sys.exit(len(p1) + len(p2))
