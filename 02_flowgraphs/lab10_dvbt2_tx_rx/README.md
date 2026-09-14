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

> **Verified, now carrying real video.** The waveform passes all five structural checks in
> `03_scripts/analyze_dvbt2.py`: occupied bandwidth **7.571 MHz**, cyclic prefix at **13.7×**,
> OFDM symbol period **exactly 1152 samples**, P1 preamble at **24.2× peak-to-mean**, and a T2
> frame period of **2,284,871 samples against 2,285,312 predicted — 0.019 % error**. The
> multiplex inside it is a real H.264 + MP2 service muxed to **6.169661 Mbit/s against the
> 6.169662 Mbit/s the modulator consumes — 0.0000 % error**, confirmed from the file's own PCR
> timestamps. See [Verification](#-verification).
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
| FFT size | 1024 | Lab default (see [config table](#-changing-the-configuration)) |
| Carrier spacing | 8928.6 Hz | $f_s / N_{fft}$ |
| Useful symbol $T_u$ | 112 µs | $1/\Delta f$ |
| Guard interval | 128 samples = 14 µs | GI 1/8 → tolerates a 4.2 km path difference |
| Symbol period | **1152 samples** | $1024 + 128$ |
| Active carriers | 853 | → occupied bandwidth **7.616 MHz** |
| T2 frame | 2,285,312 samples = **249.96 ms** | P1 (2048) + 16 P2 + 1966 data symbols |

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

$$\frac{48 \text{ FEC blocks} \times (32208 - 80)\ \text{bits}}{2{,}285{,}312 / 9{,}142{,}857\ \text{s}}
= \mathbf{6{,}169{,}662\ \text{bit/s}}$$

```bash
cd 03_scripts
./make_video_ts.py ~/Downloads/Bintang.mp4 /tmp/bintang_dvbt2.ts --standard dvbt2
```

That computes the rate from the modulation parameters, encodes H.264 + MP2 inside it, stuffs
null packets up to exactly that figure, and then checks its own work by recovering the rate
from the PCR timestamps in the finished file:

```
  PCR-derived mux rate: 6.169661 Mbit/s
  expected            : 6.169662 Mbit/s  (-0.0000 % error)
```

No ffmpeg? This still works, it just has no picture:

```bash
./make_test_ts.py --out /tmp/bintang_dvbt2.ts --seconds 10 --rate 6169662
```

> #### ⚠️ Correction to earlier versions of this lab
>
> This page used to say `--rate 4e6`, and the ffmpeg example used `-muxrate 4000000`. **That is
> wrong**, and it is wrong in a way that hides itself. The file source loops, so the modulator
> never starves — it simply reads the file 1.54× faster than the stream's own clock says it
> should. With a pictureless test stream nothing visibly breaks. Put video in it and the
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
(1920×1080 H.264 + AAC, 209 s) re-encoded to 1280×720 H.264 High@4.0 with MP2 audio:

```
/tmp/bintang_dvbt2.ts
  161,208,684 bytes = 857,493 packets of 188
  sync byte 0x47 present on 857,493/857,493 (100.000 %)
  PID 256 video 79.88 % | PID 257 audio 3.25 % | PID 8191 null 16.31 %
  PAT 0.25 % | PMT 4096 0.25 % | SDT 17 0.05 %
  PCR-derived mux rate: 6.169661 Mbit/s
  expected            : 6.169662 Mbit/s  (-0.0000 % error)
```

That stream was modulated and re-analysed, and it still passes all five checks — occupied
bandwidth 7.571 MHz, cyclic prefix 13.7×, symbol period exactly 1152, P1 at 24.2×, T2 frame
2,284,871 samples against 2,285,312 predicted. **The waveform now carries a real picture**, and
the rate it was muxed at was confirmed from the file's own PCR timestamps rather than assumed.

On hardware, the USRP **TX** chain was queried (without ever starting a flowgraph, so no samples
were streamed): it delivers the DVB-T2 elementary rate to **0.019 ppm** and supports the required
9.14 MHz analog bandwidth.

### What was not tested

- **No television has locked to this signal.** The waveform is structurally correct by five
  independent measurements, it now carries a decodable H.264 + MP2 service, and the chain is the
  gr-dtv reference implementation used for the DVB-T2 validation vectors — but "a TV locks" is a
  claim only you can verify. **This is the one remaining measurement in this lab.**
- **1K FFT is unusual for broadcasting.** It is a legal DVB-T2 mode and part of the validation
  vectors every tuner is tested against, but Malaysian and European broadcasters use 32K. If
  your television refuses to find the service, that is the first thing to suspect — see
  [Changing the Configuration](#-changing-the-configuration).
- **The video path was verified by decoding the transport stream, not by watching a television.**
  `ffprobe` reports H.264 High@4.0 1280×720 yuv420p plus MP2 48 kHz stereo, and still frames
  decode correctly out of the finished multiplex.
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
| `carriermode` | framemapper, freqinterleaver, pilotgenerator |

### Known-good presets

These come from the official gr-dtv validation vectors, so every combination is legal. **Do not
invent combinations** — the standard restricts which pilot patterns may be used with which
FFT/guard-interval pairs.

| Preset | FFT | Const. | Rate | GI | PP | Carriers | datasyms | fecblocks | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **vv011 (lab default)** | 1K | QPSK | 1/2 | 1/8 | PP3 | normal | 1966 | 48 | Lightest CPU, most robust |
| vv010 | 2K | 16QAM | 3/5 | 1/8 | PP2 | normal | 983 | 93 | |
| vv009 | 4K | 64QAM | 2/3 | 1/32 | PP7 | normal | 100 | 31 | |
| vv004 | 8K T2GI | 64QAM | 3/4 | 19/256 | PP5 | extended | 81 | 50 | |
| germany-g1 | 16K | 64QAM | 1/2 | 19/128 | PP2 | extended | 118 | 139 | Closest to a real broadcast |

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
