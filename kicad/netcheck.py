"""Compare the KiCad netlist (la4440.net) against the ngspice deck (../sim/amp_full.cir).

Usage: /usr/bin/python3 netcheck.py la4440.net ../sim/amp_full.cir
Net names do not matter, only the partition: every group of pins the deck
says share a node must be one KiCad net, and no two deck nodes may be merged.
"""
import re
import sys
sys.path.insert(0, "/home/lahiru/.claude/skills/circuit-sim")
from schem import spice_nodes

# KiCad "REF.pin" -> deck "REF.pin" (deck = ../sim/amp_full.cir)
REFMAP = {
    # U1 has no deck key (spice_nodes skips X lines): map each pin to a deck pin on the same node
    "U1.1": "R7.a", "U1.2": "R5.b", "U1.3": "C1.b", "U1.4": "R9.b", "U1.5": "C9.a", "U1.6": "R6.b",
    "U1.7": "R8.a", "U1.8": "C2.b", "U1.9": "C4.a", "U1.10": "C4.b", "U1.11": "C11.a", "U1.12": "C3.a",
    "U1.13": "C3.b", "U1.14": "C1.b",
    "Q1.1": "Q1.E", "Q1.2": "Q1.B", "Q1.3": "Q1.C",          # 2N3904 symbol: E B C
    "Q2.1": "Q2.E", "Q2.2": "Q2.B", "Q2.3": "Q2.C",          # Q_PNP_EBC
    # volume pot = two resistors per gang in the deck
    "RV1.1": "RV1AT.a", "RV1.2": "RV1AT.b", "RV1.3": "RV1AB.b",
    "RV2.1": "RV1BT.a", "RV2.2": "RV1BT.b", "RV2.3": "RV1BB.b",
    "SW1.1": "Rsw1.a", "SW1.2": "Rsw1.b",
    "J1.1": "VsL.a", "J1.2": "VsL.b", "J1.3": "VsR.a",
    "J2.1": "RV1AT.a", "J2.2": "RV1AT.b", "J2.3": "RV1BT.a", "J2.4": "RV1BT.b", "J2.5": "RV1AB.b",
    "J2.6": "R12.a",
    "J3.1": "Rsw1.a", "J3.2": "Rsw1.b",
    "J4.1": "Vcc.a", "J4.2": "Vcc.b", "J7.1": "C1.b",
    "J5.1": "RL1.a", "J5.2": "RL1.b", "LS1.1": "RL1.a", "LS1.2": "RL1.b",
    "J6.1": "RL2.a", "J6.2": "RL2.b", "LS2.1": "RL2.a", "LS2.2": "RL2.b",
    # the deck's 5R Zobel resistors are two 10R 1 W in parallel on the board
    "R14.1": "R1.a", "R14.2": "R1.b", "R15.1": "R1.a", "R15.2": "R1.b",
    "R16.1": "R2.a", "R16.2": "R2.b", "R17.1": "R2.a", "R17.2": "R2.b",
    # polarised caps drawn + first where the deck lists the + node second
    "C3.1": "C3.b", "C3.2": "C3.a", "C13.1": "C13.b", "C13.2": "C13.a", "C14.1": "C14.b", "C14.2": "C14.a",
}
SKIP_PINS = set()
SKIP_REFS = {"JQ1", "JQ2"}
_SUB = ("Rin1 Rf1 Rnf1 Rc1 Cc1 Ro1 Rin2 Rf2 Rnf2 Rc2 Cc2 Ro2 Dmute Rdc Rbs1 Rbs2 Rg1 Rg2 Vctl "
        "VsR RV1AB RV1BB").split()
DECK_IGNORE = {"%s.%s" % (r, p) for r in _SUB for p in ("a", "b", "anode", "cathode")}
DIODE_PIN = {"1": "cathode", "2": "anode"}
TWO_PIN = {"1": "a", "2": "b"}


def kicad_nets(netfile):
    txt = open(netfile).read()
    txt = txt[txt.find("(nets"):]
    nets = {}
    for chunk in txt.split("(net (code")[1:]:
        name = re.search(r'\(name "([^"]+)"\)', chunk).group(1)
        nets[name] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk)
    return nets


def main(netfile, deck):
    dm = spice_nodes(deck)
    problems, seen, node_of_net = [], set(), {}
    for name, pins in kicad_nets(netfile).items():
        nodes = {}
        live = [p for p in pins if p[0] not in SKIP_REFS and "%s.%s" % p not in SKIP_PINS and not p[0].startswith("#")]
        for ref, pin in live:
            key = "%s.%s" % (ref, pin)
            if key in REFMAP:
                dkey = REFMAP[key]
            elif ref[0] == "D":
                dkey = "%s.%s" % (ref, DIODE_PIN[pin])
            else:
                dkey = "%s.%s" % (ref, TWO_PIN[pin])
            if dkey not in dm:
                problems.append("%s -> %s not in deck" % (key, dkey))
                continue
            seen.add(dkey)
            nodes.setdefault(dm[dkey], []).append(key)
        if len(nodes) > 1:
            problems.append("KiCad net %s merges deck nodes %s" % (name, nodes))
        if len(live) == 1:
            problems.append("KiCad net %s has a single pin %s" % (name, live))
        if nodes:
            node = list(nodes)[0]
            if node in node_of_net:
                problems.append("deck node %s split across KiCad nets %s and %s" % (node, node_of_net[node], name))
            node_of_net[node] = name
    missing = set(dm) - seen - DECK_IGNORE
    if missing:
        problems.append("deck pins never seen in KiCad netlist: %s" % sorted(missing))
    return problems


if __name__ == "__main__":
    probs = main(sys.argv[1], sys.argv[2])
    print("NETCHECK:", probs or "OK")
    sys.exit(1 if probs else 0)
