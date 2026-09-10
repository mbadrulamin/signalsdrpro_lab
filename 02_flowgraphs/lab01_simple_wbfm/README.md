# 🟢 Lab 01 — The Simplest WBFM Receiver

> **Time:** 30 minutes  
> **Difficulty:** Beginner  
> **Blocks used:** 6  
> **Concepts:** Signal chain, sample rate, basic demodulation

---

## 🎯 Goal

Build the **minimum viable FM radio** using just three functional blocks. By the end, you'll be listening to real broadcast FM through your speakers and you'll understand exactly what each block is doing.

---

## 📐 Architecture

```
┌──────────────┐     ┌─────────────┐     ┌────────────┐
│ USRP Source  │────▶│ WBFM Receive│────▶│ Audio Sink │
│   (B210)     │     │             │     │            │
└──────────────┘     └─────────────┘     └────────────┘
```

That's it. **Three blocks.** Plus three "variable" blocks to hold tunable parameters.

---

## 📋 Blocks Explained

### 1. Variables (×3)

Variables are not "blocks" — they're named constants that other blocks reference.

| Variable | Value | Purpose |
|---|---|---|
| `samp_rate` | `1000000` (1 MSPS) | Sample rate for the USRP |
| `freq` | `100e6` (100 MHz) | Center RF frequency, controllable via GUI slider |
| `gain` | `40` | RF gain in dB, controllable via GUI slider |

**Why use variables instead of hard-coded numbers?**
- Changing one variable updates every block that references it.
- GUI sliders let you adjust values in real-time while the flowgraph runs.
- Your flowgraph is self-documenting — you see the parameters at a glance.

### 2. USRP Source (`uhd_usrp_source`)

This is the block that talks to the SignalSDR Pro (in B210 mode).

| Parameter | Value | Why |
|---|---|---|
| Output Type | Complex float32 | IQ samples are complex |
| Device Address | `""` (empty) | Auto-detect the first B210 |
| Num Channels | 1 | We only need 1 RX channel for mono FM |
| Sample Rate | `samp_rate` | From our variable |
| Clock Rate | 0 | Auto |
| Ch0 Center Freq | `freq` | From our variable |
| Ch0 Gain | `gain` | From our variable |
| Ch0 Antenna | `"TX/RX"` | The wideband antenna port |
| Ch0 Bandwidth | 0 | Auto (let UHD choose) |

**What this block does internally:**
1. Talks to UHD, which uploads FPGA/FW to the SignalSDR Pro
2. Tells the Zynq to tune the LO to `freq` Hz
3. Sets the LNA/VGA to `gain` dB
4. Starts streaming IQ samples over USB 3.0
5. Outputs complex samples at `samp_rate` Hz

**Data type:** `gr_complex` (32-bit float I + 32-bit float Q = 8 bytes per sample)

**Throughput:** 1 MSPS × 8 bytes = 8 MB/s over USB

### 3. WBFM Receive (`analog_wfm_rcv`)

This is a **composite block** that performs:
1. FM demodulation (using the quadrature demodulator from Fundamentals 04)
2. De-emphasis (75 μs, US standard)
3. Decimation to audio rate

| Parameter | Value | Why |
|---|---|---|
| Quadrature Rate | `samp_rate` (1 MSPS) | Input sample rate |
| Audio Decimation | `20` | Output rate = 1M/20 = 50 kHz |

**Internal processing chain:**
```
Complex in (1 MSPS)
    ↓ Quadrature Demod
Float (1 MSPS)
    ↓ Audio LPF + decimation by 20
Float (50 kHz)
```

The audio output is a mono signal suitable for playback.

**Data type in:** `gr_complex`  
**Data type out:** `float`

### 4. Audio Sink (`audio_sink`)

Plays audio through your PC's speakers.

| Parameter | Value | Why |
|---|---|---|
| Sample Rate | `50000` | Must match WBFM Receive's output |
| Num Inputs | 1 | Mono |
| Device Name | `""` (empty) | Default audio device |
| OK to Block | True | Wait if buffer empty |

---

## 🔄 Signal Flow — What's Happening at Each Step

Let's trace a single sample through the flowgraph:

1. **At the antenna:** Electromagnetic waves from FM stations induce tiny voltages (~μV). Multiple stations are present simultaneously at different frequencies.

2. **Inside the AD9361:**
   - The LNA amplifies all signals.
   - The LO is tuned to `freq` (say, 100 MHz).
   - The mixer downconverts: a station at 100.1 MHz becomes +100 kHz IF; one at 99.9 MHz becomes −100 kHz IF.
   - IQ mixers produce complex I/Q samples.
   - The ADC digitizes at 1 MSPS.

3. **After USRP Source:** A stream of 1,000,000 complex samples per second. Each sample has magnitude ~0.01 (well below full scale) and contains all stations within ±500 kHz of `freq`.

4. **Inside WBFM Receive:**
   - The Quadrature Demodulator computes `arg(s[n]·s*[n-1])` for each sample pair. This gives the instantaneous frequency deviation = audio.
   - A de-emphasis filter (75 μs) cuts high frequencies to undo broadcast pre-emphasis.
   - A 5-tap decimator reduces rate by 20×.

5. **After WBFM Receive:** A stream of 50,000 float samples per second — the audio signal in volts.

6. **Inside Audio Sink:** PulseAudio buffers ~20 ms of audio and sends it to your sound card.

7. **At the speaker:** You hear the FM station!

---

## 🔬 What You Should See / Hear

### Frequency Tuning
- Drag the `freq` slider across 87.5–108 MHz
- At station frequencies, you hear music/talk
- Between stations, you hear hiss (thermal noise)

### Gain Adjustment
- Low gain (0 dB): Weak stations are inaudible
- Optimal gain (30–50 dB): Clear audio, no distortion
- Excessive gain (70+ dB): Distorted audio, clipping

### Visualizing IQ
Add a **QT GUI Frequency Sink** connected to the USRP Source output. You'll see:
- A flat noise floor around -80 to -100 dB
- Bumps at the frequencies of active stations
- The center spike at 0 Hz (DC offset from the mixer — normal)

---

## 🔧 Tuning the Parameters

| Situation | What to change |
|---|---|
| Can't hear any stations | Increase `gain` to 50 dB; check antenna |
| Audio is distorted **on strong stations only** | See "no volume control" below — lower `gain` |
| Audio is distorted at all signal levels | Decrease `gain` to 30 dB |
| Only hear hiss | Change `freq` — you're between stations |
| Choppy audio | Lower `samp_rate` to 500 kSPS |
| `O` characters in console | Buffer overflow — lower `samp_rate` |

### The one thing this flowgraph cannot do: control volume

There are three blocks. None of them is a volume control, and `WBFM Receive` has no automatic
gain either — its output amplitude follows the transmitter's modulation depth directly.

On a live SignalSDR Pro receiving a strong local station at `gain = 55`, this flowgraph's audio
was measured peaking at **1.86**, where the Audio Sink clips at **±1.0**. The audio is loud and
audibly distorted, and the only lever you have is the RF `gain` slider — which is the wrong tool,
because it also changes the noise figure.

That is not a bug; it is what "three blocks" costs you. [Lab 03](../lab03_advanced_wbfm/README.md)
adds an AGC and a Multiply Const, and the problem disappears. Keep this in mind as you read
Lab 02 and Lab 03 — every block they add exists because something like this went wrong.

### A note on the `bw0` parameter

The USRP Source sets `bw0: samp_rate`, which configures the AD9361's analog filter. It looks
like a detail and it is not: leaving it unset lets the analog filter default to **56 MHz**, and
LO/DC leakage then accounts for ~84 % of everything the ADC sees. Measured on real hardware,
adding this one parameter improved this flowgraph's audio SNR from 34.6 dB to **53.2 dB**. See
[Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md).

---

## 🧪 Testing the Flowgraph

1. **Open:** `gnuradio-companion lab01_simple_wbfm.grc`
2. **Execute:** Press F5 or click ▶
3. **Tune:** Drag the frequency slider to a local station (find frequencies online at https://radio-locator.com/ or by scanning).
4. **Listen:** Confirm clear, undistorted audio.
5. **Observe:** Change gain and sample rate, note the effect on audio quality.

---

## ❓ Questions to Ponder

1. Why is the audio sample rate 50 kHz instead of the standard 48 kHz or 44.1 kHz?
   → Because 1 MSPS / 20 = 50 kHz. The WBFM Receive block picks integer decimation factors. This slight mismatch doesn't affect playback much.

2. What happens if you set `samp_rate` = 2 MSPS but forget to update Audio Decimation?
   → Audio rate becomes 2M/20 = 100 kHz. The Audio Sink will play audio 2× faster, raising pitch by an octave.

3. What if `gain` = 0 dB?
   → You'll hear only the strongest stations very faintly. The AD9361's noise floor dominates.

4. What if you set the center frequency to 2.4 GHz (Wi-Fi band)?
   → You'll hear broadband noise, but no intelligible audio — Wi-Fi uses digital modulation, not FM.

---

## 📚 Key Takeaways

- A complete FM receiver can be built with just **3 blocks**.
- The USRP Source handles all the hardware complexity; you focus on signal processing.
- Variables + GUI sliders make flowgraphs **interactive** and **educational**.
- Sample rates must match throughout the chain — a mismatch causes pitch shifts or errors.

---

**Next:** [Lab 02 — Enhanced WBFM with Visualization →](../lab02_enhanced_wbfm/README.md)
