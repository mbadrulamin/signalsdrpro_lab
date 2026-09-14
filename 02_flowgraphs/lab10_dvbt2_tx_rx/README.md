# 📺 Lab 10 — DVB-T2: Build a Television Transmitter

> **Time:** 4 hours
> **Difficulty:** Expert
> **Theory needed:** [Fund. 08 Digital Modulation](../../01_fundamentals/08_digital_modulation.md) · [Fund. 10 Error Detection](../../01_fundamentals/10_error_detection_and_framing.md) · **[Fund. 11 OFDM](../../01_fundamentals/11_ofdm_and_broadcast_systems.md)**
> **New blocks:** the twelve-stage gr-dtv DVB-T2 chain, OFDM Cyclic Prefixer, USRP **Sink**
> **Flowgraphs:** three — generate (no RF), transmit (RF), analyse
> **Hardware:** 1–2 SignalSDR Pro, and a real DVB-T2 TV or USB tuner
>
> ### 🚨 This is the first lab in this repository that **transmits**.
> Read [Before You Transmit](#-before-you-transmit-anything) before you open any flowgraph.

---

## 🚨 Before You Transmit Anything

DVB-T2 occupies **8 MHz of licensed broadcast spectrum**. Radiating it is not a grey area — in
every country it is a serious offence, and it can knock out television reception for your
neighbours across a wide area. A DVB-T2 signal looks exactly like a real broadcast, so
interference from it is indistinguishable from a broadcaster's own fault, which is precisely why
regulators treat it harshly.

### The only acceptable setups

| | Setup | Notes |
|---|---|---|
| ✅ | **Faraday cage / shielded enclosure** | What this lab is designed for. Both SDRs and the TV inside |
| ✅ | **Direct cable, TX → attenuator → RX/TV** | Simplest and safest. 40–60 dB of attenuation, no antennas anywhere |
| ✅ | **File only** — `lab10_dvbt2_generate.grc` | No RF at all. Everything except the final demonstration |
| ❌ | "Low power should be fine" | It is not. A few mW into an antenna at UHF carries for hundreds of metres |
| ❌ | "I picked an empty channel" | Empty where you are is not empty at the top of the hill |
| ❌ | Antenna connected "just to test" | This is how people transmit by accident |

### The defaults are deliberately inert

`lab10_dvbt2_tx.grc` ships with **`tx_amplitude = 0.0` and `tx_gain = 0 dB`**. Running it
radiates essentially nothing until you deliberately raise both sliders. That is not an
inconvenience — it is the safety interlock. **Check what is connected to the TX/RX port before
you touch either slider.**

> ⚠️ The TX/RX port is bidirectional. If an antenna is attached from an earlier lab — the FM whip
> from Labs 01–08, for instance — it is still attached now.

---

## 🎯 Goal

Build a **complete digital television transmitter** from the standard's own building blocks,
then prove it works by having a real television lock to it.

This is the most sophisticated signal in the repository by a wide margin. It layers, in order:

```
   MPEG-2 transport stream
     → baseband framing         → scrambling
     → BCH outer code           → LDPC inner code      (Fundamentals 10)
     → bit interleaving         → QAM mapping          (Fundamentals 08)
     → cell + time interleaving → frame mapping
     → frequency interleaving   → pilot insertion + IFFT   (Fundamentals 11)
     → cyclic prefix            → P1 preamble
   → 7.6 MHz of RF
```

Twelve stages. Every one exists to defeat a specific channel impairment, and by the end of this
lab you should be able to say which.

> **Verified, in the mode real broadcasters use.** The lab now transmits **32K extended,
> 256QAM, CR 2/3, GI 1/128, PP7 — 40.000738 Mbit/s**, which is what UK Freeview HD and
> Malaysian MYTV put on air. The waveform passes all five structural checks in
> `03_scripts/analyze_dvbt2.py`: occupied bandwidth **7.693 MHz** against 7.768 predicted,
> cyclic prefix at **19.9×**, OFDM symbol period **33,022 samples against 33,024**, P1 preamble
> at **23.9×**, and a T2 frame of **1,983,028 samples against 1,983,488 — 0.023 % error**. The
> multiplex inside it is a real H.264 + MP2 service muxed to **40.000737 Mbit/s against the
> 40.000738 the modulator consumes — 0.0000 % error**, confirmed from the file's own PCR.
>
> **Not verified:** no television has locked to it yet. That is
> [the one measurement left](#what-was-not-tested), and it needs your TV.

---

## 📖 Background: What DVB-T2 Is

DVB-T2 (ETSI EN 302 755) is the second-generation European terrestrial television standard. It
carries 30–40 Mbit/s through an 8 MHz channel — roughly **50 % more than DVB-T** in the same
spectrum — and it does so in the worst channel a broadcaster faces: an indoor aerial, in a city,
with reflections from every building.

| | DVB-T (1997) | DVB-T2 (2009) |
|---|---|---|
| Inner FEC | Convolutional | **LDPC** (64800-bit) |
| Outer FEC | Reed–Solomon | **BCH** |
| Constellations | up to 64QAM | up to **256QAM**, rotated |
| FFT sizes | 2K, 8K | 1K, 2K, 4K, 8K, **16K, 32K** |
| Pilot patterns | one | **eight** (PP1–PP8) |
| Typical capacity | 24 Mbit/s | **36–40 Mbit/s** |
| Multiple services | one stream | **PLPs** with independent robustness |

The gain comes almost entirely from **better coding** (Fundamentals 10) and **more OFDM
options** (Fundamentals 11), not from more bandwidth.

### Why you can transmit it but not receive it in GNU Radio

`gr-dtv` ships a **complete DVB-T2 transmitter** and **no DVB-T2 receiver**. That asymmetry is
not an oversight — a T2 demodulator needs P1 detection, integer and fractional frequency
recovery, channel estimation from eight possible pilot patterns, L1 signalling decode,
de-interleaving across time, an iterative LDPC decoder and a BCH decoder. It is a person-year of
work and several existing commercial implementations.

So this lab does what the industry does: **transmit with software, receive with silicon.** A
€15 USB tuner contains a demodulator chip that does all of the above, and it is the right tool.

> If you want a full software round trip, gr-dtv *does* include a complete **DVB-T** (first
> generation) transmitter *and* receiver. See [Going Further](#-going-further).

---

## 📐 Architecture

### Three flowgraphs

| File | RF? | Purpose |
|---|---|---|
| **`lab10_dvbt2_generate.grc`** | **No** | Build the waveform, write it to a file. Start here |
| `lab10_dvbt2_analyze.grc` | optional | Measure a waveform: spectrum, symbol timing, statistics |
| `lab10_dvbt2_tx.grc` | **Yes** | Transmit. Cage or cable only |

### The transmit chain

```
   MPEG-2 TS file (188-byte packets)
        │
        ▼
  ┌─────────────────┐  1. BB Header        slice into BBFRAMEs, describe the coding
  ├─────────────────┤  2. BB Scrambler     energy dispersal, so data cannot make a line spectrum
  ├─────────────────┤  3. BCH encoder      outer code - kills the LDPC error floor
  ├─────────────────┤  4. LDPC encoder     inner code - 64800-bit codewords, near Shannon
  ├─────────────────┤  5. Bit interleaver  spread a codeword over bits of differing reliability
  ├─────────────────┤  6. QAM mapper       bits → constellation points (rotated)
  ├─────────────────┤  7. Cell + TIME      spread one codeword over hundreds of milliseconds
  │                 │     interleaver
  ├─────────────────┤  8. Frame mapper     build the T2 frame + L1 signalling in the P2 symbols
  ├─────────────────┤  9. Freq interleaver scatter cells across carriers
  ├─────────────────┤ 10. Pilot generator  insert pilots, then IFFT → time domain
  ├─────────────────┤ 11. Cyclic prefixer  copy the last 1/8 of each symbol to its front
  ├─────────────────┤ 12. P1 insertion     prepend the 2048-sample preamble
  └────────┬────────┘
           ▼
      × tx_amplitude          ← OFDM has ~10 dB PAPR: leave headroom or the peaks clip
           │
     ┌─────┴─────┬──────────────┬──────────────┐
     ▼           ▼              ▼              ▼
 Freq Sink   Time Sink     File Sink      USRP SINK
                          (generate)     (tx, RF!)
```

### Rate plan

| Quantity | Value | Why |
|---|---|---|
| Elementary sample rate | **9.142857 MSPS** | $\frac{64}{7}$ MHz — **fixed by the standard** for an 8 MHz channel |
| FFT size | 32768 (`FFTSIZE_32K_T2GI`) | What broadcasters use. See [config table](#-changing-the-configuration) |
| Carrier spacing | 279.02 Hz | $f_s / N_{fft}$ — thirty-two times finer than the 1K mode |
| Useful symbol $T_u$ | 3.584 ms | $1/\Delta f$ |
| Guard interval | 256 samples = 28 µs | GI 1/128 → tolerates an 8.4 km path difference |
| Symbol period | **33,024 samples** = 3.612 ms | $32768 + 256$ |
| Active carriers | 27,841 (extended) | → occupied bandwidth **7.768 MHz** |
| P2 symbols | 1 | $N_{P2}$ is 1 for 16K and 32K, 16 for 1K |
| T2 frame | 1,983,488 samples = **216.94 ms** | P1 (2048) + 1 P2 + 59 data symbols |
| **Payload rate** | **40.000738 Mbit/s** | $\frac{202 \times (43040 - 80)}{216.94\ \text{ms}}$ |

> **Why 32K rather than something gentler?** Because a television has to recognise it. 1K is a
> legal DVB-T2 mode and part of the validation vectors, but no broadcaster transmits it, and a
> consumer tuner that only scans what it expects to find may simply never look. 32K extended
> with GI 1/128 and PP7 is the single most deployed DVB-T2 mode in the world.
>
> The cost is nothing here: this configuration runs at **7.8× real time** on an i7-10875H.

> **The sample rate is not a free choice.** Unlike every other lab in this repo, you cannot pick
> a convenient rate and resample: 64/7 MHz *defines* the carrier spacing, and a receiver's FFT
> will not line up with anything else. Measured on the SignalSDR Pro, UHD delivers
> **9,142,856.97 SPS** against the required 9,142,857.14 — an error of **0.019 ppm**, far inside
> tolerance.

---

## 🧪 Running the Lab

### Step 0 — Make a transport stream, with your own video in it

DVB-T2 carries an MPEG-2 Transport Stream, and **the rate is not a free choice**. This
configuration swallows exactly:

$$\frac{202 \text{ FEC blocks} \times (43040 - 80)\ \text{bits}}{1{,}983{,}488 / 9{,}142{,}857\ \text{s}}
= \mathbf{40{,}000{,}738\ \text{bit/s}}$$

```bash
cd 03_scripts
./make_video_ts.py ~/Downloads/Bintang.mp4 /tmp/bintang_dvbt2.ts \
    --standard dvbt2 --t2-fft 32k --t2-guard 1/128 --t2-rate 2/3 \
    --t2-fecblocks 202 --t2-datasyms 59 --video-bitrate 12000000
```

`--video-bitrate` matters at 40 Mbit/s: a broadcaster fills that with six or seven programmes,
and you have one. Capping the video at 12 Mbit/s gives excellent 1080p and lets the muxer stuff
the remaining 28 Mbit/s with null packets — which is precisely what a real multiplex with spare
capacity looks like.

That computes the rate from the modulation parameters, encodes H.264 + MP2 inside it, stuffs
null packets up to exactly that figure, and then checks its own work by recovering the rate
from the PCR timestamps in the finished file:

```
  PCR-derived mux rate: 40.000737 Mbit/s
  expected            : 40.000738 Mbit/s  (-0.0000 % error)
```

No ffmpeg? This still works, it just has no picture:

```bash
./make_test_ts.py --out /tmp/bintang_dvbt2.ts --seconds 10 --rate 40000738
```

> #### ⚠️ Correction to earlier versions of this lab
>
> This page used to say `--rate 4e6`, and the ffmpeg example used `-muxrate 4000000`. **That is
> wrong**, and it is wrong in a way that hides itself. The file source loops, so the modulator
> never starves — it simply reads the file faster than the stream's own clock says it should. With a pictureless test stream nothing visibly breaks. Put video in it and the
> television's clock recovery fights the PCR for a few seconds and then gives up.
>
> The rate is arithmetic. Compute it, stuff to it, and verify it from the PCR.

#### Settings that matter to a real television

`make_video_ts.py` defaults to these because consumer tuners are less forgiving than ffplay:

| Setting | Value | Why |
|---|---|---|
| Video codec | H.264 High@4.0, `yuv420p` | The DVB-T2 baseline. 10-bit or 4:2:2 will not decode |
| Audio codec | **MP2**, 48 kHz stereo | Every DVB television decodes MP2. AAC is smaller but not universal on older sets |
| GOP | 25 frames, **closed**, IDR every GOP | The TV can start at any keyframe. Long or open GOPs make channel change feel broken |
| `-sdt_period 0.5` | SDT twice a second | This is the table that puts the name in the channel list |
| Rate control | CBR with `minrate = maxrate` | A multiplex has no room to borrow from later |

### Step 1 — Generate the waveform, with no RF

```bash
cd 02_flowgraphs/lab10_dvbt2_tx_rx
python3 lab10_dvbt2_generate.py
```

Three seconds of signal is 220 MB. Watch the **Frequency Sink**: OFDM does not look like the
signals in earlier labs.

```
    Lab 07 BPSK (RRC shaped)          DVB-T2 OFDM
         ╱▔▔▔▔▔╲                   ▁▁▁████████████▁▁▁
        ╱       ╲                  ▁▁▁████████████▁▁▁
    ───╱─────────╲───              ───┴────────────┴───
      raised cosine hump           flat top, near-vertical skirts
                                   ◄──── 7.6 MHz ────►
```

**The flat top is the 853 carriers.** The near-vertical edges are what orthogonality buys you —
no guard bands, no roll-off, just a wall of carriers that stops abruptly.

### Step 2 — Prove it is really DVB-T2

```bash
cd 03_scripts
python3 analyze_dvbt2.py /tmp/dvbt2_signal_9M14_fc32.iq
```

This measures five properties the standard fixes and checks them against the configuration. All
five must pass before you consider transmitting anything.

### Step 3 — Watch the OFDM structure live

```bash
cd 02_flowgraphs/lab10_dvbt2_tx_rx
python3 lab10_dvbt2_analyze.py
```

Look at the **cyclic-prefix correlation** plot. Four blocks — Delay(1024) → Conjugate →
Multiply → Moving Average(128) — produce a peak at the start of **every OFDM symbol**:

```
    │    ╱╲          ╱╲          ╱╲          ╱╲
    │   ╱  ╲        ╱  ╲        ╱  ╲        ╱  ╲
    └──╱────╲──────╱────╲──────╱────╲──────╱────╲──▶
       ◄─── 1152 samples ───►   126 µs apart
```

That is the van de Beek estimator from
[Fundamentals 11](../../01_fundamentals/11_ofdm_and_broadcast_systems.md), built from primitives,
finding symbol timing with **no pilots, no preamble and no knowledge of the data**. It works
purely because the guard interval is a copy.

The **amplitude histogram** shows the Rayleigh distribution — the visible cost of OFDM's PAPR.

### Step 4 — Transmit (cage or cable only)

Set up first:

```
  ┌──────────────┐                                  ┌──────────────┐
  │ Laptop 1     │   TX/RX ──[ 30 dB ]──[ 30 dB ]── │ TV / USB     │
  │ SignalSDR #1 │            attenuators           │ tuner        │
  │ lab10_tx.grc │                                  └──────────────┘
  └──────────────┘         (or: everything inside a Faraday cage)
```

Then:

1. **Check the antenna port.** Physically look at it.
2. Choose `center_freq` — a UHF TV channel **that is unused where you are**. UK/EU channel 21 is
   474 MHz; channel `n` is $474 + 8(n-21)$ MHz.
3. Run `lab10_dvbt2_tx.py`.
4. Raise `tx_gain` to about 20 dB.
5. Raise `tx_amplitude` **slowly**, from 0 toward 0.25. Watch the Time Sink — if the peaks flatten
   at ±1 you are clipping, and the spectrum will regrow into the adjacent channel.
6. On the TV, run a manual channel scan on that frequency.

**What success looks like:** the TV reports signal strength and quality, and finds one service
named **SDR LAB TV**. Most TVs have a hidden signal-meter page — that is where the interesting
numbers are (MER, BER before and after LDPC).

### Step 5 — Receive with the second SDR

Enable `usrp_source` in `lab10_dvbt2_analyze.grc` (and disable `file_source` + `throttle`). Now
you are measuring a genuine over-the-air OFDM signal: the cyclic-prefix correlation still
appears, but now with real multipath and noise in it.

**Compare the correlation peak sharpness with the file version.** Multipath broadens it — you are
directly observing the channel's delay spread.

---

## 🔬 Verification

### What was tested

The generated waveform was analysed with `03_scripts/analyze_dvbt2.py`:

```
1. Occupied bandwidth (99% power)
     measured 7.571 MHz    expected 7.616 MHz  (853 carriers x 8.929 kHz)      PASS
2. Cyclic prefix correlation at lag N_fft
     peak/median = 13.4x                                                        PASS
3. OFDM symbol period
     measured 1152 samples     expected 1152 = 1024 + 128                       PASS
4. P1 preamble detection
     3 detections, peak/mean = 24.3x                                            PASS
5. T2 frame period
     measured 2,284,869 samples = 249.91 ms
     expected 2,285,312 samples = 249.96 ms   (0.019% error)                    PASS

   PAPR (99.99th percentile / mean): 9.6 dB
RESULT: 5/5 checks passed - this is a valid DVB-T2 waveform
```

The `lab10_dvbt2_analyze.grc` flowgraph was then run headlessly against that waveform and its
correlator recovered **47,557 symbol-timing peaks with a median spacing of 1153 samples** against
the 1152 predicted.

The transport stream generator was verified by parsing its own output back: **0 bad sync bytes,
all 446 PSI sections CRC-valid**, and the service name round-trips through the SDT.

**The video stream was then built and put through the same modulator.** `Bintang.mp4`
(1920×1080 H.264 + AAC, 209 s) re-encoded to 1920×1080 H.264 High@4.0 at 12 Mbit/s with MP2
audio, muxed up to the mode's full 40 Mbit/s:

```
/tmp/bintang_dvbt2.ts
  1,045,172,276 bytes = 5,559,427 packets of 188
  sync byte 0x47 present on 5,559,427/5,559,427 (100.000 %)
  PID 8191 null 74.58 % | PID 256 video 24.83 % | PID 257 audio 0.50 %
  PAT 0.04 % | PMT 4096 0.04 % | SDT 17 0.01 %
  PCR-derived mux rate: 40.000737 Mbit/s
  expected            : 40.000738 Mbit/s  (-0.0000 % error)
```

The payload rate was also confirmed against the running chain rather than only derived:
86,779,200 transport bytes went in and **exactly 80.0000 T2 frames of 1,983,488 samples** came
out — 1,084,740 bytes per frame, 40.000738 Mbit/s.

That stream was modulated and analysed, and passes all five checks — occupied bandwidth
**7.693 MHz** against 7.768 predicted, cyclic prefix **19.9×**, symbol period **33,022 against
33,024**, P1 at **23.9×**, T2 frame **1,983,028 against 1,983,488**. **The waveform now carries
a real picture, in the mode a television expects to find.**

**Real-time transmission was checked on the radio** with `tx_amplitude = 0`, so nothing
radiated. Six underflows occurred, all of them in the **first 1.6 seconds** while the buffers
prime; across the following 70 seconds there were **none**. The chain runs at 7.8× real time on
average but delivers a whole T2 frame at once every 216.9 ms, so it needs a reservoir — the
`tx_scale` block holds 4,194,304 samples (about two frames) and the USRP sink is given 1024 send
frames. Without those, a chain with 7.8× headroom still stutters.

On hardware, the USRP **TX** chain was queried (without ever starting a flowgraph, so no samples
were streamed): it delivers the DVB-T2 elementary rate to **0.019 ppm** and supports the required
9.14 MHz analog bandwidth.

### What was not tested

- **No television has locked to this signal.** The waveform is structurally correct by five
  independent measurements, it now carries a decodable H.264 + MP2 service, and the chain is the
  gr-dtv reference implementation used for the DVB-T2 validation vectors — but "a TV locks" is a
  claim only you can verify. **This is the one remaining measurement in this lab.**
- **The mode is now the one broadcasters use** (32K extended / 256QAM / CR 2/3 / GI 1/128 /
  PP7), so "my TV does not support this mode" is no longer a likely explanation if it fails to
  find the service. If it still does not, suspect signal level or the channel frequency before
  the configuration.
- **256QAM needs a good signal.** It is the least forgiving constellation in the standard,
  wanting roughly 20 dB C/N against QPSK's 5 dB. Over a cable that is easy; over the air with
  improvised antennas it may not be. If the TV sees the channel but cannot lock, drop to
  `germany-g7` (64QAM CR 2/3, 31.7 Mbit/s) before suspecting anything else.
- **The video path was verified by decoding the transport stream, not by watching a television.**
  `ffprobe` reports H.264 High@4.0 1920×1080 yuv420p plus MP2 48 kHz stereo, and still frames
  decode correctly out of the finished multiplex.
- **Nothing was transmitted at non-zero amplitude in this configuration.** The real-time check
  ran with `tx_amplitude = 0`.
- **The 12 stages are not individually verified.** The LDPC and BCH encoders are exercised, but
  proving they are *correct* would need a receiver.

**If you complete Step 4, please report what your TV showed** — that is the missing measurement.

---

## ⚙️ Changing the Configuration

DVB-T2's parameters are GRC **enums**, so they cannot be driven from a single variable. Changing
the mode means editing several blocks **consistently** — and an inconsistent set produces a
signal no receiver can decode, usually with no error message.

### Which blocks share which parameter

| Parameter | Blocks that must agree |
|---|---|
| `fftsize` | framemapper, freqinterleaver, pilotgenerator, p1insertion **+ the `fft_len` variable** |
| `guardinterval` | framemapper, freqinterleaver, pilotgenerator, p1insertion **+ `cp_len`** |
| `pilotpattern` | framemapper, freqinterleaver, pilotgenerator |
| `constellation` | bitinterleaver, modulator, cellinterleaver, framemapper |
| `rate` | bbheader, bbscrambler, bch, ldpc, bitinterleaver, framemapper |
| `numdatasyms` | framemapper, freqinterleaver, pilotgenerator, p1insertion **+ the variable** |
| `carriermode` | framemapper, freqinterleaver, pilotgenerator, p1insertion |
| `l1constellation` | framemapper (alone — but it must suit the mode) |
| `fecblocks` | cellinterleaver, framemapper **+ the variable** |

### Known-good presets

These come from the official gr-dtv profiles shipped in `/usr/share/gnuradio/examples/dtv/`, so
every combination is legal. **Do not invent combinations** — the standard restricts which pilot
patterns may be used with which FFT/guard-interval pairs, and *gr-dtv does not check*: it will
accept `32K` with `GI 1/4` and `PP1` and hand you a signal no receiver on earth can decode, with
no error message.

| Preset | FFT | Const. | Rate | GI | PP | Carriers | datasyms | fecblocks | Mbit/s | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| **vv003 (lab default)** | 32K T2GI | 256QAM | 2/3 | 1/128 | PP7 | extended | 59 | 202 | **40.00** | **What Freeview HD and MYTV transmit** |
| vv016 | 32K T2GI | 256QAM | 3/4 | 1/128 | PP7 | extended | 59 | 200 | 44.6 | Same, less protection |
| vv001 / vv019 | 32K T2GI | 256QAM | 3/5 | 1/128 | PP7 | extended | 59 | 202 | 36.0 | vv019 has rotation off |
| germany-g6 | 32K | 256QAM | 3/5 | 1/32 | PP4 | normal | 55 | 179 | 33.0 | Real German broadcast |
| germany-g7 | 32K | 64QAM | 2/3 | 1/16 | PP2 | extended | 63 | 150 | 31.7 | Real German broadcast |
| vv036 | 32K | 256QAM | 3/5 | 1/8 | PP2 | normal | 53 | 162 | 30.2 | UK DTG test profile |
| vv008 | 16K | 256QAM | 4/5 | 1/32 | PP6 | extended | 100 | 168 | 37.5 | |
| germany-g1 | 16K | 64QAM | 1/2 | 19/128 | PP2 | extended | 118 | 139 | 21.5 | Real German broadcast |
| vv015 | 8K | 256QAM | 3/5 | 1/32 | PP7 | extended | 238 | 200 | 36.0 | |
| vv011 (old default) | 1K | QPSK | 1/2 | 1/8 | PP3 | normal | 1966 | 48 | 6.17 | Lightest CPU; **no broadcaster uses it** |

Ten parameters move together for a mode change, not seven — `carriermode` and
`l1constellation` matter too, and the L1 constellation is easy to miss: vv003 signals its L1 in
**64QAM**, while the old 1K default used **BPSK**.

The corresponding `.grc` files are in `/usr/share/gnuradio/examples/dtv/` — open one alongside
yours and copy the values across.

---

## 🐛 Troubleshooting

### "The TV finds nothing"
In order of likelihood:
1. **The configuration is inconsistent.** Run `analyze_dvbt2.py` first — if the five checks pass,
   the signal is fine and the problem is RF or the TV.
2. `tx_amplitude` or `tx_gain` is still 0. They start there deliberately.
3. Signal too *strong* — a TV front end overloads easily on a cable. Add 20 dB more attenuation.
4. Wrong channel on the TV, or the TV is set to DVB-T rather than DVB-T2.

### "The TV locks but the picture is blank"
Expected with `make_test_ts.py` — there is no video in the stream. Use the ffmpeg command in
Step 0.

### "Signal quality is poor / it keeps dropping lock"
Almost always **clipping**. OFDM's 10 dB PAPR means an average level of 0.25 already produces
peaks near 1.0. Lower `tx_amplitude` and watch the Time Sink: if the peaks look flat-topped, you
are clipping, and the spectrum will show shoulders growing on either side.

### "The flowgraph will not start / shared memory error"
Some blocks buffer entire T2 frames:
```bash
sudo sysctl -w kernel.shmmax=1073741824
```

### "It runs far slower than real time"
Expected for the larger configurations. 9.14 MSPS through twelve stages including an LDPC encoder
is genuinely heavy. Use the 1K/QPSK default, close the GUI sinks, and prefer `sc16` over `fc32`
on the USRP sink to halve the USB load.

### "`U` characters in the terminal while transmitting"
TX **underflow** — the host is not feeding the SDR fast enough, so the transmitter emits gaps.
The TV will lose lock. Same fixes as above.

### "analyze_dvbt2.py says P1 detection FAILED"
If checks 1–3 pass but 4 fails, your `--fft`/`--gi`/`--datasyms` arguments do not match how the
signal was actually generated. The P1 detector itself correlates the C part against A at **lag
542** — getting that lag wrong (1024 is the tempting mistake) makes it find nothing at all.

---

## ❓ Questions to Ponder

1. **Why is the sample rate 64/7 MHz and not something round?**
   It makes the carrier spacing an exact submultiple of the 8 MHz channel:
   $\Delta f = \frac{64/7}{N_{fft}}$ MHz, which for 32K gives 279 Hz and packs 27,841 carriers
   into 7.77 MHz. Every DVB-T2 receiver's FFT is built around it.

2. **The chain has three interleavers. Why not one?**
   Each defeats a different impairment. **Bit** interleaving spreads a codeword across
   constellation bits of unequal reliability. **Cell/time** interleaving spreads it across
   hundreds of milliseconds, so an impulse — a car ignition, a light switch — cannot destroy a
   whole codeword. **Frequency** interleaving spreads it across carriers, so a notch from
   multipath cannot either. Time and frequency are genuinely different axes of failure.

3. **Why does the cyclic prefix let a single complex division equalise multipath?**
   It turns linear convolution with the channel into *circular* convolution, and circular
   convolution is multiplication in the DFT domain. See
   [Fundamentals 11](../../01_fundamentals/11_ofdm_and_broadcast_systems.md).

4. **What is `tx_amplitude = 0.25` protecting you from?**
   PAPR. The measured signal has 9.6 dB of peak-to-average, so an average of 0.25 already puts
   peaks near full scale. At 1.0 the peaks clip, generating spectral regrowth into the adjacent
   channel — the exact thing that makes an illegal transmission also an *interfering* one.

5. **Why does the standard bother with rotated constellations?**
   Rotating the constellation makes I and Q each carry information about the whole symbol, so if
   a deep fade destroys one component the other can still recover the point. It is essentially
   free diversity, and it costs only a small amount of receiver complexity.

6. **You have two SDRs. What else could the second one do here?**
   Measure the transmitter, not the content: adjacent-channel power ratio, spectral regrowth
   versus `tx_amplitude`, and constellation quality — see
   [Test & Measurement](../../04_applications/14_test_measurement_and_infrastructure.md). That is
   what a broadcast engineer actually does with a second receiver.

---

## 🚀 Going Further

### A full software round trip: DVB-T (first generation)

`gr-dtv` includes both a transmitter **and a receiver** for DVB-T. That makes a complete
SDR-to-SDR loop possible, with the transport stream recovered at the far end:

```
/usr/share/gnuradio/examples/dtv/dvbt_tx_8k.grc
/usr/share/gnuradio/examples/dtv/dvbt_rx_8k.grc
```

Doing this **after** Lab 10 is the right order: T2 shows you the modern architecture, T1 lets you
watch every stage undone. The receive chain — OFDM symbol acquisition, reference-signal
demodulation, demapping, inner deinterleaving, Viterbi, convolutional deinterleaving,
Reed–Solomon, energy descrambling — is a guided tour of everything in Fundamentals 08–11.

### Other directions

- **Measure your own transmitter** — ACPR and spectral regrowth versus drive level
- **Add a second PLP** with different robustness, and see the TV list two services
- **Deliberately impair the channel** — add noise, multipath and Doppler with a Channel Model
  block, and find the cliff edge where the TV loses lock. That is the DVB-T2 equivalent of Lab
  07's BER curve
- **Compare 1K against 32K FFT** with the same content, and measure how much longer an echo each
  survives

---

## 📚 Key Takeaways

- **OFDM inverts the usual trade:** many slow carriers instead of one fast one, which turns a
  brutal equalisation problem into one division per carrier.
- **The cyclic prefix is the whole trick.** It is why OFDM tolerates multipath, and why
  single-frequency networks are possible at all.
- **PAPR is what OFDM costs**, and it is why the amplitude slider matters more than the gain one.
- **Modern FEC is layered**: LDPC for capacity, BCH for the floor.
- **Transmitting is a different discipline from receiving.** A receiver that is wrong is
  disappointing; a transmitter that is wrong is somebody else's problem.
- **Transmit with software, receive with silicon** when the receiver is a person-year of work.
  Knowing when *not* to implement something is engineering too.

---

## 📖 References

1. ETSI EN 302 755 — *DVB-T2* (the normative standard)
2. ETSI TS 102 831 — DVB-T2 implementation guidelines
3. [gr-dtv examples](file:///usr/share/gnuradio/examples/dtv/) — the validation vectors this lab's configuration comes from
4. van de Beek, Sandell & Börjesson, "ML Estimation of Time and Frequency Offset in OFDM Systems", IEEE Trans. SP, 1997 — the cyclic-prefix estimator you build in Step 3
5. ISO/IEC 13818-1 — MPEG-2 Systems (the transport stream `make_test_ts.py` writes)
