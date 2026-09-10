# ✈️ Lab 09 — ADS-B Aircraft Receiver (1090 MHz Mode S)

> **Time:** 3 hours
> **Difficulty:** Expert
> **Theory needed:** [Fund. 06 Noise & SNR](../../01_fundamentals/06_noise_snr_and_gain.md) · [Fund. 08 Digital Modulation](../../01_fundamentals/08_digital_modulation.md) (PPM section) · [Fund. 10 Error Detection & Framing](../../01_fundamentals/10_error_detection_and_framing.md)
> **New blocks:** Complex to Mag, Embedded Python Block (ADS-B Decoder), triggered Time Sink
> **Flowgraphs:** two — `lab09_adsb_receiver.grc` (live) and `lab09_adsb_from_file.grc` (offline)
> **Blocks in flowgraph:** 14 — *the simplest flowgraph since Lab 02, and the hardest lab in the repo*

---

## 🎯 Goal

Receive aircraft. Not a signal that represents aircraft — the actual broadcasts that every
airliner in the sky emits twice a second, carrying its 24-bit identity, its callsign, its
altitude, its velocity, and its position to a quarter of a metre.

> **This lab has been verified.** Run against a synthetic 1090 MHz capture containing 80 known
> frames at 20 dB SNR, the flowgraph recovered **80 of 80** (100 %) — correctly reporting
> ICAO `4840D6` / callsign `KLM1023`, ICAO `40621D` at 38,000 ft at 52.2572 °N 3.9194 °E, and
> ICAO `485020` at 159 kt heading 183°. Those decoded values match the canonical reference
> frames from the Mode S literature exactly. See [Verification](#-verification).

### Why this lab is different

Look at the flowgraph: **14 blocks.** Fewer than Lab 03. There is no channel filter, no AGC, no
PLL, no Costas loop, no symbol synchroniser, no resampler.

```
   USRP  →  Complex to Mag  →  ADS-B Decoder  →  count
```

That is the entire receiver.

The difficulty has moved. In Labs 07 and 08 the hard part was *synchronisation* — three
feedback loops fighting noise. Here the modulation is so simple that a magnitude detector and a
threshold suffice. **The hard part is the link budget and the framing.** ADS-B is difficult
because the signal is genuinely faint and because you must decide, 2 million times a second,
whether the bump you just saw was an aeroplane or a fluctuation.

---

## 📖 Background: Mode S and ADS-B

### The history in one paragraph

Secondary surveillance radar interrogates aircraft transponders on 1030 MHz; transponders reply
on 1090 MHz. **Mode S** (Select) added addressed interrogation — each aircraft has a unique
24-bit ICAO address. **ADS-B** (Automatic Dependent Surveillance–Broadcast) then removed the
interrogator entirely: aircraft simply *broadcast* their GPS-derived position, unprompted,
about twice a second. It is Automatic (no operator), Dependent (on the aircraft's own
navigation), Surveillance, and Broadcast (to anyone). Including you.

### The physical layer

| Property | Value |
|---|---|
| Frequency | 1090 MHz |
| Modulation | Pulse Position Modulation (PPM) |
| Data rate | 1 Mbit/s (1 µs per bit) |
| Pulse width | 0.5 µs |
| Frame | 8 µs preamble + 56 or 112 data bits |
| Extended squitter (ADS-B) | DF 17, always 112 bits → 120 µs total |
| Error detection | CRC-24, generator `0xFFF409` |
| Transmit power | 70–500 W (typically ~125 W for airliners) |

**PPM:**

```
  1 µs bit period, 0.5 µs pulse

  bit = 1:   ▛▀▀▀▜________        pulse in the FIRST half
  bit = 0:   _______▛▀▀▀▜         pulse in the SECOND half
```

Every bit contains exactly one pulse, so the average power is constant and the receiver can
recover timing from the data itself. It costs bandwidth — a 1 Mbit/s PPM signal spreads over
several MHz — but the receiver becomes trivial. That was the right trade in 1975 and it is
still the right trade for a safety-of-life system.

### The preamble

```
   µs  0    0.5   1.0   1.5   2.0   2.5   3.0   3.5   4.0   4.5   5.0 ... 8.0
       ▛▀▜         ▛▀▜                           ▛▀▜         ▛▀▜
       ███         ███                           ███         ███    (quiet)
        │           │                             │           │
  pulses at 0, 1.0, 3.5 and 4.5 µs
```

The spacing is deliberately **non-uniform**. A uniform pulse train correlates strongly with
shifted copies of itself, giving ambiguous detection; this pattern does not. It is the same
principle as a good sync word (Fundamentals 10) expressed in the time domain.

At 2 MSPS the preamble is 16 samples, with pulses at sample indices **0, 2, 7, 9** and silence
everywhere else. That geometry is hard-coded in the decoder — which is exactly why the sample
rate is not negotiable in this lab.

### The frame

```
 ┌────────┬─────┬──────────┬────────────────────────┬────────────┐
 │ 8 µs   │ DF  │ CA       │ ICAO address           │ ME payload │  Parity
 │preamble│ 5 b │ 3 b      │ 24 b                   │ 56 b       │  24 b
 └────────┴─────┴──────────┴────────────────────────┴────────────┘
          └──────────────── 112 bits, 112 µs ──────────────────────┘
```

`DF = 17` is the ADS-B extended squitter. The **ME** payload's first 5 bits are the **Type
Code**, which says what the rest means:

| Type Code | Contents |
|---|---|
| 1–4 | Aircraft identification (callsign) |
| 5–8 | Surface position |
| 9–18 | Airborne position (barometric altitude) |
| 19 | Airborne velocity |
| 20–22 | Airborne position (GNSS height) |

### The link budget — why this is hard

Fundamentals 06's machinery, applied honestly:

- Aircraft transmitter: 125 W = **51 dBm**
- Free-space path loss at 100 km, 1090 MHz:
  $20\log_{10}(100) + 20\log_{10}(1090) + 32.45 = 40 + 60.75 + 32.45 = \mathbf{133.2}$ dB
- Received power: $51 - 133.2 = \mathbf{-82.2}$ dBm (line of sight, 0 dBi antenna)
- Noise floor in 2 MHz with NF = 8 dB: $-174 + 63 + 8 = \mathbf{-103}$ dBm
- **SNR ≈ 21 dB** — decodable, but with nothing to spare

Now change one thing:

| Change | New SNR |
|---|---|
| Antenna indoors (10 dB wall loss) | 11 dB — marginal |
| 3 m of cheap RG-58 at 1090 MHz (~3 dB) | 18 dB |
| Wrong antenna (FM whip at 1090 MHz, ~10 dB mismatch) | 11 dB |
| Aircraft below the horizon | **no signal at all**, at any gain |

**ADS-B is line-of-sight.** The radio horizon for an aircraft at altitude $h$ feet is roughly

$$
d_{\text{nm}} \approx 1.23\sqrt{h_{\text{ft}}}
$$

An airliner at 38,000 ft is visible to about 240 nautical miles (440 km) — *if* nothing is in
the way. A hill, a building, or the curve of the Earth ends the conversation. This is why
antenna placement matters more than anything else in this lab.

---

## 📐 Architecture

```
      ┌──────────────┐
      │ USRP Source  │  1090 MHz, 2 MSPS, gain ~60 dB
      └──────┬───────┘  (or File Source + Throttle)
             │
             ├──────────────────────▶ Freq Sink (see the bursts)
             ▼
      ┌──────────────────┐
      │ Complex to Mag   │   |I + jQ|
      └──────┬───────────┘   ADS-B is on-off keyed: all the information
             │               is in the magnitude. No phase needed at all.
             ├──────────────────────▶ Time Sink (triggered) ← SEE the pulses
             ▼
      ┌────────────────────────────────────────────────────┐
      │ ADS-B Decoder  (Embedded Python Block)             │
      │                                                     │
      │  1. preamble correlation  hi = mean(m[0,2,7,9])    │
      │                           lo = mean(the 12 gaps)   │
      │                           accept if hi-lo > thresh │
      │                           AND hi > ratio * lo      │
      │                                                     │
      │  2. PPM slice   bit = m[first half] > m[second]    │
      │                                                     │
      │  3. CRC-24      remainder must be 0                │
      │                                                     │
      │  4. decode      DF, ICAO, type code, then          │
      │                 callsign / altitude / CPR / speed  │
      └────────────────┬───────────────────────────────────┘
                       ▼
                 Number Sink              terminal:
                 (frame count)     [ADS-B] ICAO 4840D6  KLM1023  38000 ft ...
```

**Note what is absent.** No channel filter (the signal is 4 MHz wide and we only have 2 —
that is fine, we just need the pulse envelope). No AGC (the threshold is set explicitly). No
carrier or timing recovery (PPM needs neither). Simplicity is the modulation's whole point.

---

## 📋 Inside the Decoder Block

Open `adsb_decoder` in GRC (right-click → Properties) to read the source. Four stages.

### 1. Preamble correlation

```python
hi = mean(m[n+0], m[n+2], m[n+7], m[n+9])         # where pulses should be
lo = mean(m[n+1], m[n+3..6], m[n+8], m[n+10..15]) # where silence should be
accept if (hi - lo) > threshold and hi > ratio * lo
```

Both conditions matter, and they fail differently:

- `hi - lo > threshold` is an **absolute** test. It rejects noise-level bumps.
- `hi > ratio * lo` is a **relative** test. It rejects a strong but *shapeless* burst — an
  interferer, a DME pulse, or the tail of a previous frame — that happens to be loud
  everywhere.

The whole scan is vectorised over the buffer with NumPy, so it costs about a dozen array
operations per work call rather than a Python loop over 2 million samples.

### 2. PPM slicing

```python
d = m[p+16 : p+240]                       # the 112 data bits, 2 samples each
bits = (d[0::2] > d[1::2]).astype(int)    # first half louder → 1
```

Two lines. That is the entire demodulator. Compare with the Costas loop, the Gardner TED and
the polyphase interpolator that Lab 07 needed for BPSK.

### 3. CRC-24 — the real receiver

```python
GEN = 0x1FFF409          # x^24 + x^23 + ... + x^10 + x^3 + 1
def crc24(bits):
    reg = 0
    for b in bits:
        reg = ((reg << 1) | b) & 0x1FFFFFF
        if reg & 0x1000000:
            reg ^= GEN
    return reg & 0xFFFFFF
```

For DF 17 the parity field is a plain CRC, so a valid frame gives **remainder zero**.

> **This is where the receiver actually lives.** In the verification run, 147 preamble
> candidates produced **80** CRC-valid frames. Two thirds of the detections were noise, and the
> CRC silently threw all of them away. With a 24-bit check the odds of a random 112-bit pattern
> passing are $2^{-24} \approx 6\times10^{-8}$ — so a frame that passes is a frame you can
> trust, and you can afford to set the preamble threshold *generously*.
>
> Lower the threshold and you get more candidates, more CPU, and — because the CRC is doing the
> real work — **more aircraft**. That is a genuinely counter-intuitive design lesson: with a
> strong error check downstream, a sloppy detector upstream is a feature.

### 4. Payload decode

**Callsign** (TC 1–4): eight 6-bit characters from a custom alphabet, packed into the ME field.

**Altitude** (TC 9–18): a 12-bit AC field. If the Q bit is set, the remaining 11 bits give
$\text{alt} = 25N - 1000$ feet — a 25 ft resolution.

**Position — Compact Position Reporting (CPR).** This is the clever part. Transmitting full
latitude and longitude to 5 m would need ~50 bits. CPR sends only 17 bits each by transmitting
**position modulo a grid**, alternating between two grids (`even`, 60 zones; `odd`, 59 zones).
Two frames of opposite parity, received within about 10 seconds, are enough to resolve the
absolute position globally and unambiguously:

$$
j = \left\lfloor 59\,\text{lat}_{\text{even}} - 60\,\text{lat}_{\text{odd}} + 0.5 \right\rfloor
$$
$$
\text{lat}_{\text{even}} = \frac{360}{60}\bigl((j \bmod 60) + \text{lat}^{cpr}_{\text{even}}\bigr)
$$

It is the Chinese Remainder Theorem, applied to the surface of the Earth, to save 16 bits per
message. The number of longitude zones varies with latitude (the `NL` function) because
meridians converge — so the grid stays roughly square everywhere.

**Velocity** (TC 19): east-west and north-south components in knots, plus vertical rate in
ft/min, from which speed and heading are computed.

---

## 🧪 Running the Lab

### Step 1 — Verify offline first

As in Lab 08: never debug a decoder against a signal you do not control.

```bash
cd 03_scripts
python3 simulate_adsb_decode.py --seconds 2 --snr 20 --out /tmp/adsb_test_2Msps_fc32.iq
cd ../02_flowgraphs/lab09_adsb_receiver
python3 lab09_adsb_from_file.py
```

You should immediately see the three known aircraft. If not, the problem is in the flowgraph,
not the sky.

### Step 2 — Build an antenna

**This matters more than every parameter in the flowgraph combined.**

A quarter-wave whip for 1090 MHz:

$$
\lambda = \frac{c}{f} = \frac{3\times10^8}{1.09\times10^9} = 275\text{ mm},
\qquad \frac{\lambda}{4} = \mathbf{68.8\text{ mm}}
$$

So: 69 mm of wire on the centre conductor of an SMA connector, plus (ideally) four 69 mm
radials at 45° as a ground plane. Cost: nothing. It will comfortably outperform the telescopic
FM whip you used in Labs 01–08, which is roughly ten wavelengths long at 1090 MHz and radiates
in a hopeless pattern.

Placement, in order of importance:

1. **Outside, with sky visibility.** ADS-B is line of sight.
2. **High.** Every metre extends the horizon.
3. **Short, decent coax.** RG-58 loses ~1 dB/m at 1090 MHz. Keep it under 3 m, or use RG-6.

### Step 3 — Go live

```bash
gnuradio-companion lab09_adsb_receiver.grc
```

1. Set `rf_gain` to **60 dB** — much higher than the FM labs. This is a weak-signal problem.
2. Watch the **Signal magnitude** Time Sink. It is set to NORM trigger at level 0.2, so it
   holds still when a burst arrives. **Look for 120 µs bursts** with the four-pulse preamble
   visible at the start:

```
   ▐▌ ▐▌    ▐▌▐▌ ▐ ▐▌▐▌▐ ▌▐▌ ▐ ▌▐▌▐▌ ...
   └──preamble──┘└────── 112 data bits ──────┘
```

3. Watch the terminal:

```
[ADS-B] ICAO 4840D6  KLM1023    38000 ft    52.2572,   3.9194   470 kt  87deg  msgs=14
```

### Exercise 1 — Find the threshold sweet spot

Sweep `Preamble threshold` and record both numbers (candidates are printed by the offline
script; the GUI shows CRC-valid frames):

| Threshold | Candidates/s | CRC-valid/s | Interpretation |
|---|---|---|---|
| 0.05 | very many | highest | CPU-bound but catches the weakest aircraft |
| 0.25 | moderate | high | good default |
| 0.60 | few | lower | only strong, close aircraft |

The lesson: **the optimum is lower than intuition suggests**, because the CRC costs you nothing
to be wrong. Push the threshold down until CPU usage becomes the limit, not until false alarms
"look" acceptable.

### Exercise 2 — Watch a position assemble

A single position frame is **not** enough. Watch the terminal: altitude appears immediately,
but latitude and longitude only appear once an even *and* an odd frame have both arrived —
typically within a second, sometimes several. That delay is CPR doing its 16-bits-per-message
saving, live.

### Exercise 3 — Measure your range

Log positions for an hour and compute the great-circle distance from your antenna to the
farthest aircraft. Then compare with the radio horizon:

$$
d_{\text{nm}} \approx 1.23\left(\sqrt{h_{\text{aircraft,ft}}} + \sqrt{h_{\text{antenna,ft}}}\right)
$$

If your measured range is far short of that, the limit is your antenna or your placement, not
your DSP. Move the antenna and measure again — that experiment teaches more about radio than
any parameter change in the flowgraph.

### Exercise 4 — Add short-frame (56-bit) support

The decoder only handles 112-bit frames. Mode S also uses **56-bit** frames (DF 0, 4, 5, 11).
Add them: try slicing 56 bits as well as 112 at each candidate, and check the CRC of each.

There is a catch, and it is instructive: for DF 4/5/20/21 the parity is **XORed with the
aircraft's ICAO address**, so the remainder is *not* zero — it *is* the address. You would need
a list of addresses you have already seen from DF 17 frames to validate them. See
[Fundamentals 10](../../01_fundamentals/10_error_detection_and_framing.md).

### Exercise 5 — Plot the aircraft

Have the decoder append CSV to a file:

```python
print(f"{time.time()},{icao:06X},{ac['callsign']},{ac['alt']},{ac['lat']},{ac['lon']}",
      file=open('/tmp/adsb.csv', 'a'))
```

Then plot it with `folium` or `matplotlib`. Seeing your own aircraft tracks appear over a map,
decoded from first principles by code you understand end to end, is the pay-off for nine labs.

---

## 🔬 Verification

The generated flowgraph was executed headlessly against a synthetic capture containing 80
frames built from four canonical Mode S messages at 20 dB SNR:

```
$ QT_QPA_PLATFORM=offscreen python3 lab09_adsb_from_file.py
[ADS-B] ICAO 4840D6  KLM1023   msgs=20
[ADS-B] ICAO 40621D   38000 ft    52.2572,   3.9194  msgs=40
[ADS-B] ICAO 485020  159 kt 183deg  msgs=20

CRC-valid frames: 80 / 80        preamble candidates: 147
```

The four source frames and their expected decodes are the standard reference vectors:

| Hex frame | Expected | Decoded |
|---|---|---|
| `8D40621D58C382D690C8AC2863A7` | pos even, 38000 ft | ✅ |
| `8D40621D58C386435CC412692AD6` | pos odd, 38000 ft | ✅ |
| `8D4840D6202CC371C32CE0576098` | callsign KLM1023 | ✅ |
| `8D485020994409940838175B284F` | 159 kt, 183°, −832 ft/min | ✅ |

CPR global decoding of the even/odd pair gives **52.2572 °N, 3.9194 °E**, matching the
published value to the full precision of the encoding.

`03_scripts/simulate_adsb_decode.py --selftest` re-runs these vectors and the CRC directly.

---

## 🐛 Troubleshooting

### "Zero frames, ever"
In order of likelihood:
1. **Wrong antenna.** An FM whip at 1090 MHz is not an antenna, it is a resistor. Build the
   69 mm quarter-wave.
2. **Antenna indoors.** Walls cost ~10 dB. Go outside or to a window with sky visibility.
3. **Gain too low.** Try 60–70 dB. Unlike the FM labs, you are noise-limited, not signal-limited.
4. **No aircraft.** Check [FlightRadar24](https://www.flightradar24.com/) for traffic overhead
   right now. Rural areas at night are genuinely quiet.

### "The offline file decodes but live gives nothing"
Then the flowgraph is correct and the problem is entirely RF: antenna, placement, gain, or
traffic. That is exactly why Step 1 exists.

### "Thousands of candidates, almost no valid frames"
Working as designed. The CRC is filtering noise. Raise the threshold only if CPU is the
constraint — filtering harder will lose you aircraft.

### "One CPU core is pinned"
The preamble scan runs on every sample at 2 MSPS. Raise `threshold`, or reduce the Time Sink's
`update_time`. If you need more headroom, the scan is the place to optimise (a coarse
pre-screen on `m > threshold` before the full four-pulse test).

### "Frames decode but positions never appear"
You need an even **and** an odd frame from the same aircraft. Distant aircraft heard
intermittently may never give you both in the 10-second window CPR requires. Altitude will
still work — it is in every position frame.

### "Positions are wildly wrong (in the wrong hemisphere)"
CPR's global decode is only unambiguous if the two frames are close in time. If they are far
apart the aircraft has moved between grid cells. The reference implementation adds a
sanity check against a locally-known position; ours does not, which is worth knowing before you
trust the output.

### "`O` characters in the terminal"
USB overflow at 2 MSPS. Close other applications, or use a USB 3.0 port directly (not a hub).

---

## ❓ Questions to Ponder

1. **Why 2 MSPS exactly, when the signal is several MHz wide?**
   We do not need to reproduce the pulse *shape*, only decide which half of each 1 µs bit is
   louder. Two samples per bit is the minimum that answers that question. Higher rates (dump1090
   often uses 2.4 MSPS) improve the decision slightly at the cost of CPU and USB bandwidth.

2. **Why does ADS-B need no carrier or timing recovery, when BPSK needed both?**
   Because it is on-off keyed and self-clocking. There is no phase to track (magnitude discards
   it) and every bit contains a pulse, so the preamble alone establishes timing for the whole
   120 µs frame — the transmitter's clock cannot drift meaningfully in that time.

3. **What happens when two aircraft transmit simultaneously?**
   The frames collide and both usually fail CRC. At 1090 MHz with heavy traffic this is common
   and it is why the format is short and repeated twice a second — the system relies on
   repetition rather than error correction, exactly as Fundamentals 10 describes. Advanced
   decoders attempt to separate overlapping frames by amplitude.

4. **The CRC rejects two thirds of the detections. Is the detector badly designed?**
   No — it is *deliberately* generous. A 24-bit CRC gives $6\times10^{-8}$ false-accept odds, so
   the cheapest way to hear more aircraft is to detect more aggressively and let the CRC clean
   up. Design the detector for recall and the validator for precision.

5. **Could you transmit ADS-B?**
   Technically yes, in about twenty lines. **Do not.** Injecting false aircraft into air traffic
   surveillance is a serious crime in every jurisdiction and endangers lives. This lab is
   receive-only, and that is not a technical limitation.

6. **Aircraft broadcast their position unencrypted and unauthenticated. Why?**
   Because ADS-B is a *cooperative safety* system: aircraft must be able to see each other
   directly, with no infrastructure and no key distribution, and so must anyone on the ground
   who might need to help. That openness is the design goal. It also means the system trusts
   whatever it is told, which is a well-documented and much-debated weakness.

---

## 📚 Key Takeaways

- **Simple modulation, hard reception.** Fourteen blocks and a brutal link budget. Not every
  hard problem is a DSP problem.
- **The antenna is the receiver.** 69 mm of wire, outdoors, beats any amount of gain tuning.
- **A strong error check lets you be a sloppy detector.** With CRC-24 downstream, lowering the
  preamble threshold hears *more* aircraft, not more noise.
- **Non-uniform sync patterns exist for a reason** — they are what makes correlation
  unambiguous.
- **CPR is worth studying on its own.** Modular arithmetic saving 16 bits per message, twice a
  second, for every aircraft on Earth.
- **Line of sight is a hard physical limit.** No processing gain recovers a signal blocked by
  the horizon.

---

## 🚀 What's Next?

You have now built, from first principles, receivers for: wideband FM, stereo MPX, AM,
narrowband FM, a synchronised BPSK link, RDS data, and Mode S. That covers analog and digital,
broadcast and packet, audio and data.

Directions from here, roughly in order of difficulty:

- 🛰️ **NOAA APT weather satellites** (137 MHz) — Doppler tracking and image decoding
- 🌦️ **Meteor-M LRPT** (137 MHz) — QPSK, Viterbi FEC, JPEG-ish image reconstruction
- 📟 **POCSAG / FLEX pagers** (150/450 MHz) — trivially simple, still very much alive
- 📶 **LoRa** (868/915 MHz) — chirp spread spectrum, a genuinely different modulation
- 📱 **GSM** with `gr-gsm` — real cellular signalling
- 🛰️ **GPS** — the deepest of all: 20 dB below the noise floor, recovered by correlation

Each one reuses this repo's method: read the theory, plan the rates, build the chain, validate
against a signal you control, then point it at the sky.

---

## 📖 References

1. ICAO Annex 10 Vol. IV — the normative Mode S specification
2. Junzi Sun, *[The 1090 MHz Riddle](https://mode-s.org/decode/)* — the best free resource on ADS-B decoding, and the source of the canonical test frames used here
3. [dump1090](https://github.com/antirez/dump1090) — the classic C decoder; its preamble test is the ancestor of ours
4. RTCA DO-260B — ADS-B minimum operational performance standards
