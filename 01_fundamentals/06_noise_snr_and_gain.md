# 📉 Fundamentals 06 — Noise, SNR, Gain & Dynamic Range

> **Prerequisite:** Sampling & Filters (Fundamentals 05)
> **Time to read:** 45 minutes
> **Used by:** Lab 05, Lab 06, Lab 08, Lab 09

---

## Why This Chapter Exists

Every receiver question that starts with *"why can't I hear it?"* is answered here.

- Why does turning the gain up past 50 dB make reception **worse**?
- What does "sensitivity −110 dBm" actually promise?
- What SNR do I need before the FM audio becomes listenable?
- Why does decimating from 2 MSPS to 240 kSPS make a weak station suddenly appear?

These are not opinions. They are arithmetic, and this chapter gives you the arithmetic.

---

## Part 1 — Decibels, Properly

### The definition

A decibel is a **ratio of powers** on a log scale:

$$
G_{dB} = 10 \log_{10}\frac{P_2}{P_1}
$$

For **voltages or amplitudes**, because $P \propto V^2$:

$$
G_{dB} = 20 \log_{10}\frac{V_2}{V_1}
$$

> ⚠️ The 10-vs-20 distinction is the single most common mistake in SDR. **Power → 10. Voltage
> or amplitude → 20.** GNU Radio's FFT sinks display power, so they use 10. AGC references and
> filter gains are amplitudes, so they use 20.

### Numbers worth memorising

| Ratio | Power dB | Amplitude dB |
|---|---|---|
| 2× | 3.01 dB | 6.02 dB |
| 4× | 6.02 dB | 12.04 dB |
| 10× | 10 dB | 20 dB |
| 100× | 20 dB | 40 dB |
| 1000× | 30 dB | 60 dB |

### Absolute units

A bare "dB" is a ratio. Add a suffix to make it absolute:

| Unit | Reference | Used for |
|---|---|---|
| **dBm** | 1 milliwatt | RF power at an antenna or connector |
| **dBW** | 1 watt | Transmitter power ($0$ dBW $= 30$ dBm) |
| **dBFS** | ADC full scale | Digital level inside the SDR |
| **dBc** | The carrier | Spurious and harmonic levels |
| **dBi** | Isotropic radiator | Antenna gain |

$$
P_{dBm} = 10\log_{10}\!\left(\frac{P_{\text{watts}}}{0.001}\right)
$$

| Signal | Power | dBm |
|---|---|---|
| Strong local FM at your antenna | 1 μW | −30 dBm |
| Typical usable FM broadcast | 1 pW | −90 dBm |
| Weak but decodable narrowband | 10 fW | −110 dBm |
| GPS at the Earth's surface | 0.1 fW | −130 dBm |

### dBFS — the digital side

Inside GNU Radio, `fc32` samples are floats nominally in $[-1, +1]$. A full-scale sine has
amplitude 1.0 and RMS $1/\sqrt{2}$, defined as **0 dBFS**. So:

$$
P_{dBFS} = 20 \log_{10}\!\left(\frac{V_{\text{rms}}}{1/\sqrt 2}\right)
= 10 \log_{10}\!\left(2 \cdot \overline{|x[n]|^2}\right)
$$

Everything you see in a QT GUI Frequency Sink is dBFS-per-FFT-bin, **not** dBm. To convert you
need the receiver's absolute calibration, which consumer SDRs do not provide. Treat the sink
as a relative instrument.

---

## Part 2 — Where Noise Comes From

### Thermal (Johnson–Nyquist) noise

Every resistor at temperature $T$ generates noise power in bandwidth $B$:

$$
\boxed{N = k T B}
$$

with $k = 1.38 \times 10^{-23}$ J/K. At room temperature ($T_0 = 290$ K):

$$
kT_0 = 4.00 \times 10^{-21} \text{ W/Hz} = -174 \text{ dBm/Hz}
$$

**−174 dBm/Hz is the number to memorise.** It is the noise floor of the universe at room
temperature, and no receiver can do better.

$$
N_{dBm} = -174 + 10\log_{10}B
$$

| Bandwidth | $10\log_{10}B$ | Thermal noise floor |
|---|---|---|
| 1 Hz | 0 dB | −174 dBm |
| 3 kHz (SSB) | 34.8 dB | −139.2 dBm |
| 15 kHz (NBFM) | 41.8 dB | −132.2 dBm |
| 200 kHz (WBFM) | 53.0 dB | −121 dBm |
| 2 MHz (full SDR span) | 63.0 dB | −111 dBm |

> **This table explains decimation.** Narrowing your processing bandwidth from 2 MHz to
> 15 kHz drops the noise you accept by $10\log_{10}(2\times10^6/15\times10^3) = 21$ dB, while
> leaving your wanted signal untouched. That 21 dB is free SNR. It is why every receiver in
> this repo decimates aggressively, and why a station invisible on the waterfall can be
> perfectly audible after the channel filter.

### Noise figure

Real hardware adds its own noise. The **noise factor** $F$ is how much worse the SNR gets:

$$
F = \frac{\text{SNR}_{\text{in}}}{\text{SNR}_{\text{out}}}, \qquad NF = 10\log_{10}F
$$

The effective noise floor becomes:

$$
\boxed{N_{dBm} = -174 + 10\log_{10}B + NF}
$$

| Device | Typical NF |
|---|---|
| Cooled radio-astronomy LNA | 0.3 dB |
| Good external LNA | 1–2 dB |
| AD9361 (SignalSDR Pro / B210) front end | 4–8 dB depending on gain and band |
| RTL-SDR | 6–10 dB |
| Same receiver with the gain turned *down* | 20 dB+ |

### Friis: why the first amplifier decides everything

For a cascade of stages with gains $G_i$ (linear) and noise factors $F_i$:

$$
\boxed{F_{\text{total}} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2} + \cdots}
$$

The first stage's noise adds in full; every later stage is divided by all the gain ahead of
it. **The first amplifier sets your noise figure.**

> **Worked example.** SDR alone: $NF = 8$ dB. Add a mast-head LNA with $NF = 1$ dB and
> $G = 20$ dB in front of it:
> $F_1 = 10^{0.1} = 1.26$, $G_1 = 100$, $F_2 = 10^{0.8} = 6.31$.
> $$F_{\text{tot}} = 1.26 + \frac{6.31 - 1}{100} = 1.312 \Rightarrow NF = 1.18\text{ dB}$$
> Nearly 7 dB of sensitivity, gained by adding one part — **at the antenna**. Put the same
> LNA at the far end of the coax and the cable loss becomes $F_1$ and you gain almost nothing.

---

## Part 3 — SNR and What Each Mode Needs

$$
\text{SNR}_{dB} = P_{\text{signal},dBm} - N_{dBm}
$$

| Mode | SNR for usable copy | SNR for good quality |
|---|---|---|
| WBFM broadcast (mono) | 12 dB | 30 dB |
| WBFM broadcast (stereo) | 25 dB | 40 dB |
| NBFM voice | 10 dB | 20 dB |
| AM voice (airband) | 6 dB | 15 dB |
| BPSK, uncoded, BER $10^{-3}$ | 7 dB $E_b/N_0$ | 10 dB |
| ADS-B (Mode S) | 8 dB | 15 dB |

> **Note the stereo penalty.** The L−R subcarrier sits at 38 kHz where FM's triangular noise
> spectrum is much worse, and after the stereo matrix its noise adds to the L+R noise. Stereo
> costs roughly **20 dB** of SNR versus mono. This is exactly why your Lab 04 receiver hisses
> on distant stations while Lab 01 sounds fine on the same signal, and why commercial radios
> "blend to mono" when the signal weakens.

### FM's quieting threshold

FM has a **capture/threshold effect**. Below about 10 dB carrier-to-noise ratio the
demodulator output degrades catastrophically (you hear a roar); above it, the output SNR
improves *faster* than the input:

$$
\text{SNR}_{\text{out}} \approx \text{SNR}_{\text{in}} + 20\log_{10}\!\left(\frac{\Delta f}{f_m}\right) + 4.8 \text{ dB}
$$

For WBFM broadcast, $\Delta f/f_m = 75/15 = 5$, giving about **+18.8 dB** of FM improvement
gain. That is why FM broadcast sounds so much cleaner than AM at the same received power —
and why it needs so much more bandwidth to do it. There is no free lunch; you traded
bandwidth for SNR.

---

## Part 4 — Gain: the Three Kinds, and How to Set Them

The SignalSDR Pro / B210 front end has a **single 0–76 dB gain control** in GNU Radio, but
internally it drives several stages. What matters is the trade-off it controls:

```
   too little gain              just right              too much gain
 ┌────────────────┐        ┌────────────────┐       ┌────────────────┐
 │ signal buried  │        │ signal well    │       │ front end      │
 │ in ADC noise   │        │ above noise,   │       │ compressed;    │
 │                │        │ far from clip  │       │ spurs & IMD    │
 │ NF is terrible │        │                │       │ everywhere     │
 └────────────────┘        └────────────────┘       └────────────────┘
```

### The procedure that always works

1. Set gain to **0 dB**. Look at the QT GUI Frequency Sink.
2. Raise gain in 5 dB steps. Watch the **noise floor** rise.
3. Stop as soon as the noise floor starts moving up with the gain. At that point you are
   noise-limited by the front end, not the ADC — extra gain adds nothing but distortion risk.
4. Back off 5 dB. That is your operating point. For FM broadcast on a decent antenna this is
   typically **30–45 dB**.

### Symptoms of too much gain

- The waterfall shows evenly-spaced "ghost" carriers that move when you change gain → **IMD**.
- A strong local station appears at several frequencies at once → front-end compression.
- Audio distorts on strong stations but is fine on weak ones → clipping.
- `uhd` prints `O` (overflow) — that is a *USB* problem, not gain; lower the sample rate.

### 1 dB compression point and dynamic range

An amplifier is linear until it isn't. The **P1dB** point is where output has fallen 1 dB
below the ideal straight line. **Spurious-free dynamic range (SFDR)** is the window between
the noise floor and the level where distortion products emerge:

$$
\text{DR}_{dB} = P_{\text{max}} - N_{\text{floor}}
$$

An ideal $b$-bit ADC gives:

$$
\text{SNR}_{ADC} = 6.02b + 1.76 \text{ dB}
$$

| Bits | Ideal SNR |
|---|---|
| 8 (RTL-SDR) | 49.9 dB |
| 12 (AD9361 / SignalSDR Pro) | 74.0 dB |
| 14 | 86.0 dB |
| 16 | 98.1 dB |

### Processing gain — buying SNR back with DSP

Filtering to a narrower bandwidth improves SNR by:

$$
\boxed{G_p = 10\log_{10}\frac{B_{\text{wide}}}{B_{\text{narrow}}}}
$$

And an $N$-point FFT spreads noise across $N$ bins, so each bin's noise drops by
$10\log_{10}N$ relative to the full-band power — which is why a 4096-point FFT reveals
carriers you cannot see with 256 points. **The signal stays in one bin; the noise splits
across all of them.**

This is also, in one line, the reason spread-spectrum systems (GPS, CDMA) work at all: GPS
arrives 20 dB *below* the noise floor and is recovered by correlating over a 1023-chip code,
buying $10\log_{10}(1023) = 30$ dB of processing gain.

---

## Part 5 — AGC: Automatic Gain Control

The blocks `analog_agc2_xx` (Labs 03, 06) implement a feedback loop that drives the signal
amplitude toward a **reference**:

$$
e[n] = \text{reference} - |y[n]|
$$
$$
g[n+1] = g[n] + \mu \, e[n], \qquad y[n] = g[n]\,x[n]
$$

where $\mu$ is `attack_rate` when the signal is too loud and `decay_rate` when too quiet.

| Parameter | Meaning | Typical |
|---|---|---|
| `reference` | Target output amplitude | 0.5 |
| `attack_rate` | Loop gain while turning gain **down** | 0.01 (fast) |
| `decay_rate` | Loop gain while turning gain **up** | 0.001 (slow) |
| `max_gain` | Clamp, prevents runaway on silence | 65536 |

**Attack fast, decay slow.** Fast attack protects against a sudden strong signal; slow decay
stops the AGC from "pumping" the noise floor up between words. The time constant is roughly:

$$
\tau \approx \frac{1}{\mu f_s}
$$

At $f_s = 384$ kHz with `attack_rate` $= 0.01$: $\tau \approx 260\ \mu\text{s}$. With
`decay_rate` $= 0.001$: $\tau \approx 2.6$ ms.

> ⚠️ **Never put AGC before the channel filter.** The AGC would be driven by the strongest
> signal anywhere in the 2 MHz span, not by the station you are listening to — so a strong
> neighbour would turn *your* station down. Order is always: **filter → AGC → demodulate.**

---

## Part 6 — Squelch

Squelch mutes the output when the signal is too weak, so you get silence instead of a roar.

`analog_pwr_squelch_xx` compares a running power estimate against a threshold in dB:

$$
\bar{P}[n] = (1-\alpha)\bar{P}[n-1] + \alpha |x[n]|^2, \qquad
\text{open if } 10\log_{10}\bar{P}[n] > \text{threshold}
$$

| Parameter | Meaning | Notes |
|---|---|---|
| `threshold` | dB (relative to full scale) | Typical −50 to −30 |
| `alpha` | Averaging constant | 0.01; smaller = steadier, slower |
| `ramp` | Samples to fade in/out | > 0 avoids audible clicks |
| `gate` | `True` = stop producing samples entirely | Use `False` for audio |

> **`gate` matters more than it looks.** With `gate = True` the block emits *no samples* when
> closed, which starves the audio sink and can stall the flowgraph. For anything feeding an
> Audio Sink, use `gate = False` — it emits zeros instead, which is silence.

**Setting the threshold empirically:** tune to an empty frequency, read the power on a QT GUI
Number Sink fed from a Complex-to-Mag-Squared → Log10 chain, and set the threshold about
**5 dB above** what you see.

---

## Part 7 — The Link Budget

Putting it all together, for any link:

$$
P_{\text{rx}} = P_{\text{tx}} + G_{\text{tx}} - L_{\text{path}} + G_{\text{rx}} - L_{\text{cable}}
$$

Free-space path loss:

$$
\boxed{L_{\text{fs}}(dB) = 20\log_{10}d_{\text{km}} + 20\log_{10}f_{\text{MHz}} + 32.45}
$$

> **Worked example — can I hear that FM station 30 km away?**
> - $P_{tx} = 50$ kW ERP $= 77$ dBm
> - $L_{fs} = 20\log_{10}(30) + 20\log_{10}(100) + 32.45 = 29.5 + 40 + 32.45 = 102$ dB
> - Antenna gain $G_{rx} = 0$ dBi (telescopic whip), cable loss 1 dB
> - $P_{rx} = 77 - 102 + 0 - 1 = -26$ dBm
>
> Noise floor in 200 kHz with $NF = 8$ dB: $-174 + 53 + 8 = -113$ dBm.
> **SNR = 87 dB.** Full stereo, no problem. In practice buildings and terrain eat 20–40 dB of
> that, and you still have 50 dB to spare. This is why FM broadcast is easy — and why ADS-B
> in Lab 09, at 1090 MHz with a 1 W transmitter 100 km away, is genuinely hard.

---

## 🧠 Self-Check

1. What is the thermal noise floor in a 15 kHz channel with a 6 dB noise figure?
   **Answer:** $-174 + 10\log_{10}(15000) + 6 = -174 + 41.8 + 6 = -126.2$ dBm.

2. You decimate from 2 MSPS to 250 kSPS. How much SNR do you gain?
   **Answer:** $10\log_{10}(2\times10^6 / 250\times10^3) = 9.0$ dB.

3. Your signal is 4× larger in amplitude than another. How many dB?
   **Answer:** 12.04 dB (amplitude → 20·log₁₀).

4. Why put the LNA at the antenna, not at the receiver?
   **Answer:** Friis — the first stage sets $NF$. Coax loss ahead of the LNA adds directly to
   the noise figure and cannot be recovered.

5. Your AGC "pumps" — the background noise swells between words. Which parameter?
   **Answer:** `decay_rate` is too high. Lower it so the gain recovers slowly.

6. Why does an FM station sound fine in mono but hiss in stereo?
   **Answer:** The L−R subcarrier at 38 kHz sits where FM's noise density is much higher, and
   the matrix adds its noise to the L+R path — roughly a 20 dB SNR penalty.

7. A 12-bit ADC has what ideal SNR, and does more RF gain improve it?
   **Answer:** $6.02 \times 12 + 1.76 = 74$ dB. More RF gain only helps until the front-end
   noise dominates the ADC noise; past that it just eats headroom.

---

**Next:** [Fundamentals 07 — AM & Narrowband FM →](./07_am_and_narrowband_fm.md)
