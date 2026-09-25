# 💠 Fundamentals 08 — Digital Modulation

> **What you will learn:** how radios send **bits**: bits vs symbols; constellations (BPSK,
> QPSK, QAM); Gray coding; pulse shaping and the root-raised-cosine filter; **bit error rate**
> and Eb/N0; how to set noise correctly in a simulation; differential encoding; and pulse
> position modulation (PPM).
> **Before this:** [Fundamentals 02 — IQ](./02_iq_sampling.md),
> [05 — Filters](./05_sampling_and_filters.md), [06 — Noise](./06_noise_snr_and_gain.md).
> **Time:** about 55 minutes. **Used by:** Labs 07, 08, 09.

---

## Why this chapter exists

Until now, every signal was **analog**: a smooth wave in, a smooth wave out. From Lab 07 on,
the signals carry **bits**:

- **Lab 07** — a BPSK link you build and measure, in simulation
- **Lab 08** — RDS, the data inside FM broadcasts
- **Lab 09** — ADS-B, the messages from aircraft

Digital radio has one big advantage for learning: you can **predict** how many bits a link will
get wrong, then **measure** it, and see the two agree. Lab 07 does exactly that.

---

## Part 1 — Bits, symbols and baud

Three things that people often mix up:

| Name | Symbol | Unit | Meaning |
|---|---|---|---|
| **Bit rate** | $R_b$ | bits per second | how much information per second |
| **Symbol rate** | $R_s$ | **baud** (symbols per second) | how many times per second the signal changes |
| **Bits per symbol** | $k$ | — | how many bits each symbol carries |

A **symbol** is one "mark" the transmitter sends. If there are *M* possible symbols, each one
carries *k* = log₂ *M* bits:

$$
\boxed{R_b = R_s \times k}
$$

| Scheme | Possible symbols (M) | Bits each (k) | 1000 baud gives |
|---|---|---|---|
| BPSK | 2 | 1 | 1 kbit/s |
| QPSK | 4 | 2 | 2 kbit/s |
| 8PSK | 8 | 3 | 3 kbit/s |
| 16QAM | 16 | 4 | 4 kbit/s |
| 256QAM | 256 | 8 | 8 kbit/s |

**The bandwidth depends on the symbol rate, not the bit rate.** So more points per symbol means
more data in the same bandwidth — but the points are closer together, so you need a cleaner
signal. That is the basic trade. **Shannon's limit** sets the absolute maximum any system can
reach:

$$
C = B \log_2\!\left(1 + \frac{S}{N}\right) \quad \text{bits per second}
$$

### Samples per symbol (sps)

In a flowgraph there is a third rate: **samples per symbol**, `sps`.

$$
\text{sample rate} = R_s \times \text{sps}
$$

`sps = 2` is the minimum. `sps = 4` to `8` is usual, because it gives the timing-recovery block
enough samples to work with. Lab 07 uses `sps = 4`.

---

## Part 2 — The constellation

Each symbol is one **IQ point** ([Fundamentals 02](./02_iq_sampling.md)). Draw all the allowed
points on the I/Q graph, and you have the **constellation**.

### BPSK — two points

```
        Q
        │
   ──●──┼──●──  I
    -1  │  +1
```

Two points, as far apart as possible (180°). **BPSK** (binary phase-shift keying) is the most
robust modulation there is. RDS (Lab 08) uses it.

### QPSK — four points

```
        Q
    ●   │   ●
        │
  ──────┼──────  I
        │
    ●   │   ●
```

**QPSK** carries **twice** the data of BPSK in the same bandwidth, with the **same error rate
per bit**. How? It is really two BPSK signals at once: one on I, one on Q.

### Gray coding

Give **neighbouring** points labels that differ by only **one** bit. Noise usually pushes a
symbol to a *neighbour*, so a symbol error then costs only one wrong bit, not two.

```
  Gray-coded QPSK:          Plain binary:
      01 │ 00                   01 │ 00
    ─────┼─────               ─────┼─────
      11 │ 10                   11 │ 10
   neighbours differ         01 and 10 are neighbours
   in 1 bit  ✅              but differ in 2 bits  ❌
```

Gray coding costs nothing and roughly halves the errors. Always use it.

### How robust is each scheme?

The important number is the **distance between the closest two points** (d_min, for the same
average power). Noise must push a symbol that far to cause an error.

| Scheme | Points | Closest distance | Robustness |
|---|---|---|---|
| BPSK | 2 | 2.000 | best |
| QPSK | 4 | 1.414 | excellent |
| 8PSK | 8 | 0.765 | good |
| 16QAM | 16 | 0.632 | medium |
| 64QAM | 64 | 0.309 | needs a very clean signal |

---

## Part 3 — Pulse shaping

### Square pulses are bad neighbours

If you switch between symbols instantly (square pulses), the signal spreads far to both sides
in frequency, and splashes into neighbouring channels. That is not allowed.

### What we need

A pulse that:

1. is **compact in frequency** (does not splash), and
2. is exactly **zero at every other symbol's sampling moment** — so symbols do not blur into
   each other. That blurring is called **ISI** (inter-symbol interference).

### The raised cosine, and its roll-off α

The standard answer is the **raised-cosine** pulse. Its **roll-off** α (0 to 1) sets how
gently its spectrum falls off at the edges. The signal's width is:

$$
\boxed{B = R_s \, (1 + \alpha)}
$$

| α | Width | Behaviour |
|---|---|---|
| 0 | $R_s$ (the minimum possible) | rings forever; timing must be perfect |
| 0.2 | $1.2\,R_s$ | narrow, still fussy |
| **0.35** | $1.35\,R_s$ | **the usual compromise** (Lab 07) |
| 1.0 | $2\,R_s$ | very forgiving, but wide |

<details>
<summary><b>Going deeper:</b> the raised-cosine spectrum</summary>

$$
P(f) = \begin{cases}
T & |f| \le \frac{1-\alpha}{2T} \\[4pt]
\frac{T}{2}\left[1 + \cos\!\left(\frac{\pi T}{\alpha}\left(|f| - \frac{1-\alpha}{2T}\right)\right)\right] & \frac{1-\alpha}{2T} < |f| \le \frac{1+\alpha}{2T} \\[4pt]
0 & \text{otherwise}
\end{cases}
$$
</details>

### Why the filter is split in two: root raised cosine

The best receiver in noise uses a **matched filter**: a filter shaped like the transmitted
pulse. So we split the raised cosine in two equal halves, called **root raised cosine (RRC)**:
one at the transmitter, one at the receiver.

$$
\underbrace{\text{RRC}}_{\text{transmitter}} \times \underbrace{\text{RRC}}_{\text{receiver}} = \underbrace{\text{raised cosine}}_{\text{no ISI}}
$$

One design solves two problems at once: the signal stays narrow, **and** the receiver is the
best possible in noise.

In GNU Radio:

```python
from gnuradio.filter import firdes
taps = firdes.root_raised_cosine(
    1.0,          # gain
    samp_rate,    # sample rate
    symbol_rate,  # symbol rate
    0.35,         # roll-off (alpha)
    11 * sps)     # number of taps
```

**Rule:** start with `11 * sps` taps. Fewer cuts the pulse short and brings ISI back. More only
costs CPU.

---

## Part 4 — Bit error rate (BER)

### Eb/N0 — the fair way to compare

**Eb/N0** is the energy per bit (E_b) compared with the noise density (N₀), in dB. It is related
to SNR by:

$$
\boxed{\frac{E_b}{N_0} = \text{SNR} \times \frac{\text{bandwidth}}{\text{bit rate}}}
$$

Always compare systems at the **same Eb/N0**, not the same SNR. SNR depends on the bandwidth you
measure in, so it rewards whichever system uses more bandwidth.

### The BER of BPSK and QPSK

$$
P_b = Q\!\left(\sqrt{\frac{2E_b}{N_0}}\right)
$$

**Q**(*x*) is the chance that random noise (Gaussian) is bigger than *x* — exactly the chance that
noise pushes a symbol across to the wrong side. **BPSK and QPSK have the same curve.**

### The numbers to remember

| Eb/N0 | BPSK / QPSK BER |
|---|---|
| 0 dB | 7.86 × 10⁻² |
| 2 dB | 3.75 × 10⁻² |
| 4 dB | 1.25 × 10⁻² |
| 6 dB | 2.39 × 10⁻³ |
| 8 dB | 1.91 × 10⁻⁴ |
| 10 dB | 3.87 × 10⁻⁶ |
| 12 dB | 9.01 × 10⁻⁹ |

Look how steep it is: from 8 to 10 dB, the errors fall about **50 times**. Digital links have a
**cliff**: they work well, and then suddenly they don't. Lab 07 measures this cliff.

Calculate it yourself:

```bash
python3 -c "
from math import erfc, sqrt
for ebno_db in range(0, 13, 2):
    e = 10**(ebno_db/10)
    print(f'{ebno_db:>3} dB   BER = {0.5*erfc(sqrt(e)):.3e}')"
```

<details>
<summary><b>Going deeper:</b> Q(x), and the BER of M-PSK and M-QAM</summary>

$$
Q(x) = \frac{1}{\sqrt{2\pi}}\int_x^{\infty} e^{-t^2/2}\,dt = \tfrac{1}{2}\operatorname{erfc}\!\left(\frac{x}{\sqrt 2}\right)
$$

$$
\text{M-PSK } (M \ge 4): \quad P_b \approx \frac{2}{\log_2 M}\, Q\!\left(\sqrt{\frac{2E_b\log_2 M}{N_0}}\sin\frac{\pi}{M}\right)
$$

$$
\text{M-QAM}: \quad P_b \approx \frac{4}{\log_2 M}\left(1 - \frac{1}{\sqrt M}\right) Q\!\left(\sqrt{\frac{3\log_2 M}{M-1}\cdot\frac{E_b}{N_0}}\right)
$$
</details>

### Setting the noise correctly in a simulation

GNU Radio's **Channel Model** and **Noise Source** take a **noise voltage** *A*. We measured it:
*A* is the **total** noise amplitude — *A*²/2 goes on I and *A*²/2 on Q. Check it yourself:

```bash
python3 -c "
from gnuradio import gr, blocks, analog
import numpy as np
tb = gr.top_block()
src = analog.noise_source_c(analog.GR_GAUSSIAN, 1.0, 0)
hd, sk = blocks.head(gr.sizeof_gr_complex, 200000), blocks.vector_sink_c()
tb.connect(src, hd, sk); tb.run()
d = np.array(sk.data())
print('total var %.3f   I var %.3f   Q var %.3f' % (np.var(d), np.var(d.real), np.var(d.imag)))"
```

✅ about `total var 1.000   I var 0.500   Q var 0.500`.

So, for a transmitted signal with an average power of 1, the noise voltage for a chosen Eb/N0 is:

$$
\boxed{A = \sqrt{\frac{\text{sps}}{k \times 10^{(E_b/N_0)/10}}}}
$$

Why `sps`? Each symbol's energy is spread over `sps` samples, but the noise per sample stays the
same. **There is no extra factor of 2.** Get it wrong by 2, and the whole BER curve moves by
3 dB — which looks exactly like a broken receiver. Lab 07 uses this formula, and its measured
BER lands on the theory curve.

---

## Part 5 — Differential encoding

### The problem: upside down

The receiver's carrier-recovery loop ([Fundamentals 09](./09_synchronization.md)) finds the
frequency, but **cannot know the absolute phase**. For BPSK it is equally happy locked the right
way up or **upside down** (180° off). Upside down, every bit is inverted — and nothing tells you.

### The fix: send the changes

Send whether each bit **changed**, not the bit itself:

$$
d[n] = d[n-1] \oplus b[n] \quad \text{(transmitter)} \qquad
\hat b[n] = d[n] \oplus d[n-1] \quad \text{(receiver)}
$$

(⊕ is XOR: 1 if the two bits differ, 0 if they are the same.)

If the receiver is upside down, **every** *d* is inverted — but whether two neighbours differ does
not change. **The problem cancels out.**

**The cost:** one wrong symbol now spoils **two** bits, so the BER roughly **doubles**. In signal
terms that is small: about **0.5 dB** at a BER of 10⁻⁴ (0.3–1.1 dB, depending on the level).
RDS (Lab 08) uses differential encoding, and Lab 07 lets you switch it off to see the difference.

---

## Part 6 — On-off keying and PPM

Not all digital modulation uses phase. Two simple kinds matter for Lab 09.

### OOK — on-off keying

The carrier is simply switched **on** for 1 and **off** for 0. Easy to make, easy to receive (just
measure the size). It needs about 3 dB more average power than BPSK. For a very cheap chip, or a
1970s aircraft transponder design, that is a good trade.

### PPM — pulse position modulation

The **position** of a pulse inside each bit period carries the bit:

```
  ADS-B (Mode S), 1 µs per bit:

  bit = 1:   ███░░░      pulse in the first half
  bit = 0:   ░░░███      pulse in the second half
```

Its big advantage: **every bit has exactly one pulse**. The average power is constant, and the
receiver never loses track of the timing. The cost is bandwidth: a 1 Mbit/s PPM signal is several
MHz wide.

Decoding is one comparison per bit: **is the first half or the second half stronger?** No carrier
recovery, no PLL. Lab 09 does it in about fifteen lines of NumPy.

---

## ✅ Summary

- **Bit rate = symbol rate × bits per symbol.** Bandwidth depends on the **symbol** rate.
- A **constellation** shows the allowed IQ points. More points = more data, but needs a cleaner
  signal. Use **Gray coding**.
- **RRC at both ends** gives a narrow signal, no ISI, and the best receiver in noise.
  Width = *R*ₛ(1 + α).
- Compare systems by **Eb/N0**. BPSK and QPSK: BER = Q(√(2 Eb/N0)). There is a **cliff**.
- GNU Radio's noise voltage is the **total** complex amplitude: *A* = √(sps / (k·10^(Eb/N0/10))).
- **Differential encoding** removes the upside-down problem for about 0.5 dB.
- **PPM** (ADS-B) needs no carrier recovery at all.

## 🧠 Check yourself

1. A QPSK link runs at 2400 baud with α = 0.35. What is its bit rate and width?
   <details><summary>Answer</summary>2400 × 2 = 4800 bit/s; 2400 × 1.35 = 3240 Hz.</details>
2. What BER does BPSK give at Eb/N0 = 7 dB?
   <details><summary>Answer</summary>Q(√(2 × 10^0.7)) = Q(3.17) ≈ 7.7 × 10⁻⁴.</details>
3. BPSK and QPSK have the same BER curve, but QPSK sends twice the data. How?
   <details><summary>Answer</summary>QPSK is two BPSK signals at once (on I and on Q). Each
   carries half the bits with half the power, so the energy per bit is the same.</details>
4. Why split the raised cosine into two RRC filters?
   <details><summary>Answer</summary>So the receiver's filter matches the transmitted pulse
   (best in noise), while the two together still give no ISI.</details>
5. What does differential encoding cost, and what does it buy?
   <details><summary>Answer</summary>It doubles the BER (about 0.5 dB of signal at BER 10⁻⁴).
   It removes the 180° upside-down problem.</details>
6. Your constellation shows a slowly turning ring instead of dots. What is wrong?
   <details><summary>Answer</summary>A frequency error that nothing is correcting: the carrier
   recovery loop is not locked. See Fundamentals 09.</details>

**Next:** [Fundamentals 09 — Synchronisation →](./09_synchronization.md)
