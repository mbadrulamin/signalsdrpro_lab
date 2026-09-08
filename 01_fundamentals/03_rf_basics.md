# 📻 Fundamentals 03 — RF Basics

> **Prerequisite:** IQ Sampling  
> **Time to read:** 30 minutes

---

## What Is "RF"?

**RF** stands for **Radio Frequency** — any electromagnetic signal with a frequency roughly between **20 kHz and 300 GHz**. Above 300 GHz we enter the infrared/optical range; below 20 kHz the signals don't radiate efficiently from practical antennas.

---

## The Radio Spectrum

| Band | Frequency | Wavelength | Common uses |
|---|---|---|---|
| VLF | 3–30 kHz | 10–100 km | Submarine communication |
| LF | 30–300 kHz | 1–10 km | AM longwave radio, time signals |
| MF | 300 kHz – 3 MHz | 100–1000 m | AM broadcast radio |
| HF | 3–30 MHz | 10–100 m | Shortwave, amateur radio |
| VHF | 30–300 MHz | 1–10 m | **FM broadcast (88–108 MHz)**, air traffic, TV |
| UHF | 300 MHz – 3 GHz | 10 cm – 1 m | TV, cellular (4G/5G), Wi-Fi, GPS, ADS-B |
| SHF | 3–30 GHz | 1–10 cm | Satellite, radar, Wi-Fi (5 GHz) |
| EHF | 30–300 GHz | 1–10 mm | 5G mmWave, imaging |

The SignalSDR Pro covers **70 MHz to 6 GHz**, which spans the upper VHF, all of UHF, and part of SHF. That's an enormous range — it includes FM radio, TV, cell phones, GPS, ADS-B airplane transponders, Wi-Fi, Bluetooth, and more.

---

## What Does a Transceiver Do?

A transceiver (like the SignalSDR Pro) is a box that:

1. **Receives:** Antenna → RF amplifier → Mixer (downconversion) → IF/baseband filter → ADC → digital samples
2. **Transmits:** Digital samples → DAC → IF/baseband filter → Mixer (upconversion) → RF amplifier → Antenna

The **mixer** is the magic component that moves signals between RF and baseband frequencies. It multiplies the incoming signal with a **local oscillator (LO)** at frequency $f_{LO}$:

$$
\text{RF signal at } f_{RF} \times \text{LO at } f_{LO} \rightarrow \text{output at } (f_{RF} - f_{LO}) \text{ and } (f_{RF} + f_{LO})
$$

The sum term $(f_{RF} + f_{LO})$ is filtered out. We keep the difference $(f_{RF} - f_{LO})$, which is called the **Intermediate Frequency (IF)** or **baseband** if it's at DC.

### Example: Tuning 100 MHz

- Set LO = 100 MHz
- A station at 100.1 MHz becomes 100 kHz IF
- A station at 99.9 MHz becomes −100 kHz IF (IQ sampling captures this!)

By adjusting the LO, we can "tune" to any frequency within the transceiver's range.

---

## Gain and Attenuation

**Gain** is how much a block amplifies a signal, measured in dB.

**Attenuation** is negative gain (signal gets weaker).

Every RF chain has several gain stages:
- **LNA** (Low Noise Amplifier) — near the antenna, amplifies weak signals with minimal added noise
- **VGA** (Variable Gain Amplifier) — programmable, lets you adjust signal level
- **PGA** (Programmable Gain Amplifier) — fine-grained gain at baseband

The SignalSDR Pro's AD9361 chip has:
- RX gain range: **0 to 76 dB**
- TX gain range: **0 to 89.8 dB**

> ⚠️ **Too much gain** causes **clipping** — the signal hits the ADC's maximum value and distorts.
> **Too little gain** means the signal is lost in quantization noise.

A good starting rule: aim for the IQ samples to have a peak amplitude of about **0.3 to 0.5** (on a scale of -1 to +1).

---

## Bandwidth and Sample Rate

The AD9361 can handle up to **56 MHz of RF bandwidth** and up to **61.44 MSPS** (million samples per second).

When you set a sample rate in GNU Radio's USRP Source block, you're telling UHD: "give me this many IQ samples per second." The AD9361's internal filters will adjust to give you that bandwidth.

**Rule of thumb:** For an FM broadcast signal (≈200 kHz bandwidth), 1 MSPS is plenty. For wideband applications like LTE sniffing, you might use 15 MSPS.

---

## Filters — The Unsung Heroes

Filters remove unwanted parts of a signal. They are classified by what they **pass**:

| Filter | Passes | Removes |
|---|---|---|
| Low-pass (LPF) | Low frequencies | High frequencies |
| High-pass (HPF) | High frequencies | Low frequencies |
| Band-pass (BPF) | A band of frequencies | Both below and above |
| Band-stop / Notch | Everything except a band | A specific narrow band |

In GNU Radio, filters are built with blocks like:
- `Low Pass Filter`
- `Band Pass Filter`
- `FIR Filter` (custom)
- `FFT Filter` (fast, for long filters)

Every real-world SDR receiver uses multiple filters. You'll see many in the later labs.

---

## Antennas

An antenna is a device that converts electromagnetic waves into electrical voltages (and vice versa).

Key properties:
- **Resonance frequency:** Antenna works best at a specific frequency (depends on its physical length)
- **Gain:** How directional it is (dBi)
- **Impedance:** Usually 50 ohms (must match the transceiver's input)

For FM broadcast (88–108 MHz), a simple **half-wave dipole** is about 1.4 meters long. The SignalSDR Pro has SMA connectors — you can use any SMA antenna.

> 🎯 **Practical tip:** Even a simple telescopic whip antenna works for strong FM stations. For weak signals (like ADS-B at 1090 MHz), you need a proper antenna.

---

## Putting It All Together

When you plug an antenna into the SignalSDR Pro and tune to 100 MHz, this is what happens physically:

```
EM wave (100 MHz)
   ↓
Antenna converts to voltage (very small, ~μV)
   ↓
LNA amplifies (low noise)
   ↓
Mixer downconverts using LO at 100 MHz → baseband at 0 Hz
   ↓
IQ mixer (with 90° LO offset) → produces I and Q streams
   ↓
ADC digitizes at (say) 1 MSPS → 1M complex samples/second
   ↓
Zynq FPGA buffers and sends via USB 3.0
   ↓
Cypress FX3 chip streams to host PC
   ↓
UHD driver delivers samples to GNU Radio
   ↓
Your flowgraph processes the samples
```

**You are holding the entire radio in software.** The hardware is just a fast analog front-end.

---

**Next:** [Fundamentals 04 — FM Modulation Theory →](./04_fm_theory.md)
