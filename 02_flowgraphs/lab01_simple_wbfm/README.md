# 🟢 Lab 01 — The Simplest FM Receiver

> **What you will build:** a working FM radio from just **three blocks**.
> **What you will learn:** what a flowgraph is, what variables and sliders do, and what each
> block does to the signal.
> **Before this:** [Fundamentals 01–04](../../01_fundamentals/01_signals_basics.md), and a
> working setup ([Setup 04](../../00_setup/04_verify_setup.md)).
> **Time:** about 30 minutes. **Difficulty:** beginner. **Needs the radio:** yes.

---

## 🎯 Goal

By the end of this lab you will:

1. hear a real FM station through your computer's speakers, and
2. understand what each of the three blocks does.

---

## 1. Run it first

Understanding is easier once you have heard it working. Open a terminal:

```bash
cd "02_flowgraphs/lab01_simple_wbfm"
gnuradio-companion lab01_simple_wbfm.grc
```

GNU Radio Companion (GRC) opens and shows the flowgraph. Press **F5** (or click the ▶ button)
to run it.

> 💡 You can also run it without GRC: `python3 lab01_simple_wbfm.py`. It is the same program.

A small window opens with two sliders:

- **FM Station (Hz)** — which station to listen to. Starts at 100 MHz.
- **RF Gain (dB)** — how much the radio amplifies the signal. Starts at 40.

**Drag the station slider** to a frequency where you know there is a station. In the
Kuala Lumpur area, **89.9 MHz** (BFM) is a good test. Turn up your computer's volume.

🎧 **You should hear music or speech.** If you hear only hiss, see
[Troubleshooting](#-troubleshooting) below.

---

## 2. The flowgraph

A **flowgraph** is a diagram of blocks connected by arrows. Samples flow along the arrows from
left to right. Each block does one job.

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ USRP Source  │───────▶│ WBFM Receive │───────▶│  Audio Sink  │
│ (the radio)  │   IQ   │ (FM decoder) │ audio  │  (speakers)  │
└──────────────┘        └──────────────┘        └──────────────┘
  1,000,000                                        50,000
  IQ samples/s                                     audio samples/s
```

That's it: **three working blocks**. There are also three **variable** blocks that hold
settings, and the **Options** block that every flowgraph has.

---

## 3. The blocks, one by one

### 3.1 Variables — named settings

A **variable** is a named number that other blocks can use. Instead of typing `1000000` into
three different blocks, you type it once and call it `samp_rate`.

| Variable | Value | What it means | Type |
|---|---|---|---|
| `samp_rate` | `1000000` | Sample rate: 1 million IQ samples per second (1 MSPS) | plain variable |
| `freq` | `100.0e6` | The station frequency: 100 MHz. (`100.0e6` means 100.0 × 10⁶) | **slider** (QT GUI Range) |
| `gain` | `40` | Receiver gain in dB | **slider** (QT GUI Range) |

**Why use variables?**

- Change it once, and every block that uses it updates.
- A **QT GUI Range** variable appears as a **slider** when the flowgraph runs. You can change
  it while listening.
- You can see all the important settings at a glance.

### 3.2 USRP Source — the radio

This block controls the SignalSDR Pro (in USRP B210 mode) and delivers its IQ samples.

| Setting | Value | Why |
|---|---|---|
| Output Type | Complex float32 | IQ samples are complex numbers ([Fundamentals 02](../../01_fundamentals/02_iq_sampling.md)) |
| Device Address | `""` (empty) | Use the first radio UHD finds |
| Num Channels | 1 | Mono FM needs only one receiver |
| Sample Rate | `samp_rate` | From the variable: 1 MSPS |
| Ch0 Center Freq | `freq` | From the slider: where to tune |
| Ch0 Gain | `gain` | From the slider |
| Ch0 Antenna | `TX/RX` | The antenna connector to use |
| **Ch0 Bandwidth** (`bw0`) | **`samp_rate`** | **Sets the hardware filter to 1 MHz. Very important — see below** |

**What it does when the flowgraph starts:**

1. UHD finds the radio and loads its FPGA image (this takes a few seconds).
2. It tunes the radio's LO to `freq` ([Fundamentals 03](../../01_fundamentals/03_rf_basics.md)).
3. It sets the amplifiers to `gain` dB.
4. It sets the hardware filter to `bw0`.
5. It streams IQ samples over USB: 1,000,000 per second.

**Data rate:** each complex sample is 8 bytes, so 1 MSPS × 8 bytes = **8 MB per second**.

> ⚠️ **Why `bw0` matters so much.** If the bandwidth is left empty, the radio's filter opens to
> **56 MHz**. Then a lot of unwanted energy — mostly the spike in the centre of the spectrum —
> gets in. On a real SignalSDR Pro at 89.9 MHz, that spike was **84 %** of everything received.
> Setting `bw0` to the sample rate cut it to **16 %**, and the audio SNR (how clean it sounds)
> went from **34.6 dB** to **53.2 dB**. That is a big, clearly audible improvement.
> See [VERIFICATION.md, Lesson 1](../../VERIFICATION.md#lesson-1--one-missing-setting-cost-up-to-43-db).

### 3.3 WBFM Receive — the FM decoder

This block turns IQ samples into audio. It is a **hierarchical block**: several blocks packed
into one, for convenience.

| Setting | Value | Why |
|---|---|---|
| Quadrature Rate | `samp_rate` | The sample rate coming in: 1 MSPS |
| Audio Decimation | `20` | Keep 1 of every 20 samples: 1,000,000 ÷ 20 = **50,000** audio samples/s |

**Inside it, three steps happen:**

```
 IQ in (1,000,000 samples/s)
    │
    ▼  1. Quadrature Demod — measures how fast the IQ arrow turns → that is the audio
    │
    ▼  2. Low-pass filter + decimate by 20 — removes everything above ~15 kHz,
    │     then keeps 1 sample in 20
    ▼  3. De-emphasis — turns the treble back down (75 µs)
    │
 audio out (50,000 samples/s)
```

**Decimation** means "keep only some of the samples". Audio does not need 1 million samples
per second — 50,000 is plenty. But you must **filter first**: if you throw away samples
without filtering, high-frequency signals fold back into the audio as false sounds (this is
**aliasing**, from [Fundamentals 01](../../01_fundamentals/01_signals_basics.md#52-what-goes-wrong-if-you-sample-too-slowly-aliasing)).

> 💡 **Malaysia note:** this block always uses 75 µs de-emphasis (the US standard). Malaysian
> stations use 50 µs. The result is slightly dull treble. It is a small effect. Lab 04 builds
> de-emphasis by hand with the correct value.

| | Data type |
|---|---|
| Input | complex (blue port) |
| Output | float (orange port) |

### 3.4 Audio Sink — the speakers

Sends the audio to your computer's sound card.

| Setting | Value | Why |
|---|---|---|
| Sample Rate | `50000` | **Must equal** the WBFM Receive output: 1,000,000 ÷ 20 = 50,000 |
| Device Name | `""` (empty) | Use the computer's default sound output |
| OK to Block | Yes | Let the sound card set the pace |

> ⚠️ If the Audio Sink's sample rate does not match the audio coming in, the sound plays at the
> wrong speed and pitch, and you get warnings about the audio buffer. See Question 2 below.

---

## 4. Follow one sample through the radio

1. **At the antenna.** Radio waves from many FM stations create a tiny voltage — a few
   microvolts. All stations are there at once, at different frequencies.
2. **Inside the AD9361 chip.** The signal is amplified. It is mixed with the LO at `freq`
   (say 100 MHz). A station at 100.1 MHz moves to +100 kHz; one at 99.9 MHz moves to −100 kHz.
   The filter (`bw0`) removes everything outside ±500 kHz. The ADCs measure I and Q.
3. **Out of the USRP Source.** 1,000,000 IQ samples per second. They contain every station
   within ±500 kHz of `freq`. The wanted station is at the centre.
4. **Inside WBFM Receive.** The demodulator measures how much the IQ angle changes from each
   sample to the next — that change is the audio. Then filter, decimate and de-emphasis.
5. **Out of WBFM Receive.** 50,000 audio samples per second, as numbers roughly between −1
   and +1.
6. **Inside the Audio Sink.** The sound system (PulseAudio or PipeWire) buffers a few
   milliseconds of audio and plays it.
7. **At the speaker.** You hear the station.

---

## 5. Things to try

### Change the station

- Drag **FM Station** across 87.5–108 MHz.
- On a station: music or speech.
- Between stations: hiss. That hiss is noise — from the world around you and from the radio's
  own electronics.

### Change the gain

| Gain | What you hear |
|---|---|
| 0–10 dB | Weak stations disappear. Only strong ones are heard, faintly |
| **30–50 dB** | **Usually the best range.** Clear sound |
| 60–76 dB | Strong stations become distorted. Noise and false signals rise |

### Look at the signal (optional)

Add a **QT GUI Frequency Sink** block and connect it to the USRP Source output. Set its centre
frequency to `freq` and bandwidth to `samp_rate`. Run again. You will see:

- a flat, grassy **noise floor**, often around −80 to −100 dB,
- **humps** where there are stations,
- a **spike at the centre** — the radio's own leak, not a station.

Lab 02 does this properly.

---

## 6. The one thing this radio cannot do: volume control

None of the three blocks is a volume control. The WBFM Receive block does not adjust the level
automatically either. Its output level simply follows how strongly the station modulates.

On a real SignalSDR Pro, with a strong local station and `gain = 55`, the audio peaked at
**1.86**. The Audio Sink can only play values between **−1.0 and +1.0**. Anything bigger is
cut off (**clipped**), so the sound is loud and distorted.

The only other control you have is the **gain** slider. That is the wrong tool: gain changes
the signal *before* decoding, and it affects noise. It is not a volume knob.

This is not a bug. It is the price of using only three blocks. **Lab 03** adds a real volume
control (starting at 0.5), and the problem goes away. As you do Labs 02 and 03, notice that
every new block is there to fix a problem like this one.

> 💡 Turning the gain down does **not** make FM quieter. An FM decoder ignores how strong the
> signal is; loudness comes only from how far the transmitter swings its frequency. Lower gain
> only makes it noisier. That is why you need a separate volume control.

---

## 🔧 Troubleshooting

| Problem | Try this |
|---|---|
| Only hiss, everywhere | Move the station slider — you are between stations. Check the antenna is screwed on |
| No stations at all, even strong ones | Raise gain to 50. Check the antenna. Hold it near a window |
| Distorted sound on strong stations only | Lower your computer's volume; Lab 03 fixes this properly (see Section 6) |
| Distorted sound on every station, plus false stations on the spectrum | The radio is overloaded. Lower the gain to about 30 |
| Choppy sound, `O` printed in the terminal | The computer is not keeping up. Close other programs. Use a USB 3.0 port on the computer itself, not a hub |
| `aU` or `aO` printed in the terminal | The audio buffer ran empty or overfilled. Usually harmless if rare. Check the Audio Sink rate is 50000 |
| `No devices found` | See [Setup 05 — Troubleshooting](../../00_setup/05_troubleshooting.md) |

> 💡 **Finding station frequencies.** Look at the spectrum (see Section 5), or look up your
> local stations in the [Malaysia reference](../../05_reference/04_malaysia.md).

---

## ✅ Summary

- A working FM radio needs only **three blocks**: USRP Source → WBFM Receive → Audio Sink.
- **Variables** hold settings. **QT GUI Range** variables become **sliders**.
- Always set the USRP Source's **bandwidth** (`bw0`) to the sample rate.
- Sample rates must match along the chain: 1,000,000 ÷ 20 = 50,000 into a 50,000 Audio Sink.
- **Gain is not volume.** This radio has no volume control — Lab 03 adds one.

## 🧠 Check yourself

1. Why is the audio rate 50 kHz and not the usual 48 kHz or 44.1 kHz?
   <details><summary>Answer</summary>Because 1,000,000 ÷ 20 = 50,000. The WBFM Receive block
   can only divide by a whole number, and 1,000,000 is not a whole-number multiple of 48,000.
   Sound cards handle 50 kHz fine.</details>
2. You change `samp_rate` to 2,000,000 but forget to change Audio Decimation (still 20).
   What happens?
   <details><summary>Answer</summary>WBFM Receive now produces 2,000,000 ÷ 20 = 100,000
   audio samples per second. But the Audio Sink plays only 50,000 per second. So each second
   of sound takes two seconds to play: it sounds <b>slow and an octave too low</b>. The radio
   keeps sending samples faster than they are used, so samples are thrown away — you will see
   <code>O</code> (overflow) in the terminal and the sound will be broken up. To fix it, set
   Audio Decimation to 40.</details>
3. What happens if you set the gain to 0 dB?
   <details><summary>Answer</summary>Only the very strongest stations can be heard, and
   faintly. The radio's own noise is bigger than most signals.</details>
4. What do you hear if you tune to 2.4 GHz (the Wi-Fi band)?
   <details><summary>Answer</summary>Only noise and buzzing. Wi-Fi is a digital signal, not
   FM. The FM decoder cannot turn it into sound.</details>
5. Why must the flowgraph filter the signal before it decimates?
   <details><summary>Answer</summary>To prevent aliasing. Without the filter, signals above
   the new, lower rate would fold back into the audio as false sounds that cannot be
   removed.</details>

**Next:** [Lab 02 — FM Radio with a Spectrum Display →](../lab02_enhanced_wbfm/README.md)
