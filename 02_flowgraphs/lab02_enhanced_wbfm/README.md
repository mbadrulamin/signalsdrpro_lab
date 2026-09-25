# 🟡 Lab 02 — FM Radio with a Spectrum Display

> **What you will build:** the Lab 01 radio, plus three live displays: a **spectrum**, a
> **waterfall** and an **IQ time plot**. The audio is also changed to the standard 48 kHz.
> **What you will learn:** how to *see* radio signals, and how to change a sample rate with a
> **Rational Resampler**.
> **Before this:** [Lab 01](../lab01_simple_wbfm/README.md).
> **Time:** about 45 minutes. **Difficulty:** beginner. **Needs the radio:** yes.

---

## 🎯 Goal

In Lab 01 you could only *hear* the radio. Now you will also *see* what it receives. By the
end you will be able to:

1. find stations by looking at the screen instead of guessing,
2. read a spectrum, a waterfall and an IQ plot, and
3. change a sample rate by a fraction, like 24/125.

---

## 1. Run it first

```bash
cd "02_flowgraphs/lab02_enhanced_wbfm"
gnuradio-companion lab02_enhanced_wbfm.grc
```

Press **F5**. A window opens with two sliders (**FM Station** and **RF Gain**) and three
displays. Look at the **Spectrum** display: each hump is a station. Drag the **FM Station**
slider until a big hump sits in the middle. You should hear it.

---

## 2. The flowgraph

The USRP Source now feeds **four** blocks at once. Three are displays. One is the radio path.

```
                           ┌────────────────────┐
                      ┌───▶│ QT GUI Freq Sink    │  "Spectrum"
                      │    └────────────────────┘
                      │    ┌────────────────────┐
┌──────────────┐      ├───▶│ QT GUI Waterfall    │  "Waterfall"
│ USRP Source  │──────┤    └────────────────────┘
│  2 MSPS      │      │    ┌────────────────────┐
└──────────────┘      ├───▶│ QT GUI Time Sink    │  "IQ Time Domain"
                      │    └────────────────────┘
                      │    ┌──────────────┐    ┌──────────────┐    ┌────────────┐
                      └───▶│  Rational    │───▶│ WBFM Receive │───▶│ Audio Sink │
                           │  Resampler   │    │   ÷ 8        │    │  48 kHz    │
                           │ ×24 ÷125     │    └──────────────┘    └────────────┘
                           └──────────────┘
         2,000,000  ──────────▶  384,000  ─────────────▶  48,000 samples per second
```

> 💡 **One output can feed many blocks.** Each block gets its own copy of the same samples.
> The displays do not change the signal going to the radio path.

### What changed from Lab 01

| | Lab 01 | Lab 02 |
|---|---|---|
| Sample rate | 1 MSPS | **2 MSPS** — see more of the band at once |
| Displays | none | spectrum, waterfall, IQ time plot |
| Audio rate | 50 kHz | **48 kHz** — the standard rate every sound card supports |
| New block | — | **Rational Resampler** to get from 2 MSPS to 384 kSPS |

---

## 3. The new blocks

### 3.1 QT GUI Frequency Sink — the spectrum

Shows **how strong each frequency is**, updated 10 times a second. Frequency is along the
bottom, strength (in dB) up the side. This is the frequency view from
[Fundamentals 01](../../01_fundamentals/01_signals_basics.md#3-two-ways-to-look-at-a-signal).

| Setting | Value | Meaning |
|---|---|---|
| Type | Complex | It takes IQ samples |
| FFT Size | 2048 | The screen width is split into 2048 frequency slots ("bins") |
| Center Frequency | `freq` | So the axis shows real frequencies (e.g. 100.0 MHz), not offsets |
| Bandwidth | `samp_rate` | The display is 2 MHz wide |
| Update Period | 0.10 s | 10 updates per second |
| Y axis | −140 to +10 dB | The strength range shown |

**What you see:**

- **Humps** about 200 kHz wide — FM stations.
- A flat, grassy line — the **noise floor**.
- A thin **spike in the centre** — the radio's own leak (the "DC spike"), not a station.

> 💡 **Resolution:** 2 MHz ÷ 2048 bins ≈ **1 kHz per bin**. A bigger FFT size shows finer
> detail but updates more slowly and uses more CPU.

### 3.2 QT GUI Waterfall Sink — the spectrum over time

The waterfall is a spectrum that **scrolls**. Each new spectrum is drawn as one coloured line
at the top. Older lines move down. Colour shows strength: bright = strong, dark = weak.

```
  frequency →
  ┃   ▓▓   ░   ██  ┃  ← now
  ┃   ▓▓   ░   ██  ┃
  ┃   ▓▓       ██  ┃     a station that is always on = a straight vertical stripe
  ┃   ▓▓   ░   ██  ┃     a signal that comes and goes = a broken stripe
  ┃   ▓▓   ░   ██  ┃  ← a few seconds ago
```

The waterfall is the best tool for finding signals that **come and go**, like walkie-talkie
calls or data bursts. On a normal spectrum they flash too quickly to notice.

> ⚠️ The waterfall uses the most CPU of any block here. If the audio breaks up, disable it
> (right-click → Disable).

### 3.3 QT GUI Time Sink — the IQ waveform

Shows the **raw IQ samples over time** (the time view). For complex input it draws two lines:
**I** and **Q**.

Use it to check the **signal level**:

- Both lines should stay well inside **−1 to +1**. If they touch ±1, the radio is
  **clipping** — lower the gain.
- If the lines are tiny and fuzzy, the signal is weak or the gain is too low.

### 3.4 Rational Resampler — changing the sample rate by a fraction

**The problem.** We want **48 kHz** audio, because every sound card supports it. The
WBFM Receive block can only divide by a whole number. If we want to divide by 8, its input
must be 48,000 × 8 = **384,000** samples per second. But the radio gives us **2,000,000**.

2,000,000 ÷ 384,000 = 5.208… — not a whole number. So we need to change the rate by a
**fraction**.

**The fraction.**

$$
\frac{384{,}000}{2{,}000{,}000} = \frac{384}{2000} = \frac{24}{125}
$$

So we **multiply by 24** (called **interpolation**) and **divide by 125** (called
**decimation**). A **Rational Resampler** does both in one block. ("Rational" means "a
fraction of two whole numbers".)

$$
2{,}000{,}000 \times \frac{24}{125} = 384{,}000
$$

| Setting | Value | Meaning |
|---|---|---|
| Type | `ccc` | Complex in, complex out, complex filter (IQ stays IQ) |
| Interpolation | `24` | Multiply the rate by 24 |
| Decimation | `125` | Divide the rate by 125 |
| Taps | `[]` (empty) | Let GNU Radio design the filter automatically |
| Fractional BW | `0` | Let GNU Radio choose the filter width |

**How it works inside** (you don't need this to use it):

1. **Up:** put 23 zeros between every pair of input samples (×24 rate).
2. **Filter:** a low-pass filter smooths the zeros into proper in-between values, and removes
   anything that would cause aliasing.
3. **Down:** keep 1 sample in every 125 (÷125 rate).

The real block is cleverer than this: it never actually calculates the samples it will throw
away. This trick is called a **polyphase** filter, and it makes the resampler fast.

> 💡 **Always reduce the fraction.** 384/2000 and 24/125 give the same result, but the smaller
> numbers need a much smaller internal filter, so they use less CPU.

---

## 4. What to look for

### On the spectrum

When tuned to a station:

- A hump about **180–200 kHz** wide in the centre.
- Other stations as humps **200 kHz, 400 kHz…** away (FM stations are 200 kHz apart).
- The noise floor, often around **−90 to −110 dB**.

**Change the gain** and watch: all signals rise and fall together — and so does the noise
floor. More gain does not separate the signal from the noise; it lifts both.

### On the waterfall

- **Vertical stripes** = stations that are always on.
- **Stripes that get brighter and darker** = fading. The signal reaches you by several paths
  (bouncing off buildings) that add and cancel. This is called **multipath**.
- **Short blobs** = signals that come and go.

### On the IQ time plot

- Two lines (I and Q), wiggling quickly.
- On a strong FM station the **size** of the wiggle stays nearly constant. That is FM: the size
  of the IQ arrow does not change, only its speed of turning
  ([Fundamentals 04](../../01_fundamentals/04_fm_theory.md)).

---

## 5. Experiments

1. **Count the stations.** How many humps can you see across the 2 MHz?
2. **Sweep the band.** Drag **FM Station** slowly from 87.5 to 108 MHz and watch the
   waterfall draw the band.
3. **Gain to 0.** Watch the stations sink into the noise floor.
4. **Gain to 70.** Watch the IQ time plot. Do the lines touch ±1? Does the spectrum show new,
   false humps? Those false signals are **intermodulation** — too much gain.
5. **Check the width.** Zoom into one station (use the mouse wheel on the spectrum). Is it about
   200 kHz wide?

---

## 6. All settings at a glance

| Block | Setting | Value |
|---|---|---|
| Variable `samp_rate` | | 2,000,000 |
| Variable `quad_rate` | | 384,000 |
| Variable `audio_rate` | | 48,000 |
| Slider `freq` | range | 87.5–108 MHz, steps of 100 kHz, starts at 100 MHz |
| Slider `gain` | range | 0–76 dB, starts at 40 |
| USRP Source | Sample Rate / Bandwidth (`bw0`) | `samp_rate` / `samp_rate` |
| USRP Source | Center Freq / Gain / Antenna | `freq` / `gain` / `TX/RX` |
| Rational Resampler | Interpolation / Decimation | 24 / 125 |
| WBFM Receive | Quadrature Rate / Audio Decimation | `quad_rate` (384,000) / 8 |
| Audio Sink | Sample Rate | `audio_rate` (48,000) |

---

## 🔧 Troubleshooting

| Problem | Try this |
|---|---|
| Choppy audio, `O` in the terminal | The computer is too slow. Disable the waterfall, or lower the FFT size |
| Displays freeze or update slowly | Same: disable the waterfall first |
| No humps anywhere | Check the antenna. Raise the gain to 50 |
| Humps visible, but only hiss | The station is not in the centre. Drag the slider until the hump is centred |
| New humps appear when you raise the gain | Too much gain (intermodulation). Lower it |

---

## ✅ Summary

- **Spectrum** = strength vs frequency. **Waterfall** = spectrum over time. **Time plot** =
  I and Q over time.
- One block output can feed several blocks.
- A **Rational Resampler** changes the rate by a fraction: interpolate (×) then decimate (÷).
- Reduce the fraction (24/125, not 384/2000) to save CPU.
- More gain lifts the signal *and* the noise.

## 🧠 Check yourself

1. Why does the waterfall scroll?
   <details><summary>Answer</summary>Each new spectrum is drawn at the top, and older ones
   move down. Up and down is time.</details>
2. What is the thin spike exactly in the centre of the spectrum?
   <details><summary>Answer</summary>The radio's own tuning signal (LO) leaking into its
   input — the DC spike. It is not a station.</details>
3. What would happen if you removed the resampler and fed 2 MSPS straight into WBFM Receive
   (with its Quadrature Rate set to 2,000,000 and decimation 8)?
   <details><summary>Answer</summary>The audio would come out at 2,000,000 ÷ 8 = 250,000
   samples per second, but the Audio Sink expects 48,000. The rates would not match (see Lab 01,
   question 2).</details>
4. Why is the resampler type `ccc`?
   <details><summary>Answer</summary>The signal is still IQ (complex) before it is
   demodulated, so the input and output must be complex.</details>
5. The FFT size is 2048 and the bandwidth is 2 MHz. How wide is each frequency bin?
   <details><summary>Answer</summary>2,000,000 ÷ 2048 ≈ 977 Hz, about 1 kHz.</details>

**Next:** [Lab 03 — An FM Radio That Sounds Good →](../lab03_advanced_wbfm/README.md)
