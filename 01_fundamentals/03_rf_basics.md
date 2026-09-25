# 📻 Fundamentals 03 — RF Basics

> **What you will learn:** what "RF" means, how the radio spectrum is divided, how a radio
> tunes (the mixer), what gain does, what filters do, and what happens inside the SignalSDR Pro
> from the antenna to your program.
> **Before this:** [Fundamentals 02 — IQ Sampling](./02_iq_sampling.md).
> **Time:** about 30 minutes.

---

## 1. What is RF?

**RF** means **radio frequency**. It is the range of frequencies used for radio: roughly from
**20 kHz up to 300 GHz**.

- Below that range, waves do not leave an antenna well. (You would need an antenna kilometres
  long.)
- Above 300 GHz, the waves behave more like heat and light (infrared).

An RF signal is an **electromagnetic wave**: energy that travels through space at the speed of
light. When it passes an antenna, it creates a tiny changing voltage — often only a few
millionths of a volt (**microvolts, µV**). An SDR measures that voltage.

---

## 2. The radio spectrum

The radio range is divided into named bands. Each band is ten times higher in frequency than
the one below it.

**Wavelength** is the distance one wave travels during one cycle. Higher frequency means shorter
wavelength. A quick formula: wavelength in metres ≈ **300 ÷ frequency in MHz**. So a 100 MHz
FM signal has a wavelength of about 3 m.

| Band | Frequency | Wavelength | Common uses |
|---|---|---|---|
| VLF (very low) | 3–30 kHz | 10–100 km | Talking to submarines |
| LF (low) | 30–300 kHz | 1–10 km | Longwave radio, time signals |
| MF (medium) | 300 kHz – 3 MHz | 100 m – 1 km | AM radio |
| HF (high) | 3–30 MHz | 10–100 m | Shortwave radio, amateur radio |
| VHF (very high) | 30–300 MHz | 1–10 m | **FM radio (88–108 MHz)**, aircraft voice, marine radio |
| UHF (ultra high) | 300 MHz – 3 GHz | 10 cm – 1 m | TV, mobile phones, Wi-Fi, GPS, aircraft tracking |
| SHF (super high) | 3–30 GHz | 1–10 cm | Satellites, radar, 5 GHz Wi-Fi |
| EHF (extremely high) | 30–300 GHz | 1–10 mm | 5G "mmWave", scanners |

The SignalSDR Pro covers **70 MHz to 6 GHz**: the top of VHF, all of UHF, and the start of
SHF. That includes FM radio, TV, mobile phones, GPS, aircraft tracking, Wi-Fi and Bluetooth.

---

## 3. What a transceiver does

A **transceiver** can **trans**mit and re**ceive**. The SignalSDR Pro is one.

**When receiving**, the signal goes through these steps:

```
 antenna → amplifier → mixer → filter → ADC → numbers to the computer
```

**When transmitting**, the same steps happen in reverse:

```
 numbers from the computer → DAC → filter → mixer → amplifier → antenna
```

- An **ADC** (analog-to-digital converter) turns a voltage into numbers.
- A **DAC** (digital-to-analog converter) turns numbers into a voltage.

The most important part is the **mixer**. It is what lets the radio tune.

---

## 4. How a radio tunes: the mixer

### 4.1 The problem

An FM station at 100 MHz wiggles 100 million times per second. It is hard and expensive to
measure something that fast with high accuracy. It would be much easier if we could **slow it
down** first, without losing the information it carries.

### 4.2 The solution: shift the frequency down

The radio makes its own internal signal, called the **local oscillator (LO)**. The **mixer**
multiplies the incoming signal by the LO. The result contains **two** new frequencies:

- the **difference**: RF − LO
- the **sum**: RF + LO

A filter throws away the sum. We keep the difference.

**Example.** Set the LO to 100 MHz:

| Incoming station | RF − LO | Result |
|---|---|---|
| 100.1 MHz | 100.1 − 100 | **+100 kHz** |
| 100.0 MHz | 100.0 − 100 | **0 Hz** (the centre) |
| 99.9 MHz | 99.9 − 100 | **−100 kHz** |

The stations keep their shape and their spacing. They have simply **slid down** to near zero,
where they are easy to measure. The negative result (−100 kHz) is possible because of IQ —
see [Fundamentals 02](./02_iq_sampling.md).

**To tune, you only change the LO.** Set the LO to 95 MHz, and the stations around 95 MHz
slide down to zero instead. When you move the frequency slider in GNU Radio, you are changing
the LO.

> 💡 **Words you will meet:** a signal that has been shifted down to around 0 Hz is called
> **baseband**. Older radios shifted down to a fixed middle frequency instead, called the
> **intermediate frequency (IF)**, such as 10.7 MHz in FM radios.

<details>
<summary><b>Going deeper:</b> why multiplying makes a sum and a difference</summary>

A trigonometric identity:

$$
\cos(a) \cdot \cos(b) = \tfrac{1}{2}\cos(a - b) + \tfrac{1}{2}\cos(a + b)
$$

With $a = 2\pi f_{RF} t$ and $b = 2\pi f_{LO} t$, the product contains the frequencies
$f_{RF} - f_{LO}$ and $f_{RF} + f_{LO}$. An IQ mixer uses a cosine and a sine LO, and the
result is a single complex (IQ) output at $f_{RF} - f_{LO}$ only.
</details>

---

## 5. Gain

**Gain** is how much a signal is made stronger. It is measured in **dB**
([Fundamentals 01](./01_signals_basics.md#6-decibels-db--the-language-of-signal-strength)).
**Attenuation** is the opposite: making a signal weaker.

A receiver has several amplifiers, one after another:

- **LNA** (low-noise amplifier) — right after the antenna. It boosts weak signals while adding
  as little noise as possible.
- **Variable-gain amplifiers** — later in the chain. They set the final level for the ADC.

In GNU Radio, you set them all with **one** number: the **gain** setting of the USRP Source
block. UHD shares it out between the amplifiers for you.

| SignalSDR Pro (AD9361) | Range |
|---|---|
| Receive gain | **0 to 76 dB** |
| Transmit gain | **0 to 89.8 dB** |

### 5.1 How much gain?

The ADC can only measure numbers up to a maximum ("full scale").

- **Too much gain:** strong signals hit the maximum and get cut off. This is called
  **clipping**. It sounds harsh and creates false signals all over the spectrum.
- **Too little gain:** the signal is so small that the ADC's own tiny steps (its "rounding
  noise") become a problem, and weak stations disappear.

> 💡 **Starting rule:** the IQ samples should peak around **0.3 to 0.5** (on a scale where 1.0
> is the maximum). In practice, start with a gain of about **40 dB** for FM and adjust.
> [Fundamentals 06](./06_noise_snr_and_gain.md) gives a better method.

> ⚠️ **Gain is not volume.** Gain sets how strong the signal is *inside the radio*, before it
> is decoded. Volume is set *after* decoding. Turning up the gain to make the sound louder
> often makes it **worse**. Lab 03 adds a proper volume control.

---

## 6. Sample rate and bandwidth on the SignalSDR Pro

The AD9361 can see up to **56 MHz** of spectrum at once, and sample at up to **61.44 MSPS**.

When you set the sample rate in the USRP Source block, you tell UHD: "give me this many IQ
samples every second." With IQ, the sample rate is also the width of spectrum you see.

| Signal | Its width | A sensible sample rate |
|---|---|---|
| One FM station | about 0.2 MHz | 1–2 MSPS |
| A group of FM stations | a few MHz | 2–10 MSPS |
| One 4G (LTE) channel | up to 20 MHz | 15–30 MSPS |
| One DVB-T2 TV channel | 7.6 MHz | about 9–10 MSPS |

> ⚠️ **Higher is not always better.** Each extra sample must travel over USB and be processed
> by your computer. If the computer cannot keep up, you will see `O` (overflow) printed in the
> terminal and hear gaps in the audio. Use the lowest rate that fits your signal.

> ⚠️ **Also set the analog bandwidth.** The USRP Source has a separate setting called `bw0`,
> for the hardware filter in front of the ADC. Set it to the same value as the sample rate. If
> you leave it empty, the filter opens to 56 MHz and lets in a lot of extra noise. All the labs
> do this for you.

---

## 7. Filters

A **filter** lets some frequencies through and blocks others. Radios use filters everywhere:
to pick one station, to remove noise, and to stop aliasing
([Fundamentals 01](./01_signals_basics.md#52-what-goes-wrong-if-you-sample-too-slowly-aliasing)).

Filters are named after what they **let through**:

| Filter | Lets through | Blocks | Picture |
|---|---|---|---|
| **Low-pass** (LPF) | low frequencies | high frequencies | `▇▇▇▇▁▁▁▁` |
| **High-pass** (HPF) | high frequencies | low frequencies | `▁▁▁▁▇▇▇▇` |
| **Band-pass** (BPF) | one range in the middle | everything outside it | `▁▁▇▇▇▁▁▁` |
| **Band-stop / notch** | everything except one range | one narrow range | `▇▇▇▁▇▇▇▇` |

GNU Radio has blocks for each: **Low Pass Filter**, **High Pass Filter**, **Band Pass Filter**,
and more general ones (**FIR Filter**, **FFT Filter**). You will use them from Lab 02 onwards.
[Fundamentals 05](./05_sampling_and_filters.md) explains how they work inside.

---

## 8. Antennas

An **antenna** turns radio waves into a voltage (when receiving), and a voltage into radio
waves (when transmitting).

Three things matter:

- **Length.** An antenna works best at the frequency it is cut for. A simple antenna is about
  a **quarter** or a **half** of the wavelength long. For FM at 100 MHz (wavelength 3 m), a
  half-wave **dipole** is about 1.4–1.5 m long from tip to tip.
- **Gain and direction.** Some antennas hear equally from all directions. Others (like a TV
  aerial) point one way and hear that way better. Antenna gain is measured in **dBi**.
- **Impedance.** Almost all radio equipment, including the SignalSDR Pro, expects
  **50 ohms**. Use 50-ohm antennas and cables.

The SignalSDR Pro uses **SMA** connectors (small, screw-on). Any SMA antenna fits.

> 💡 A telescopic whip is fine for strong FM stations. For weak or high-frequency signals —
> like aircraft at 1090 MHz — you need an antenna cut for that frequency. See the
> [Antennas reference](../05_reference/03_antennas.md).

---

## 9. The whole journey: antenna to program

Here is what happens when you tune the SignalSDR Pro to 100 MHz:

```
  radio waves at 100 MHz
        │
        ▼
  ANTENNA         turns waves into a tiny voltage (microvolts)
        │
        ▼
  LNA             amplifies it, adding very little noise
        │
        ▼
  IQ MIXERS       multiply by the LO (100 MHz) and by a 90°-shifted copy
        │         → two outputs, I and Q, now centred on 0 Hz
        ▼
  FILTER (bw0)    removes everything outside the band you asked for
        │
        ▼
  ADCs            measure I and Q, e.g. 1 million times per second
        │
        ▼
  ZYNQ FPGA       collects the samples and packs them for USB
        │
        ▼
  USB 3.0         carries them to your computer
        │
        ▼
  UHD DRIVER      hands them to GNU Radio
        │
        ▼
  YOUR FLOWGRAPH  turns the numbers into sound, pictures or data
```

Everything above the ADC is fixed electronics. Everything below it is software you control.

---

## ✅ Summary

- **RF** is radio frequency: about 20 kHz to 300 GHz. The SignalSDR Pro covers 70 MHz – 6 GHz.
- Wavelength (m) ≈ 300 ÷ frequency (MHz).
- A **mixer** shifts signals down by the **LO** frequency. Tuning = changing the LO.
- **Gain** makes the signal stronger inside the radio. Too much causes **clipping**. Gain is
  not volume.
- With IQ, sample rate = the width you see. Set `bw0` equal to the sample rate.
- **Filters** keep the frequencies you want. **Antennas** work best when cut for the frequency.

## 🧠 Check yourself

1. The LO is at 90.0 MHz. A station is at 90.3 MHz. Where does it appear after the mixer?
   <details><summary>Answer</summary>At +300 kHz (90.3 − 90.0 = 0.3 MHz).</details>
2. What is the wavelength of a 300 MHz signal?
   <details><summary>Answer</summary>About 1 m (300 ÷ 300).</details>
3. Your audio is harsh and distorted on a strong station. What should you try first?
   <details><summary>Answer</summary>Lower the gain. The ADC is probably clipping.</details>
4. What happens if the computer cannot keep up with the sample rate?
   <details><summary>Answer</summary>Samples are lost: you see <code>O</code> in the
   terminal and hear gaps. Lower the sample rate.</details>
5. Which filter would you use to keep only frequencies below 15 kHz?
   <details><summary>Answer</summary>A low-pass filter.</details>

**Next:** [Fundamentals 04 — How FM Works →](./04_fm_theory.md)
