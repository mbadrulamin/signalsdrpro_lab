# 🔴 Lab 04 — Stereo WBFM with Full MPX Decoding

> **Time:** 2 hours  
> **Difficulty:** Advanced  
> **New blocks:** Quadrature Demod, PLL Refout, Multiply, Add/Sub, De-emphasis Filter  
> **Concepts:** Stereo multiplexing, PLL, subcarrier recovery, matrix operations

---

## 🎯 Goal

Decode **true stereo FM** by manually extracting the L+R and L−R components from the MPX baseband. This lab demonstrates what GNU Radio can really do — we'll rebuild the entire receiver chain from first principles, **without** using the black-box WBFM Receive block.

---

## 📖 Background: How Stereo FM Works

As explained in [Fundamentals 04](../../01_fundamentals/04_fm_theory.md), an FM broadcast signal contains a multiplexed (MPX) baseband:

```
Amplitude
  │
  │ [L+R]   [Pilot]    [L-R DSB-SC]   [RDS]
  │ 0-15kHz  19kHz    23-53kHz        57kHz
  └───────────────────────────────────────────
  0    15    19    23        53        57  kHz
```

- **L+R** (0–15 kHz): Sum of left and right channels (mono)
- **Pilot** (19 kHz): Reference tone at exactly half the stereo subcarrier
- **L−R DSB-SC** (23–53 kHz): Difference signal, double-sideband suppressed-carrier at 38 kHz
- **RDS** (57 kHz): Digital data (ignored here)

To recover L and R:
$$
L = \frac{(L+R) + (L-R)}{2}, \quad R = \frac{(L+R) - (L-R)}{2}
$$

The challenge: the 38 kHz subcarrier is **not transmitted**. Only the 19 kHz pilot is. So we must **double** the pilot to recover the 38 kHz subcarrier.

---

## 📐 Architecture

```
USRP Source (2 MSPS)
      │
      ▼
Low Pass Filter (cutoff 100 kHz)
      │
      ▼
Rational Resampler (2M → 240k)
      │
      ▼
Quadrature Demod ─────── MPX signal (mono + stereo + pilot)
      │
      ├──────────────────────────────┐
      │                              │
      ▼                              ▼
┌─────────────────┐         ┌──────────────────────┐
│ LPF (0–15 kHz)  │         │ BPF (18.5–19.5 kHz)  │
│ extracts L+R    │         │ extracts pilot tone  │
└────────┬────────┘         └──────────┬───────────┘
         │                             │
         │                             ▼
         │                     ┌───────────────┐
         │                     │ PLL Refout    │
         │                     │ locks to 19kHz│
         │                     │ output = 19kHz│
         │                     │ sine wave     │
         │                     └───────┬───────┘
         │                             │
         │                             ▼
         │                     ┌───────────────┐
         │                     │ Multiply by   │
         │                     │ itself → 38kHz│
         │                     │ (× 2)         │
         │                     └───────┬───────┘
         │                             │
         │                             ▼
         │                     ┌───────────────┐
         │                     │ Multiply with │
         │                     │ MPX (float ×  │
         │                     │ float) → L-R  │
         │                     └───────┬───────┘
         │                             │
         │                             ▼
         │                     ┌───────────────┐
         │                     │ LPF (0–15 kHz)│
         │                     │ extracts L-R  │
         │                     └───────┬───────┘
         │                             │
         │                             ▼
         │                     ┌───────────────┐
         │                     │ Scale ×2      │
         │                     │ (DSB-SC halves│
         │                     │  amplitude)   │
         │                     └───────┬───────┘
         │                             │
         ▼                             ▼
  ┌────────────┐               ┌────────────┐
  │ De-emph    │               │ De-emph    │
  │ (50/75 μs) │               │ (50/75 μs) │
  └──────┬─────┘               └──────┬─────┘
         │                            │
         ▼                            ▼
   ┌────────────────────────────────────────┐
   │  Matrix:                               │
   │  Left  = (L+R) + (L-R)                 │
   │  Right = (L+R) - (L-R)                 │
   │  (using Add and Subtract blocks)       │
   └────────────────────┬───────────────────┘
                        │
                        ▼
                 ┌────────────┐
                 │ Audio Sink │ (stereo)
                 └────────────┘
```

---

## 📋 Block-by-Block Explanation

### Stage 1: IQ to MPX Baseband

#### USRP Source
- Center freq: `freq` (88–108 MHz)
- Sample rate: `samp_rate` = 2 MSPS
- Gain: 40 dB

#### Low Pass Filter
- Complex in/out, cutoff 100 kHz
- Removes all signals outside ±100 kHz of tuned frequency

#### Rational Resampler
- 2 MSPS → 240 kSPS (ratio 12/100 = 3/25)
- 240 kSPS is plenty for the 100 kHz MPX signal
- Reduces CPU load

#### Quadrature Demod
- Converts IQ to real-valued MPX signal
- This is the heart of FM demodulation (see Fundamentals 04)

**Output:** A real-valued float stream at 240 kSPS containing the full MPX signal.

---

### Stage 2: L+R Extraction

#### Low Pass Filter (audio)
- Type: `fff` (float in/out)
- Cutoff: 15 kHz
- Transition: 1 kHz
- Extracts the mono sum signal (L+R)

---

### Stage 3: Pilot Tone Recovery

#### Band Pass Filter
- Type: `fff`
- Low cutoff: 18.5 kHz
- High cutoff: 19.5 kHz
- Transition: 500 Hz
- Isolates the 19 kHz pilot tone

#### PLL Refout (`pll_refout_cc`)
- Locks a complex oscillator to the pilot tone
- Outputs a clean 19 kHz complex sinusoid: $e^{j 2\pi \cdot 19000 \cdot t}$
- Type: `cc` (complex in, complex out)

Wait — our pilot is a real signal. We need to convert it to complex first:

**Float to Complex** block:
- Real input: pilot
- Imaginary input: 0
- Output: complex pilot

Then the PLL locks and produces a clean 19 kHz complex reference.

#### Multiply (×2 trick)
To get 38 kHz: multiply the 19 kHz complex signal by itself!

$$
e^{j 2\pi \cdot 19k \cdot t} \cdot e^{j 2\pi \cdot 19k \cdot t} = e^{j 2\pi \cdot 38k \cdot t}
$$

**Multiply** block (complex × complex):
- Input 1: PLL output (19 kHz complex)
- Input 2: PLL output (same)
- Output: 38 kHz complex subcarrier

#### Convert 38 kHz to Real
The MPX signal is real-valued, so we need a real 38 kHz signal to multiply with.

**Complex to Real** block: takes the real part of the 38 kHz complex signal.

---

### Stage 4: L−R Recovery

#### Multiply MPX × 38 kHz (`blocks_multiply_xx`, type ff)

The L−R signal is DSB-SC at 38 kHz. Multiplying the MPX by a 38 kHz carrier demodulates it:

$$
\text{MPX}(t) \cdot \cos(2\pi \cdot 38k \cdot t) = \frac{L-R}{2} + \text{high-frequency terms}
$$

(The factor of 1/2 comes from the DSB-SC product identity.)

Both inputs are **float** (the MPX from Quadrature Demod and the real part of the doubled subcarrier). Output is also **float**.

> 💡 This is simpler than converting MPX to complex and multiplying complex × complex — because both signals are real, we can work entirely in the float domain.

#### Low Pass Filter (L−R) (`low_pass_filter`, type fff)
- Type: `fff`
- Cutoff: 15 kHz
- Extracts L−R, removes the high-frequency products

---

### Stage 5: De-Emphasis

Apply 50 μs (or 75 μs for North America) de-emphasis to both L+R and L−R paths.

**De-emphasis filter** is a first-order IIR:

$$
H(s) = \frac{1}{1 + s\tau} \quad\text{or in z-domain:}\quad H(z) = \frac{1 - e^{-T/\tau}}{1 - e^{-T/\tau} z^{-1}}
$$

In GNU Radio, use a **Single Pole IIR Filter** (`filter_singlepole_iir_ff`) with:
- Taps: $\alpha = 1 - e^{-T_s / \tau}$

Where $T_s = 1/240000$ and $\tau = 50 \times 10^{-6}$ s.

Compute:
$$
\alpha = 1 - e^{-1/240000/0.000050} = 1 - e^{-0.0833} \approx 0.0800
$$

So taps ≈ **0.08** (adjust for 75 μs: α ≈ 0.0533).

---

### Stage 6: Stereo Matrix

Using Add (`add_ff`) and Subtract (`sub_ff`) blocks:

```
Left  = (L+R) + (L-R)    [using Add]
Right = (L+R) - (L-R)    [using Subtract]
```

Then combine into a 2-channel stream with **Streams to Stream** (2 inputs) or use **Float to Short** then play as stereo.

Or more directly, use **Audio Sink** with `num_inputs = 2`.

---

## 🔬 Mathematical Deep Dive

Let's trace the math through the full chain.

### FM signal at antenna
$$
s(t) = A \cos\!\left(2\pi f_c t + 2\pi \Delta f \int_0^t m(\tau) \, d\tau\right)
$$

Where $m(t)$ is the MPX baseband:
$$
m(t) = [L(t) + R(t)] + P \cos(2\pi \cdot 19k \cdot t) + [L(t) - R(t)] \cos(2\pi \cdot 38k \cdot t) + \text{RDS}(t)
$$

### After Quadrature Demod
$$
y(t) \propto m(t)
$$

We recover the MPX baseband directly.

### L+R Path
$$
\text{LPF}_{15k}[y(t)] = L(t) + R(t)
$$

### Pilot Path
$$
\text{BPF}_{18.5k-19.5k}[y(t)] = P \cos(2\pi \cdot 19k \cdot t)
$$

PLL locks: output = $e^{j 2\pi \cdot 19k \cdot t}$.

Self-multiply: $e^{j 2\pi \cdot 19k \cdot t} \cdot e^{j 2\pi \cdot 19k \cdot t} = e^{j 2\pi \cdot 38k \cdot t}$

Real part: $\cos(2\pi \cdot 38k \cdot t)$.

### L−R Path
$$
y(t) \cdot \cos(2\pi \cdot 38k \cdot t) = \ldots + [L(t) - R(t)] \cos^2(2\pi \cdot 38k \cdot t) + \ldots
$$

Using the identity $\cos^2(\theta) = \frac{1}{2} + \frac{1}{2}\cos(2\theta)$:

$$
= \frac{L(t) - R(t)}{2} + \text{high-frequency at 76 kHz}
$$

After LPF:
$$
\text{LPF}_{15k}[y(t) \cdot \cos(2\pi \cdot 38k \cdot t)] = \frac{L(t) - R(t)}{2}
$$

Multiply by 2 to get $L-R$ (or just scale at the end).

### Matrix
$$
L = (L+R) + (L-R) = 2L \\
R = (L+R) - (L-R) = 2R
$$

Divide by 2 (or scale by 0.5) to get correct levels.

---

## 🎛️ GUI Controls

| Control | Range | Purpose |
|---|---|---|
| Frequency | 87.5–108 MHz | Tune the station |
| RF Gain | 0–76 dB | Hardware gain |
| De-emphasis | {50, 75} μs | Switch between EU/US standards |
| Volume | 0.0–3.0 | Output audio level |

---

## 🧪 Testing the Flowgraph

1. **Open:** `gnuradio-companion lab04_stereo_wbfm.grc`
2. **Execute:** Press F5
3. **Tune** to a known **stereo** FM station (most music stations are stereo; talk stations are often mono).
4. **Listen** — you should hear clear stereo separation.
5. **Compare** with Lab 01 (mono WBFM Receive):
   - Mono: single channel, everything "in the middle"
   - Stereo: instruments/voices panned left and right
6. **Visualize** with a QT GUI Time Sink on L and R outputs — they should be different waveforms.
7. **Verify** stereo by listening with headphones.

---

## 🐛 Troubleshooting

### "Audio sounds like a buzz or whine"
→ The PLL isn't locked properly. Check the BPF is centered on 19 kHz exactly. Try increasing the PLL bandwidth.

### "No stereo effect, just mono"
→ The L-R path isn't working. Verify the multiply is producing a signal, and the LPF is extracting L-R.

### "Audio is 2× too loud"
→ You forgot to divide by 2 in the matrix. Add a Multiply Const with value 0.5 at the end.

### "Audio is too quiet"
→ You might have an extra 0.5× scaling somewhere. Trace the gain through the chain.

### "PLL drifts"
→ Pilot tone is too weak. Increase RF gain or check the station actually transmits stereo.

---

## ❓ Questions to Ponder

1. Why is the pilot at 19 kHz and not 38 kHz?
   → To save bandwidth and to allow simple doubling (19 kHz × 2 = 38 kHz).

2. Why is L-R transmitted as DSB-SC and not as a simple signal?
   → DSB-SC suppresses the 38 kHz carrier, saving power and reducing interference.

3. What happens to mono-only stations?
   → They transmit only L+R. The 19 kHz pilot may be absent. The L-R path outputs silence. Result: mono playback (correct!).

4. What's the effect of swapping L+R and L-R in the matrix?
   → L and R are swapped — you hear "inside-out" stereo.

---

## 📚 Key Takeaways

- **You can rebuild any SDR from first principles** — you don't need black-box blocks.
- **Stereo FM is an elegant engineering solution** from the 1960s — still used today.
- **PLLs are essential** whenever you need to recover a suppressed carrier.
- **Understanding the math** lets you debug and extend any flowgraph.

---

## 🚀 What's Next?

You now have the skills to tackle the next series of labs:
- ✈️ **ADS-B Airplane Detection** — detect aircraft at 1090 MHz, decode their positions
- 📻 **FM Transmitter** — broadcast your own signal (be careful with local laws!)
- 📡 **Weather Satellite Reception** — Meteor-M LRPT at 137.9 MHz
- 📱 **GSM Sniffing** — decode GSM control channels with LTESniffer / gr-gsm

---

## 📖 References

1. Wikipedia: [FM broadcasting](https://en.wikipedia.org/wiki/FM_broadcasting)
2. GNU Radio Wiki: [WBFM Stereo](https://wiki.gnuradio.org/index.php?title=WBFM_Stereo)
3. Ettus Research: [USRP B210 Manual](https://files.ettus.com/manual/page_usrp_b200.html)
4. Signalens: [SignalSDR Pro](https://signalens.com/)
