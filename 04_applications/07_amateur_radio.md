# 🎙️ 07 — Amateur Radio

> The only domain where you are **encouraged** to transmit — once you are licensed. Amateur radio
> is also where most SDR innovation happens: FT8, WSPR, SSTV decoders and the whole GNU Radio
> ecosystem grew out of it.
>
> [← Land Mobile](./06_land_mobile_and_professional.md) · [Catalogue index](./README.md) · [Next: IoT & ISM →](./08_iot_ism_and_short_range.md)

---

## Why this domain matters even if you never transmit

Amateur signals are **deliberately open**. Protocols are published, decoders are open source,
operators *want* to be received, and reception reports are welcomed rather than treated with
suspicion. That makes amateur bands the ideal place to test a new decoder: you can email the
operator and ask whether you got it right.

> 🔴 **Transmitting requires a licence** in every country. Exams are inexpensive and mostly
> straightforward, and the licence is what turns your SignalSDR Pro from a receiver into a
> transceiver. Receiving amateur traffic needs no licence anywhere.

---

## Band plan (where to point your SDR)

| Band | Frequency | Your SDR | Character |
|---|---|---|---|
| 160 m | 1.8–2.0 MHz | 🔻 | Night-time, regional |
| 80 m | 3.5–4.0 MHz | 🔻 | Night-time, national |
| 40 m | 7.0–7.3 MHz | 🔻 | Reliable day and night |
| 30 m | 10.1–10.15 MHz | 🔻 | Digital modes only |
| 20 m | 14.0–14.35 MHz | 🔻 | **The classic DX band** |
| 17/15/12 m | 18.068–24.99 MHz | 🔻 | Daytime, solar-cycle dependent |
| 10 m | 28.0–29.7 MHz | 🔻 | Spectacular when open |
| 6 m | 50–54 MHz | 🔻 | "The magic band" — sporadic-E |
| **2 m** | **144–148 MHz** | ✅ | **Local, repeaters, satellites** |
| 1.25 m | 222–225 MHz | ✅ | North America |
| **70 cm** | **430–440 MHz** | ✅ | **Repeaters, satellites, digital** |
| 33 cm | 902–928 MHz | ✅ | North America |
| 23 cm | 1240–1300 MHz | ✅ | ATV, satellites |
| 13 cm | 2300–2450 MHz | ✅ | |
| 9 cm and up | 3.4 GHz+ | ✅/🔺 | Microwave experimentation |

**Everything from 2 m upward is directly within your hardware's reach.** Below 50 MHz you need
an upconverter — and that is where most of the interesting weak-signal work happens.

---

## Voice modes

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **SSB (USB/LSB)** | HF bands, 6 m, 2 m | single sideband | ⭐⭐ | 🔻/✅ | 🟢 LSB below 10 MHz, USB above, by convention. In IQ this is just an asymmetric filter |
| **FM repeaters** | 2 m, 70 cm | NBFM, ±5 kHz | ⭐ | ✅ | 🟢 [Lab 06](../02_flowgraphs/lab06_multimode_receiver/README.md) receives these directly |
| **FM simplex** | 145.500, 433.500 MHz calling | NBFM | ⭐ | ✅ | 🟢 |
| **AM (nostalgia operation)** | 29.0, 50.4, 144.4 MHz | AM | ⭐ | ✅ | 🟢 A small but devoted community |
| **D-STAR** | 2 m, 70 cm | GMSK 4800, AMBE | ⭐⭐⭐⭐ | ✅ | 🟢 Icom's digital voice; internet-linked |
| **System Fusion (C4FM)** | 2 m, 70 cm | C4FM | ⭐⭐⭐⭐ | ✅ | 🟢 Yaesu's system |
| **DMR (amateur)** | 2 m, 70 cm | 4FSK TDMA | ⭐⭐⭐⭐ | ✅ | 🟢 Brandmeister and other networks |
| **M17** | 2 m, 70 cm | 4FSK, **Codec2** | ⭐⭐⭐ | ✅ | 🟢 **Fully open source, patent-free.** The one to study — no proprietary vocoder |
| **FreeDV** | HF | OFDM + Codec2 | ⭐⭐⭐ | 🔻 | 🟢 Open digital voice over SSB |

---

## Weak-signal digital modes

These are the crown jewels: modes designed to be decoded **below the noise floor**, using exactly
the synchronisation and coding theory from [Fundamentals 09](../01_fundamentals/09_synchronization.md)
and [10](../01_fundamentals/10_error_detection_and_framing.md).

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **FT8** | 14.074, 7.074, 3.573, 50.313 MHz +… | 8-FSK, 15 s slots, LDPC | ⭐⭐⭐ | 🔻/✅ | 🟢 Decodes at **−21 dB SNR**. The most-used mode on HF today |
| **FT4** | 14.080 MHz +… | 4-FSK, 7.5 s | ⭐⭐⭐ | 🔻/✅ | 🟢 Faster, less sensitive |
| **WSPR** | 14.0956, 7.0386 MHz +… | 4-FSK, 110 s, ~1.5 Hz wide | ⭐⭐⭐ | 🔻/✅ | 🟢 Decodes at **−28 dB SNR**. Beacons report to a global database |
| **JT65 / JT9** | HF, VHF | MFSK | ⭐⭐⭐ | 🔻/✅ | 🟢 FT8's predecessors; still used for EME |
| **Q65** | VHF/UHF | MFSK, tolerant of Doppler | ⭐⭐⭐⭐ | ✅📡 | 🟢 Designed for meteor and moonbounce |
| **MSK144** | 50.260, 144.150 MHz | MSK, 72 ms frames | ⭐⭐⭐⭐ | ✅📡 | 🟢 Meteor scatter — decodes from a fraction of a second of reflection |
| **PSK31** | 14.070 MHz +… | BPSK, 31.25 baud | ⭐⭐ | 🔻 | 🟢 **A perfect Lab 07 follow-on** — differentially encoded BPSK, exactly what you built |
| **RTTY** | 14.080 MHz +… | 45.45 baud FSK, Baudot | ⭐⭐ | 🔻 | 🟢 The oldest digital mode still in daily use |
| **Olivia / Contestia** | HF | MFSK with FEC | ⭐⭐⭐ | 🔻 | 🟢 Very robust chat modes |
| **JS8Call** | HF | FT8 framing, free text | ⭐⭐⭐ | 🔻 | 🟢 Keyboard conversation at FT8 sensitivity |
| **VARA / ARDOP** | HF | adaptive OFDM | ⭐⭐⭐⭐ | 🔻 | 🟢 High-rate data for email over radio |
| **Winlink** | HF/VHF | over VARA/Pactor/packet | ⭐⭐⭐⭐ | 🔻/✅ | 🟢 Email with no internet — used in disaster response |

---

## Packet, telemetry and networking

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **APRS** | 144.390 (NA), 144.800 (EU) MHz | AFSK 1200, AX.25 | ⭐⭐⭐ | ✅ | 🟢 Position, weather, messages. **An excellent third data project** |
| **APRS via ISS** | 145.825 MHz | same, from orbit | ⭐⭐⭐ | ✅📡 | 🟢 |
| **AX.25 packet BBS** | 144–145, 430 MHz | AFSK 1200 / G3RUH 9600 | ⭐⭐⭐ | ✅ | 🟢 |
| **AREDN / HamNet** | 2.4, 5.8 GHz | modified 802.11 | ⭐⭐⭐⭐ | ✅ | 🟢 Amateur mesh networking |
| **Amateur telemetry beacons** | 2 m, 70 cm | CW / FSK | ⭐⭐ | ✅ | 🟢 Solar, temperature, battery data from remote sites |
| **Balloon telemetry (HAB)** | 434.075–434.775 MHz | RTTY, LoRa, Horus 4FSK | ⭐⭐⭐ | ✅📡 | 🟢 Amateur high-altitude balloons. Chase them like radiosondes |

---

## Images

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **SSTV** | 14.230, 144.500 MHz +… | AFSK image lines | ⭐⭐ | 🔻/✅ | 🟢 Scottie, Martin, Robot modes. **A picture appears line by line** |
| **DATV (digital ATV)** | 70 cm, 23 cm, QO-100 | DVB-S/S2 | ⭐⭐⭐⭐ | ✅📡 | 🟢 Amateur television |
| **Analog FSTV** | 70 cm, 23 cm | vestigial sideband | ⭐⭐⭐ | ✅📡 | 🟢 |

---

## Propagation experiments

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **EME (moonbounce)** | 144, 432, 1296 MHz | JT65, Q65, CW | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 500,000 km path loss and 2.5 s round trip. The ultimate weak-signal challenge |
| **Meteor scatter** | 50, 144 MHz | MSK144 | ⭐⭐⭐⭐ | ✅📡 | 🟢 See [Weather & Environment](./05_weather_and_environment.md) |
| **Aurora** | 50, 144 MHz | CW/SSB, distorted | ⭐⭐⭐ | ✅📡 | 🟢 |
| **Sporadic-E** | 28–144 MHz | any | ⭐⭐ | ✅ | 🟢 Summer openings of 1000–2000 km |
| **Trans-equatorial (TEP)** | 50, 144 MHz | any | ⭐⭐⭐ | ✅ | 🟢 |
| **Grey-line propagation** | HF | any | ⭐⭐ | 🔻 | 🟢 The dawn/dusk terminator enhances long paths |
| **Beacon monitoring** | 28.2, 50.0–50.1, 144.4 MHz | CW | ⭐ | ✅/🔻 | 🟢 Continuous propagation indicators |

---

## Try this first: WSPR (even without a licence)

**Receive-only WSPR is the single most instructive weak-signal project available**, and it needs
no licence.

- The signal is **1.5 Hz wide**, 4-FSK, sent over 110.6 seconds
- It decodes reliably at **−28 dB SNR** — the signal is 600× weaker than the noise in its own
  bandwidth
- Every decode you upload appears on `wsprnet.org` with a map of who you heard and how far away

Run `WSJT-X` fed from your SDR, leave it overnight on 20 m, and in the morning you will have a
map of the world showing which paths were open while you slept. It makes
[Fundamentals 06's](../01_fundamentals/06_noise_snr_and_gain.md) processing-gain equation
viscerally real: the gain comes from spending 110 seconds and 1.5 Hz on six bits per second.

---

## Then: PSK31, because you already built it

PSK31 is **differentially encoded BPSK at 31.25 baud** — precisely the link you built and
measured in [Lab 07](../02_flowgraphs/lab07_bpsk_link_sim/README.md), just slower and with
varicode text instead of a PN pattern. Swap your BER monitor for a varicode decoder and your Lab
07 flowgraph becomes a real HF receiver.

That substitution — same chain, real signal — is the shortest path from "I simulated a digital
link" to "I decoded a stranger in another country".

---

[← Land Mobile](./06_land_mobile_and_professional.md) · [Catalogue index](./README.md) · [Next: IoT & ISM →](./08_iot_ism_and_short_range.md)
