import json, sys
sys.path.insert(0, "/home/lahiru/.claude/skills/circuit-sim")
from circuitjs import Circuit, HEADER_AUDIO
from connectivity import cjs_posts

ck = Circuit(HEADER_AUDIO)
refs = []
def add(ref, fn, *a, **k):
    refs.append(ref); fn(*a, **k)

# one channel. LA4440 drawn as its equivalent: op-amp + internal Rf 20k / RNF 50 / ri 30k,
# split +/-6.6 V supply so the output idles at 0 V (the real chip idles at 6.8 V)
add("Vs", ck.vac, 48, 336, 48, 256, 0.15, freq=1000)
ck.gnd(48, 336)
add("Rs", ck.r, 48, 256, 48, 176, 100)
ck.w(48, 176, 128, 176)
add("RV1", ck.pot, 128, 176, 128, 336, 100e3, position=1.0, label="Volume")
ck.gnd(128, 336)
wx, wy = [(x, y) for n, x, y in cjs_posts(ck.lines[-2].split())[1] if n == "wiper"][0]
ck.w(wx, wy, 224, wy)
add("Rlaw", ck.r, 224, wy, 224, wy + 80, 10e3)
ck.gnd(224, wy + 80)
add("Cw", ck.c, 224, wy, 304, wy, 47e-6)
add("Rser", ck.r, 304, wy, 400, wy, 5.6e3)
add("Rin", ck.r, 400, wy, 400, wy + 80, 30e3)
ck.gnd(400, wy + 80)
ck.w(400, wy, 480, wy)
refs.append("U1"); ck._add("a 480 %d 576 %d 8 6.1 -6.3 7.5e6 0 0 3000" % (wy - 16, wy - 16))
ck.w(480, wy - 32, 480, wy - 96)
add("Rf", ck.r, 576, wy - 96, 480, wy - 96, 20e3)
ck.w(576, wy - 16, 576, wy - 96)
add("Rnf", ck.r, 480, wy - 96, 384, wy - 96, 50)
add("Rnfx", ck.r, 384, wy - 96, 384, wy - 176, 470)
add("C1", ck.c, 384, wy - 176, 304, wy - 176, 47e-6)
ck.gnd(304, wy - 176)
add("C7", ck.c, 576, wy - 16, 672, wy - 16, 2200e-6)
add("Rspk", ck.r, 672, wy - 16, 672, wy + 64, 4)
ck.gnd(672, wy + 64)
add("C5", ck.c, 576, wy - 16, 576, wy + 48, 0.1e-6)
add("R1", ck.r, 576, wy + 48, 576, wy + 128, 5)
ck.gnd(576, wy + 128)
ck.note(48, 420, 400, 420, "LA4440 one channel, 30 dB: drag Volume, scope Rspk", 16)
url = ck.save("la4440-channel", ".")

deck = {"_refs": refs,
        "Vs": ["0", "src"], "Rs": ["src", "inp"], "RV1": ["inp", "0", "wip"],
        "Rlaw": ["wip", "0"], "Cw": ["wip", "w2"], "Rser": ["w2", "in1"], "Rin": ["in1", "0"],
        "U1": ["fbn", "in1", "out1"], "Rf": ["out1", "fbn"], "Rnf": ["fbn", "nf"],
        "Rnfx": ["nf", "nfc"], "C1": ["nfc", "0"], "C7": ["out1", "spk"], "Rspk": ["spk", "0"],
        "C5": ["out1", "zb"], "R1": ["zb", "0"]}
json.dump(deck, open("la4440-channel.deck.json", "w"), indent=1)
print(len(url))
