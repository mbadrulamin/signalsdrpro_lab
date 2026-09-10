# 🛩️ Fundamentals 07 — AM, SSB & Narrowband FM

> **Prerequisite:** FM Theory (Fundamentals 04), Noise & SNR (Fundamentals 06)
> **Time to read:** 40 minutes
> **Used by:** Lab 06

---

## Why This Chapter Exists

Fundamentals 04 taught you one modulation: wideband FM. That is a single point in a large
design space. This chapter fills in the rest of the **analog** space — AM, DSB, SSB, and
narrowband FM — because Lab 06 builds a receiver that demodulates *all* of them, and because
the interesting signals on the air are mostly not broadcast FM:

| Band | Mode | What's there |
|---|---|---|
| 118–137 MHz | **AM** | Aircraft ↔ tower voice |
| 144–148 MHz | **NBFM**, SSB | Amateur 2 m |
| 156–162 MHz | **NBFM** | Marine VHF |
| 162.400–162.550 MHz | **NBFM** | NOAA weather radio |
| 380–470 MHz | **NBFM** | Business, PMR446, amateur 70 cm |
| 3–30 MHz | **SSB**, AM, CW | Shortwave, amateur HF |

> ⚖️ **Legal note.** Receiving is legal in most countries, but *acting on*, recording, or
> retransmitting some of these (especially aircraft, marine distress, and any encrypted or
> public-safety traffic) is restricted, and rules vary a lot by jurisdiction. Check your local
> regulations. Everything in this lab is receive-only.

---

## Part 1 — Amplitude Modulation, Revisited

### The equation

$$
s_{AM}(t) = A_c \bigl[1 + m \cdot x(t)\bigr] \cos(2\pi f_c t)
$$

where $x(t)$ is the audio normalised to $[-1, +1]$ and $m$ is the **modulation index**.

### Spectrum

Expand with the product-to-sum identity. For a single tone $x(t) = \cos(2\pi f_m t)$:

$$
s_{AM}(t) = A_c\cos(2\pi f_c t)
+ \frac{A_c m}{2}\cos\bigl(2\pi (f_c\!+\!f_m)t\bigr)
+ \frac{A_c m}{2}\cos\bigl(2\pi (f_c\!-\!f_m)t\bigr)
$$

```
        carrier
           │
   LSB  ───┼───  USB
    ▁▁▂▃  ███  ▃▂▁▁
  ────────┼────────────  f
        f_c
   ◄── B = 2·f_m ──►
```

**Bandwidth:** $B_{AM} = 2 f_m$. Airband voice is limited to about 3 kHz, so an airband
channel is ~6–8 kHz wide (channels are spaced 25 kHz, or 8.33 kHz in Europe).

### Power efficiency — AM's fatal flaw

Total power splits between carrier and sidebands:

$$
P_{\text{total}} = \underbrace{\frac{A_c^2}{2}}_{\text{carrier}} + \underbrace{\frac{A_c^2 m^2}{4}}_{\text{both sidebands}}
$$

$$
\eta = \frac{P_{\text{sidebands}}}{P_{\text{total}}} = \frac{m^2}{2 + m^2}
$$

| $m$ | Efficiency | Comment |
|---|---|---|
| 0.5 | 11.1 % | Typical conservative broadcast |
| 1.0 | 33.3 % | **The theoretical maximum** |
| > 1.0 | — | **Overmodulation** — envelope goes negative, severe distortion |

At best, **two thirds of an AM transmitter's power carries no information at all.** The
carrier is pure overhead. That single fact motivates DSB-SC and SSB.

### Why airband still uses AM in 2026

Three genuinely good reasons, all about safety:

1. **No capture effect.** If two aircraft transmit at once, an FM receiver locks to the
   stronger and the weaker vanishes silently. An AM receiver plays *both*, producing an
   audible heterodyne whistle — the controller hears that something went wrong.
2. **Graceful degradation.** AM fades into noise smoothly. FM falls off a cliff at threshold.
3. **Simple, provable receivers.** An envelope detector is a diode and a capacitor. Certifying
   that is far cheaper than certifying a PLL.

### Demodulation method 1: envelope detection

$$
\hat{x}(t) = |s_{\text{baseband}}(t)| = \sqrt{I^2 + Q^2}
$$

In GNU Radio this is **Complex to Mag**, then remove the DC (the carrier) with a subtract or a
high-pass. Advantages: dead simple, no carrier recovery, immune to frequency offset.
Disadvantage: it is nonlinear, so noise and signal intermodulate — about 3 dB worse than
coherent detection at low SNR.

The block `analog_am_demod_cf` does envelope detection plus an audio lowpass in one step.

### Demodulation method 2: coherent detection

Multiply by a locally regenerated carrier of exactly the right frequency **and phase**:

$$
s(t)\cdot 2\cos(2\pi f_c t) = A_c[1 + m x(t)](1 + \cos(4\pi f_c t)) \xrightarrow{\text{LPF}} A_c[1 + m x(t)]
$$

3 dB better in noise, but it needs a PLL locked to the carrier — and a phase error $\phi$
costs you $\cos\phi$ in amplitude. Lab 06 uses envelope detection; Lab 07 uses coherent
detection for RDS, where there is no choice.

### Frequency offset in AM: it doesn't matter (much)

If your tuning is off by $\Delta f$, the envelope detector still works — the whole complex
baseband just rotates, and $|\cdot|$ is rotation-invariant. This is a real practical
advantage. A coherent detector, by contrast, produces a $\cos(2\pi \Delta f t)$ fade.

---

## Part 2 — DSB-SC and SSB

### DSB-SC: delete the carrier

$$
s_{DSB}(t) = x(t)\cos(2\pi f_c t)
$$

100 % of the power is now in the sidebands. The cost: an envelope detector no longer works,
because the envelope $|x(t)|$ loses the sign of $x(t)$. You **must** use coherent detection,
which means recovering a carrier that was deliberately not transmitted.

You have already met DSB-SC: the **L−R stereo subcarrier in Lab 04** is DSB-SC at 38 kHz, and
the 19 kHz pilot exists precisely to let you regenerate the suppressed carrier. **RDS in Lab
07 is DSB-SC too.** This is not an exotic mode — it is everywhere.

### SSB: delete one sideband as well

The two sidebands of a DSB signal are mirror images: they carry identical information. Throw
one away:

$$
s_{SSB}(t) = x(t)\cos(2\pi f_c t) \mp \hat{x}(t)\sin(2\pi f_c t)
$$

where $\hat{x}(t)$ is the **Hilbert transform** of $x(t)$ (every frequency component shifted
by −90°). Minus gives USB, plus gives LSB.

| Mode | Bandwidth | Power efficiency |
|---|---|---|
| AM | $2f_m$ | ≤ 33 % |
| DSB-SC | $2f_m$ | 100 % |
| **SSB** | $f_m$ | **100 %** |

SSB is the most spectrally efficient analog voice mode ever deployed: half the bandwidth and
three times the useful power of AM, i.e. roughly a **9 dB** advantage. This is why every HF
amateur and maritime voice link uses it.

### The SDR way to receive SSB

Here is the elegant part. In IQ, a Hilbert transform is unnecessary — **you just filter one
side of zero**:

```
  Complex baseband after tuning to the suppressed carrier:

     LSB          USB
   ▓▓▓▓▓▓░░░░│░░░░▓▓▓▓▓▓
  -3k     -300  +300   +3k     Hz

  For USB: bandpass +300 Hz … +3000 Hz  (asymmetric — only possible with complex signals!)
  For LSB: bandpass −3000 Hz … −300 Hz
```

Then take the real part. An asymmetric filter around DC is meaningless for a real signal but
perfectly natural for a complex one. This is one of the clearest demonstrations of why
Fundamentals 02 mattered.

---

## Part 3 — Narrowband FM

### Same equation, different deviation

$$
s_{FM}(t) = A\cos\!\left(2\pi f_c t + 2\pi \Delta f \int_0^t x(\tau)d\tau\right)
$$

The **modulation index** is what separates NBFM from WBFM:

$$
\boxed{\beta = \frac{\Delta f}{f_m}}
$$

| Mode | $\Delta f$ | $f_m$ | $\beta$ | Carson BW |
|---|---|---|---|---|
| **NBFM** (voice) | 5 kHz | 3 kHz | 1.67 | 16 kHz |
| **NBFM** (2.5 kHz dev) | 2.5 kHz | 3 kHz | 0.83 | 11 kHz |
| **WBFM** (broadcast) | 75 kHz | 15 kHz | 5.0 | 180 kHz |

Carson's rule, again: $B \approx 2(\Delta f + f_m) = 2 f_m(\beta + 1)$.

### Why $\beta$ decides everything

Recall from Fundamentals 06 that FM's noise advantage is

$$
G_{FM} \approx 20\log_{10}\beta + 4.8 \text{ dB}
$$

| Mode | $\beta$ | FM gain |
|---|---|---|
| NBFM | 1.67 | 9.2 dB |
| WBFM | 5.0 | 18.8 dB |

**WBFM buys ~10 dB more SNR by spending 11× the bandwidth.** Broadcasters have spectrum and
want fidelity; a handheld radio has neither. Neither choice is wrong — they optimise different
things. This trade is the central engineering decision in every communication system.

### Demodulating NBFM

Identical to WBFM — quadrature demod — but the gain constant differs. GNU Radio's
`analog_quadrature_demod_cf` computes:

$$
y[n] = \text{gain}\cdot\arg\bigl(s[n]\,s^*[n-1]\bigr)
$$

For the output to be the audio scaled to $\pm 1$, set:

$$
\boxed{\text{gain} = \frac{f_s}{2\pi \Delta f}}
$$

| $f_s$ | $\Delta f$ | gain |
|---|---|---|
| 48 kHz | 5 kHz | 1.528 |
| 384 kHz | 75 kHz | 0.815 |
| 240 kHz | 75 kHz | 0.509 |

> **The most common NBFM bug** is leaving the WBFM gain in place. The audio still works — FM
> demod is scale-invariant in *quality* — but it comes out ~15× too loud or too quiet, and
> people go looking for a broken filter instead of a wrong constant.

The block `analog_nbfm_rx` wraps quad demod + de-emphasis + audio filtering, taking
`max_dev` directly. Lab 06 uses it.

### CTCSS — the sub-audible tone squelch

Most NBFM services transmit a continuous low-frequency tone (67.0 – 250.3 Hz) below the voice
band, so a receiver can stay silent unless the *right* tone is present. If your NBFM audio has
a persistent low hum, that is CTCSS — high-pass at 300 Hz to remove it.

---

## Part 4 — Choosing a Demodulator: the decision table

| If the signal… | Mode | Demodulator | GNU Radio block |
|---|---|---|---|
| has a strong steady carrier and its envelope carries audio | AM | Envelope | `analog_am_demod_cf` |
| is symmetric with no visible carrier | DSB-SC | Coherent (PLL) | `analog_pll_carriertracking_cc` + multiply |
| occupies only one side and sounds like ducks when mistuned | SSB | Filter one side, take real | Freq-xlating filter + `blocks_complex_to_real` |
| has constant amplitude and ~12 kHz width | NBFM | Quadrature | `analog_nbfm_rx` |
| has constant amplitude and ~180 kHz width | WBFM | Quadrature | `analog_wfm_rcv` |

### Reading the waterfall

```
AM:      ▁▁▂▅█████▅▂▁▁     bright vertical carrier line, symmetric skirts
DSB-SC:  ▁▁▅███ ███▅▁▁     symmetric, gap in the middle
SSB:     ▁▁▁▁▁▁████▅▂▁     all energy on one side, ragged (speech-shaped)
NBFM:    ▁▂▅█████▅▂▁       constant-width block, no bright centre line
WBFM:    ▂▅███████████▅▂   ~200 kHz wide, visible pilot spike at ±19 kHz in MPX
```

---

## 🧠 Self-Check

1. An AM transmitter runs 100 W at $m = 0.8$. How much power carries information?
   **Answer:** $\eta = 0.64/(2+0.64) = 24.2\%$, so 24.2 W.

2. NBFM with $\Delta f = 5$ kHz and $f_m = 3$ kHz. Carson bandwidth?
   **Answer:** $2(5+3) = 16$ kHz.

3. You have a quadrature demod at $f_s = 96$ kHz for a $\Delta f = 5$ kHz NBFM signal. Gain?
   **Answer:** $96000/(2\pi \times 5000) = 3.056$.

4. Why does airband use AM, when FM would sound better?
   **Answer:** Simultaneous transmissions must both be audible — FM's capture effect would
   silently hide one aircraft. Safety beats fidelity.

5. Why can't an envelope detector demodulate DSB-SC?
   **Answer:** The envelope is $|x(t)|$, which loses the sign of $x(t)$ — every negative
   excursion is folded positive.

6. How do you receive USB in an SDR without a Hilbert transform?
   **Answer:** Tune to the suppressed carrier and bandpass only the positive-frequency side
   (+300 to +3000 Hz) of the complex baseband, then take the real part.

---

**Next:** [Fundamentals 08 — Digital Modulation →](./08_digital_modulation.md)
