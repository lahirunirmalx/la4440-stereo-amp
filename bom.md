# Bill of materials

Board: 90 x 70 mm, 2 layers. Every resistor, film cap and transistor position has through-hole holes
plus an SMD twin (1206 / 2512 / SOT-23) on the same net: fit either. Electrolytics are through-hole only.
"Stock" is the author's parts bin (`in hand`) versus what has to be ordered (`buy`).

Reference designators match the simulation deck `sim/amp_full.cir`, except: R14+R15 are the deck's R1
(two 10R in parallel), R16+R17 are R2, RV1/RV2 are the two gangs of the deck's RV1 (RV1AT/RV1AB, RV1BT/RV1BB).

## On the board

| Ref | Value | Footprint | Job | Stock |
|---|---|---|---|---|
| U1 | LA4440 (Sanyo) | SIP-14H, 2.54 mm | 2 x 6 W amplifier | in hand |
| R3, R4 | 10k 0.25 W 1% | axial 7.62 / 1206 | taper resistors (linear pot -> near-log law) | in hand |
| R5, R6 | 5.6k | axial 7.62 / 1206 | series input R, mute 40 -> 55 dB | in hand |
| R7, R8 | 470 | axial 7.62 / 1206 | RNF': gain 51.5 -> 30 dB. 1k for sources above 1 V (24.5 dB) | in hand |
| R9 | 1.8k | axial 7.62 / 1206 | mute pin current, 6.9 mA at 13.2 V | in hand |
| R10, R11, R12, R13 | 47k, 10k, 4.7k, 100k | axial 7.62 / 1206 | mute driver bias | in hand |
| R14, R15, R16, R17 | 10R 1 W | axial 12.7 / 2512 | Zobel resistors, two in parallel per channel (5 ohm) | in hand |
| C1, C2 | 47 uF 50 V | radial D8 P3.5 | feedback-leg caps (NF1, NF2) | in hand |
| C10 | 47 uF 50 V | radial D8 P3.5 | mute time constant (CO) | in hand |
| C13, C14 | 47 uF 50 V | radial D8 P3.5 | wiper coupling caps (pot scratch, X9C104 step clicks) | in hand |
| C3, C4 | 1000 uF 25 V | radial D12.5 P5 | bootstrap (datasheet 100 uF) | in hand |
| C9 | 1000 uF 25 V | radial D12.5 P5 | pin 5 ripple filter (datasheet 220 uF): slower, quieter start | in hand |
| C7, C8 | 2200 uF 25 V | radial D12.5 P5 | output caps, 18 Hz into 4 ohm | in hand |
| C11 | 2200 uF 25 V | radial D12.5 P5 | supply reservoir | in hand |
| Q1 | 2N3904 | TO-92 / SOT-23 + pinout field JQ1 | mute level shift | in hand |
| Q2 | 2N5401 | TO-92 / SOT-23 + pinout field JQ2 | mute high-side switch | in hand |
| J3 | 1x2 header | 2.54 mm | to the panel mute toggle SW1 | buy |
| C5, C6 | 0.1 uF polyester film, 50 V+ | 5 mm / 1206 | Zobel caps (datasheet requires film) | buy |
| C12 | 0.1 uF film or X7R | 5 mm / 1206 | supply decoupling at pin 11 | buy |
| J1 | 1x3 header | 2.54 mm | line in: L, GND, R | buy |
| J2 | 1x6 header | 2.54 mm | volume / control: 1 L in, 2 L wiper, 3 R in, 4 R wiper, 5 GND, 6 MUTE_CTL | buy |
| J4 | 2-pin screw terminal 5.08 mm | Phoenix MKDS-1,5 | DC in, 12 to 15 V (18 V max) | buy |
| J5, J6 | 2-pin screw terminal 5.08 mm | Phoenix MKDS-1,5 | speakers L, R | buy |
| J7 | M3 plated hole | 3.2 mm pad | heatsink to GND (datasheet: fin to GND) | (board) |

## Off the board

| Ref | Value | Job | Stock |
|---|---|---|---|
| SW1 | MTS-112 toggle (check it has the pins you need: SPST is enough) | manual mute, wired to J3 | in hand |
| RV1/RV2 | dual 100k LINEAR pot (B100K), on the panel, wired to J2 pins 1-5 | volume. Linear, not log, so two X9C104 can replace it with the same curve | buy |
| - | 2 x X9C104 (later) | digital volume on J2. Need 5 V and CS / INC / U-D from a microcontroller | in hand |
| LS1, LS2 | 4 to 8 ohm speakers | | buy |
| - | heatsink, about 5 C/W, two 3.4 mm holes 30 mm apart (the LA4440 tab), ground it with a wire to J7 | required | buy |
| - | 3.5 mm stereo jack, wired to J1 | | buy |
| - | 12 to 15 V DC 2 A adapter (or a bench supply) | | buy |

## Buy list

- 1 x dual 100k linear pot (B100K)
- 3 x 0.1 uF polyester film capacitor (C5, C6, C12)
- 1 x 1x3, 1 x 1x6, 1 x 1x2 pin header + mating plugs
- 3 x 2-pin 5.08 mm screw terminal
- 1 x heatsink for the LA4440, 3 x M3 screw + nut
- 1 x 3.5 mm stereo jack, 2 x speakers
- 1 x 12 to 15 V 2 A DC adapter
- 3 x 47 uF 50 V: only if the VLF receiver (another project on the same bench) is also built - this board uses all 5 in stock
