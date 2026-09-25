# 🔬 Fundamentals 05 — Sampling, Filters and Changing the Sample Rate

> **What you will learn:** what really happens when you sample; how aliasing works; how FIR
> filters work and **how many taps** one needs; how to reduce (decimate) or change (resample)
> the sample rate safely; the Frequency Xlating FIR Filter; and the de-emphasis filter.
> **Before this:** [Fundamentals 02 — IQ](./02_iq_sampling.md), and you should have done
> [Lab 02](../02_flowgraphs/lab02_enhanced_wbfm/README.md).
> **Time:** about 50 minutes. **Used by:** Labs 05, 06, 07, 08, 09.

---

## Why this chapter exists

In Labs 01–04 you typed numbers into filter blocks — `cutoff = 100000`, `width = 20000`,
`decim = 125` — and the radio worked. You were following a recipe.

This chapter explains the recipe. Afterwards, for any wire in any flowgraph, you can answer:

1. What is the **sample rate** on this wire, and why?
2. What does this **filter** keep, and what does it remove?
3. How many **taps** does the filter need, and how much CPU does that cost?
4. Is it **safe** to reduce the sample rate here, or will another station fold on top of mine?

---

## Part 1 — Sampling and aliasing

### What sampling does to the spectrum

When you sample a signal *f*ₛ times per second, something surprising happens to its spectrum:
it gets **copied**. The sampled signal's spectrum is the original spectrum, repeated again and
again, every *f*ₛ hertz, forever:

```
The original signal, from −B to +B:

              ┌───┐
   ───────────┤   ├───────────────────────────────  frequency
             -B   +B

After sampling at fs — a copy every fs:

   ┌───┐      ┌───┐      ┌───┐      ┌───┐
 ──┤   ├──────┤   ├──────┤   ├──────┤   ├────────  frequency
   -fs        0          fs         2fs
```

These copies are called **images** or **aliases**. As long as the copies **do not overlap**,
nothing is lost: you can always get the original back.

<details>
<summary><b>Going deeper:</b> why sampling makes copies</summary>

Sampling every $T_s$ seconds is the same as multiplying by a train of spikes:

$$
x_s(t) = x(t) \cdot \sum_{n=-\infty}^{\infty} \delta(t - nT_s)
$$

Multiplying in time is **convolution** in frequency. The spectrum of a spike train with
spacing $T_s$ is another spike train, with spacing $f_s = 1/T_s$. Convolving with it copies the
spectrum at every multiple of $f_s$:

$$
X_s(f) = f_s \sum_{k=-\infty}^{\infty} X(f - k f_s)
$$

That one equation is the whole theory of sampling.
</details>

### The Nyquist rule, exactly

The copies do not overlap if:

| Kind of samples | Rule | In words |
|---|---|---|
| **Real** (one number each, like audio) | $f_s > 2B$ | sample rate more than **twice** the highest frequency |
| **IQ** (two numbers each, like an SDR) | $f_s > B$ | sample rate more than the **total width** |

**IQ gives you twice as much for the same sample rate.** At 2 MSPS, your SignalSDR Pro shows a
full 2 MHz of spectrum (from −1 MHz to +1 MHz), not 1 MHz.

### What aliasing does

If a signal lies **outside** the range the sample rate can hold (±*f*ₛ/2), it does not
disappear. It **folds back** and appears at a false frequency:

$$
f_{\text{alias}} = f_0 - k \cdot f_s, \qquad k = \text{the whole number nearest to } f_0 / f_s
$$

The false copy looks **exactly** like a real signal at that frequency. No later processing can
remove it. So a filter must remove out-of-range signals **before** every reduction in sample
rate — never after.

> **Example.** You reduce the rate to 240 kSPS (so you can hold ±120 kHz). A strong pager
> transmitter is 260 kHz away from your tuned frequency. The nearest whole number to
> 260 ÷ 240 is 1, so it folds to 260 − 240 = **20 kHz** — right inside the FM station you are
> listening to. You would hear interference and never know why. **Filter first.**

### Sample rates on the SignalSDR Pro

| Rate | Width you see | Data (fc32) | Notes |
|---|---|---|---|
| 250 kSPS | 250 kHz | 2 MB/s | one FM station, just |
| 1 MSPS | 1 MHz | 8 MB/s | Lab 01; about 5 FM stations |
| 2 MSPS | 2 MHz | 16 MB/s | Labs 02–09; easy over USB 3.0 |
| 8 MSPS | 8 MHz | 64 MB/s | wide scanning; watch for `O` (overflow) |
| 20 MSPS | 20 MHz | 160 MB/s | near the practical USB 3.0 limit |

`fc32` (complex float32) is 8 bytes per sample. `sc16` (complex 16-bit integers) is 4 bytes —
half the USB load. Lab 05 uses this.

---

## Part 2 — FIR filters

### What an FIR filter does

An **FIR** (finite impulse response) filter makes each output sample from a **weighted average
of the last *N* input samples**:

$$
y[n] = h[0]\,x[n] + h[1]\,x[n-1] + h[2]\,x[n-2] + \dots + h[N-1]\,x[n-N+1]
$$

The weights *h*[*k*] are called the **taps**. *N* is the number of taps. Choosing the right
weights makes the filter keep some frequencies and remove others.

FIR filters are used almost everywhere in SDR because:

- **They are always stable.** There is no feedback, so they cannot "run away".
- **They can delay every frequency equally** (if the taps are symmetric). Every frequency is
  delayed by exactly (*N* − 1)/2 samples, so the shape of the signal is kept. Audio and data
  both need this. (Remember this delay — it caused the Lab 04 stereo bug.)
- **They are simple for a computer:** just multiply and add.

### The perfect filter is impossible

A perfect low-pass filter would pass everything below the cutoff and remove everything above,
with a vertical wall in between. Its taps would go on **forever** — impossible to build. If you
simply cut them short, the filter leaks: its "stop" region only reaches about **−21 dB**, no
matter how many taps you use.

### Windows: smoothing the taps

The fix is to fade the taps gently to zero at both ends, using a **window**. Different windows
give different results:

| Window | GNU Radio name | How much it blocks (stopband) |
|---|---|---|
| Rectangular (no fading) | `window.WIN_RECTANGULAR` | 21 dB |
| Bartlett | `window.WIN_BARTLETT` | 27 dB |
| Hann | `window.WIN_HANN` | 44 dB |
| **Hamming** | `window.WIN_HAMMING` | **53 dB** |
| Blackman | `window.WIN_BLACKMAN` | 74 dB |
| Blackman-Harris | `window.WIN_BLACKMAN_HARRIS` | 92 dB |
| Kaiser (β = 6.76) | `window.WIN_KAISER` | 70 dB |

**Hamming is used in every lab here.** 53 dB is enough to push a neighbouring FM station below
the noise, and it needs fewer taps than Blackman.

### How many taps? The most useful formula in practical SDR

$$
\boxed{N = \frac{A_{dB} \times f_s}{22 \times \Delta f}}
$$

- $A_{dB}$ — how much the window blocks (from the table: 53 for Hamming)
- $f_s$ — the sample rate going **into** the filter
- $\Delta f$ — the **transition width**: how quickly the filter goes from "pass" to "block"
  (the `width` setting in GNU Radio)

This is exactly the formula GNU Radio's `firdes` uses. It then rounds *N* up to an odd number.

> **Example — Lab 03's channel filter.** 2,000,000 samples/s, transition 20 kHz, Hamming:
>
> $$N = \frac{53 \times 2{,}000{,}000}{22 \times 20{,}000} = 240.9 \rightarrow \mathbf{241} \text{ taps}$$
>
> Each output needs 241 multiplications, and there are 2 million outputs per second: about
> **480 million** multiplications per second. That is real CPU work. Halve the transition to
> 10 kHz and you need 481 taps — **twice** the work.

**Three rules that follow from the formula:**

1. **Sharp filters are expensive.** Ask for the widest transition your signal allows.
2. **Cost grows with the input sample rate.** Filter at the lowest rate you can — reduce the
   rate in steps.
3. **A stronger window is cheaper than a sharper edge.** Hamming → Blackman costs 1.4× the taps
   for 21 dB more blocking. Halving the transition costs 2× the taps.

Check it yourself:

```bash
python3 -c "
from gnuradio.filter import firdes
from gnuradio.fft import window
t = firdes.low_pass(1.0, 2e6, 100e3, 20e3, window.WIN_HAMMING, 6.76)
print('taps:', len(t))"
```

✅ `taps: 241`

---

## Part 3 — Changing the sample rate

### Decimation: filter, then keep 1 in M

To **reduce** the sample rate by a whole number *M*:

1. **Low-pass filter** so nothing is left above the new limit (*f*ₛ / 2*M*). **This step is
   required.**
2. **Keep every M-th sample**, throw the rest away.

Skip step 1, and everything between the new limit and the old one folds into your signal —
permanently.

### The decimating filter saves work

A simple approach would calculate every filter output, then throw away *M* − 1 of every *M*. A
**decimating FIR filter** only calculates the outputs it keeps. That is *M* times less work:

$$
\text{multiplications per second} = \frac{N \times f_s}{M}
$$

GNU Radio's filter blocks do this when you set their `decim` setting above 1. **Always use the
filter's own `decim`**, not a separate "Keep 1 in N" block.

### Interpolation: add zeros, then filter

To **increase** the rate by *L*: put *L* − 1 zeros between samples, then low-pass filter. The
zeros create unwanted copies of the spectrum; the filter removes them.

### Resampling by a fraction L/M

To change the rate by a fraction, **interpolate by L, filter, then decimate by M** — all in one
**Rational Resampler** block (Lab 02):

$$
f_{\text{out}} = f_{\text{in}} \times \frac{L}{M}
$$

**Always reduce the fraction to its lowest terms**, because the block works internally at
*f*ₛ × *L*.

> **Example — Lab 03's resampler.** 2,000,000 → 384,000.
> 384,000 ÷ 2,000,000 = 0.192 = **24/125** (lowest terms). So interpolation = 24,
> decimation = 125. Internally that is 2,000,000 × 24 = 48 million samples per second — which is
> why the block uses a clever "polyphase" method that never actually calculates with the zeros.

A helper to find L and M:

```bash
python3 -c "
from math import gcd
fin, fout = 2000000, 384000
g = gcd(fin, fout)
print(f'interp={fout//g}  decim={fin//g}')"
```

✅ `interp=24  decim=125`

### Plan your rates backwards

Choose sample rates so every step divides nicely:

```
2,000,000  ──×24 ÷125──▶  384,000  ──÷8──▶  48,000   ✅ clean
2,000,000  ────────────▶   441,000  ────▶   44,100   ⚠️ 441/2000 — big, costly filters
```

**Start from the audio rate and work backwards.** 48 kHz audio × 8 = 384 kHz; × 125/24 =
2 MSPS at the radio. Everything comes out as whole numbers.

---

## Part 4 — Band-pass and frequency-shifting filters

### A band-pass filter from a low-pass filter

Multiply a low-pass filter's taps by a cosine at frequency *f*₀, and its pass region moves up to
*f*₀. That is how `firdes.band_pass()` works. Lab 04 uses a band-pass filter to pick out the
19 kHz stereo pilot.

<details>
<summary><b>Going deeper:</b> the formula</summary>

$$
h_{\text{BP}}[k] = 2\,h_{\text{LP}}[k] \cos\!\left(2\pi \frac{f_{\text{center}}}{f_s} k\right)
$$

A **complex** band-pass filter (`firdes.complex_band_pass`) multiplies by
$e^{j2\pi f_{\text{center}} k / f_s}$ instead, and so passes only the positive frequency.
Lab 04 uses this for the pilot.
</details>

### The Frequency Xlating FIR Filter — tuning in software

This block (Lab 05 and Lab 06) does three things in one step:

1. **Shift** the chosen frequency (`center_freq`) down to 0 Hz.
2. **Filter** with low-pass taps.
3. **Decimate** by *M*.

It is efficient because the shift is built into the taps (so it costs nothing extra) and it
only calculates the outputs it keeps.

**Why it matters:** tune the radio once to the middle of a band. Then pick **any** channel inside
that band in software — instantly, with no hardware retuning. This is the heart of
software-defined radio.

```
      2 MHz of spectrum from the SDR
   ─────────────────────────────────────
   │     ▲        ▲         ▲          │
   │  ch A     ch B      ch C          │
   └──┬────────┬─────────┬─────────────┘
      │        │         │
   xlating  xlating   xlating     ← three filters, one tuner:
   filter   filter    filter        three channels at once
```

<details>
<summary><b>Going deeper:</b> the equation</summary>

$$
y[n] = \sum_k h[k] \; x[nM - k] \; e^{-j 2\pi f_{\text{offset}} (nM-k)/f_s}
$$
</details>

---

## Part 5 — IIR filters, and de-emphasis

An **IIR** (infinite impulse response) filter uses **feedback**: each output depends on
earlier outputs as well as inputs. It can be much sharper for the same number of coefficients,
but it does not delay all frequencies equally, and a badly designed one can become unstable.

This course uses one IIR filter: the **de-emphasis** filter for FM
([Fundamentals 04 §6](./04_fm_theory.md#6-pre-emphasis-and-de-emphasis)). It is the simplest
possible IIR filter, with one setting, α:

$$
y[n] = \alpha \, x[n] + (1-\alpha)\, y[n-1], \qquad
\boxed{\alpha = 1 - e^{-1/(f_s \, \tau)}}
$$

In words: each output is mostly the previous output, nudged a little (by α) towards the new
input. That smooths out fast changes — high frequencies — just like a resistor and capacitor.

| Sample rate | τ | α |
|---|---|---|
| 240 kHz | 50 µs | 0.0800 |
| 240 kHz | 75 µs | 0.0540 |
| 48 kHz | 50 µs | 0.3408 |
| 48 kHz | 75 µs | 0.2425 |

> ⚠️ **α depends on the sample rate.** If you move the de-emphasis to a wire with a different
> rate but keep the old α, the treble will be wrong. This is a common bug in home-made FM
> receivers.

Calculate them yourself:

```bash
python3 -c "
import math
for fs in (240000, 48000):
    for tau in (50e-6, 75e-6):
        print(f'fs={fs:>7}  tau={tau*1e6:>3.0f}us  alpha={1-math.exp(-1/(fs*tau)):.4f}')"
```

---

## Part 6 — A checklist for every new flowgraph

Before you build a chain, fill in a table like this for every wire (example: Lab 03):

| # | Wire | Sample rate | Type | Width present | Width wanted |
|---|---|---|---|---|---|
| 1 | SDR → low-pass filter | 2 MSPS | complex | ±1 MHz | ±100 kHz |
| 2 | filter → resampler | 2 MSPS | complex | ±100 kHz | — |
| 3 | resampler → demod | 384 kSPS | complex | ±100 kHz | ✅ fits in ±192 kHz |
| 4 | demod → audio | 48 kSPS | float | 0–15 kHz | ✅ fits in 0–24 kHz |

Then ask three questions for each row:

1. **Does the wanted width fit inside ±(rate ÷ 2)?** If not, it will alias.
2. **Is there a filter before every reduction in rate?** If not, it will alias.
3. **Do the data types match at both ends?** GRC checks this one for you. It does **not** check
   the other two.

---

## ✅ Summary

- Sampling makes **copies** of the spectrum every *f*ₛ. Nyquist: real needs *f*ₛ > 2B; **IQ needs
  *f*ₛ > B**.
- **Aliasing** cannot be undone. Always filter **before** reducing the sample rate.
- An **FIR filter** is a weighted average of recent samples. Symmetric taps delay everything by
  (*N* − 1)/2 samples.
- **Taps: *N* = A × *f*ₛ / (22 × Δ*f*).** Sharp edges and high rates are expensive.
- **Decimate** with the filter's own `decim`. **Resample** with the fraction in lowest terms.
- The **Frequency Xlating FIR Filter** shifts, filters and decimates in one step: software tuning.
- De-emphasis **α depends on the sample rate**.

## 🧠 Check yourself

1. You sample IQ at 500 kSPS. How much spectrum do you see?
   <details><summary>Answer</summary>500 kHz: from −250 kHz to +250 kHz around the tuned
   frequency.</details>
2. A 300 kHz tone is present when you sample at 240 kSPS. Where does it appear?
   <details><summary>Answer</summary>The nearest whole number to 300/240 is 1, so it appears
   at 300 − 240 = 60 kHz.</details>
3. A Hamming low-pass filter at 384 kSPS with a 5 kHz transition. How many taps?
   <details><summary>Answer</summary>53 × 384,000 / (22 × 5,000) = 185.0 → 185 taps.</details>
4. Change 1.92 MSPS to 48 kSPS with a Rational Resampler. What are interpolation and decimation?
   <details><summary>Answer</summary>48,000/1,920,000 = 1/40: interpolation 1, decimation
   40.</details>
5. Why must the anti-alias filter come *before* the decimator?
   <details><summary>Answer</summary>Decimation folds everything above the new limit into the
   band. Once folded, the false signal is identical to a real one and cannot be
   removed.</details>
6. You move de-emphasis from a 240 kHz wire to a 48 kHz wire, but keep α = 0.08. What happens?
   <details><summary>Answer</summary>At 48 kHz, α = 0.08 means τ ≈ 250 µs instead of 50 µs.
   The corner frequency falls from about 3.2 kHz to about 640 Hz, so far too much treble is
   removed: the audio sounds <b>muffled</b>. You need α = 0.3408 at 48 kHz.</details>

**Next:** [Fundamentals 06 — Noise, SNR and Gain →](./06_noise_snr_and_gain.md)
