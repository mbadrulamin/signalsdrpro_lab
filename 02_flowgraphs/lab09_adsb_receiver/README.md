# ✈️ Lab 09 — Track Aircraft (ADS-B at 1090 MHz)

> **What you will build:** a receiver for **ADS-B** — the messages every airliner broadcasts
> twice a second with its identity, callsign, altitude, speed and position.
> **What you will learn:** pulse position modulation, detecting a message start (a
> **preamble**), a 24-bit CRC, how aircraft squeeze their position into 17 bits (**CPR**), and
> why the **antenna** decides everything here.
> **Before this:** [Lab 08](../lab08_rds_decoder/README.md), and
> [Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md),
> [08](../../01_fundamentals/08_digital_modulation.md) (the PPM section) and
> [10](../../01_fundamentals/10_error_detection_and_framing.md).
> **Time:** about 3 hours. **Difficulty:** expert.
> **Needs the radio:** optional — there is a second flowgraph that reads a file.

**Two flowgraphs:**

| File | Input | Use it to |
|---|---|---|
| `lab09_adsb_from_file.grc` | a test file you generate | check the decoder, with known aircraft |
| `lab09_adsb_receiver.grc` | the live radio at 1090 MHz | receive real aircraft |

---

## 🎯 Goal

Receive real aircraft. Not a simulation — the actual messages that airliners send, about
twice a second, with their 24-bit identity, callsign, altitude, speed, and position to about
**5 metres**.

> ✅ **The decoder is tested.** On a test recording with 80 known messages at 20 dB SNR, it
> decoded **80 out of 80**: aircraft `4840D6` with callsign `KLM1023`, aircraft `40621D` at
> 38,000 ft at 52.2572 °N 3.9194 °E, and aircraft `485020` at 159 knots heading 183°. These
> match the standard test messages exactly. See [Verification](#-verification).
>
> ⚠️ **Real reception is not yet proven here** — with the wrong antenna, we received nothing.
> That result, and why, is in [Verification](#-verification) too.

### Why this lab is different

The flowgraph has only **14 blocks** — fewer than Lab 03. No channel filter, no AGC, no PLL,
no Costas loop, no Symbol Sync:

```
   USRP  →  Complex to Mag  →  ADS-B Decoder  →  count
```

That is the whole receiver.

In Labs 07 and 08, the hard part was **synchronisation**. Here the modulation is so simple that
measuring the signal's size is enough. **The hard part is getting enough signal** (the
antenna), and deciding, 2 million times a second, whether a small bump is an aircraft or just
noise.

---

## 1. Background: Mode S and ADS-B

### A short history

Air traffic radar on the ground sends a question on **1030 MHz**. The aircraft's
**transponder** answers on **1090 MHz**. **Mode S** gave every aircraft a unique 24-bit
**ICAO address**. **ADS-B** then went further: aircraft **broadcast** their GPS position about
twice a second, without being asked. Anyone can receive it — including you.

- **A**utomatic — no pilot action needed.
- **D**ependent — on the aircraft's own navigation (GPS).
- **S**urveillance — it tells others where the aircraft is.
- **B**roadcast — to everyone.

### The signal

| Property | Value |
|---|---|
| Frequency | 1090 MHz |
| Modulation | **PPM** — pulse position modulation |
| Data rate | 1 Mbit/s (1 µs per bit) |
| Pulse width | 0.5 µs |
| One message | 8 µs preamble + 112 data bits = 120 µs |
| ADS-B message type | "DF 17", always 112 bits |
| Error check | 24-bit CRC |
| Transmitter power | 70–500 W (airliners usually about 125 W) |

**How PPM works.** Every 1 µs bit has **one** pulse. *Where* the pulse is gives the bit:

```
  1 µs bit, 0.5 µs pulse

  bit = 1:   ▛▀▀▀▜________        pulse in the FIRST half
  bit = 0:   _______▛▀▀▀▜         pulse in the SECOND half
```

Because every bit has a pulse, the receiver never loses track of time, and it only needs to
ask one question per bit: **is the first half or the second half louder?**

### The preamble — "a message starts here"

Each message starts with four pulses, at 0, 1.0, 3.5 and 4.5 µs:

```
   µs  0    0.5   1.0   1.5   2.0   2.5   3.0   3.5   4.0   4.5   5.0 ... 8.0
       ▛▀▜         ▛▀▜                           ▛▀▜         ▛▀▜
       ███         ███                           ███         ███    (quiet)
```

The gaps are deliberately **uneven**. An even pattern would look similar when shifted by one
step, so the receiver could lock on in the wrong place. This uneven pattern only matches in one
position.

At 2 MSPS (2 samples per µs), the preamble is 16 samples long, with pulses at samples
**0, 2, 7 and 9**. The decoder expects exactly this. **That is why the sample rate must be
2 MSPS in this lab.**

### The message

```
 ┌─────────┬──────┬──────┬─────────────────┬────────────────┬───────────┐
 │ 8 µs    │ DF   │ CA   │ ICAO address    │ ME: the data   │ CRC       │
 │ preamble│ 5 b  │ 3 b  │ 24 b            │ 56 b           │ 24 b      │
 └─────────┴──────┴──────┴─────────────────┴────────────────┴───────────┘
           └──────────────────── 112 bits = 112 µs ──────────────────────┘
```

**DF** ("downlink format") = 17 means ADS-B. The first 5 bits of the data are the **type
code**, which says what the rest is:

| Type code | Contains |
|---|---|
| 1–4 | Callsign (the flight number, like `KLM1023` or `MAS370`) |
| 5–8 | Position on the ground |
| 9–18 | Position in the air, with pressure altitude |
| 19 | Speed and direction |
| 20–22 | Position in the air, with GPS height |

### Why this is hard: the link budget

A **link budget** adds up the gains and losses between transmitter and receiver
([Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md)). For an aircraft 100 km
away:

| Item | Value |
|---|---|
| Aircraft transmitter: 125 W | **+51 dBm** |
| Loss over 100 km of free space at 1090 MHz | **−133.2 dB** |
| Power reaching your antenna | 51 − 133.2 = **−82.2 dBm** |
| Receiver noise in 2 MHz (noise figure 8 dB) | −174 + 63 + 8 = **−103 dBm** |
| **SNR** | **about 21 dB** — enough, but not by much |

Now change one thing:

| Change | New SNR |
|---|---|
| Antenna indoors (a wall costs ~10 dB) | 11 dB — only just works |
| 3 m of cheap RG-58 cable (~3 dB at 1090 MHz) | 18 dB |
| Wrong antenna (FM whip, ~10 dB lost) | 11 dB |
| Aircraft below the horizon | **nothing at all**, at any gain |

**ADS-B needs line of sight.** The distance you can see an aircraft at height *h* feet is
roughly:

$$
d_{\text{nautical miles}} \approx 1.23\sqrt{h_{\text{feet}}}
$$

An airliner at 38,000 ft can be seen up to about 240 nautical miles (440 km) — **if** nothing is
in the way. A hill or a building blocks it completely. That is why **where you put the
antenna** matters more than anything else in this lab.

---

## 2. The flowgraph

```
      USRP Source   1090 MHz, 2 MSPS, gain 60 dB   (or: File Source + Throttle)
          │
          ├──────────────────────▶ Spectrum (see the bursts)
          ▼
      Complex to Mag      the size of each sample, √(I² + Q²)
          │               ADS-B is pulses on and off: all the information is in the size.
          │               No phase needed.
          ├──────────────────────▶ Time plot (triggered) ← see the pulses
          ▼
      ADS-B Decoder (Embedded Python Block)
          1. find a preamble
          2. read 112 bits: which half is louder?
          3. check the 24-bit CRC
          4. read the data: callsign, altitude, position, speed
          │
          ▼
      Number display (messages)      terminal: [ADS-B] ICAO 4840D6  KLM1023  ...
```

**What is missing, on purpose:**

- **No channel filter.** The ADS-B signal is wider than 2 MHz, but we only need the rough
  shape of the pulses, not every detail.
- **No AGC.** The detection threshold is set by hand.
- **No carrier or timing recovery.** PPM needs neither: we only measure size, and every bit has
  a pulse.

### Controls

| Control | Default | What it does |
|---|---|---|
| RF Gain | 60 dB | Much higher than the FM labs: aircraft signals are weak |
| Preamble threshold | 0.25 | How big a bump must be to count as a possible message |
| Preamble ratio | 3.0 | How much bigger the pulses must be than the gaps between them |

---

## 3. Inside the decoder

In GRC, right-click `adsb_decoder` → Properties to read the code.

### Step 1 — Find the preamble

```python
hi = mean(m[n+0], m[n+2], m[n+7], m[n+9])         # where the 4 pulses should be
lo = mean(m[n+1], m[n+3..6], m[n+8], m[n+10..15]) # where it should be quiet
accept if (hi - lo) > threshold and hi > ratio * lo
```

Two tests, which catch different problems:

- **`hi − lo > threshold`** — the pulses must be clearly bigger than the gaps. Rejects small
  noise bumps.
- **`hi > ratio × lo`** — the pulses must be *several times* bigger than the gaps. Rejects a
  loud signal that is loud everywhere (interference, or the end of another message).

The check is done on the whole buffer at once with NumPy, not one sample at a time in a Python
loop. That is what makes 2 million checks per second possible in Python.

### Step 2 — Read the bits

```python
d = m[p+16 : p+240]                       # the 112 bits, 2 samples each
bits = (d[0::2] > d[1::2]).astype(int)    # first half louder → 1
```

Two lines. That is the whole demodulator. Compare that with the Costas loop and Symbol Sync
that BPSK needed in Lab 07.

### Step 3 — The CRC (this is where the real work happens)

```python
GEN = 0x1FFF409          # the 24-bit CRC generator
def crc24(bits):
    reg = 0
    for b in bits:
        reg = ((reg << 1) | b) & 0x1FFFFFF
        if reg & 0x1000000:
            reg ^= GEN
    return reg & 0xFFFFFF
```

For an ADS-B message (DF 17), a correct message gives a CRC result of **zero**.

> 💡 **A surprising lesson.** In the test run, the preamble test found **147** possible
> messages. Only **80** passed the CRC. So almost half of what the detector found was noise, and
> the CRC quietly threw it away.
>
> The chance that random noise passes a 24-bit CRC is 1 in 2²⁴ — about 1 in 17 million. So a
> message that passes can be trusted. That means you can make the **preamble test generous**
> (a lower threshold). You will get more false starts, but the CRC removes them, and you will
> hear **more real aircraft**.
>
> **Rule:** with a strong error check at the end, it is fine for the first detector to be
> "sloppy".

### Step 4 — Read the data

**Callsign** (type 1–4): eight characters, 6 bits each.

**Altitude** (type 9–18): a 12-bit field. Usually, altitude = 25 × N − 1000 feet (25 ft steps).

**Position — CPR (Compact Position Reporting).** The clever part. Sending full latitude and
longitude to about 5 m would need about 50 bits. CPR sends only **17 bits each**. How?

It sends the position **within a grid square**, not the full position. It uses two slightly
different grids, "even" (60 zones) and "odd" (59 zones), and alternates between them. One
message is ambiguous, but an **even and an odd message together**, received within about
10 seconds, give the exact position anywhere on Earth.

<details>
<summary><b>Going deeper:</b> the CPR latitude formula</summary>

$$
j = \left\lfloor 59\,\text{lat}_{\text{even}} - 60\,\text{lat}_{\text{odd}} + 0.5 \right\rfloor
$$
$$
\text{lat}_{\text{even}} = \frac{360}{60}\bigl((j \bmod 60) + \text{lat}^{cpr}_{\text{even}}\bigr)
$$

This is the Chinese Remainder Theorem applied to the surface of the Earth. The number of
longitude zones changes with latitude (the `NL` function), because lines of longitude get closer
together towards the poles; this keeps the grid squares roughly square everywhere.
</details>

**Speed** (type 19): the east-west and north-south speeds in knots, and the climb rate in
feet per minute. From these the decoder works out speed and heading.

---

## 4. Running the lab

### Step 1 — Test with known aircraft (no radio)

As in Lab 08: never debug a decoder on a signal you do not control.

```bash
cd 03_scripts
python3 simulate_adsb_decode.py --seconds 2 --snr 20 --out /tmp/adsb_test_2Msps_fc32.iq
cd ../02_flowgraphs/lab09_adsb_receiver
python3 lab09_adsb_from_file.py
```

You should see the three known aircraft straight away:

```
[ADS-B] ICAO 4840D6  KLM1023   msgs=54
[ADS-B] ICAO 40621D   38000 ft    52.2572,   3.9194  msgs=116
[ADS-B] ICAO 485020  159 kt 183deg  msgs=60
```

If not, the problem is in the flowgraph, not the sky.

### Step 2 — Build an antenna

**This matters more than every setting in the flowgraph put together.**

A **quarter-wave** antenna for 1090 MHz:

$$
\lambda = \frac{c}{f} = \frac{3\times10^8}{1.09\times10^9} = 275\text{ mm},
\qquad \frac{\lambda}{4} = \mathbf{69\text{ mm}}
$$

So: a **69 mm** piece of wire on the centre pin of an SMA connector. For best results, add four
more 69 mm wires ("radials") from the outer part of the connector, sloping down at 45°. Cost:
almost nothing. It will be far better than the FM telescopic whip, which is about ten times too
long for 1090 MHz. See the [Antennas reference](../../05_reference/03_antennas.md).

Where to put it, most important first:

1. **Outside, with a view of the sky.** ADS-B needs line of sight.
2. **High up.** Every metre higher lets you see further.
3. **Short, good cable.** RG-58 loses about 1 dB per metre at 1090 MHz. Keep it under 3 m.

### Step 3 — Go live

```bash
gnuradio-companion lab09_adsb_receiver.grc
```

1. **RF Gain** starts at **60 dB** — much higher than for FM.
2. Watch the **Signal magnitude** time plot. It only updates when a bump above 0.2 arrives, so
   it freezes on a burst. Look for **120 µs bursts**, with the four preamble pulses at the start:

```
   ▐▌ ▐▌    ▐▌▐▌ ▐ ▐▌▐▌▐ ▌▐▌ ▐ ▌▐▌▐▌ ...
   └─preamble─┘└────── 112 data bits ──────┘
```

3. Watch the terminal. A line looks like this (an invented example — your aircraft will
   differ; Malaysian-registered aircraft have addresses starting with `75`):

```
[ADS-B] ICAO 75xxxx  MAS123    38000 ft     3.1234,  101.5678   470 kt  87deg  msgs=14
```

> 💡 Near Kuala Lumpur, KLIA and Subang give constant traffic. Check
> [FlightRadar24](https://www.flightradar24.com/) to see what is overhead right now, and
> compare.

---

## 5. Exercises

### Exercise 1 — Find the best threshold

Change **Preamble threshold** and watch the message count:

| Threshold | Possible messages | Good messages | Meaning |
|---|---|---|---|
| 0.05 | very many | most | catches the weakest aircraft, but uses much more CPU |
| 0.25 | moderate | many | a good default |
| 0.60 | few | fewer | only strong, close aircraft |

The best threshold is **lower** than you might expect, because a wrong guess costs nothing —
the CRC removes it. Lower it until the CPU becomes the limit.

### Exercise 2 — Watch a position appear

Altitude appears straight away. Latitude and longitude only appear after **both** an even and
an odd message from the same aircraft have arrived — usually within a second, sometimes longer.
That wait is CPR at work.

### Exercise 3 — Measure your range

Record positions for an hour. Work out the distance from your antenna to the furthest aircraft.
Compare it with the radio horizon:

$$
d_{\text{nm}} \approx 1.23\left(\sqrt{h_{\text{aircraft, ft}}} + \sqrt{h_{\text{antenna, ft}}}\right)
$$

If your range is much shorter, the limit is your antenna or where you put it — not the
software. Move the antenna and measure again. You will learn more about radio from this than
from any setting in the flowgraph.

### Exercise 4 — Add short (56-bit) messages

The decoder only reads 112-bit messages. Mode S also has **56-bit** messages (DF 0, 4, 5, 11).
Try reading 56 bits as well as 112 at each possible start, and check the CRC of each.

There is a catch: for DF 4, 5, 20 and 21, the CRC is **mixed with the aircraft's address**, so
the result is not zero — it *is* the address. To check them, you need a list of addresses you
have already seen in DF 17 messages. See
[Fundamentals 10](../../01_fundamentals/10_error_detection_and_framing.md).

### Exercise 5 — Draw the aircraft on a map

Make the decoder add a line to a CSV file for each position:

```python
print(f"{time.time()},{icao:06X},{ac['callsign']},{ac['alt']},{ac['lat']},{ac['lon']}",
      file=open('/tmp/adsb.csv', 'a'))
```

Then plot it with `folium` or `matplotlib`. Seeing aircraft tracks on a map, decoded by code you
understand from start to end, is the reward for nine labs of work.

---

## 🔬 Verification

### With test signals — the decoder is correct

The flowgraph was run on a test recording with 80 messages, made from four standard Mode S
test messages, at 20 dB SNR:

```
$ python3 lab09_adsb_from_file.py
[ADS-B] ICAO 4840D6  KLM1023   msgs=20
[ADS-B] ICAO 40621D   38000 ft    52.2572,   3.9194  msgs=40
[ADS-B] ICAO 485020  159 kt 183deg  msgs=20

CRC-valid frames: 80 / 80        preamble candidates: 147
```

| Message (hex) | Should be | Decoded |
|---|---|---|
| `8D40621D58C382D690C8AC2863A7` | position (even), 38000 ft | ✅ |
| `8D40621D58C386435CC412692AD6` | position (odd), 38000 ft | ✅ |
| `8D4840D6202CC371C32CE0576098` | callsign KLM1023 | ✅ |
| `8D485020994409940838175B284F` | 159 kt, 183°, −832 ft/min | ✅ |

The even + odd pair gives **52.2572 °N, 3.9194 °E**, exactly the published answer.

`03_scripts/simulate_adsb_decode.py --selftest` checks these messages and the CRC directly.
`03_scripts/test_labs_offline.py lab09` runs the real flowgraph on a test recording.

### On real radio — nothing received, and we know why

On a live SignalSDR Pro at 1090 MHz, **zero** messages were received, on both antenna ports,
at every gain:

| Antenna port | Gain | Middle noise level | Highest peak | Good messages |
|---|---|---|---|---|
| TX/RX | 70 dB | 0.0674 | 0.316 | **0** |
| TX/RX | 76 dB | 0.1279 | 0.604 | **0** |
| RX2 | 70 dB | 0.0669 | 0.325 | **0** |
| RX2 | 76 dB | 0.1205 | 0.564 | **0** |

**What the numbers say.** Raising the gain from 70 to 76 dB (+6 dB) raised the noise from
0.0674 to 0.1279: ×1.90, which is **+6.0 dB**. The noise went up exactly as much as the gain.
That means the receiver is only hearing **its own noise**
([Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md)). More gain cannot help,
because no signal is arriving.

The antenna was an FM whip — about ten times too long for 1090 MHz, and badly matched. That is
item 1 in the troubleshooting list below.

**So: the decoder is proven; real reception is not.** If you build the 69 mm antenna, put it
outside, and receive aircraft, you have gone one step further than this repository.

---

## 🔧 Troubleshooting

### Zero messages, ever

Most likely first:

1. **Wrong antenna.** An FM whip at 1090 MHz hardly works at all. Build the 69 mm antenna.
   (This is what happened in the test above.)

   **How to tell whether it is the antenna or the gain:** raise the gain by 6 dB and watch the
   noise level. If the noise also rises by 6 dB, more gain is useless — no signal is arriving,
   so fix the antenna. If the noise hardly moves, keep raising the gain.
2. **Antenna indoors.** A wall costs about 10 dB. Go outside, or to a window facing open sky.
3. **Gain too low.** Try 60–70 dB.
4. **No aircraft.** Check [FlightRadar24](https://www.flightradar24.com/). Some areas are quiet
   at night.

| Other problem | Cause and fix |
|---|---|
| The test file decodes, but live gives nothing | The flowgraph is fine. The problem is the antenna, placement, gain or traffic. That is why Step 1 exists |
| Thousands of possible messages, very few good ones | Working as designed: the CRC is removing noise. Only raise the threshold if the CPU cannot keep up |
| One CPU core at 100 % | The preamble search runs on every sample. Raise the threshold, or slow the displays |
| Messages decode, but positions never appear | You need both an even and an odd message from the same aircraft within ~10 s. Distant aircraft may never give both. Altitude still works |
| Positions are completely wrong | CPR only works if the even and odd messages are close in time. Real decoders also check against a known nearby position; ours does not |
| `O` printed in the terminal | USB cannot keep up. Use a USB 3.0 port on the computer itself, not a hub. Close other programs |

---

## ✅ Summary

- ADS-B is **PPM at 1 Mbit/s on 1090 MHz**: the pulse position in each 1 µs gives the bit.
- The receiver is very simple: **measure size, find the preamble, compare halves, check CRC**.
- A **24-bit CRC** makes each message trustworthy, so the first detector can be generous.
- **CPR** sends position in 17 bits; you need an even and an odd message to decode it.
- **The antenna is the receiver.** 69 mm of wire, outside, beats any amount of gain.
- ADS-B needs **line of sight**. Nothing can recover a signal blocked by the horizon.

## 🧠 Check yourself

1. Why does this receiver not need a Costas loop or Symbol Sync?
   <details><summary>Answer</summary>PPM carries information in *when* a pulse happens, and
   we only measure the size of the signal — so the phase does not matter. Every bit has a
   pulse, and the preamble gives the timing for the whole 120 µs message.</details>
2. Why must the sample rate be exactly 2 MSPS?
   <details><summary>Answer</summary>The decoder expects 2 samples per 1 µs bit, and the
   preamble pulses at samples 0, 2, 7 and 9. Any other rate breaks that pattern.</details>
3. The detector finds 147 possible messages, but only 80 pass the CRC. Is the detector bad?
   <details><summary>Answer</summary>No. It is generous on purpose. The CRC removes the false
   starts almost perfectly, so being generous finds more real aircraft.</details>
4. You raise the gain by 6 dB, and the noise level also rises by 6 dB. What does this mean?
   <details><summary>Answer</summary>The receiver only hears its own noise. More gain will not
   help. Improve the antenna.</details>
5. Could you transmit ADS-B with the SignalSDR Pro?
   <details><summary>Answer</summary>Technically yes. <b>Never do it.</b> Putting false
   aircraft into air traffic systems is a serious crime and puts lives at risk. This lab only
   receives, on purpose.</details>

---

## 🚀 What's next?

You have now built receivers for wide FM, stereo, AM, narrow FM, a digital BPSK link, RDS data
and Mode S. That covers analog and digital, audio and data.

**[Lab 10](../lab10_dvbt2_tx_rx/README.md) transmits for the first time**: you build a DVB-T2
television transmitter that a real TV can receive. Labs 11 and 12 then build the TV receiver
and a two-way video link. Read
[Fundamentals 11](../../01_fundamentals/11_ofdm_and_broadcast_systems.md) first — and prepare a
**Faraday cage or a cable**, because Labs 10 and 12 transmit.

For ideas beyond the labs, see **[the Applications Catalogue](../../04_applications/README.md)**:
589 signals and projects, with a
[difficulty ladder](../../04_applications/README.md#-where-to-start--a-suggested-path). Good
next steps after this lab:

- 🚢 **[AIS](../../04_applications/03_maritime.md)** — ships instead of aircraft
- 🛰️ **[Meteor-M LRPT](../../04_applications/04_satellite_and_space.md)** — weather satellite
  pictures (the older NOAA APT satellites were switched off in 2025)
- 🎈 **[Radiosondes](../../04_applications/05_weather_and_environment.md)** — weather balloons
- 📡 **[Passive radar](../../04_applications/11_radar_and_sensing.md)** — detect the same aircraft
  without their help, and check against your ADS-B results
- 🧭 **[GPS from raw IQ](../../04_applications/10_navigation_and_timing.md)** — a big final
  project

---

## 📖 References

1. ICAO Annex 10 Volume IV — the official Mode S specification
2. Junzi Sun, *[The 1090 MHz Riddle](https://mode-s.org/decode/)* — the best free guide to ADS-B
   decoding, and the source of the test messages used here
3. [dump1090](https://github.com/antirez/dump1090) — the classic ADS-B decoder in C
4. RTCA DO-260B — the ADS-B performance standard
