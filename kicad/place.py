"""Footprint placement for la4440.kicad_pcb: ref -> (x, y, rotation), board-local mm.
Board 90 x 70 mm. U1 along the top edge, heatsink tab toward the edge; inputs, volume
header and mute driver on the left (pin 1 end), feedback parts under pins 1 and 7,
bootstraps under pins 9-13, outputs and speaker terminals on the right (pin 14 end)."""

PLACE = {
    "U1":  (24.0, 5.5, 0), "J7": (64.0, 4.0, 0),
    # input and volume (left column)
    "J1":  (2.5, 10.0, 0), "J2": (2.5, 21.0, 0), "J3": (2.5, 40.0, 0),
    "R5":  (7.2, 10.5, 0), "R3": (7.2, 14.0, 0), "C13": (8.0, 20.0, 0),
    "R6":  (7.2, 27.0, 0), "R4": (7.2, 30.5, 0), "C14": (8.0, 37.0, 0),
    # mute driver (bottom left)
    "JQ2": (5.0, 46.5, 0), "Q2":  (19.5, 51.0, 180),
    "R10": (3.5, 55.3, 0),
    "Q1":  (5.0, 59.5, 0), "JQ1": (11.5, 59.5, 0),
    "R11": (23.0, 47.5, 270), "R12": (26.5, 47.5, 270), "R13": (30.0, 47.5, 270), "R9": (33.5, 47.5, 270),
    "C10": (24.0, 63.0, 0),
    # feedback legs under pins 1 and 7, ripple filter
    "R7":  (24.0, 10.2, 270), "C1": (22.5, 26.0, 0),
    "R8":  (38.3, 10.2, 270), "C2": (35.0, 27.0, 0),
    "C9":  (26.0, 38.0, 0),
    # bootstraps under pins 9-13
    "C4":  (44.0, 16.0, 0), "C3": (57.3, 16.0, 0),
    # supply (bottom middle)
    "J4":  (38.5, 64.0, 0), "C11": (52.0, 61.0, 0), "C12": (40.0, 54.0, 0),
    # outputs (right)
    "C5":  (68.0, 9.5, 0), "R14": (71.5, 14.0, 0), "R15": (71.5, 19.0, 0),
    "C7":  (64.0, 31.0, 0), "C8": (64.0, 46.0, 0),
    "J5":  (82.0, 34.0, 90), "J6": (82.0, 50.0, 90),
    "R16": (69.0, 58.0, 0), "R17": (69.0, 63.0, 0), "C6": (66.0, 67.0, 0),
}

JQ_REFS = ("JQ1", "JQ2")

# (text, x, y, size[, 'B' = back silk, mirrored]) board-local mm
TEXTS = [
    ("LA4440 STEREO AMP r1", 77.0, 6.2, 1.0),
    ("HS GND", 64.0, 8.3, 0.8),
    ("IN L G R", 2.5, 6.0, 0.8, "B"),
    ("VOL 1-6", 2.5, 37.0, 0.8, "B"),
    ("MUTE SW", 6.5, 41.0, 0.8, "B"),
    ("DC 12-15V", 41.0, 57.0, 0.8, "B"),
    ("SPK L", 82.0, 24.0, 0.8),
    ("SPK R", 82.0, 40.0, 0.8),
]
