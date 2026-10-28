# Simulation (ngspice 42)

Every number in the README and in `docs/notes.html` comes from one of these decks.

| Deck | What it checks |
|---|---|
| `amp.cir` | One channel with the behavioural LA4440 (Rf 20k, RNF 50, ri 30k, fH 20 kHz, output at 0.515 VCC, 0.5 V swing limit). Included by the run decks. |
| `amp_full.cir` | The whole board: both channels, volume pot, taper and series resistors, mute driver, supply. The KiCad netlist is checked against this deck (`kicad/netcheck.py`). |
| `run_gain.cir` | Gain and -3 dB points vs RNF' (0, 220, 470, 1000 ohm). |
| `run_vol.cir` | Volume law with the 10k taper resistor, and channel mismatch for X9C104 end-to-end tolerance (80k / 120k). |
| `run_law.cir` | Volume law for taper resistors 22k, 15k, 10k and none. |
| `run_fp.cir` | Clipping level and output power at 13.2 V and 12 V. |
| `run_full.cir` | Mute pin current by toggle and by GPIO, at 13.2 V and 12 V; both channels' gain. |

Run any of them with `ngspice -b run_gain.cir | grep RESULT`.

`build_schem.py`, `build_cjs.py` and `build_page.py` produced the figures, the CircuitJS link
(`la4440-channel.txt` / `.url.txt`, checked with `--deck la4440-channel.deck.json`) and `docs/notes.html`.
They import the circuit-sim helpers from the author's bench (`schem.py`, `circuitjs.py`, `connectivity.py`)
and are kept here as the record of how the page was made; the decks run on plain ngspice.

The LA4440 has no maker SPICE model. The behavioural model reproduces the datasheet's gain, input
resistance, bandwidth, output bias and swing; it does not model the mute attenuation, distortion,
turn-on behaviour or the bootstrap.
