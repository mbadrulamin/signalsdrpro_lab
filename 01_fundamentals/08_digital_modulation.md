# 💠 Fundamentals 08 — Digital Modulation

> **Prerequisite:** IQ Sampling (02), Sampling & Filters (05), Noise & SNR (06)
> **Time to read:** 55 minutes
> **Used by:** Lab 07, Lab 08, Lab 09

---

## Why This Chapter Exists

Everything so far has been **analog**: a continuous waveform in, a continuous waveform out.
From here on the signals carry **bits** — RDS (Lab 07), ADS-B (Lab 09), and the BPSK/QPSK link
you will build and measure in Lab 08.

Digital modulation is where SDR stops being a radio and starts being a computer. It is also
where the mathematics pays off most directly: you can *predict* the bit error rate of a link
from theory and then measure it and watch the two curves lie on top of each other. Lab 08 does
exactly that.

---

## Part 1 — Bits, Symbols, Baud

Three quantities people constantly confuse:

| Quantity | Symbol | Unit | Meaning |
|---|---|---|---|
| Bit rate | $R_b$ | bits/s | Information per second |
| Symbol rate | $R_s$ | baud | Waveform changes per second |
| Bits per symbol | $k$ | — | $k = \log_2 M$ for an $M$-ary constellation |

$$
\boxed{R_b = R_s \cdot k = R_s \log_2 M}
$$

| Scheme | $M$ | $k$ | 1000 baud gives |
|---|---|---|---|
| BPSK | 2 | 1 | 1 kbit/s |
| QPSK | 4 | 2 | 2 kbit/s |
| 8PSK | 8 | 3 | 3 kbit/s |
| 16QAM | 16 | 4 | 4 kbit/s |
| 256QAM | 256 | 8 | 8 kbit/s |

**Bandwidth is set by the symbol rate, not the bit rate.** Doubling $M$ doubles your data in
the same bandwidth — and costs SNR. That is the fundamental trade, and Shannon puts a hard
ceiling on it:

$$
C = B \log_2\!\left(1 + \frac{S}{N}\right) \quad \text{bits/s}
$$

### Samples per symbol

In a flowgraph, the third rate that matters is `sps`:

$$
f_s = R_s \cdot \text{sps}
$$

`sps = 2` is the minimum that satisfies Nyquist for the pulse shape; `sps = 4` to `8` gives
the timing recovery loop something to interpolate between and is the practical choice. Lab 08
uses `sps = 4`.

---

## Part 2 — The Constellation

A digital symbol is a **complex number**. Plot the set of allowed values on the I/Q plane and
you have the **constellation**.

### BPSK — two points on the real axis

$$
s_m \in \{+1, -1\}, \qquad k = 1
$$

```
        Q
        │
   ──●──┼──●──  I
    -1  │  +1
```

The two points are $180°$ apart — the maximum possible separation for a given power. BPSK is
therefore the most robust modulation there is, and it is what RDS and (in effect) ADS-B use.

### QPSK — four points

$$
s_m \in \left\{\tfrac{\pm 1 \pm j}{\sqrt 2}\right\}, \qquad k = 2
$$

```
        Q
    ●   │   ●
        │
  ──────┼──────  I
        │
    ●   │   ●
```

QPSK carries twice the data of BPSK **in the same bandwidth at the same $E_b/N_0$**. That
sounds free, and nearly is: QPSK is two independent BPSK signals on the I and Q axes.

### Gray coding

Adjacent constellation points must differ by exactly **one bit**. When noise causes an error,
it almost always moves the symbol to a *neighbour* — so one symbol error costs one bit error
instead of two.

```
  Gray-coded QPSK:          Naive binary:
      01 │ 00                   01 │ 00
    ─────┼─────               ─────┼─────
      11 │ 10                   11 │ 10
   neighbours differ         01↔10 differs in
   in 1 bit  ✅              2 bits  ❌
```

Gray coding is free and roughly halves the BER at practical SNRs. Always use it.

### Constellation summary

| Scheme | Points | Min distance $d_{\min}$ (unit avg power) | Robustness |
|---|---|---|---|
| BPSK | 2 | 2.000 | Best |
| QPSK | 4 | 1.414 | Excellent |
| 8PSK | 8 | 0.765 | Good |
| 16QAM | 16 | 0.632 | Moderate |
| 64QAM | 64 | 0.309 | Needs high SNR |

$d_{\min}$ is what noise has to cross to cause an error, so it *is* the robustness.

---

## Part 3 — Pulse Shaping

### The problem with square pulses

A rectangular pulse of duration $T$ has spectrum $\operatorname{sinc}(fT)$ — sidelobes falling
off at only 13 dB, extending forever. Transmit that and you splatter across your neighbours'
channels. Regulators will not allow it, and neither should you.

### The Nyquist ISI criterion

We need a pulse $p(t)$ that is **compact in frequency** but still has **zero value at every
other symbol instant**, so symbols do not smear into each other (inter-symbol interference):

$$
p(nT) = \begin{cases} 1 & n = 0 \\ 0 & n \neq 0 \end{cases}
$$

### Raised cosine

The classic solution, parameterised by **roll-off** $\alpha \in [0,1]$:

$$
P(f) = \begin{cases}
T & |f| \le \frac{1-\alpha}{2T} \\[4pt]
\frac{T}{2}\left[1 + \cos\!\left(\frac{\pi T}{\alpha}\left(|f| - \frac{1-\alpha}{2T}\right)\right)\right] & \frac{1-\alpha}{2T} < |f| \le \frac{1+\alpha}{2T} \\[4pt]
0 & \text{otherwise}
\end{cases}
$$

**Occupied bandwidth:**

$$
\boxed{B = R_s (1 + \alpha)}
$$

| $\alpha$ | Bandwidth | Time-domain behaviour |
|---|---|---|
| 0 | $R_s$ (Nyquist minimum) | Infinite ringing, brutal timing sensitivity |
| 0.2 | $1.2 R_s$ | Tight spectrum, still fussy |
| **0.35** | $1.35 R_s$ | **The standard compromise** |
| 1.0 | $2 R_s$ | Very forgiving timing, wasteful |

### Root raised cosine — why the filter is split in half

The optimal receiver for AWGN is a **matched filter**: correlate with the transmitted pulse
shape. So we put $\sqrt{P(f)}$ at the transmitter and $\sqrt{P(f)}$ at the receiver. Their
product is $P(f)$ — the full raised cosine, which satisfies the Nyquist criterion — *and* the
receiver filter is matched to the transmit pulse, which is optimal in noise.

$$
\underbrace{\text{RRC}}_{\text{TX}} \times \underbrace{\text{RRC}}_{\text{RX}} = \underbrace{\text{RC}}_{\text{zero ISI}}
$$

This is the single most elegant idea in digital communications: one filter design solves the
spectral-containment problem and the noise-optimality problem simultaneously.

In GNU Radio:

```python
from gnuradio.filter import firdes
taps = firdes.root_raised_cosine(
    1.0,          # gain
    samp_rate,    # sampling rate
    symbol_rate,  # symbol rate
    0.35,         # excess bandwidth (roll-off alpha)
    11 * sps)     # number of taps
```

**Rule:** use `11 * sps` taps as a starting point. Fewer truncates the pulse and reintroduces
ISI; many more just costs CPU.

---

## Part 4 — Bit Error Rate

### The Q function

$$
Q(x) = \frac{1}{\sqrt{2\pi}}\int_x^{\infty} e^{-t^2/2}\,dt = \frac{1}{2}\operatorname{erfc}\!\left(\frac{x}{\sqrt 2}\right)
$$

$Q(x)$ is the probability that a zero-mean unit-variance Gaussian exceeds $x$ — exactly the
probability that noise pushes a symbol across the decision boundary.

### $E_b/N_0$ — the honest way to compare systems

$$
\frac{E_b}{N_0} = \frac{\text{energy per bit}}{\text{noise power spectral density}}
$$

Related to SNR by:

$$
\boxed{\frac{E_b}{N_0} = \text{SNR} \cdot \frac{B}{R_b}}
$$

Compare systems at equal $E_b/N_0$, never equal SNR — otherwise you are just rewarding
whichever one uses more bandwidth.

### The BER equations

$$
\text{BPSK: } \quad P_b = Q\!\left(\sqrt{\frac{2E_b}{N_0}}\right)
$$

$$
\text{QPSK (Gray): } \quad P_b = Q\!\left(\sqrt{\frac{2E_b}{N_0}}\right)
$$

$$
\text{$M$-PSK, } M \ge 4: \quad P_b \approx \frac{2}{\log_2 M}\, Q\!\left(\sqrt{\frac{2E_b\log_2 M}{N_0}}\sin\frac{\pi}{M}\right)
$$

$$
\text{$M$-QAM: } \quad P_b \approx \frac{4}{\log_2 M}\left(1 - \frac{1}{\sqrt M}\right) Q\!\left(\sqrt{\frac{3\log_2 M}{M-1}\cdot\frac{E_b}{N_0}}\right)
$$

**BPSK and QPSK have identical BER curves.** QPSK gets twice the throughput for free — in
$E_b/N_0$ terms. It pays for it in sensitivity to phase error, not in noise performance.

### The table to know by heart

| $E_b/N_0$ (dB) | BPSK/QPSK BER |
|---|---|
| 0 | 7.86 × 10⁻² |
| 2 | 3.75 × 10⁻² |
| 4 | 1.25 × 10⁻² |
| 6 | 2.39 × 10⁻³ |
| 8 | 1.91 × 10⁻⁴ |
| 10 | 3.87 × 10⁻⁶ |
| 12 | 9.01 × 10⁻⁹ |

Note how steep this is: **2 dB more signal buys you two orders of magnitude fewer errors** in
the interesting region. Digital links have a "cliff" — they work, and then abruptly they do
not. Lab 08 measures this cliff on your own machine.

```bash
python3 -c "
from math import erfc, sqrt, log10
for ebno_db in range(0, 13, 2):
    e = 10**(ebno_db/10)
    ber = 0.5*erfc(sqrt(e))
    print(f'{ebno_db:>3} dB   BER = {ber:.3e}')
"
```

### Setting noise in a simulation

GNU Radio's Channel Model and Noise Source take a **noise voltage** $A$. Measured empirically,
`analog.noise_source_c(GR_GAUSSIAN, A)` produces complex noise whose **total** variance is
$A^2$ — that is, $A^2/2$ in each of I and Q:

```bash
python3 -c "
from gnuradio import gr, blocks, analog
import numpy as np
tb = gr.top_block()
src = analog.noise_source_c(analog.GR_GAUSSIAN, 1.0, 0)
hd, sk = blocks.head(gr.sizeof_gr_complex, 200000), blocks.vector_sink_c()
tb.connect(src, hd, sk); tb.run()
d = np.array(sk.data())
print('total var %.3f   I var %.3f   Q var %.3f' % (np.var(d), np.var(d.real), np.var(d.imag)))
"
```

So to hit a target $E_b/N_0$ with unit-power transmitted samples:

$$
\boxed{A = \sqrt{\frac{\text{sps}}{k \cdot 10^{E_b/N_0 \,/\, 10}}}}
$$

The `sps` appears because oversampling spreads the same symbol energy over more samples, so
each sample carries $1/\text{sps}$ of a symbol's energy while the noise variance per sample
stays put. **There is no extra factor of 2** — GNU Radio's `noise_voltage` is already the
total complex standard deviation, not the per-component one. Getting this wrong by a factor of
2 shifts your whole BER curve by 3 dB, which looks exactly like a broken receiver.

Lab 07 uses this formula and plots the measured curve against the theoretical one — if the
calibration were wrong, the two curves would not lie on top of each other.

---

## Part 5 — Differential Encoding

### The phase ambiguity problem

A carrier recovery loop (Fundamentals 09) locks the frequency, but it **cannot know the
absolute phase**. For BPSK, the loop is equally happy locked at $0°$ or $180°$ — so your
whole bitstream may come out inverted, and you will not be told.

### The fix: encode in *transitions*

$$
d[n] = d[n-1] \oplus b[n] \quad \text{(encoder)}
$$
$$
\hat b[n] = d[n] \oplus d[n-1] \quad \text{(decoder)}
$$

If the receiver inverts every $d[n]$, the XOR of two consecutive inverted bits is unchanged.
**The ambiguity cancels.**

Cost: about **3 dB** at low SNR, because one channel error now corrupts two decoded bits.

> RDS (Lab 07) uses exactly this scheme, which is why the Lab 07 flowgraph has a Differential
> Decoder block right after the slicer, and why Lab 08 lets you toggle differential encoding
> on and off and watch the BER curve shift.

---

## Part 6 — On-Off Keying and PPM

Not all digital modulation is phase-based. Two amplitude schemes matter for Lab 09.

### OOK / ASK

The carrier is simply switched on and off. Trivial to generate, trivial to detect (envelope
detector), and roughly 3 dB worse than BPSK — but when your transmitter is a $0.10 chip or a
1970s aircraft transponder, that is the right trade.

### Pulse Position Modulation (PPM)

The **position** of a pulse within a fixed slot carries the bit:

```
  Mode S / ADS-B, 1 µs per bit:

  bit = 1:   ███░░░      pulse in first half
  bit = 0:   ░░░███      pulse in second half
```

PPM's great virtue: **every bit contains exactly one pulse**, so the average power is constant
and the receiver can recover timing from the data itself with no preamble-free ambiguity. Its
cost is bandwidth — a 1 Mbit/s PPM signal occupies several MHz.

Detection is a two-sample comparison per bit:

$$
\hat{b}[n] = \begin{cases} 1 & |r(t_n)| > |r(t_n + T/2)| \\ 0 & \text{otherwise}\end{cases}
$$

No carrier recovery, no phase tracking, no PLL. Lab 09 implements this in about fifteen lines
of NumPy.

---

## 🧠 Self-Check

1. A QPSK link runs at 2400 baud with $\alpha = 0.35$. Bit rate and bandwidth?
   **Answer:** $R_b = 2400 \times 2 = 4800$ bit/s; $B = 2400 \times 1.35 = 3240$ Hz.

2. What BER does BPSK give at $E_b/N_0 = 7$ dB?
   **Answer:** $Q(\sqrt{2 \times 10^{0.7}}) = Q(3.16) \approx 7.7 \times 10^{-4}$.

3. Why do BPSK and QPSK have the same BER curve, yet QPSK sends twice the data?
   **Answer:** QPSK is two orthogonal BPSK channels (I and Q). Each carries half the bits at
   half the power, so the per-bit energy-to-noise ratio is unchanged.

4. Why split the raised cosine into two root-raised-cosine filters?
   **Answer:** So the receiver filter is matched to the transmit pulse (optimal SNR) while the
   *cascade* still satisfies the Nyquist zero-ISI criterion.

5. What does differential encoding cost, and what does it buy?
   **Answer:** Costs ~3 dB (errors come in pairs); buys immunity to the carrier recovery
   loop's 180° phase ambiguity.

6. Your constellation plot shows a slowly rotating ring instead of dots. Diagnosis?
   **Answer:** Uncorrected frequency offset — the carrier recovery loop is not locked. See
   Fundamentals 09.

---

**Next:** [Fundamentals 09 — Synchronization →](./09_synchronization.md)
