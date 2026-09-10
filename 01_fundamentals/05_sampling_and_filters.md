# 🔬 Fundamentals 05 — Sampling, Filters & Resampling

> **Prerequisite:** IQ Sampling (Fundamentals 02), and you should have run Lab 02.
> **Time to read:** 50 minutes
> **Used by:** Lab 05, Lab 06, Lab 07, Lab 08, Lab 09

---

## Why This Chapter Exists

In Labs 01–04 you typed numbers into filter blocks — `cutoff = 100000`, `width = 20000`,
`decim = 125` — and the radio worked. You were following a recipe.

This chapter turns the recipe into **engineering**. After reading it you will be able to
answer, for any block in any flowgraph:

- What sample rate is at this wire, and why?
- What is the cutoff, and what happens to everything above it?
- How many taps does this filter cost, and how much CPU is that?
- Is this decimation safe, or am I about to alias a neighbouring station on top of mine?

Every later lab in this repo depends on these four answers.

---

## Part 1 — Sampling and the Nyquist Criterion

### The sampling operation

Sampling a continuous signal $x(t)$ every $T_s$ seconds gives the sequence

$$
x[n] = x(nT_s), \qquad f_s = \frac{1}{T_s}
$$

Mathematically, sampling is multiplication by an impulse train:

$$
x_s(t) = x(t) \cdot \sum_{n=-\infty}^{\infty} \delta(t - nT_s)
$$

Multiplication in time is **convolution in frequency**. The Fourier transform of an impulse
train of spacing $T_s$ is another impulse train of spacing $f_s$, so:

$$
\boxed{X_s(f) = f_s \sum_{k=-\infty}^{\infty} X(f - k f_s)}
$$

**This single equation is the whole theory of sampling.** The spectrum of the sampled signal
is the original spectrum **repeated forever** at multiples of $f_s$. These copies are called
**images** or **aliases**.

```
Original spectrum X(f), bandlimited to ±B:

              ┌───┐
   ───────────┤   ├───────────────────────────────  f
             -B   +B

After sampling at fs — copies every fs:

   ┌───┐      ┌───┐      ┌───┐      ┌───┐
 ──┤   ├──────┤   ├──────┤   ├──────┤   ├────────  f
   -fs        0          fs         2fs
```

### Nyquist, stated precisely

The copies do not overlap if and only if

$$
f_s > 2B \quad \text{(real signal, bandwidth } B \text{ one-sided)}
$$

$$
f_s > B \quad \text{(complex/IQ signal, bandwidth } B \text{ total)}
$$

**IQ sampling buys you a factor of two.** This is the practical payoff of Fundamentals 02: a
complex signal has no conjugate-symmetry constraint, so its spectrum occupies $-f_s/2$ to
$+f_s/2$ with no waste. When your SignalSDR Pro runs at 2 MSPS complex, you see a genuine
2 MHz of spectrum, not 1 MHz.

### What aliasing actually does

If a component sits at frequency $f_0 > f_s/2$, sampling folds it to

$$
f_{\text{alias}} = f_0 - k f_s \quad \text{where } k = \operatorname{round}\!\left(\frac{f_0}{f_s}\right)
$$

The folded copy is **indistinguishable** from a genuine signal at that frequency. No amount
of later DSP can remove it. This is why an anti-alias filter must come **before** every rate
reduction, never after.

> **Worked example.** You sample at $f_s = 240$ kSPS. A strong pager transmitter sits
> 260 kHz away from your tuned frequency. $k = \operatorname{round}(260/240) = 1$, so it
> aliases to $260 - 240 = 20$ kHz — right on top of the FM stereo pilot tone. Your Lab 04
> stereo decoder would lose lock and you would never know why. **Filter first.**

### Sample rate reality check for the SignalSDR Pro

| Rate | Complex bandwidth | Bytes/s (fc32) | Comment |
|---|---|---|---|
| 250 kSPS | 250 kHz | 2.0 MB/s | One FM channel, minimum for WBFM |
| 1 MSPS | 1 MHz | 8.0 MB/s | Lab 01 default; ~5 FM channels |
| 2 MSPS | 2 MHz | 16.0 MB/s | Labs 03–04; comfortable on USB 3.0 |
| 8 MSPS | 8 MHz | 64.0 MB/s | Wideband scanning; watch for overflow `O` |
| 20 MSPS | 20 MHz | 160.0 MB/s | Near the B210 USB 3.0 practical ceiling |

At `fc32` (complex float32) each sample is 8 bytes. At `sc16` it is 4 bytes — halving the
USB load at the cost of some dynamic range headroom. Lab 05 uses this fact.

---

## Part 2 — FIR Filters

### The FIR equation

A **Finite Impulse Response** filter computes each output as a weighted sum of the last $N$
inputs:

$$
y[n] = \sum_{k=0}^{N-1} h[k] \, x[n-k]
$$

The coefficients $h[k]$ are the **taps**. In the frequency domain this is multiplication:

$$
Y(e^{j\omega}) = H(e^{j\omega}) X(e^{j\omega}), \qquad
H(e^{j\omega}) = \sum_{k=0}^{N-1} h[k] e^{-j\omega k}
$$

FIR filters are the workhorse of SDR because they are:

- **Unconditionally stable** — no feedback, so no way to blow up.
- **Exactly linear phase** if the taps are symmetric ($h[k] = h[N-1-k]$), meaning all
  frequencies are delayed by the same $\frac{N-1}{2}$ samples. Audio and data both need this.
- **Cheap to parallelise** — it is a dot product.

### The ideal filter and why it is impossible

The ideal lowpass with cutoff $f_c$ has a rectangular frequency response. Its impulse
response is the inverse transform:

$$
h_{\text{ideal}}[k] = 2\frac{f_c}{f_s}\,\operatorname{sinc}\!\left(2\frac{f_c}{f_s}k\right),
\qquad \operatorname{sinc}(x) = \frac{\sin \pi x}{\pi x}
$$

This is **infinitely long** and non-causal. To build it we must truncate it — and truncation
in time is multiplication by a rectangle, which convolves the frequency response with a
`sinc`, producing ripple. The worst ripple never goes below about **−21 dB** no matter how
many taps you add. This is the **Gibbs phenomenon**.

### Windows: trading transition width for stopband depth

The fix is to taper the truncated impulse response with a **window** $w[k]$:

$$
h[k] = h_{\text{ideal}}[k] \cdot w[k]
$$

| Window | GNU Radio constant | Stopband attenuation $A_{dB}$ |
|---|---|---|
| Rectangular | `window.WIN_RECTANGULAR` | 21 dB |
| Bartlett | `window.WIN_BARTLETT` | 27 dB |
| Hann | `window.WIN_HANN` | 44 dB |
| **Hamming** | `window.WIN_HAMMING` | **53 dB** |
| Blackman | `window.WIN_BLACKMAN` | 74 dB |
| Blackman-Harris | `window.WIN_BLACKMAN_hARRIS` | 92 dB |
| Kaiser ($\beta = 6.76$) | `window.WIN_KAISER` | 70 dB |

(Yes, `WIN_BLACKMAN_hARRIS` really is spelled with a lowercase `h` in GNU Radio 3.10. It is a
long-standing typo that became API.)

**Hamming is the default in every lab here** because 53 dB is enough to push an adjacent FM
station below the noise floor, and it costs far fewer taps than Blackman.

### The tap-count equation

This is the single most useful formula in practical SDR — and it is the *exact* formula GNU
Radio's `firdes` uses internally (a form of the fred harris rule):

$$
\boxed{N = \frac{A_{dB} \cdot f_s}{22 \cdot \Delta f}}
$$

Where $\Delta f$ is the **transition width** (the `width` parameter in GNU Radio's Low Pass
Filter block) and $A_{dB}$ is the window attenuation from the table above. `firdes` then
rounds $N$ up to the next odd number so the filter has an exact integer group delay.

> **Worked example — the Lab 03 pre-filter.**
> $f_s = 2{,}000{,}000$, cutoff $= 100$ kHz, width $= 20$ kHz, Hamming ($A_{dB} = 53$):
> $$N = \frac{53 \times 2{,}000{,}000}{22 \times 20{,}000} = 240.9 \rightarrow 241 \text{ taps}$$
> At 2 MSPS that costs $241 \times 2 \times 10^6 \approx 4.8 \times 10^8$ multiply-accumulates
> per second. That is real CPU. Halve the transition width to 10 kHz and you get 481 taps —
> the cost **doubles**.

**Three rules of thumb that follow directly from the equation:**

1. Narrow transitions are expensive. Ask for the widest transition band the application
   tolerates.
2. Cost scales with the *input* sample rate. Filter as late (and as slowly) as you can — or
   better, decimate in stages.
3. A deeper window is cheaper than you think. Going Hamming → Blackman is only 1.4× the taps
   for 21 dB more rejection. Going 20 kHz → 10 kHz transition is 2× the taps for *nothing*.

### Verify it yourself

```bash
python3 -c "
from gnuradio.filter import firdes
from gnuradio.fft import window
t = firdes.low_pass(1.0, 2e6, 100e3, 20e3, window.WIN_HAMMING, 6.76)
print('taps:', len(t))
"
```

---

## Part 3 — Decimation, Interpolation, Resampling

### Decimation = filter, then throw away

To reduce the sample rate by an integer factor $M$:

1. **Lowpass filter** to $f_s / (2M)$ — this is mandatory, not optional.
2. Keep every $M$-th sample.

$$
y[n] = x[nM] \quad \text{(after filtering)}
$$

Skip step 1 and everything between $f_s/(2M)$ and $f_s/2$ folds into your band. Forever.

### The decimating-FIR trick

A naive implementation filters at the input rate and then discards $M-1$ out of every $M$
outputs — computing results you immediately throw away. A **decimating FIR** only computes
the outputs it keeps, cutting the work by exactly $M$:

$$
\text{MACs/s} = \frac{N \cdot f_s}{M}
$$

GNU Radio's Low Pass Filter block does this automatically when you set `decim > 1`. **Always
use the block's own `decim` parameter** rather than a separate Keep-1-in-N block.

### Interpolation = insert zeros, then filter

To increase the rate by $L$: insert $L-1$ zeros between samples, then lowpass at $f_s/(2L)$
with gain $L$. The zero-stuffing creates $L-1$ spectral images; the filter removes them.

### Rational resampling $L/M$

Arbitrary rate changes use interpolate-by-$L$, filter, decimate-by-$M$ — done in a single
polyphase structure so the zeros are never actually multiplied.

$$
f_{\text{out}} = f_{\text{in}} \cdot \frac{L}{M}
$$

Always reduce $L/M$ to lowest terms with `gcd`, because the internal filter runs at
$f_{\text{in}} \cdot L$.

> **Worked example — Lab 03's resampler.**
> $2{,}000{,}000 \to 384{,}000$. Ratio $= 384000/2000000 = 0.192 = 24/125$.
> $\gcd(24,125) = 1$, so `interp = 24`, `decim = 125`. Internal rate is
> $2 \times 10^6 \times 24 = 48$ MSPS — which is why polyphase (not literal zero-stuffing)
> matters so much.

**Handy helper:**

```bash
python3 -c "
from math import gcd
fin, fout = 2000000, 384000
g = gcd(int(fin), int(fout))
print(f'interp={int(fout)//g}  decim={int(fin)//g}')
"
```

### Choosing rates that divide nicely

Pick your chain so every stage is an integer or a small rational:

```
2,000,000  ──/125·24──▶  384,000  ──/8──▶  48,000   ✅ clean
2,000,000  ──────────▶   441,000  ─────▶   44,100   ⚠️  ratio 441/2000, big filters
```

**Design your rates backwards from the audio sink.** 48 kHz audio × 8 = 384 kHz quadrature
rate; 384 kHz × 125/24 = 2 MSPS at the radio. Everything falls out cleanly.

---

## Part 4 — Bandpass and Frequency-Translating Filters

### Bandpass from lowpass

Multiplying a lowpass impulse response by a cosine shifts its passband:

$$
h_{\text{BP}}[k] = 2 h_{\text{LP}}[k] \cos\!\left(2\pi \frac{f_{\text{center}}}{f_s} k\right)
$$

This is exactly how `firdes.band_pass()` works, and it is what Lab 04 uses to pull the 19 kHz
pilot out of the MPX signal.

### Frequency Xlating FIR Filter — the channelizer

This is the block that makes multi-channel receivers possible, and Lab 06 is built on it. It
performs three operations in one pass:

1. **Mix** the input down by $-f_{\text{offset}}$: $x[n] \cdot e^{-j 2\pi f_{\text{offset}} n / f_s}$
2. **Filter** with lowpass taps
3. **Decimate** by $M$

$$
y[n] = \sum_k h[k] \; x[nM - k] \; e^{-j 2\pi f_{\text{offset}} (nM-k)/f_s}
$$

The efficiency win: the mixer is folded into the taps, so it costs nothing extra, and the
whole thing runs at the **output** rate.

**Why this matters.** Tune the SDR once to the middle of a band, then select any channel
inside that band purely in software — instantly, with no hardware retune and no PLL settling
time. That is the essence of software-defined radio.

```
      2 MHz of spectrum from the SDR
   ─────────────────────────────────────
   │     ▲        ▲         ▲          │
   │  ch A     ch B      ch C          │
   └──┬────────┬─────────┬─────────────┘
      │        │         │
   xlating  xlating   xlating     ← three filters, one tuner
   filter   filter    filter
```

---

## Part 5 — IIR Filters (and the de-emphasis filter)

An **Infinite Impulse Response** filter feeds output back into itself:

$$
y[n] = \sum_{k=0}^{P} b_k x[n-k] - \sum_{k=1}^{Q} a_k y[n-k]
$$

IIR filters achieve a given selectivity with **far fewer** coefficients than FIR, but they
are not linear-phase and can be unstable. In this lab we use exactly one: the single-pole
de-emphasis filter.

The analog RC response $H(s) = \frac{1}{1 + s\tau}$ discretises (impulse invariance) to

$$
H(z) = \frac{\alpha}{1 - (1-\alpha)z^{-1}}, \qquad
\boxed{\alpha = 1 - e^{-T_s/\tau} = 1 - e^{-1/(f_s \tau)}}
$$

| $f_s$ | $\tau$ | $\alpha$ |
|---|---|---|
| 240 kHz | 50 μs | 0.0800 |
| 240 kHz | 75 μs | 0.0540 |
| 48 kHz | 50 μs | 0.3408 |
| 48 kHz | 75 μs | 0.2425 |

> ⚠️ **$\alpha$ depends on the sample rate.** If you change the rate at which de-emphasis is
> applied and keep the old $\alpha$, your treble will be wrong. This is a very common bug in
> home-made FM receivers.

```bash
python3 -c "
import math
for fs in (240000, 48000):
    for tau in (50e-6, 75e-6):
        print(f'fs={fs:>7}  tau={tau*1e6:>3.0f}us  alpha={1-math.exp(-1/(fs*tau)):.4f}')
"
```

---

## Part 6 — A Design Checklist

Before you wire up any new chain, fill in this table for every wire:

| # | Wire | Sample rate | Data type | Bandwidth present | Bandwidth wanted |
|---|---|---|---|---|---|
| 1 | SDR → LPF | 2 MSPS | complex | ±1 MHz | ±100 kHz |
| 2 | LPF → resamp | 2 MSPS | complex | ±100 kHz | — |
| 3 | resamp → demod | 384 kSPS | complex | ±100 kHz | ✅ fits |
| 4 | demod → audio | 48 kSPS | float | 0–15 kHz | ✅ fits |

Three questions per row:

1. **Does the wanted bandwidth fit inside ±(rate/2)?** If not, you will alias.
2. **Is there a filter before every rate reduction?** If not, you will alias.
3. **Does the data type match on both ends?** GRC catches this one for you; the other two it
   does not.

---

## 🧠 Self-Check

1. You sample at 500 kSPS complex. What total bandwidth do you see?
   **Answer:** 500 kHz, from −250 kHz to +250 kHz relative to the tuned frequency.

2. A 300 kHz tone is present when sampling at 240 kSPS. Where does it appear?
   **Answer:** $k = \operatorname{round}(300/240) = 1$, so at $300-240 = 60$ kHz.

3. Design a Hamming lowpass at $f_s = 384$ kHz with a 5 kHz transition. How many taps?
   **Answer:** $N = 53 \times 384{,}000 / (22 \times 5{,}000) = 185.0 \rightarrow 185$ taps.

4. Convert 1.92 MSPS to 48 kSPS with a rational resampler. What are interp and decim?
   **Answer:** $48000/1920000 = 1/40$, so `interp = 1`, `decim = 40`.

5. Why must the anti-alias filter come *before* the decimator?
   **Answer:** Decimation folds everything above the new Nyquist rate into the band
   irreversibly; once folded, the alias is arithmetically identical to a real signal.

6. You move de-emphasis from a 240 kHz wire to a 48 kHz wire and keep $\alpha = 0.08$. What
   happens?
   **Answer:** The corner frequency moves up by 5×, so the filter barely cuts treble — the
   audio sounds bright and hissy. You need $\alpha = 0.3411$ for 50 μs at 48 kHz.

---

**Next:** [Fundamentals 06 — Noise, SNR & Gain →](./06_noise_snr_and_gain.md)
