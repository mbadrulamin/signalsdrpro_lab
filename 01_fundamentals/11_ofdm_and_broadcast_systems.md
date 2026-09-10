# 🌐 Fundamentals 11 — OFDM & Modern Broadcast Systems

> **Prerequisite:** Digital Modulation (08), Synchronization (09), Error Detection (10)
> **Time to read:** 55 minutes
> **Used by:** Lab 10

---

## Why This Chapter Exists

Every digital signal in this repository so far has been **single-carrier**: one constellation,
one symbol at a time, at one frequency. RDS sends 1187.5 symbols per second on one subcarrier.
ADS-B sends a million pulses per second on one carrier. Lab 07's BPSK link sends 100,000.

Every modern broadcast and cellular system does something completely different. Wi-Fi, LTE, 5G,
DAB, DVB-T/T2, and Meteor's successors all use **OFDM** — thousands of carriers at once, each
one crawling along at a few hundred symbols per second.

This chapter explains why that inversion is not just an option but a necessity, and it is the
theory behind [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md).

---

## Part 1 — The Problem OFDM Solves

### Multipath, and why speed makes it worse

A transmitted signal reaches you by several paths: direct, plus reflections off buildings, hills
and aircraft. Each has a different delay.

```
    TX ─────────────────────────▶ RX      direct,       0 µs
       ╲                        ╱
        ╲──── building ────────╱          reflected,   +3 µs
         ╲                    ╱
          ╲──── hillside ────╱             reflected,  +12 µs
```

The channel is therefore a filter with an impulse response several microseconds long:

$$
y(t) = \sum_i a_i \, x(t - \tau_i)
$$

Now consider what that does to a single-carrier link at symbol period $T_s$:

| Symbol rate | $T_s$ | 12 µs echo spans |
|---|---|---|
| 1 kBaud | 1000 µs | 1.2 % of a symbol — harmless |
| 100 kBaud | 10 µs | **1.2 symbols** — serious ISI |
| 10 MBaud | 0.1 µs | **120 symbols** — catastrophic |

**The faster you send, the more symbols an echo smears across.** A 20 Mbit/s single-carrier
terrestrial TV signal would need an equaliser spanning hundreds of taps, adapting continuously,
and it would still fail whenever the channel changed.

### The inversion

OFDM's answer is to refuse the premise. Instead of one carrier at 10 MBaud, use **1000 carriers
at 10 kBaud each**. The total throughput is identical, but each symbol is now 100 µs long, and a
12 µs echo occupies 12 % of it instead of 120 symbols of it.

$$
\boxed{\text{Split the data across } N \text{ carriers} \Rightarrow \text{symbol period} \times N}
$$

That is the whole idea. Everything else is engineering to make it practical.

---

## Part 2 — How OFDM Works

### The orthogonality condition

Put $N$ carriers at spacing $\Delta f$ and transmit for a duration $T_u$. The transmitted
symbol is

$$
s(t) = \sum_{k=0}^{N-1} X_k \, e^{\,j 2\pi k \Delta f\, t}, \qquad 0 \le t < T_u
$$

The carriers do not interfere with each other **if and only if**

$$
\boxed{\Delta f = \frac{1}{T_u}}
$$

Because then, for $k \neq l$:

$$
\int_0^{T_u} e^{\,j2\pi k \Delta f t}\, e^{-j2\pi l \Delta f t}\, dt
= \int_0^{T_u} e^{\,j2\pi (k-l) t / T_u}\, dt = 0
$$

an exact integer number of cycles, integrating to zero. The carriers **overlap in frequency**
and are still perfectly separable. That is why OFDM is spectrally efficient: no guard bands
between carriers.

```
   Single carrier              OFDM: carriers overlap, still orthogonal
                                each peak sits on its neighbours' nulls
        ╱▔▔▔╲                    ╱╲  ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
       ╱     ╲                  ╱  ╳╱  ╳╱  ╳╱  ╳╱  ╳╱  ╲
   ───╱───────╲───          ───╱──╱─╲──╱─╲──╱─╲──╱─╲───╲───
```

### The IFFT is the modulator

Sample $s(t)$ at $N$ points and the sum becomes exactly an inverse DFT:

$$
x[n] = \frac{1}{N}\sum_{k=0}^{N-1} X_k\, e^{\,j 2\pi k n / N}
$$

**This is the reason OFDM took over.** Generating a thousand carriers would need a thousand
oscillators and a thousand mixers. Instead it is *one FFT*, which costs $O(N \log N)$. The
receiver undoes it with a forward FFT. A 1970s idea became practical the moment DSP hardware
could run an FFT in real time, and it has dominated ever since.

| | Single carrier | OFDM |
|---|---|---|
| Modulator | mixer + pulse shaping | **IFFT** |
| Demodulator | matched filter + equaliser | **FFT** + one complex multiply per carrier |
| Multipath handling | long adaptive equaliser | cyclic prefix (below) |
| Cost | $O(\text{taps})$ per symbol | $O(\log N)$ per carrier |

---

## Part 3 — The Cyclic Prefix: the Crucial Trick

Orthogonality holds only over an exact integer number of cycles. A delayed echo breaks that —
it drags a fragment of the *previous* symbol into the integration window, and every carrier
leaks into every other.

The fix is beautiful. **Copy the last $N_{cp}$ samples of the symbol and paste them in front:**

```
        ┌──────── useful part, N samples ────────┐
        │                                        │
   ┌────┴────┐                              ┌────┴────┐
   │  copy   │                              │  last   │
   │ of last │   ← this is the guard →      │  N_cp   │
   │  N_cp   │                              │ samples │
   └─────────┴────────────────────────────────────────┘
    N_cp                    N
   ◄─── Tg ──►◄────────── Tu ──────────►
   ◄──────────── Ts = Tg + Tu ─────────►
```

Two things happen at once:

1. **Any echo delayed by less than $T_g$ still sees a complete cycle** of every carrier inside
   the integration window, so orthogonality survives.
2. Linear convolution with the channel becomes **circular** convolution, and circular
   convolution in time is plain multiplication in the DFT domain:

$$
\boxed{Y_k = H_k X_k + N_k}
$$

That is the payoff. **Equalising a multipath channel becomes one complex division per
carrier** — $\hat{X}_k = Y_k / H_k$ — instead of an adaptive filter with hundreds of taps.

### The price, and the trade

The cyclic prefix carries no new information. It costs:

$$
\text{efficiency} = \frac{T_u}{T_u + T_g} = \frac{1}{1 + \text{GI}}
$$

| Guard interval | Overhead | Max echo delay ($T_u = 112$ µs) | Path difference |
|---|---|---|---|
| 1/32 | 3.1 % | 3.5 µs | 1.05 km |
| 1/16 | 5.9 % | 7.0 µs | 2.1 km |
| **1/8** | **11.1 %** | **14 µs** | **4.2 km** |
| 1/4 | 20.0 % | 28 µs | 8.4 km |

Longer guard = more multipath immunity = less throughput. That single slider is the central
design decision in every OFDM system.

### Single-frequency networks — the spectacular consequence

If the guard interval is longer than the delay spread, the receiver cannot tell a *reflection*
from a *second transmitter*. So you can run **every transmitter in a country on the same
frequency**, and a receiver midway between them treats the further one as a harmless echo.

For DVB-T2 with a 32K FFT at 8 MHz:

$$
T_u = \frac{32768}{9.142857\times10^6} = 3.584\ \text{ms}, \qquad
T_g = \frac{T_u}{8} = 448\ \mu\text{s}
$$

$$
d_{\max} = c\, T_g = 3\times10^8 \times 448\times10^{-6} = \mathbf{134\ km}
$$

Transmitters 134 km apart, same frequency, constructively adding. That is why European DTT uses
one channel per multiplex nationwide, where the old analog system needed a different frequency
in every town. **OFDM did not just improve terrestrial TV; it changed how spectrum is planned.**

---

## Part 4 — Pilots

The receiver needs $H_k$ to equalise. It gets it from **pilots**: carriers whose value is known
in advance, at a boosted amplitude.

| Pilot type | Purpose |
|---|---|
| **Scattered** | Move in a pattern across carriers and symbols; interpolate between them to estimate $H_k$ everywhere |
| **Continual** | Same carriers every symbol; used for fine frequency and phase tracking |
| **Edge** | At the band edges, so interpolation does not have to extrapolate |
| **P2 / preamble** | Carry the L1 signalling that says how everything else is configured |

```
   carrier ─────────────────────────────────────▶
 s  ● · · · ● · · · ● · · · ● · · · ● · · ·      ● = scattered pilot
 y  · · ● · · · ● · · · ● · · · ● · · · ● ·      · = data cell
 m  · · · · ● · · · ● · · · ● · · · ● · · ·
 b  · · · · · · ● · · · ● · · · ● · · · ● ·      the pattern repeats every
 o  ● · · · ● · · · ● · · · ● · · · ● · · ·      4 symbols here (PP-style)
 l  ▼
```

The pattern is a sampling problem in two dimensions: pilots must be dense enough in **frequency**
to track the channel's delay spread, and dense enough in **time** to track its Doppler. DVB-T2
defines eight patterns (PP1–PP8) so a broadcaster can trade pilot overhead against how fast the
channel changes — dense pilots for mobile reception, sparse for rooftop aerials.

---

## Part 5 — PAPR: What OFDM Costs

An OFDM symbol is the sum of $N$ independent random carriers. By the central limit theorem the
time-domain signal is therefore **complex Gaussian** — and its envelope is Rayleigh, with a long
tail.

$$
\text{PAPR} = \frac{\max |x[n]|^2}{\overline{|x[n]|^2}}
$$

The theoretical worst case is $N$ (30 dB for $N=1024$) when every carrier peaks together.
Statistically it is far lower — around **10–12 dB** in practice.

> **Measured in Lab 10:** the generated DVB-T2 signal has a PAPR of **9.6 dB** at the 99.99th
> percentile. You can see the Rayleigh tail directly on the amplitude histogram in
> `lab10_dvbt2_analyze.grc`.

### Why 10 dB is expensive

A power amplifier must stay linear up to the *peak*, but you only get paid for the *average*. A
10 dB PAPR means running a 100 W amplifier to deliver 10 W of average power — and burning the
difference as heat. This is why:

- Broadcast transmitters use enormous, expensive, heavily cooled amplifiers
- DVB-T2 offers optional PAPR reduction (tone reservation, and "ACE")
- **Uplinks** in LTE use SC-FDMA rather than OFDMA — a handset battery cannot afford 10 dB of
  backoff, so the standard deliberately uses a different, lower-PAPR scheme in that direction

It is also why, in [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md), the transmitter's
digital amplitude defaults to 0.25 rather than 1.0: leave headroom, or the peaks clip and the
spectrum regrows into the neighbouring channel.

---

## Part 6 — Synchronising an OFDM Receiver

Three things must be found, in this order.

### 1. Symbol timing — from the cyclic prefix

The guard interval is a *copy*, so $x[n]$ and $x[n+N]$ are identical inside it. Correlate:

$$
\gamma(d) = \sum_{n=d}^{d+N_{cp}-1} x[n]\, x^*[n+N]
$$

$|\gamma(d)|$ peaks once per OFDM symbol, at the start of the guard interval. This is the
**van de Beek estimator**, and it is remarkable for needing no pilots, no preamble and no
knowledge of the data — just the structure of the signal.

**Lab 10 builds exactly this from four blocks:** Delay → Conjugate → Multiply → Moving Average.
Measured on a real DVB-T2 waveform, it produces peaks every **1152 samples** (= 1024 + 128), a
result you can watch live on a Time Sink.

### 2. Fractional frequency offset — free, from the same correlation

$$
\hat{\varepsilon} = \frac{1}{2\pi}\arg \gamma(\hat d)
$$

A frequency error rotates the two copies relative to each other, so the *phase* of the same
correlation gives the offset — in units of carrier spacing, over $\pm\frac{1}{2}$ a spacing.

### 3. Integer frequency offset and frame sync — from a preamble

The fractional estimator cannot see a whole-carrier shift. Broadcast systems add a preamble:
DVB-T2's **P1 symbol** is a 2048-sample structure `C | A | B`, where C and B are
frequency-shifted copies of parts of A. Correlating C against A with that shift removed gives a
sharp peak — **24× peak-to-mean, measured in Lab 10** — that marks the frame start and reveals
the integer offset simultaneously.

> ⚠️ **OFDM is exquisitely sensitive to frequency error.** Carrier spacing for a DVB-T2 32K
> symbol is only **279 Hz**. An offset of a few tens of Hz destroys orthogonality and every
> carrier bleeds into its neighbours. Single-carrier systems shrug off far worse. This is OFDM's
> real weakness, and it is why every OFDM receiver spends so much effort on frequency tracking.

---

## Part 7 — Concatenated FEC: Why Two Codes

DVB-T2, DVB-S2 and 5G all use the same layered structure:

```
   data ──▶ [ BCH outer ] ──▶ [ LDPC inner ] ──▶ modulation
                  │                  │
        cleans up the floor    does the heavy lifting
```

**LDPC** (low-density parity check) codes, decoded by iterative belief propagation, get within
about **1 dB of the Shannon limit**. DVB-T2 uses 64800-bit codewords. But iterative decoders
have an **error floor**: below a certain BER they stop improving, because of rare structures in
the code graph that trap the decoder.

**BCH** is an algebraic block code with no error floor at all. Applied *outside* the LDPC, it
corrects the handful of residual errors the LDPC leaves. Together:

| Code | Role | Strength | Weakness |
|---|---|---|---|
| LDPC | inner | Near-capacity | Error floor around $10^{-7}$ |
| BCH | outer | No floor, cheap | Weak on its own |

Compare with the previous generation: DVB-T used **convolutional + Reed-Solomon**, the same
architecture with 1990s codes, and paid about 3 dB more for the same reliability. And with
[Fundamentals 10's](./10_error_detection_and_framing.md) ADS-B, which uses no FEC at all and
relies on repetition — a perfectly good choice when messages repeat twice a second.

**There is no universally right amount of coding.** There is only the right amount for your
channel, your latency budget and your ability to retransmit.

---

## Part 8 — Where OFDM Is Used

| System | Carriers | Spacing | Notes |
|---|---|---|---|
| **DVB-T2** | 853 – 27,841 | 279 Hz – 8.9 kHz | 1K to 32K FFT, [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md) |
| DVB-T | 1705 / 6817 | 1.1 / 4.5 kHz | 2K / 8K, convolutional + RS |
| **DAB / DAB+** | 1536 | 1 kHz | DQPSK, no channel estimation needed |
| Wi-Fi 802.11a/g | 52 | 312.5 kHz | 64-point FFT |
| Wi-Fi 802.11ax | up to 1960 | 78.125 kHz | OFDMA — carriers shared between users |
| **LTE downlink** | up to 1200 | 15 kHz | OFDMA |
| LTE uplink | — | 15 kHz | **SC-FDMA**, to save the handset's PAPR |
| 5G NR | scalable | 15–240 kHz | Spacing scales with the band |
| ADSL / VDSL | up to 4096 | 4.3 kHz | OFDM down a telephone line — "DMT" |
| PLC (powerline) | varies | — | OFDM over mains wiring |

**If a modern system moves a lot of data through a messy channel, it is almost certainly OFDM.**

---

## 🧠 Self-Check

1. Why does OFDM use many slow carriers rather than one fast one?
   **Answer:** A longer symbol period makes a fixed multipath delay a smaller fraction of a
   symbol, so inter-symbol interference becomes manageable.

2. What exactly is the orthogonality condition?
   **Answer:** $\Delta f = 1/T_u$. Each carrier then completes an integer number of cycles in
   the integration window, so its correlation with every other carrier is exactly zero.

3. Why is the cyclic prefix a *copy* rather than just silence?
   **Answer:** Silence would prevent inter-symbol interference but would not make the channel
   convolution circular. The copy does, which is what reduces equalisation to one complex
   division per carrier.

4. A DVB-T2 system uses a 32K FFT at 8 MHz with GI 1/8. How far apart can SFN transmitters be?
   **Answer:** $T_u = 3.584$ ms, $T_g = 448$ µs, $d = c T_g = 134$ km.

5. Your OFDM receiver has a 200 Hz frequency error and the carrier spacing is 279 Hz. What
   happens?
   **Answer:** Catastrophe — 0.72 of a carrier spacing destroys orthogonality, and every carrier
   leaks into its neighbours. You need the integer offset from a preamble and the fractional
   offset from the cyclic prefix.

6. Why does LTE use OFDMA downlink but SC-FDMA uplink?
   **Answer:** PAPR. A base station can afford a 10 dB backoff; a battery-powered handset's
   amplifier cannot, so the uplink uses a lower-PAPR scheme.

7. Why concatenate BCH with LDPC instead of just using a stronger LDPC?
   **Answer:** LDPC's iterative decoder has an error floor caused by trapping sets, which more
   iterations do not fix. An algebraic outer code has no floor and cleans up the residue cheaply.

---

**Next:** [Lab 10 — DVB-T2 Transmitter & Receiver →](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md)
