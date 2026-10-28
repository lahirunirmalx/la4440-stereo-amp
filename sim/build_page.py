import re
A = "/home/lahiru/.claude/skills/circuit-sim/assets/"
css = open(A + "notes-page.css").read()
css += """
  .pin { fill: var(--warn); font-size: 11px; font-family: var(--mono); }
  .pol { fill: var(--red); font-weight: 700; font-size: 14px; }
  .tiny { font-size: 11px; fill: var(--ink-2); }
  .buy { color: var(--warn); font-weight: 700; }
  .hand { color: var(--green); font-weight: 700; }
"""
fig1 = open("fig1.svg.part").read()
fig2 = open("fig2.svg.part").read()
url = open("la4440-channel.url.txt").read().strip()

def rows(r):
    return "\n".join("<tr>" + "".join(
        f'<td class="{c[0]}">{c[1]}</td>' if isinstance(c, tuple) else f"<td>{c}</td>" for c in row) + "</tr>"
        for row in r)

H, B = ("hand", "in hand"), ("buy", "buy")
bom = rows([
 [("ref", "U1"), "LA4440 (SIP-14)", H, "The amplifier. 2 x 6 W at 13.2 V (datasheet, 10% THD)."],
 [("ref", "R3, R4"), "10k", H, "Taper resistors: make the linear pot behave like a log pot."],
 [("ref", "R5, R6"), "5.6k", H, "Lift mute from 40 to 55 dB (datasheet). Costs 1.5 dB of gain."],
 [("ref", "R7, R8"), "470", H, "RNF': sets gain to 30 dB instead of 51.5 dB. Change to 1k for loud sources (24 dB)."],
 [("ref", "R1, R2"), "2 x 10R 1 W in parallel, each", H, "Zobel resistor, 5 ohm (datasheet 4.7). Uses 4 of the 10 x 10R."],
 [("ref", "R9"), "1.8k", H, "Mute current about 6.9 mA (datasheet 1k at 9 V = 8.3 mA; 1.5k not in the kit)."],
 [("ref", "R10, R11, R12, R13"), "47k, 10k, 4.7k, 100k", H, "Mute driver bias."],
 [("ref", "Q1, Q2"), "2N3904, 2N5401", H, "GPIO mute driver: Q1 level shift, Q2 switches VCC to the mute pin."],
 [("ref", "SW1"), "MTS-112 toggle", H, "Manual mute. Check its pin count first."],
 [("ref", "C1, C2, C10, C13, C14"), "47 uF 50 V", H, "NF caps, mute cap, wiper caps. <b>Uses all 5 in stock.</b>"],
 [("ref", "C3, C4, C9"), "1000 uF 25 V", H, "Bootstrap (datasheet 100 uF) and pin 5 (datasheet 220 uF): slower start, quieter turn-on."],
 [("ref", "C7, C8, C11"), "2200 uF 25 V", H, "Output caps (bass to 18 Hz into 4 ohm) and supply reservoir."],
 [("ref", "RV1"), "Dual 100k LINEAR (B100K)", B, "Volume. Linear, not log, so it matches the X9C104 exactly. Later: 2 x X9C104 (in hand)."],
 [("ref", "-"), "Heatsink, about 5 C/W, tab to GND", B, "Required: several watts dissipated at full volume."],
 [("ref", "C5, C6"), "0.1 uF polyester film", B, "Zobel caps. The datasheet requires film; they stop oscillation."],
 [("ref", "C12"), "0.1 uF film or ceramic", B, "Supply decoupling at pin 11."],
 [("ref", "J2"), "6-pin header + plug", B, "Pot / X9C104 connector: 1 L in, 2 L wiper, 3 R in, 4 R wiper, 5 GND, 6 MUTE_CTL."],
 [("ref", "-"), "3.5 mm stereo jack, 2 speaker terminals", B, "Connectors."],
 [("ref", "-"), "12 to 15 V DC, 2 A adapter", B, "Or the bench PSU (in hand). Never above 18 V."],
 [("ref", "-"), "47 uF 50 V x 3", B, "Only if the VLF receiver is also built - this amp takes all 5."],
])

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LA4440 stereo amp - volume pot, mute, X9C104-ready</title>
<style>
{css}
</style>
</head>
<body>
<div class="shell">

  <div class="topbar">
    <button id="themeBtn" type="button" aria-label="Toggle colour theme">Theme</button>
  </div>

  <header class="masthead">
    <span class="eyebrow">Bench notes / Audio</span>
    <h1>LA4440 stereo amplifier with volume, mute and a digital-pot upgrade path</h1>
    <p class="lede">
      2 x 4.4 W clean into 4 ohm at 13.2 V (model), 30 dB gain, flat from 20 Hz. Volume is a
      dual 100k linear pot that two X9C104 digital pots (in hand) replace on the same header;
      mute is a toggle now and a GPIO later, wired in parallel. Every part except the pot,
      three film caps, the connectors and a heatsink is in the catalog.
    </p>
  </header>

  <section>
    <div class="sec-head">
      <span class="eyebrow">The problem</span>
      <h2>The LA4440 has too much gain for a volume pot</h2>
    </div>
    <div class="prose">
      <p>The chip's gain is fixed at 51.5 dB (x376). Full power needs only 18 mV at the input, so a
      phone at 1 V would reach full volume in the first 2% of the pot's travel - that is tap 1 or 2
      of the 100 taps on an X9C104. The volume control would be useless.</p>
      <div class="key">
        <span class="eyebrow">The mechanism</span>
        <p>The datasheet lets you lower the gain with a resistor RNF' in series with the
        feedback capacitor on pins 1 and 7: gain = 20k / (50 + RNF'). 470 ohm gives 30 dB, so full
        power now needs 0.18 V and the pot uses its whole travel. "Adjustable gain" is the volume pot;
        RNF' sets its range. The digital pot cannot replace RNF' - its 1k steps are too coarse for a
        0 to 500 ohm job.</p>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Figure 1</span>
      <h2>Volume and mute</h2>
      <p>Both channels; everything a later ESP32 controls comes in on header J2.</p>
    </div>
    <figure>
      <div class="fig-body">
{fig1}
      </div>
      <figcaption>
        <b>Mute pulls 6.9 mA into pin 4 at 13.2 V, by toggle or GPIO.</b> SW1 and Q2 are in parallel,
        so the GPIO driver can be fitted now and used later. A 3.3 V GPIO high on MUTE_CTL turns Q1 on,
        Q1 turns Q2 on. For the X9C104 swap: unplug RV1, plug the two X9C104s into J2 pins 1 to 5;
        they also need 5 V and three ESP32 lines (CS, INC, U/D), and the firmware must store the wiper
        (CS high while INC is high) or the volume is lost at power-off.
        Solid dot = joined; wires crossing with no dot are not connected.
      </figcaption>
    </figure>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Figure 2</span>
      <h2>LA4440 core, outputs and supply</h2>
      <p>The datasheet's stereo circuit, with RNF' added and parts swapped for what is in hand.</p>
    </div>
    <figure>
      <div class="fig-body">
{fig2}
      </div>
      <figcaption>
        <b>Outputs idle at 6.8 V; the 2200 uF caps take bass down to 18 Hz into 4 ohm.</b> R7 and R8
        set 30 dB. C5/C6 with R1/R2 (each two 10R in parallel) are the Zobel networks the datasheet
        requires against oscillation. Pins 3, 8 and 14 and the heatsink tab go to ground. Brown
        numbers are LA4440 pins.
      </figcaption>
    </figure>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Bill of materials</span>
      <h2>Parts for a 12 to 15 V supply</h2>
    </div>
    <div class="tw">
      <table>
        <thead><tr><th>Ref</th><th>Value</th><th>Stock</th><th>Job</th></tr></thead>
        <tbody>
{bom}
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Simulated, hand checked</span>
      <h2>Gain, band and full power</h2>
      <p>run_gain.cir and run_fp.cir, 13.2 V, 4 ohm, pot full up.</p>
    </div>
    <div class="tw">
      <table>
        <thead><tr><th>RNF'</th><th class="num">Gain</th><th class="num">Low -3 dB</th><th class="num">High -3 dB</th><th class="num">Source for full power</th><th>Hand check</th></tr></thead>
        <tbody>
          <tr><td class="ref">0 (datasheet)</td><td class="num">49.4 dB</td><td class="num">64 Hz</td><td class="num">21 kHz</td><td class="num">20 mV pk</td><td>51.5 dB less 1.5 dB = 50.0 (model 0.6 dB low). NF corner 1/(2 pi 47u 50) = 68 Hz: bass-light.</td></tr>
          <tr><td class="ref">220</td><td class="num">35.8 dB</td><td class="num">24 Hz</td><td class="num">101 kHz</td><td class="num">96 mV pk</td><td>20k/270 = 37.4 dB less 1.5 dB = 35.9.</td></tr>
          <tr><td class="ref"><b>470 (chosen)</b></td><td class="num">30.3 dB</td><td class="num">20 Hz</td><td class="num">190 kHz</td><td class="num">0.18 V pk</td><td>20k/520 = 31.7 dB less 1.5 dB = 30.2. Agrees.</td></tr>
          <tr><td class="ref">1000</td><td class="num">24.5 dB</td><td class="num">19 Hz</td><td class="num">370 kHz</td><td class="num">0.35 V pk</td><td>For hot sources.</td></tr>
        </tbody>
      </table>
    </div>
    <div class="tw">
      <table>
        <thead><tr><th>Supply</th><th class="num">Source 0.10 V pk</th><th class="num">0.15 V</th><th class="num">0.20 V</th><th class="num">0.30 V</th></tr></thead>
        <tbody>
          <tr><td class="ref">13.2 V</td><td class="num">1.3 W</td><td class="num">2.9 W</td><td class="num">4.5 W (clipping)</td><td class="num">4.6 W (clipped)</td></tr>
          <tr><td class="ref">12 V</td><td class="num">1.3 W</td><td class="num">2.9 W</td><td class="num">3.7 W (clipping)</td><td class="num">3.7 W (clipped)</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Sweeps</span>
      <h2>Volume law, channel match and mute drive</h2>
    </div>
    <div class="tw">
      <table>
        <thead><tr><th>Pot position (or X9C104 tap)</th><th class="num">Plain linear pot</th><th class="num">With 10k taper R (built)</th></tr></thead>
        <tbody>
          <tr><td>100% (tap 99)</td><td class="num">0 dB</td><td class="num">0 dB</td></tr>
          <tr><td>75%</td><td class="num">-6.2 dB</td><td class="num">-13.0 dB</td></tr>
          <tr><td>50%</td><td class="num">-10.6 dB</td><td class="num">-18.4 dB</td></tr>
          <tr><td>25%</td><td class="num">-15.7 dB</td><td class="num">-22.6 dB</td></tr>
          <tr><td>10%</td><td class="num">-21.9 dB</td><td class="num">-26.5 dB</td></tr>
          <tr><td>5%</td><td class="num">-27.1 dB</td><td class="num">-30.0 dB</td></tr>
          <tr><td>2%</td><td class="num">-34.4 dB</td><td class="num">-35.8 dB</td></tr>
          <tr><td>1% (tap 1)</td><td class="num">-40.2 dB</td><td class="num">-40.9 dB</td></tr>
        </tbody>
      </table>
    </div>
    <div class="tw">
      <table>
        <thead><tr><th>Swept</th><th>Range tested</th><th>Result</th></tr></thead>
        <tbody>
          <tr><td>X9C104 end-to-end tolerance</td><td>80k to 120k (+/-20%)</td><td>With the 10k taper R: up to 2.7 dB apart (+/-1.3 dB) between 30% and 60%, 0 dB at full. Firmware can trim one channel by a few taps.</td></tr>
          <tr><td>Mute drive, GPIO</td><td>MUTE_CTL 3.3 V, 13.2 V supply</td><td>Pin 4 at 0.71 V, 6.9 mA in. Q1 collector 0.04 V (saturated).</td></tr>
          <tr><td>Mute drive, toggle</td><td>SW1 closed</td><td>6.9 mA. Same as GPIO.</td></tr>
          <tr><td>Mute drive at 12 V</td><td>GPIO</td><td>6.2 mA. Above the 5.3 mA the datasheet's minimum (6 V, 1k) gives.</td></tr>
          <tr><td>Not muted</td><td>MUTE_CTL 0 V, SW1 open</td><td>Pin 4 at 0.36 V, about 10 nA: off.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Where the simulation corrected me</span>
      <h2>What I had wrong on paper</h2>
    </div>
    <div class="prose">
      <p><strong>CORRECTED.</strong> The datasheet circuit (RNF' = 0) reaches clipping at 20 mV of input, so a 1 V source clips at 2% of pot travel. RNF' = 470 moves clipping to 0.18 V (run_gain.cir, run_fp.cir). Not optional with a 100-tap digital pot.</p>
      <p><strong>CORRECTED.</strong> I expected the 10k taper resistor to hide the X9C104's +/-20% tolerance. It does the opposite: the fixed 10k load makes the law depend more on the pot's own value, so 80k against 120k is 2.7 dB apart at 30 to 60% travel (run_vol.cir, with the taper R). Without it the gap is 1.4 dB. A per-channel firmware offset fixes it; a mechanical dual pot also has 1 to 3 dB gang tracking error.</p>
      <p><strong>CONFIRMED.</strong> Low corner 20 Hz at RNF' 470, set by 2200 uF into 4 ohm (18 Hz by hand). At RNF' 0 it is 64 Hz because the 47 uF NF cap against 50 ohm then dominates (68 Hz by hand).</p>
      <p><strong>CONFIRMED.</strong> Mute current (VCC - 0.7) / 1.8k = 6.9 mA, simulated 6.9 mA (run_full.cir).</p>
      <p><strong>LIMIT.</strong> Clean output ends at 4.4 W into 4 ohm at 13.2 V (model); the datasheet's 6 W is at 10% distortion.</p>
      <p><strong>MODEL.</strong> The behavioural chip (open-loop gain 3000) reads 49.4 dB at RNF' 0 against 50.0 dB expected (51.5 dB typical less 1.5 dB for R5 into the 30k input): 0.6 dB low. At 470 it agrees within 0.1 dB. The 190 kHz high corner at 30 dB is a model number, not a datasheet one.</p>
      <div class="note"><strong>The one to watch.</strong> Mute pop. The wiper caps C13/C14 are what the datasheet says makes AC-mute pop worse; they are there to stop pot scratch and X9C104 step clicks. If mute pops, short C13/C14 first and live with some slider noise.</div>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Build notes</span>
      <h2>Building and adapting it</h2>
    </div>
    <div class="prose">
      <ul class="bullets">
        <li><strong>Verified:</strong> RNF' 1k instead of 470 gives 24.5 dB for sources hotter than 1 V (run_gain.cir).</li>
        <li><strong>Proposed:</strong> R9 1.2k raises mute current to about 10 mA if 40 dB is not reached at 6.9 mA - unsimulated attenuation, bench check.</li>
        <li><strong>Proposed:</strong> first power-up on the bench PSU at 13.2 V with a 300 mA limit and no input. Idle draw should be about 100 mA (datasheet), outputs 6.8 V.</li>
        <li><strong>Proposed:</strong> follow the datasheet layout: keep input wiring (pins 2, 6) away from the outputs (pins 10, 12), Zobels right at the pins.</li>
        <li><strong>Digital later:</strong> X9C104 powered from the ESP32's 5 V; signal stays inside its +/-5 V terminal limit. Map volume steps in firmware; tap 0 puts the wiper at ground through its 40 ohm wiper resistance, about -68 dB (hand estimate).</li>
      </ul>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Interactive</span>
      <h2>Open one channel in CircuitJS</h2>
      <p>The LA4440 is drawn as its equivalent: op-amp, internal 20k / 50 ohm feedback and 30k input, on a +/-6.6 V split supply so the output idles at 0 V. Drag the Volume slider; scope the speaker.</p>
    </div>
    <div class="btnrow">
      <a class="cta" id="cjsLink" href="{url}">Launch the interactive circuit</a>
      <button id="copyBtn" type="button">Copy the URL</button>
    </div>
    <div class="urlbox" id="urlText">{url}</div>
    <div class="note">
      Never opened in a browser. The netlist was checked with <code>connectivity.py --deck</code>
      (0 findings). The CircuitJS op-amp is ideal-ish; its bandwidth setting may not be honoured,
      so read gains from it, not the high corner. Fallback: File &gt; Import From Text with
      la4440-channel.txt.
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="eyebrow">Files</span>
      <h2>Everything behind this page</h2>
    </div>
    <div class="tw">
      <table>
        <thead><tr><th>Path</th><th>What it is</th></tr></thead>
        <tbody>
          <tr><td class="ref">sim/amp.cir</td><td>One channel with the behavioural LA4440.</td></tr>
          <tr><td class="ref">sim/amp_full.cir</td><td>Whole board: both channels, volume, mute driver, supply. The drawings are checked against this.</td></tr>
          <tr><td class="ref">sim/run_gain.cir</td><td>Gain and band edges vs RNF'.</td></tr>
          <tr><td class="ref">sim/run_vol.cir, run_law.cir</td><td>Volume law, taper resistor, X9C104 tolerance.</td></tr>
          <tr><td class="ref">sim/run_fp.cir</td><td>Clipping level at 13.2 and 12 V.</td></tr>
          <tr><td class="ref">sim/run_full.cir</td><td>Mute drive in all states, both channels.</td></tr>
          <tr><td class="ref">sim/build_schem.py, build_cjs.py</td><td>Figures and CircuitJS link, each checked against the decks.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    <p>
      ngspice 42. The LA4440 is a behavioural model built from the Sanyo ENN750F datasheet (Rf 20k,
      RNF 50, ri 30k, fH 20 kHz, output at 0.515 VCC, 0.5 V swing limit); no maker SPICE model exists.
      Not modelled: the 40 / 55 dB mute attenuation (only the mute pin current is simulated), turn-on
      thump and mute pop, the bootstrap effect and the slower start from 1000 uF on pins 5, 9 and 13
      (placeholders in the deck), distortion, heat. MTS-112 pin count unchecked. Not built.
    </p>
  </footer>

</div>

<script>
(function () {{
  var btn = document.getElementById('themeBtn');
  var root = document.documentElement;
  btn.addEventListener('click', function () {{
    var cur = root.getAttribute('data-theme');
    if (!cur) cur = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    root.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
  }});
  var copy = document.getElementById('copyBtn');
  if (copy) copy.addEventListener('click', function () {{
    var t = document.getElementById('urlText').textContent.trim();
    navigator.clipboard.writeText(t).then(function () {{
      copy.textContent = 'Copied';
      setTimeout(function () {{ copy.textContent = 'Copy the URL'; }}, 1600);
    }}, function () {{ copy.textContent = 'Select it manually'; }});
  }});
}})();
</script>
</body>
</html>
"""
out = "../docs/notes.html"
open(out, "w").write(page)
print("non-ascii:", {c for c in page if ord(c) > 127})
import xml.dom.minidom as M
for s in re.findall(r"<svg.*?</svg>", page, re.S):
    M.parseString(s)
print("svgs parse OK")
