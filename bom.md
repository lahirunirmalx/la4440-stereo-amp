# Bill of materials

Board: 90 x 70 mm, 2 layers. Every resistor, film cap and transistor position has through-hole holes
plus an SMD twin (1206 / 2512 / SOT-23) on the same net: fit either. Electrolytics are through-hole only.

Reference designators match the simulation deck `sim/amp_full.cir`, except: R14+R15 are the deck's R1
(two 10R in parallel), R16+R17 are R2, RV1/RV2 are the two gangs of the deck's RV1 (RV1AT/RV1AB, RV1BT/RV1BB).

## On the board

| Ref | Qty | Value | Footprint | Job |
|---|---|---|---|---|
| U1 | 1 | LA4440 (Sanyo) | SIP-14H, 2.54 mm | 2 x 6 W amplifier |
| R3, R4 | 2 | 10k 0.25 W 1% | axial 7.62 / 1206 | taper resistors (linear pot -> near-log law) |
| R5, R6 | 2 | 5.6k 0.25 W | axial 7.62 / 1206 | series input R, mute 40 -> 55 dB |
| R7, R8 | 2 | 470R 0.25 W | axial 7.62 / 1206 | RNF': gain 51.5 -> 30 dB. 1k for sources above 1 V (24.5 dB) |
| R9 | 1 | 1.8k 0.25 W | axial 7.62 / 1206 | mute pin current, 6.9 mA at 13.2 V (1.5k also fine) |
| R10 | 1 | 47k 0.25 W | axial 7.62 / 1206 | mute driver bias |
| R11 | 1 | 10k 0.25 W | axial 7.62 / 1206 | mute driver bias |
| R12 | 1 | 4.7k 0.25 W | axial 7.62 / 1206 | mute driver bias |
| R13 | 1 | 100k 0.25 W | axial 7.62 / 1206 | mute driver bias |
| R14, R15, R16, R17 | 4 | 10R 1 W | axial 12.7 / 2512 | Zobel resistors, two in parallel per channel (5 ohm) |
| C1, C2 | 2 | 47 uF 25 V+ electrolytic | radial D8 P3.5 | feedback-leg caps (NF1, NF2) |
| C10 | 1 | 47 uF 25 V+ electrolytic | radial D8 P3.5 | mute time constant (CO) |
| C13, C14 | 2 | 47 uF 25 V+ electrolytic | radial D8 P3.5 | wiper coupling caps (pot scratch, X9C104 step clicks) |
| C3, C4 | 2 | 1000 uF 25 V electrolytic | radial D12.5 P5 | bootstrap (datasheet 100 uF; 100 to 1000 uF all work) |
| C9 | 1 | 1000 uF 25 V electrolytic | radial D12.5 P5 | pin 5 ripple filter (datasheet 220 uF; larger = slower, quieter start) |
| C7, C8 | 2 | 2200 uF 25 V electrolytic | radial D12.5 P5 | output caps, 18 Hz into 4 ohm (1000 uF = 36 Hz) |
| C11 | 1 | 2200 uF 25 V electrolytic | radial D12.5 P5 | supply reservoir |
| C5, C6 | 2 | 0.1 uF polyester film, 50 V+ | 5 mm / 1206 | Zobel caps (datasheet requires film) |
| C12 | 1 | 0.1 uF film or X7R | 5 mm / 1206 | supply decoupling at pin 11 |
| Q1 | 1 | 2N3904 (any small NPN) | TO-92 / SOT-23 + pinout field JQ1 | mute level shift |
| Q2 | 1 | 2N5401 (any PNP rated 30 V+) | TO-92 / SOT-23 + pinout field JQ2 | mute high-side switch |
| J1 | 1 | 1x3 pin header 2.54 mm | | line in: L, GND, R |
| J2 | 1 | 1x6 pin header 2.54 mm | | volume / control: 1 L in, 2 L wiper, 3 R in, 4 R wiper, 5 GND, 6 MUTE_CTL |
| J3 | 1 | 1x2 pin header 2.54 mm | | to the panel mute toggle SW1 |
| J4 | 1 | 2-pin screw terminal 5.08 mm | Phoenix MKDS-1,5 | DC in, 12 to 15 V (18 V max) |
| J5, J6 | 2 | 2-pin screw terminal 5.08 mm | Phoenix MKDS-1,5 | speakers L, R |
| J7 | - | M3 plated hole | 3.2 mm pad | heatsink to GND (datasheet: fin to GND); part of the board |
| H1-H4 | 4 | M2.5 screws + standoffs | 2.5 mm holes | mounting |

## Off the board

| Ref | Qty | Value | Job |
|---|---|---|---|
| RV1/RV2 | 1 | dual 100k LINEAR pot (B100K), panel mount, wired to J2 pins 1-5 | volume. Linear, not log, so two X9C104 can replace it with the same curve |
| SW1 | 1 | SPST toggle switch, wired to J3 | manual mute |
| LS1, LS2 | 2 | 4 to 8 ohm speakers | |
| - | 1 | heatsink, about 5 C/W, two 3.4 mm holes 30 mm apart (the LA4440 tab); ground it with a wire to J7 | required |
| - | 1 | 3.5 mm stereo jack, wired to J1 | |
| - | 1 | 12 to 15 V DC 2 A adapter (or a bench supply) | |
| - | 2 | X9C104 digital pot (optional, later) | digital volume on J2. Need 5 V and CS / INC / U-D from a microcontroller |

## Shopping list (counts)

- 1 x LA4440
- Resistors 0.25 W: 2 x 10k, 2 x 5.6k, 2 x 470R, 1 x 1.8k, 1 x 47k, 1 x 10k, 1 x 4.7k, 1 x 100k
- 4 x 10R 1 W
- 5 x 47 uF, 3 x 1000 uF 25 V, 3 x 2200 uF 25 V
- 3 x 0.1 uF film
- 1 x 2N3904, 1 x 2N5401
- Headers: 1x3, 1x6, 1x2 + mating plugs; 3 x 2-pin 5.08 mm screw terminals
- 1 x dual 100k linear pot, 1 x SPST toggle, 1 x 3.5 mm stereo jack
- 1 x heatsink + M3 hardware, 4 x M2.5 standoffs
- 1 x 12 to 15 V 2 A adapter, 2 x speakers
