# 📤 15 — Transmit Projects

> Your SignalSDR Pro **can transmit**, from 70 MHz to 6 GHz. That makes it a fundamentally
> different instrument from a receive-only dongle — and a fundamentally more dangerous one.
>
> [← Test & Measurement](./14_test_measurement_and_infrastructure.md) · [Catalogue index](./README.md) · [Next: Oddities →](./16_oddities_and_historical.md)

---

## ⚠️ Before you transmit anything

### The four rules

1. **Get licensed.** An amateur radio licence is inexpensive, the exam is passable in a few
   weeks of study, and it makes almost everything on this page legal. Without one, almost nothing
   is.
2. **Use a dummy load while developing.** A 50 Ω terminator plus a 30 dB attenuator lets you
   build and debug a transmitter that radiates essentially nothing. Switch to an antenna only
   when you are certain what is coming out.
3. **Look at your own output before you radiate it.** Loop the TX into the RX through
   attenuators and *see* your signal. Harmonics, splatter, and "why is my bandwidth 4 MHz wide"
   are all discovered this way.
4. **Know your band edges and your power limit.** Both are legal boundaries, and a wrong digit
   in a frequency field is all it takes to cross one.

### What will get you into real trouble

- ⛔ Any transmission on **aviation, maritime distress, or emergency services** frequencies
- ⛔ **GNSS transmission that radiates** — even at microwatts, this can disrupt navigation and
  timing over a surprising area. Cable-only, shielded, or not at all
- ⛔ **Cellular transmission** on live bands — this is an IMSI-catcher offence, not a hobby
- ⛔ **Jamming**, deliberate or careless
- ⛔ **Transmitting a signal that impersonates** a real service: fake ADS-B, fake AIS, fake
  emergency alerts. These are prosecuted as endangerment

### The accident that actually happens

The commonest way people transmit illegally is not deliberate — it is **a `uhd_usrp_sink` left
connected in a flowgraph**, or a frequency variable that was still set from the previous
experiment. Before every run with an antenna attached, check what is connected to your sink and
what frequency it is on.

---

## Learning transmitters (dummy load / cable only)

Start here. Everything below radiates nothing.

| Project | Diff | Notes |
|---|---|---|
| **Unmodulated carrier** | ⭐ | The "hello world" of TX. Look at it on your own RX and measure the frequency error |
| **Two-tone test signal** | ⭐⭐ | The standard test for amplifier linearity — generates IM3 products you can measure |
| **Swept carrier (chirp)** | ⭐⭐ | Sweep through a filter and plot its response. Instant scalar network analyser |
| **AM / FM modulator** | ⭐⭐ | Transmit a tone, receive it with [Lab 06](../02_flowgraphs/lab06_multimode_receiver/README.md). **Closes the loop on Fundamentals 04 and 07** |
| **BPSK / QPSK modulator** | ⭐⭐⭐ | [Lab 07](../02_flowgraphs/lab07_bpsk_link_sim/README.md) already builds this — now over a cable instead of a simulated channel |
| **Noise source** | ⭐⭐ | Calibrated broadband noise for Y-factor noise-figure measurement |
| **Loopback BER measurement** | ⭐⭐⭐ | Lab 07's BER monitor with a real RF path in the middle. **The natural next experiment** |
| **Deliberate impairments** | ⭐⭐⭐ | Add IQ imbalance, DC offset, phase noise — then measure what your receiver tolerates |

---

## Amateur radio transmission (licence required)

| Project | Band | Diff | Notes |
|---|---|---|---|
| **WSPR beacon** | HF 🔻 / 2 m | ⭐⭐⭐ | 200 mW reported worldwide. **The best first real transmission** — your callsign appears on a global map |
| **CW / Morse beacon** | 2 m, 70 cm | ⭐⭐ | Simple, legal, and traditional |
| **FT8 transmission** | HF 🔻 / VHF | ⭐⭐⭐ | Two-way contacts at −21 dB SNR |
| **PSK31** | HF 🔻 | ⭐⭐ | The BPSK link from Lab 07, on the air |
| **SSB voice** | HF 🔻 / VHF | ⭐⭐⭐ | Implement the Hilbert/phasing method yourself |
| **NBFM repeater access** | 2 m, 70 cm | ⭐⭐ | Include the CTCSS tone |
| **APRS position beacon** | 144.390 / 144.800 MHz | ⭐⭐⭐ | AFSK 1200 in AX.25. Your position appears on aprs.fi |
| **SSTV image transmission** | 2 m, HF 🔻 | ⭐⭐⭐ | Send a picture; someone will send one back |
| **Satellite uplink (FM)** | 145 / 435 MHz | ⭐⭐⭐⭐ | Doppler-correct your **own transmission** in real time |
| **Linear transponder operation** | 145 / 435 MHz | ⭐⭐⭐⭐ | Full-duplex with Doppler on both links |
| **QO-100 uplink** | 2.4 GHz | ⭐⭐⭐⭐ | Geostationary — no tracking. A dish and a modest amplifier |
| **M17 digital voice** | 2 m, 70 cm | ⭐⭐⭐ | Open-source codec and protocol; no proprietary vocoder |
| **FreeDV** | HF 🔻 | ⭐⭐⭐ | Open digital voice over SSB |
| **DATV (DVB-S)** | 70 cm, 23 cm, QO-100 | ⭐⭐⭐⭐⭐ | Amateur television |
| **Meteor scatter (MSK144)** | 50, 144 MHz | ⭐⭐⭐⭐ | Contacts lasting a fraction of a second |
| **EME (moonbounce)** | 144, 432, 1296 MHz | ⭐⭐⭐⭐⭐ | The hardest thing an amateur can do |

---

## Build your own link

The most educational transmit projects are the ones where **you design the protocol**.

| Project | Diff | Notes |
|---|---|---|
| **Point-to-point data link** | ⭐⭐⭐ | Your own framing, your own CRC, your own modulation. [Fundamentals 08](../01_fundamentals/08_digital_modulation.md) and [10](../01_fundamentals/10_error_detection_and_framing.md) are exactly this |
| **Add FEC to your link** | ⭐⭐⭐⭐ | Convolutional + Viterbi, then measure the coding gain against your uncoded BER curve |
| **Adaptive modulation** | ⭐⭐⭐⭐ | Change constellation with SNR — the idea behind every modern standard |
| **ARQ / retransmission** | ⭐⭐⭐⭐ | Reliability on top of an unreliable channel |
| **OFDM from scratch** | ⭐⭐⭐⭐⭐ | Cyclic prefix, pilots, channel estimation. The foundation of Wi-Fi, LTE, DAB, DVB |
| **Spread spectrum link** | ⭐⭐⭐⭐ | DSSS or frequency hopping. Understand GPS from the transmit side |
| **MIMO 2×2** | ⭐⭐⭐⭐⭐ | **Your B210 has two TX and two RX channels** — genuine MIMO is possible |
| **Full-duplex experiments** | ⭐⭐⭐⭐⭐ | Self-interference cancellation. An active research area |
| **Mesh networking** | ⭐⭐⭐⭐⭐ | Routing over your own radio links |

---

## Simulation and emulation (cabled, shielded)

| Project | Diff | Notes |
|---|---|---|
| **GNSS signal simulation** | ⭐⭐⭐⭐⭐ | ⛔ **Cable and shielded chamber only, never radiated.** `gps-sdr-sim` generates a fake constellation for receiver testing |
| **Channel emulator** | ⭐⭐⭐⭐ | Reproduce multipath, fading and Doppler for repeatable receiver tests |
| **Interference generator (in a chamber)** | ⭐⭐⭐⭐ | Test how your receiver copes with a hostile environment |
| **Protocol conformance testing** | ⭐⭐⭐⭐ | Transmit deliberately malformed frames at your own device |
| **Private GSM/LTE lab network** | ⭐⭐⭐⭐⭐ | ⛔ Shielded enclosure and your own SIMs only. `srsRAN`, `OpenBTS`, `YateBTS` |
| **Replay of recorded IQ** | ⭐⭐⭐ | Transmit a Lab 05 recording back — a perfect end-to-end system test |

---

## Try this first: transmit into your own receiver

You need no licence and no antenna for the most instructive transmit experiment there is.

```
   TX port ──[ 30 dB attenuator ]──[ 20 dB attenuator ]── RX port
                (or a dummy load with deliberate leakage)
```

Then take [Lab 07](../02_flowgraphs/lab07_bpsk_link_sim/README.md) and **replace the Channel
Model with real hardware**:

```
Vector Source -> Diff Encoder -> Chunks to Symbols -> RRC -> [ USRP SINK ]
                                                                   ║ cable
[ USRP SOURCE ] -> Symbol Sync -> Costas -> Slicer -> Diff Decoder -> BER Monitor
```

Everything else stays identical. Now measure BER again — and watch it get **worse** than the
simulation predicted, because real hardware adds:

- LO phase noise (the Costas loop has to chase it)
- IQ imbalance and DC offset
- A real, sloppier frequency offset between TX and RX
- Quantisation and amplifier nonlinearity

**Quantifying that gap is the most valuable single experiment in this entire repository.** It is
the difference between "my simulation works" and "my radio works", and there is no substitute for
measuring it yourself.

---

## Then: WSPR, and let the world tell you it heard you

Once licensed, WSPR is the most rewarding low-power transmission there is. Two hundred milliwatts,
a wire antenna, and 110 seconds of transmission — and within minutes strangers' receivers on
other continents upload reports of your signal to a public database, with distance and
signal-to-noise for each path.

You will have built a transmitter, and the world will have independently verified it.

---

[← Test & Measurement](./14_test_measurement_and_infrastructure.md) · [Catalogue index](./README.md) · [Next: Oddities →](./16_oddities_and_historical.md)
