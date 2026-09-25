# 📺 Lab 10 — Build a Television Transmitter (DVB-T2)

> **What you will build:** a complete **digital TV transmitter** (DVB-T2, the system Malaysia's
> MYTV uses), from the standard's own building blocks — and a real television will receive it.
> **What you will learn:** the twelve stages of a modern broadcast transmitter; OFDM in practice;
> why the transport-stream **rate** and **clock** must be exact; and how to transmit **safely**.
> **Before this:** [Fundamentals 08](../../01_fundamentals/08_digital_modulation.md),
> [10](../../01_fundamentals/10_error_detection_and_framing.md) and
> **[11 — OFDM](../../01_fundamentals/11_ofdm_and_broadcast_systems.md)**.
> **Time:** about 4 hours. **Difficulty:** expert.
> **Hardware:** 1–2 SignalSDR Pro, and a DVB-T2 TV or USB TV tuner.

**Three flowgraphs:**

| File | Transmits? | Use it to |
|---|---|---|
| **`lab10_dvbt2_generate.grc`** | **No** | make the TV signal and save it to a file. **Start here** |
| `lab10_dvbt2_analyze.grc` | No (optional radio input) | measure a TV signal: spectrum, symbol timing, peaks |
| `lab10_dvbt2_tx.grc` | 🚨 **Yes** | transmit. **Faraday cage or cable only** |

---

## 🚨 Before you transmit anything

**This is the first lab that transmits.** Read this whole section first.

DVB-T2 uses **8 MHz of spectrum licensed to TV broadcasters**. In Malaysia, **470–694 MHz is live
MYTV digital TV**. Transmitting there without permission is an offence (Communications and
Multimedia Act 1998), and it can stop your neighbours' TVs working. A DVB-T2 signal looks exactly
like a real broadcast, which is why regulators treat interference from it seriously.

### The only safe ways to do this lab

| | Setup | Notes |
|---|---|---|
| ✅ | **Faraday cage** (a shielded box or room) | The radio, and the TV, inside |
| ✅ | **A cable: TX → attenuators → TV or second radio** | 40–60 dB of attenuation, **no antennas anywhere**. Simplest and safest — and it works *better* (see Lab 12) |
| ✅ | **File only** — `lab10_dvbt2_generate.grc` | No radio waves at all. Covers everything except the final TV test |
| ❌ | "Low power should be fine" | It is not. A few milliwatts into an antenna at UHF can travel hundreds of metres |
| ❌ | "I picked an empty channel" | Empty where you are may not be empty on the next hill |
| ❌ | An antenna connected "just to test" | This is exactly how people transmit by accident |

### The transmitter starts switched off

`lab10_dvbt2_tx.grc` starts with **`tx_amplitude = 0.0`** and **`tx_gain = 0 dB`**. It sends
essentially nothing until you raise **both** sliders on purpose. That is the safety switch.
**Look at what is connected to the `TX/RX` port before you touch either slider.**

> ⚠️ `TX/RX` is used for both transmit and receive. If the FM antenna from Labs 01–08 is still on
> it, it is still on it now.

### Check nothing is still transmitting

A flowgraph killed from a terminal does not always stop. While building this lab, a transmitter
was found **still running 16 minutes after** the command that started it had been killed. (It had
been started by `tv_playout.py --launch`. That bug is fixed: playout now makes the kernel stop the
flowgraph if playout itself dies, tested with both SIGTERM and SIGKILL.) Check anyway:

```bash
ps -eo pid,args | grep [l]ab10_dvbt2_tx
```

If you see anything, stop it **by its number (PID)**: `kill 12345`. Do **not** use `pkill -f` —
its pattern matches its own command line and it kills the terminal that ran it.

---

## 🎯 Goal

Build a **complete digital TV transmitter** from the standard's building blocks, and prove it by
having a real television find and play the channel.

This is the most complex signal in the course. Twelve stages, in order:

```
   MPEG-2 transport stream (the TV programme, as 188-byte packets)
     → baseband framing          → scrambling
     → BCH outer code            → LDPC inner code        (Fundamentals 10, 11)
     → bit interleaving          → QAM mapping            (Fundamentals 08)
     → cell and time interleaving → frame building
     → frequency interleaving    → pilots + IFFT          (Fundamentals 11)
     → cyclic prefix             → P1 preamble
   → 7.8 MHz of radio signal
```

Every stage fights a particular problem. By the end you should be able to say which.

> ✅ **Tested, in the mode broadcasters use:** **32K extended, 256QAM, code rate 2/3,
> guard 1/128, pilot pattern PP7 — 40.000738 Mbit/s**. That is what Malaysia's MYTV and the UK's
> Freeview HD transmit. The generated signal passes all five structural checks, and **a real
> television found the service and played the video** (reported by the lab's owner — see
> [Verification](#-verification)).

---

## 1. Background: what DVB-T2 is

**DVB-T2** (standard ETSI EN 302 755) is the second-generation digital terrestrial TV system. It
carries 30–40 Mbit/s in an 8 MHz channel — about **50 % more than DVB-T** in the same space —
through the hardest conditions a broadcaster faces: indoor aerials in cities, with echoes from
every building.

| | DVB-T (1997) | DVB-T2 (2009) |
|---|---|---|
| Inner error correction | convolutional | **LDPC** (64,800-bit blocks) |
| Outer error correction | Reed–Solomon | **BCH** |
| Constellations | up to 64QAM | up to **256QAM**, rotated |
| FFT sizes | 2K, 8K | 1K, 2K, 4K, 8K, 16K, **32K** |
| Pilot patterns | one | **eight** (PP1–PP8) |
| Typical capacity | 24 Mbit/s | **36–40 Mbit/s** |

The improvement comes from **better error correction** and **more OFDM options**, not from more
bandwidth.

### Why GNU Radio can send DVB-T2 but not receive it

GNU Radio's `gr-dtv` has a **complete DVB-T2 transmitter** but **no DVB-T2 receiver**. A receiver
needs P1 detection, frequency recovery, channel estimation for eight pilot patterns, signalling
decoding, time de-interleaving, an iterative LDPC decoder and a BCH decoder — about a person-year
of work.

So this lab does what the industry does: **transmit with software, receive with a chip.** A cheap
TV or USB tuner contains a chip that does all of that.

> 💡 For a full software round trip, `gr-dtv` has a complete **DVB-T** (first-generation)
> transmitter **and** receiver. [Lab 11](../lab11_tv_receiver/README.md) builds on it.

---

## 2. The transmit chain

```
   MPEG-2 TS (188-byte packets), from a file or from tv_playout.py
        │
  ┌─────────────────┐  1. BB Header           cut the stream into frames; describe the coding
  ├─────────────────┤  2. BB Scrambler        mix the bits, so data cannot make a single tone
  ├─────────────────┤  3. BCH encoder         outer code: cleans up LDPC's leftover errors
  ├─────────────────┤  4. LDPC encoder        inner code: 64,800-bit blocks, near the theoretical limit
  ├─────────────────┤  5. Bit interleaver     spread each block over bits of different reliability
  ├─────────────────┤  6. QAM mapper          bits → 256QAM points (rotated)
  ├─────────────────┤  7. Cell + time         spread each block over time, so a short burst of
  │                 │     interleaver         interference cannot destroy it
  ├─────────────────┤  8. Frame mapper        build the T2 frame, with signalling in the P2 symbol
  ├─────────────────┤  9. Freq interleaver    scatter data across carriers
  ├─────────────────┤ 10. Pilot generator     add pilots, then IFFT → time signal
  ├─────────────────┤ 11. Cyclic prefixer     copy the last 1/128 of each symbol to its front
  ├─────────────────┤ 12. P1 insertion        add the 2048-sample frame-start preamble
  └────────┬────────┘
           ▼
      × tx_amplitude         ← OFDM has ~10 dB of peaks: leave room, or they clip
           │
     ┌─────┴─────┬──────────────┬──────────────┐
     ▼           ▼              ▼              ▼
 Spectrum    Time plot      File Sink      USRP SINK
                           (generate)      (tx — RADIO!)
```

### The numbers

| Quantity | Value | Why |
|---|---|---|
| Sample rate | **9.142857 MSPS** | 64/7 MHz — **fixed by the standard** for 8 MHz channels |
| FFT size | 32,768 (`FFTSIZE_32K_T2GI`) | what broadcasters use |
| Carrier spacing | 279.02 Hz | sample rate ÷ FFT size |
| Useful symbol | 3.584 ms | 1 ÷ spacing |
| Guard interval | 256 samples = 28 µs | GI 1/128: copes with 8.4 km of extra echo path |
| **Symbol length** | **33,024 samples** = 3.612 ms | 32,768 + 256 |
| Active carriers | 27,841 (extended mode) | → **7.768 MHz** wide |
| P2 symbols | 1 | 1 for 16K and 32K |
| T2 frame | 1,983,488 samples = **216.94 ms** | P1 (2048) + 1 P2 + 59 data symbols |
| **Payload rate** | **40.000738 Mbit/s** | 202 × (43,040 − 80) bits per 216.94 ms |

> 💡 **Why 32K?** A TV has to recognise the signal. The 1K mode is legal, but no broadcaster uses
> it, and a TV that only looks for what it expects may never find it. 32K extended, GI 1/128, PP7
> is the most widely used DVB-T2 mode in the world. It runs at **7.8× real time** on the test
> laptop (Intel i7-10875H), so it costs nothing extra here.

> 💡 **The sample rate is not your choice.** 64/7 MHz sets the carrier spacing; a TV's FFT will
> not line up with anything else. Measured: UHD gives the SignalSDR Pro **9,142,856.97**
> samples/s against the required 9,142,857.14 — an error of **0.019 parts per million**. Fine.

---

## 3. Running the lab

### Step 0 — Make a transport stream (the TV programme)

DVB-T2 carries an **MPEG-2 transport stream** (TS). Its rate **must** equal what the transmitter
consumes — for this mode:

$$\frac{202 \times (43040 - 80)\ \text{bits}}{1{,}983{,}488 / 9{,}142{,}857\ \text{s}} = \mathbf{40{,}000{,}738\ \text{bit/s}}$$

**Encode once, then play it out.** Two separate steps (why: see
[Don't encode live](#dont-encode-live)):

```bash
cd 03_scripts

# 1. Encode your video once. --loop-safe cuts it at a clean loop point.
./make_video_ts.py ~/Downloads/Bintang.mp4 /tmp/bintang_dvbt2.ts \
    --standard dvbt2 --t2-fft 32k --t2-guard 1/128 --t2-rate 2/3 \
    --t2-fecblocks 202 --t2-datasyms 59 --video-bitrate 12000000 --loop-safe

# 2. Play it out forever. --copy only re-packages it: almost no CPU.
./tv_playout.py /tmp/bintang_dvbt2.ts --copy \
    --standard dvbt2 --t2-fft 32k --t2-guard 1/128 --t2-rate 2/3 \
    --t2-fecblocks 202 --t2-datasyms 59 --fifo /tmp/tv.fifo \
    --launch "python3 ../02_flowgraphs/lab10_dvbt2_tx_rx/lab10_dvbt2_tx.py"
```

`make_video_ts.py` works out the rate from the settings, encodes H.264 video and MP2 audio, fills
the rest with empty ("null") packets up to exactly that rate, and then checks its own work by
reading the rate back from the stream's clock:

```
  PCR-derived mux rate: 40.000737 Mbit/s
  expected            : 40.000738 Mbit/s  (-0.0000 % error)
```

`--launch` starts the transmitter once the FIFO (a named pipe) is ready.

**No ffmpeg, or no video?** This makes a stream with the service name but no picture:

```bash
./make_test_ts.py --out /tmp/bintang_dvbt2.ts --seconds 10 --rate 40000738
```

#### Settings a real TV needs

`make_video_ts.py` uses these by default, because TVs are stricter than computer players:

| Setting | Value | Why |
|---|---|---|
| Video | H.264 High@4.0, `yuv420p` | the DVB-T2 baseline. 10-bit or 4:2:2 will not play |
| Audio | **MP2**, 48 kHz stereo | every DVB TV plays MP2; AAC is not universal on older sets |
| GOP | 25 frames, closed, keyframe every GOP | the TV can start playing at any keyframe |
| SDT every 0.5 s | | this table puts the **name** in the TV's channel list |
| Constant bit rate | `minrate = maxrate` | a multiplex cannot borrow bits from later |
| `--video-bitrate 12000000` | 12 Mbit/s video | excellent 1080p; the other 28 Mbit/s is filled with null packets, just like a real multiplex with spare room |

#### Don't encode live

`tv_playout.py` *can* encode while it plays — don't. The 32K transmitter and a 1080p video encoder
both need several CPU cores. When the encoder falls behind, playout's buffer empties, the
transmitter has nothing to send, and it puts a **gap on the air**.

The TV survives the gap by emptying its own buffers — but audio and video recover by different
amounts, so **lip sync slips and stays slipped**. **Underruns and out-of-sync sound are the same
fault.** Playout tells you when it happens:

```
  *** UNDERRUN: buffer empty, the transmitter is putting a gap on the air.
      Pre-encode once and re-run with --copy; live encoding cannot share the
      CPU with the modulator.
```

`--copy` only re-packages the already-encoded stream: measured, 786 MB of multiplex in 0.94 s.

#### What `--loop-safe` does

A stream played in a loop must end where **both** video and audio frames end, or each lap leaves a
tiny unmatched piece. `Bintang.mp4` is 209.066 s long, but its video runs 208.960 s and its audio
209.066 s (106 ms apart). Video frames are 40 ms (25 fps) and MP2 audio frames 24 ms, so the
nearest clean cut is a multiple of **120 ms**: **209.04 s** = exactly 5,226 video frames and 8,710
audio frames.

> 💡 ffmpeg's `-shortest` sounds right but is not: it stops at whichever runs out first, leaving
> them one audio frame apart. Measured over 7.85 laps: **24 ms of slip per lap**. Cutting at an
> exact shared boundary reduced it to 8 ms, and that remainder does not grow.

#### Two mistakes this lab made, and fixed

> ⚠️ **1. The wrong rate.** Earlier versions used `--rate 4e6` (4 Mbit/s). That fails silently:
> the file source loops, so the transmitter never runs dry — it just reads the stream faster than
> the stream's own clock says. With no picture, nothing looks wrong. With video, the TV's clock
> fights the stream for a few seconds, then gives up. **Calculate the rate, fill to it, and check
> it from the clock.**

> ⚠️ **2. Looping the finished file.** The first long broadcast looked *high quality but jerky* on
> a real TV — every byte correct, yet never smooth. A transport stream carries its **own clock**
> (the **PCR**, written every 20 ms). The TV locks its 27 MHz clock to it. When a looped `.ts` file
> wraps around, the PCR jumps **backwards 208.86 seconds**, with no warning flag. The TV is handed
> frames it thinks are minutes old. Over 26 minutes this happened 7.5 times.
>
> **The fix:** loop the *input video* and let the encoder keep counting upwards — what real TV
> playout does. That is `tv_playout.py`. Tested over 4.2 laps: **0 backward clock jumps** in
> 83.9 s; the clock rose smoothly from 0.700 s to 84.580 s, one PCR every 20.00 ms.
>
> **Correct bytes are not the same as a working TV service.** Timing matters too.

### Step 1 — Make the signal, with no radio

```bash
cd 02_flowgraphs/lab10_dvbt2_tx_rx
python3 lab10_dvbt2_generate.py
```

It reads `/tmp/bintang_dvbt2.ts` and writes 3 seconds of signal (about **220 MB**) to
`/tmp/dvbt2_signal_9M14_fc32.iq`. Close the window when it has finished.

Look at the **spectrum**. OFDM looks nothing like the earlier labs:

```
    Lab 07 BPSK                       DVB-T2 OFDM
         ╱▔▔▔▔▔╲                   ▁▁▁████████████▁▁▁
        ╱       ╲                  ▁▁▁████████████▁▁▁
    ───╱─────────╲───              ───┴────────────┴───
      a smooth hump                flat top, almost vertical sides
                                   ◄──── 7.8 MHz ────►
```

**The flat top is 27,841 carriers side by side.** The almost-vertical edges show OFDM's
orthogonality: no gaps between carriers, and a sharp stop at the edge.

### Step 2 — Prove it really is DVB-T2

```bash
cd 03_scripts
python3 analyze_dvbt2.py /tmp/dvbt2_signal_9M14_fc32.iq
```

This measures five things the standard fixes, and compares them with the settings. Expected
(measured on a freshly generated signal):

```
1. Occupied bandwidth          measured 7.692 MHz    expected 7.768 MHz        PASS
2. Cyclic prefix correlation   peak/median = 19.1x                             PASS
3. OFDM symbol period          measured 33024 samples, expected 32768 + 256    PASS
4. P1 preamble detection       peak/mean = 23.9x                               PASS
5. T2 frame period             measured 1,983,025 samples, expected 1,983,488  PASS
   PAPR (99.99th percentile / mean): 9.6 dB
RESULT: 5/5 checks passed  -  this is a valid DVB-T2 waveform
```

**All five must pass before you think about transmitting.**

### Step 3 — Watch the OFDM structure live

```bash
cd 02_flowgraphs/lab10_dvbt2_tx_rx
python3 lab10_dvbt2_analyze.py
```

Look at the **cyclic-prefix correlation** plot. Four blocks — **Delay (32,768) → Conjugate →
Multiply → Moving Average (256)** — make a peak at the start of **every OFDM symbol**:

```
    │    ╱╲             ╱╲             ╱╲             ╱╲
    │   ╱  ╲           ╱  ╲           ╱  ╲           ╱  ╲
    └──╱────╲─────────╱────╲─────────╱────╲─────────╱────╲──▶
       ◄──── 33,024 samples ────►    3.61 ms apart
```

That is the **van de Beek** method from
[Fundamentals 11 §6](../../01_fundamentals/11_ofdm_and_broadcast_systems.md#part-6--how-an-ofdm-receiver-locks-on),
built from simple blocks. It finds symbol timing with **no pilots, no preamble and no knowledge of
the data** — only because the guard interval is a copy.

The **amplitude histogram** shows the long tail of peaks: OFDM's PAPR, made visible.

> 💡 **If you change the transmit mode**, change `fft_len` and `cp_len` in the analyser to match
> (for the old 1K test mode: 1024 and `fft_len // 8`). An earlier version was left at the 1K
> settings after the lab moved to 32K; on a 32K signal it showed no symbol peaks at all.

### Step 4 — Transmit (cage or cable only!)

Set up first:

```
  ┌──────────────┐                                  ┌──────────────┐
  │ Laptop       │   TX/RX ──[ 30 dB ]──[ 30 dB ]── │ TV or USB    │
  │ SignalSDR    │            attenuators           │ TV tuner     │
  │ lab10_tx     │                                  └──────────────┘
  └──────────────┘         (or: everything inside a Faraday cage)
```

Then:

1. **Look at the `TX/RX` port.** Really look. No antenna.
2. Choose `center_freq`: a UHF TV channel **not used where you are**. Channel 21 is 474 MHz;
   channel *n* is 474 + 8 × (*n* − 21) MHz. Check which channels MYTV uses in your area, and
   avoid them — even on a cable.
3. Start playout and the transmitter (Step 0).
4. Raise `tx_gain` to about 20 dB.
5. Raise `tx_amplitude` **slowly**, from 0 towards 0.25. Watch the time plot: if the peaks flatten
   at ±1, you are **clipping**, and the signal will splash into neighbouring channels.
6. On the TV, do a **manual channel scan** on that frequency.

✅ **Success:** the TV shows signal strength and quality, and finds one channel named
**SDR LAB TV**. Many TVs have a hidden signal page showing MER and error counts — that is where the
interesting numbers are.

### Step 5 — Receive with a second radio (optional)

In `lab10_dvbt2_analyze.grc`, **enable** `usrp_source` and **disable** `file_source` and
`throttle`. Now you are measuring the real transmitted signal. The symbol peaks still appear, now
with real noise and echoes. **Compare how sharp the peaks are** with the file version: echoes
widen them. You are seeing the channel's delay spread directly.

---

## 🔬 Verification

### The signal is correct

A freshly generated waveform (`lab10_dvbt2_generate.py`, 3 s from a test stream at
40,000,738 bit/s) passed all five checks in `analyze_dvbt2.py`: bandwidth **7.692 MHz** (expected
7.768), cyclic prefix **19.1×**, symbol period **33,024** samples (exact), P1 at **23.9×**, T2 frame
**1,983,025** samples against **1,983,488** (0.023 %). PAPR **9.6 dB**.

`lab10_dvbt2_analyze.py` was then run on the same file without a screen. Its correlator found
**1,105 symbol peaks spaced exactly 33,024 samples apart**, 17.6× above the median level.

The stream made from `Bintang.mp4` (1920×1080 H.264 + AAC, 209 s), re-encoded to H.264 High@4.0
at 12 Mbit/s with MP2 audio and filled to 40 Mbit/s:

```
/tmp/bintang_dvbt2.ts
  1,045,172,276 bytes = 5,559,427 packets of 188
  sync byte 0x47 present on 5,559,427/5,559,427 (100.000 %)
  PID 8191 null 74.58 % | PID 256 video 24.83 % | PID 257 audio 0.50 %
  PAT 0.04 % | PMT 4096 0.04 % | SDT 17 0.01 %
  PCR-derived mux rate: 40.000737 Mbit/s
  expected            : 40.000738 Mbit/s  (-0.0000 % error)
```

The rate was also checked against the running transmitter: 86,779,200 bytes in gave **exactly
80.0000 T2 frames** of 1,983,488 samples — 1,084,740 bytes per frame, 40.000738 Mbit/s. The
modulated video stream passed all five checks too (7.693 MHz, 19.9×, 33,022 / 33,024 samples,
P1 23.9×, 1,983,028 / 1,983,488 samples).

### Real time, and on the radio

- **Continuous playout:** 83.9 s spanning **4.2 laps** of a short clip — **0 backward clock
  jumps**, the clock rising from 0.700 s to 84.580 s, one PCR every 20.00 ms.
- **Driving the transmitter from the FIFO for 80 s** (four wraps): **4 underflows, all in the
  first 1.6 s** while the buffers filled, none after.
- **On the radio, with `tx_amplitude = 0`** (nothing radiated): 6 underflows, all in the first
  1.6 s; none in the following 70 s. The chain runs at 7.8× real time on average, but produces a
  whole T2 frame at once every 216.9 ms, so it needs a reservoir: the `tx_scale` block holds
  4,194,304 samples (about two frames), and the USRP Sink has 1024 send frames. Without those, it
  stutters even with 7.8× headroom.
- The radio's transmit chain supports the required rate (**0.019 ppm** error) and the 9.14 MHz
  analog bandwidth.

### A real television

**A real TV found the service and played the video** at high quality. That test was done by the
lab's owner, on their own low-power setup; it was reported, not recorded by a tool.

### Not yet tested

- **The smooth-playback fix has not been watched on a TV.** It is proven by measurement (above),
  but nobody has yet watched a loop point on a real set.
- **The TV result was not recorded** — no screenshot or signal-quality numbers were saved.
- **256QAM needs a clean signal** — about 20 dB C/N (QPSK needs about 5). Easy over a cable; harder
  over the air with improvised antennas. If a TV sees the channel but cannot lock, try the
  `germany-g7` preset (64QAM, 31.7 Mbit/s) before suspecting anything else.
- **The twelve stages are not individually checked.** Only a receiver could prove the LDPC and BCH
  encoders are *correct*; the TV test is that proof, end to end.

If you do Step 4, **please record what your TV shows** — signal strength, quality, MER.

---

## ⚙️ Changing the mode

DVB-T2 settings are **enums** in GRC (fixed lists), so no single variable controls them. To change
mode, you must change several blocks **so they all agree**. If they disagree, you get a signal no
receiver can decode — usually **with no error message**.

### Which blocks share which setting

| Setting | Blocks that must agree |
|---|---|
| `fftsize` | framemapper, freqinterleaver, pilotgenerator, p1insertion **+ the `fft_len` variable** (and the analyser's) |
| `guardinterval` | framemapper, freqinterleaver, pilotgenerator, p1insertion **+ `cp_len`** (and the analyser's) |
| `pilotpattern` | framemapper, freqinterleaver, pilotgenerator |
| `constellation` | bitinterleaver, modulator, cellinterleaver, framemapper |
| `rate` | bbheader, bbscrambler, bch, ldpc, bitinterleaver, framemapper |
| `numdatasyms` | framemapper, freqinterleaver, pilotgenerator, p1insertion **+ the variable** |
| `carriermode` | framemapper, freqinterleaver, pilotgenerator, p1insertion |
| `l1constellation` | framemapper (on its own — but it must suit the mode) |
| `fecblocks` | cellinterleaver, framemapper **+ the variable** |

### Presets that are known to be legal

From the official `gr-dtv` examples in `/usr/share/gnuradio/examples/dtv/`. **Do not invent
combinations.** The standard only allows some pilot patterns with some FFT/guard pairs, and
`gr-dtv` **does not check**: it will accept 32K + GI 1/4 + PP1 and give you a signal no receiver on
Earth can decode, without any error.

| Preset | FFT | Constellation | Rate | GI | PP | Carriers | Data symbols | FEC blocks | Mbit/s | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| **vv003 (this lab)** | 32K T2GI | 256QAM | 2/3 | 1/128 | PP7 | extended | 59 | 202 | **40.00** | **what Freeview HD and MYTV use** |
| vv016 | 32K T2GI | 256QAM | 3/4 | 1/128 | PP7 | extended | 59 | 200 | 44.6 | same, less protection |
| vv001 / vv019 | 32K T2GI | 256QAM | 3/5 | 1/128 | PP7 | extended | 59 | 202 | 36.0 | vv019 without rotation |
| germany-g6 | 32K | 256QAM | 3/5 | 1/32 | PP4 | normal | 55 | 179 | 33.0 | a real German broadcast |
| germany-g7 | 32K | 64QAM | 2/3 | 1/16 | PP2 | extended | 63 | 150 | 31.7 | a real German broadcast |
| vv036 | 32K | 256QAM | 3/5 | 1/8 | PP2 | normal | 53 | 162 | 30.2 | UK test profile |
| vv008 | 16K | 256QAM | 4/5 | 1/32 | PP6 | extended | 100 | 168 | 37.5 | |
| germany-g1 | 16K | 64QAM | 1/2 | 19/128 | PP2 | extended | 118 | 139 | 21.5 | a real German broadcast |
| vv015 | 8K | 256QAM | 3/5 | 1/32 | PP7 | extended | 238 | 200 | 36.0 | |
| vv011 (old lab default) | 1K | QPSK | 1/2 | 1/8 | PP3 | normal | 1966 | 48 | 6.17 | lightest on CPU; **no broadcaster uses it** |

**Ten** settings move together — including `carriermode` and `l1constellation`, which are easy to
miss (vv003 sends its signalling in 64QAM; the old 1K mode used BPSK). Open the matching `.grc`
from `/usr/share/gnuradio/examples/dtv/` next to yours and copy the values.

---

## 🔧 Troubleshooting

| Problem | Cause and fix |
|---|---|
| **"Underruns", and sound out of sync with the picture** | The same fault: live encoding cannot keep up with the transmitter. Encode once, then use `--copy` ([Don't encode live](#dont-encode-live)). If it still happens with `--copy`, the disk is too slow: raise `--buffer-seconds` |
| **The flowgraph starts, but no window ever appears** | **Playout is not running.** `ts_file` is a FIFO, and opening a FIFO waits until something writes to it — before any window is created. Start `tv_playout.py` first, or use its `--launch` option |
| `AttributeError: module 'posixpath' has no attribute 'isfifo'` | Fixed in `tv_playout.py`. Update to the current version |
| `RuntimeError: LookupError: KeyError: No devices found` | Another program still has the radio. Find it with `ps -eo pid,cmd \| grep [l]ab10` and stop it by PID |
| **The TV finds nothing** | In order: (1) run `analyze_dvbt2.py` — if all five pass, the signal is fine; (2) `tx_amplitude` or `tx_gain` is still 0; (3) the signal is too **strong** — a TV on a cable overloads easily, add 20 dB more attenuation; (4) wrong channel on the TV, or the TV is set to DVB-T only |
| The TV locks, but the picture is black | Expected with `make_test_ts.py` — it has no video. Use `make_video_ts.py` |
| Poor quality, keeps losing lock | Usually **clipping**. With ~10 dB of peaks, an average of 0.25 already reaches about 1.0 at the peaks. Lower `tx_amplitude`; flat-topped peaks on the time plot mean clipping |
| "Shared memory" error at start-up | Some blocks buffer whole T2 frames. `sudo sysctl -w kernel.shmmax=1073741824` (lasts until restart) |
| Runs slower than real time | Close the display blocks. Use `sc16` instead of `fc32` on the USRP Sink to halve the USB load. For quick experiments, the 1K preset (vv011) uses far less CPU — but a TV will probably not find it |
| `U` in the terminal while transmitting | Transmit **underflow**: the computer is not feeding the radio fast enough, so there are gaps on air, and the TV loses lock. Same fixes as above |
| `analyze_dvbt2.py`: P1 detection FAILED | If checks 1–3 pass but 4 fails, the `--fft`/`--gi`/`--datasyms` options do not match how the signal was made. (The P1 search uses a lag of **542** samples; 1024 is the tempting mistake) |

---

## ✅ Summary

- DVB-T2 is **twelve stages**, each fighting a specific problem: LDPC + BCH for errors, three
  interleavers for bursts and fades, OFDM + cyclic prefix for echoes, P1 for finding frames.
- Lab 10 uses **32K / 256QAM / 2/3 / GI 1/128 / PP7** — what real broadcasters use — at exactly
  **40.000738 Mbit/s**.
- The transport stream's **rate** and **clock** must be exact. Loop the input, not the output.
- Keep `tx_amplitude` around **0.25**: OFDM's peaks need room.
- **Transmit only into a cable or a Faraday cage.** The flowgraph starts at zero power on purpose.

## 🧠 Check yourself

1. Why is the sample rate 64/7 MHz, and not a round number?
   <details><summary>Answer</summary>The standard fixes it: it sets the carrier spacing exactly
   (279 Hz for 32K), so 27,841 carriers fit in 7.77 MHz. Every DVB-T2 receiver is built around
   it.</details>
2. Why three interleavers instead of one?
   <details><summary>Answer</summary>Each fights a different problem. <b>Bit</b> interleaving
   spreads a code block over bits of different reliability. <b>Time</b> interleaving spreads it
   over hundreds of milliseconds, so a burst of interference (a car ignition) cannot destroy it.
   <b>Frequency</b> interleaving spreads it over carriers, so a fade at one frequency cannot
   either.</details>
3. What does `tx_amplitude = 0.25` protect against?
   <details><summary>Answer</summary>Clipping of OFDM's peaks (PAPR 9.6 dB). Clipped peaks
   splash into neighbouring channels.</details>
4. Your TV played the video in high quality but it was never smooth. What was wrong?
   <details><summary>Answer</summary>Looping the finished <code>.ts</code> file made the stream's
   clock (PCR) jump backwards at each loop. Loop the input video with <code>tv_playout.py</code>
   instead.</details>
5. Why is rotating the constellation useful?
   <details><summary>Answer</summary>Rotation makes I and Q each carry information about the
   whole point. If a fade destroys one of them, the other can still recover the point — free
   protection.</details>

---

## 🚀 Going further

- **A full software round trip:** the DVB-T (first generation) transmitter **and** receiver in
  `/usr/share/gnuradio/examples/dtv/dvbt_tx_8k.grc` and `dvbt_rx_8k.grc`.
  [Lab 11](../lab11_tv_receiver/README.md) builds a full receiver from them.
- **Measure your own transmitter** with the second radio: power leaking into the next channel
  versus `tx_amplitude` — see [Test & Measurement](../../04_applications/14_test_measurement_and_infrastructure.md).
- **Damage the signal on purpose** with a Channel Model block (noise, echoes, Doppler) and find
  where the TV loses lock — the DVB-T2 version of Lab 07's BER cliff.
- **Compare 1K and 32K** with the same programme: how long an echo can each survive?

---

## 📖 References

1. ETSI EN 302 755 — the DVB-T2 standard
2. ETSI TS 102 831 — DVB-T2 implementation guidelines
3. The `gr-dtv` examples in `/usr/share/gnuradio/examples/dtv/` — where this lab's settings come from
4. van de Beek, Sandell & Börjesson, "ML Estimation of Time and Frequency Offset in OFDM Systems",
   IEEE Trans. Signal Processing, 1997 — the method you build in Step 3
5. ISO/IEC 13818-1 — MPEG-2 Systems (the transport stream)
