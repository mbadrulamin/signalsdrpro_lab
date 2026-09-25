# 🌐 Fundamentals 11 — OFDM and Modern Broadcast Systems

> **What you will learn:** why digital TV, Wi-Fi, 4G and 5G all send **thousands of slow
> carriers** instead of one fast one (**OFDM**); how an FFT makes that possible; the **cyclic
> prefix**; pilots; why OFDM is "peaky" (PAPR); how a receiver locks on; and why DVB-T2 uses
> two error-correcting codes.
> **Before this:** [Fundamentals 08](./08_digital_modulation.md), [09](./09_synchronization.md)
> and [10](./10_error_detection_and_framing.md).
> **Time:** about 55 minutes. **Used by:** Labs 10, 11 and 12.

---

## Why this chapter exists

Every digital signal so far used **one carrier**, sending one symbol at a time:

- RDS (Lab 08): 1187.5 bits per second on one subcarrier.
- ADS-B (Lab 09): a million pulses per second on one carrier.
- Lab 07's BPSK link: 100,000 symbols per second.

Modern broadcast and mobile systems do something completely different. Wi-Fi, 4G, 5G, digital
radio (DAB) and digital TV (DVB-T and DVB-T2) all use **OFDM**: **thousands of carriers at once**,
each one sending only a few hundred symbols per second.

This chapter explains why — and it is the theory behind
[Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md).

---

## Part 1 — The problem: echoes

### Echoes smear fast symbols

A signal reaches your antenna by several paths: directly, and bounced off buildings and hills.
Each path is a little longer, so each copy arrives a little later:

```
    TX ─────────────────────────▶ RX      direct,       0 µs
       ╲                        ╱
        ╲──── building ────────╱          echo,        +3 µs
         ╲                    ╱
          ╲──── hillside ────╱             echo,       +12 µs
```

This is called **multipath**. What does a 12 µs echo do to a single-carrier link?

| Symbol rate | Each symbol lasts | A 12 µs echo covers |
|---|---|---|
| 1,000 per second | 1000 µs | 1.2 % of one symbol — no problem |
| 100,000 per second | 10 µs | **1.2 symbols** — serious blurring |
| 10 million per second | 0.1 µs | **120 symbols** — hopeless |

**The faster you send, the more symbols each echo smears together.** A single-carrier digital
TV signal would need a huge, constantly adjusting **equaliser** to undo it — and would still fail
when the echoes changed.

### The answer: many slow carriers

Instead of **one** carrier at 10 million symbols per second, use **1000 carriers** at 10,000
each. The total data is the same. But each symbol now lasts 100 µs, so a 12 µs echo covers only
12 % of one symbol.

$$
\boxed{\text{Split the data over } N \text{ carriers} \Rightarrow \text{each symbol lasts } N \text{ times longer}}
$$

That is the whole idea of OFDM. The rest is how to make it practical.

---

## Part 2 — How OFDM works

### Carriers that overlap but do not interfere

Normally, carriers must be spaced apart with gaps between them, or they interfere. OFDM places
them **overlapping**, yet they still do not interfere. The rule is:

$$
\boxed{\text{carrier spacing} = \frac{1}{\text{symbol length}}}
$$

With that spacing, every carrier completes a **whole number of cycles** during one symbol. Over
that time, any two different carriers "cancel" when the receiver compares them: each carrier's
peak falls exactly on every other carrier's zero. **Orthogonal** is the mathematical word for
this. No gaps are needed, so OFDM wastes no spectrum.

```
   One carrier                  OFDM: carriers overlap, but each peak
                                sits on its neighbours' zeros
        ╱▔▔▔╲                    ╱╲  ╱╲  ╱╲  ╱╲  ╱╲  ╱╲
       ╱     ╲                  ╱  ╳╱  ╳╱  ╳╱  ╳╱  ╳╱  ╲
   ───╱───────╲───          ───╱──╱─╲──╱─╲──╱─╲──╱─╲───╲───
```

<details>
<summary><b>Going deeper:</b> why the carriers do not interfere</summary>

An OFDM symbol with *N* carriers, spacing Δ*f*, lasting *T*ᵤ:

$$
s(t) = \sum_{k=0}^{N-1} X_k \, e^{\,j 2\pi k \Delta f\, t}, \qquad 0 \le t < T_u
$$

If $\Delta f = 1/T_u$, then for two different carriers $k \neq l$:

$$
\int_0^{T_u} e^{\,j2\pi k \Delta f t}\, e^{-j2\pi l \Delta f t}\, dt
= \int_0^{T_u} e^{\,j2\pi (k-l) t / T_u}\, dt = 0
$$

— a whole number of turns, which adds up to zero.
</details>

### The IFFT makes all the carriers at once

To send 1000 carriers you might expect 1000 oscillators. Instead, one calculation does it: the
**inverse FFT** (IFFT). You put one data value (a constellation point) on each carrier, run one
IFFT, and out comes the time signal containing all the carriers. The receiver runs one **FFT** to
separate them again.

**This is why OFDM won.** The idea is from the 1960s. It became practical as soon as chips could
calculate FFTs fast enough.

| | One carrier | OFDM |
|---|---|---|
| Transmitter | mixer + pulse shaping | **IFFT** |
| Receiver | matched filter + long equaliser | **FFT** + one multiply per carrier |
| Handling echoes | a long, adapting equaliser | the cyclic prefix (next part) |

---

## Part 3 — The cyclic prefix: the key trick

The "no interference" rule needs **whole cycles** of every carrier inside the receiver's window.
An echo drags in a bit of the **previous** symbol, which breaks that — and then every carrier
leaks into every other.

The fix is simple: **copy the end of each symbol and put the copy in front of it.**

```
        ┌──────── the useful part, N samples ─────┐
        │                                         │
   ┌────┴────┐                              ┌─────┴───┐
   │  copy   │                              │  last   │
   │ of the  │   ← the "guard interval" →   │  part   │
   │  end    │                              │         │
   └─────────┴────────────────────────────────────────┘
   ◄─ guard ─►◄────────── useful part ────────────►
   ◄────────────── one whole OFDM symbol ──────────►
```

This **cyclic prefix** (CP) does two things:

1. Any echo **shorter than the guard** still leaves whole cycles of every carrier inside the
   window. The carriers stay separate.
2. It makes the echoes easy to undo. Each carrier is simply changed by one fixed amount (a size
   and an angle). The receiver undoes it with **one division per carrier** — instead of a huge
   equaliser.

$$
\boxed{Y_k = H_k X_k + \text{noise}} \qquad \Rightarrow \qquad \hat X_k = Y_k / H_k
$$

(*X*ₖ = what was sent on carrier *k*; *H*ₖ = what the channel did to it; *Y*ₖ = what arrived.)

### The price

The guard carries no new data. A longer guard handles longer echoes, but wastes more time:

| Guard (fraction of useful part) | Wasted | Longest echo, 1K-mode symbol (112 µs) | Extra path length |
|---|---|---|---|
| 1/128 | 0.8 % | 0.9 µs | 0.26 km |
| 1/32 | 3.1 % | 3.5 µs | 1.05 km |
| **1/8** | **11.1 %** | **14 µs** | **4.2 km** |
| 1/4 | 20.0 % | 28 µs | 8.4 km |

**Longer symbols need a smaller fraction.** Lab 10 uses the 32K mode, where the useful part lasts
3.584 ms. There, a guard of only **1/128** is **28 µs** — enough for echoes from 8.4 km of extra
path — while wasting less than 1 %. That is why broadcasters use 32K.

### Single-frequency networks

If the guard is longer than any echo, the receiver **cannot tell** an echo from a **second
transmitter** sending the same signal. So several transmitters can use the **same frequency**,
and a receiver between them treats the further one as a harmless echo. This is a
**single-frequency network (SFN)**.

With a 32K symbol and a 1/8 guard, the guard is 448 µs — radio travels **134 km** in that time.
Transmitters up to 134 km apart can share one channel. Analog TV needed a different frequency in
every area. **OFDM changed how countries plan their spectrum.**

<details>
<summary><b>Going deeper:</b> the SFN numbers</summary>

For DVB-T2 32K at 8 MHz (sample rate 64/7 MHz = 9.142857 MSPS):

$$
T_u = \frac{32768}{9.142857\times10^6} = 3.584\ \text{ms}, \qquad
T_g = \frac{T_u}{8} = 448\ \mu\text{s}, \qquad
d_{\max} = c\, T_g = 134\ \text{km}
$$

With GI 1/128 (Lab 10's setting): $T_g = 28\ \mu$s, $d = 8.4$ km.
</details>

---

## Part 4 — Pilots

To divide by *H*ₖ, the receiver must **know** *H*ₖ. It measures it using **pilots**: carriers
whose values are known in advance, sent a little stronger than the data.

| Pilot type | Purpose |
|---|---|
| **Scattered** | spread in a pattern over carriers and symbols; the receiver fills in between them to estimate *H* everywhere |
| **Continual** | the same carriers in every symbol; used to track frequency and phase |
| **Edge** | at the edges of the band, so nothing has to be guessed beyond the last pilot |
| **P2 / preamble** | carry the signalling that describes how everything else is set up |

```
   carrier ─────────────────────────────────────▶
 s  ● · · · ● · · · ● · · · ● · · · ● · · ·      ● = scattered pilot
 y  · · ● · · · ● · · · ● · · · ● · · · ● ·      · = data
 m  · · · · ● · · · ● · · · ● · · · ● · · ·
 b  · · · · · · ● · · · ● · · · ● · · · ● ·      the pattern repeats
 o  ● · · · ● · · · ● · · · ● · · · ● · · ·      every few symbols
 l  ▼
```

The pilots must be close enough in **frequency** to follow the echoes, and close enough in **time**
to follow changes (a moving car changes the channel quickly). DVB-T2 has eight patterns, PP1 to
PP8: dense pilots for moving receivers, sparse ones (like Lab 10's **PP7**) for fixed rooftop
aerials.

---

## Part 5 — PAPR: OFDM's cost

An OFDM signal is the sum of thousands of independent carriers. Added together, they behave like
**random noise** — most of the time the signal is moderate, but now and then many carriers line up
and make a tall **peak**.

**PAPR** (peak-to-average power ratio) measures how tall the peaks are compared with the average.

> **Measured in Lab 10:** the DVB-T2 signal has a PAPR of **9.6 dB** (at the 99.99th
> percentile). The peaks are about **9 times** the average power. You can see the long tail on the
> amplitude histogram in `lab10_dvbt2_analyze.grc`.

### Why that is expensive

An amplifier must handle the **peaks** without distortion, but you only get the **average** as
useful power. With 10 dB of PAPR, you need an amplifier able to give 100 W of peak to deliver about
10 W average. The rest becomes heat. That is why:

- broadcast transmitters use large, expensive, cooled amplifiers,
- DVB-T2 has optional PAPR-reduction tricks,
- **4G phones** send with a different, less peaky method (SC-FDMA) — a phone battery cannot
  afford that waste.

It is also why Lab 10's `tx_amplitude` must stay well below 1.0 (around **0.25**): leave room for
the peaks, or they get cut off (clipped), and the signal splashes into the next channel.

---

## Part 6 — How an OFDM receiver locks on

Three things must be found, in this order.

### 1. Where each symbol starts — from the cyclic prefix

The guard is a **copy** of the end of the symbol. So the receiver compares the signal with itself
one useful-part later. Inside the guard they match; everywhere else they do not. Averaging that
comparison over the guard length gives a **peak at the start of every symbol**. This is the
**van de Beek** method. It needs no pilots, no preamble, and no knowledge of the data — just the
structure of the signal.

**Lab 10 builds this from four blocks:** Delay → Conjugate → Multiply → Moving Average. On a real
32K DVB-T2 signal it finds a peak every **33,024 samples** (32,768 + 256), which you can watch
live.

### 2. The small frequency error — from the same comparison

A frequency error rotates the copy against the original. So the **angle** of the same comparison
tells you the frequency error — up to half a carrier spacing.

### 3. The large frequency error and the frame start — from a preamble

A whole-carrier shift cannot be seen that way. DVB-T2 adds a special preamble at the start of
every frame, the **P1 symbol**. The receiver searches for it; it gives a sharp peak — **23.9 times**
the average, measured in Lab 10 — marking the frame start and revealing the large frequency
error.

> ⚠️ **OFDM is very sensitive to frequency error.** In the 32K mode, carriers are only **279 Hz**
> apart. An error of a few tens of hertz makes every carrier leak into its neighbours.
> Single-carrier systems cope with much worse. This is OFDM's real weakness, and why OFDM receivers
> work so hard on frequency tracking.

<details>
<summary><b>Going deeper:</b> the van de Beek formulas</summary>

$$
\gamma(d) = \sum_{n=d}^{d+N_{cp}-1} x[n]\, x^*[n+N], \qquad
\hat{d} = \arg\max_d |\gamma(d)|, \qquad
\hat{\varepsilon} = \frac{1}{2\pi}\arg \gamma(\hat d)
$$

*N* is the useful length (32768), *N*₍cp₎ the guard (256), and ε the fractional frequency offset
in carrier spacings.
</details>

---

## Part 7 — Two error-correcting codes, one inside the other

DVB-T2, satellite TV (DVB-S2) and 5G all use the same two-layer design:

```
   data ──▶ [ BCH (outer) ] ──▶ [ LDPC (inner) ] ──▶ modulation
                  │                    │
        cleans up what's left     does the heavy work
```

- **LDPC** (low-density parity check) codes come within about **1 dB of the theoretical best**.
  DVB-T2 uses blocks of 64,800 bits. But LDPC decoders have an **error floor**: below a very low
  error rate they stop improving, because of rare patterns that trap the decoder.
- **BCH** is a simpler code with **no** error floor. Placed outside the LDPC, it fixes the few
  errors that LDPC leaves.

| Code | Job | Strong point | Weak point |
|---|---|---|---|
| LDPC | inner | close to the theoretical limit | error floor near 10⁻⁷ |
| BCH | outer | no floor, cheap | weak on its own |

Older DVB-T used the same design with 1990s codes (convolutional + Reed–Solomon) and needed about
3 dB more power for the same reliability. ADS-B ([Fundamentals 10](./10_error_detection_and_framing.md))
uses no correction at all, and just repeats. **There is no single right amount of coding** — only
the right amount for your channel, your delay budget, and whether you can ask again.

---

## Part 8 — Where OFDM is used

| System | Carriers | Spacing | Notes |
|---|---|---|---|
| **DVB-T2** | 853 – 27,841 | 279 Hz – 8.9 kHz | 1K to 32K; Lab 10 uses 32K (27,841 carriers) |
| DVB-T | 1,705 / 6,817 | 4.5 / 1.1 kHz | 2K / 8K; Lab 11 receives it |
| **DAB / DAB+** | 1,536 | 1 kHz | digital radio |
| Wi-Fi 802.11a/g | 52 | 312.5 kHz | 64-point FFT |
| Wi-Fi 6 (802.11ax) | up to 1,960 | 78.125 kHz | carriers shared between users |
| **4G LTE (downlink)** | up to 1,200 | 15 kHz | |
| 4G LTE (uplink) | — | 15 kHz | **SC-FDMA**, to save the phone's battery (PAPR) |
| 5G NR | many | 15–240 kHz | spacing depends on the band |
| ADSL / VDSL | up to 4,096 | 4.3 kHz | OFDM on a telephone line |

**If a modern system moves a lot of data through a messy channel, it almost certainly uses OFDM.**

---

## ✅ Summary

- Echoes smear fast symbols. **OFDM** splits the data over thousands of **slow** carriers.
- Carriers spaced at 1 ÷ (symbol length) **overlap without interfering**.
- One **IFFT** makes all carriers; one **FFT** separates them.
- The **cyclic prefix** (a copy of the symbol's end) makes echoes harmless, and turns equalising
  into one division per carrier.
- **Pilots** let the receiver measure the channel. **PAPR** (~10 dB) means amplifiers need
  headroom.
- The receiver finds **symbol timing** from the cyclic prefix and the **frame** from the P1
  preamble. OFDM is very sensitive to **frequency error**.
- DVB-T2 uses **LDPC inside BCH**.

## 🧠 Check yourself

1. Why does OFDM use many slow carriers instead of one fast one?
   <details><summary>Answer</summary>A longer symbol makes an echo a small part of one symbol,
   so echoes no longer smear symbols together.</details>
2. What spacing makes the carriers not interfere?
   <details><summary>Answer</summary>Spacing = 1 ÷ (useful symbol length). Then each carrier
   makes a whole number of cycles per symbol.</details>
3. Why is the cyclic prefix a *copy*, not just a silent gap?
   <details><summary>Answer</summary>Silence would stop symbols overlapping, but the copy also
   keeps whole cycles in the window and turns each channel effect into a single multiplication
   per carrier — so one division undoes it.</details>
4. DVB-T2 32K at 8 MHz with a 1/8 guard: how far apart can SFN transmitters be?
   <details><summary>Answer</summary>Guard = 3.584 ms ÷ 8 = 448 µs; radio travels 134 km in
   that time.</details>
5. An OFDM receiver has a 200 Hz frequency error, and the carriers are 279 Hz apart. What happens?
   <details><summary>Answer</summary>The error is 0.72 of a carrier spacing: the carriers are
   no longer separate and all leak into each other. It must be corrected first (large part from
   the P1 preamble, small part from the cyclic prefix).</details>
6. Why do 4G phones send with SC-FDMA instead of OFDM?
   <details><summary>Answer</summary>PAPR. OFDM's peaks would waste too much of the phone's
   battery in its amplifier.</details>
7. Why put BCH around LDPC instead of just making the LDPC stronger?
   <details><summary>Answer</summary>LDPC has an error floor that more decoding does not fix.
   BCH has no floor, and cheaply cleans up the few errors left.</details>

**Next:** [Lab 10 — Build a TV Transmitter →](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md)
