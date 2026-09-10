# 📻 01 — Broadcast & Media

> **34 entries** · The signals designed to be received by everyone. The easiest place to start,
> and the only domain where reception is unambiguously legal everywhere.
>
> [← Catalogue index](./README.md) · [Next: Aviation →](./02_aviation.md)

---

## Why start here

Broadcast signals are **strong, continuous, and legal**. They are also unusually rich: a single
FM broadcast carries mono audio, a stereo subcarrier, a data channel and sometimes more, all
stacked in one 200 kHz slot. That layering is why Labs 01–08 live here — you can climb from a
three-block receiver to a CRC-checked data decoder without ever retuning.

---

## Analog radio

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **FM broadcast, mono** | 87.5–108 MHz | WBFM, ±75 kHz | ⭐ | ✅ | 🟢 [Lab 01](../02_flowgraphs/lab01_simple_wbfm/README.md). Band is 76–95 MHz in Japan, 65–74 MHz for legacy OIRT |
| **FM broadcast, stereo** | same | MPX: 19 kHz pilot + L−R DSB-SC at 38 kHz | ⭐⭐ | ✅ | 🟢 [Lab 04](../02_flowgraphs/lab04_stereo_wbfm/README.md). Costs ~20 dB SNR vs mono |
| **RDS / RBDS** | 57 kHz subcarrier | Differential BPSK, 1187.5 bit/s, biphase | ⭐⭐⭐ | ✅ | 🟢 [Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md). Station name, RadioText, traffic flags |
| **AM broadcast (MW)** | 530–1710 kHz | AM | ⭐ | 🔻📡 | 🟢 Long wire or loop antenna. Night-time skywave brings in continents |
| **AM broadcast (LW)** | 148.5–283.5 kHz | AM | ⭐ | 🔻📡 | 🟢 Europe, North Africa, Asia. Very long wavelengths |
| **Shortwave broadcast** | 3.9–26.1 MHz in bands | AM, some DRM | ⭐ | 🔻📡 | 🟢 International broadcasters. Propagation changes hour by hour |
| **SCA / SCMO subcarriers** | 67 kHz, 92 kHz in FM MPX | NBFM subcarrier | ⭐⭐⭐ | ✅ | 🟡 Reading services, background music, private data. Same extraction technique as RDS |
| **Traffic Message Channel (TMC)** | RDS group 8A | inside RDS | ⭐⭐⭐ | ✅ | 🟢 Coded traffic incidents. Extend the Lab 08 decoder |
| **RDS-TMC alternative frequencies** | RDS group 0A block C | inside RDS | ⭐⭐ | ✅ | 🟢 The list a car radio uses to follow a station while driving |
| **Pirate / community FM** | 87.5–108 MHz, edges | WBFM | ⭐ | ✅ | 🟡 Often just outside the licensed band |

---

## Digital radio

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **DAB / DAB+** | 174–240 MHz (Band III) | OFDM, DQPSK, 1.536 MHz blocks | ⭐⭐⭐ | ✅🖥️ | 🟢 `welle.io` or `gr-dab`. Multiple stations per multiplex |
| **DAB, L-band** | 1452–1492 MHz | same | ⭐⭐⭐ | ✅ | 🟢 Rare now; Canada and a few others |
| **HD Radio (IBOC)** | alongside FM/AM carriers | OFDM sidebands | ⭐⭐⭐⭐ | ✅ | 🟡 US. Proprietary codec; `nrsc5` decodes it |
| **DRM (Digital Radio Mondiale)** | HF/MW/LW | COFDM | ⭐⭐⭐ | 🔻 | 🟢 `dream` decoder. Digital audio over shortwave |
| **DRM+** | VHF Band I/II | COFDM | ⭐⭐⭐ | ✅ | 🟢 Limited deployment |
| **ISDB-Tsb** | 207–222 MHz | OFDM | ⭐⭐⭐⭐ | ✅ | 🟢 Japan digital radio |
| **CDR (China Digital Radio)** | 87–108 MHz | OFDM in-band | ⭐⭐⭐⭐ | ✅ | 🟢 China |

---

## Television

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **DVB-T / DVB-T2** | 470–790 MHz | COFDM, 8 MHz channels | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Needs ≥8 MHz bandwidth. Also the best **passive radar** illuminator |
| **ATSC 1.0** | 54–88, 174–216, 470–608 MHz | 8-VSB, 6 MHz | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 North America |
| **ATSC 3.0 (NextGen TV)** | same | OFDM, LDPC | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟢 Newer, more complex |
| **ISDB-T** | 470–770 MHz | OFDM segments | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Japan, South America |
| **DTMB** | 470–806 MHz | TDS-OFDM | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 China |
| **Analog TV (PAL/NTSC/SECAM)** | legacy VHF/UHF | VSB video + FM audio | ⭐⭐ | ✅ | 🟢 Mostly switched off, but still active in some regions and by amateurs |
| **DVB-S / S2 (satellite TV)** | 10.7–12.75 GHz | QPSK/8PSK, LDPC | ⭐⭐⭐⭐ | 🔺📡 | 🟢 Needs a dish and LNB. Enormous data rates |
| **Broadcast auxiliary / ENG links** | 2, 7, 13 GHz | various | ⭐⭐⭐⭐ | 🔺📡 | 🟡 Outside-broadcast trucks feeding the studio |

---

## Studio, production and venue links

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Wireless microphones** | 470–698 MHz, 1.8 GHz, 2.4 GHz | NBFM or digital | ⭐⭐ | ✅ | 🟡 Theatre, church, conference. Often in TV "white space" |
| **In-ear monitors (IEM)** | 470–870 MHz | NBFM stereo | ⭐⭐ | ✅ | 🟡 What performers hear on stage |
| **Wireless intercom** | 1.9 GHz (DECT), 2.4 GHz | digital | ⭐⭐⭐ | ✅ | 🟡 Production crew talkback |
| **Studio-transmitter links (STL)** | 300–960 MHz, 7 GHz | FM or digital | ⭐⭐⭐ | ✅📡 | 🟡 How the studio feeds the transmitter site |
| **Assistive listening systems** | 72–76 MHz, 216–217 MHz | NBFM | ⭐ | ✅ | 🟡 Cinemas, museums, places of worship |
| **Drive-in cinema / talking house** | 87.5–108 MHz | WBFM, low power | ⭐ | ✅ | 🟢 Tiny licensed-exempt transmitters |
| **Radio-controlled clock broadcasts** | see [Navigation & Timing](./10_navigation_and_timing.md) | | | | |

---

## Try this first

**Sweep the entire FM band and log every station's RDS.** You already have every piece:

```bash
# Lab 08's decoder, driven across the band
cd 02_flowgraphs/lab08_rds_decoder
# capture 12 s per station with Lab 05's recorder, then decode each file
```

You will discover, as this repo's own verification did, that **the decoder is far more sensitive
than the spectrum display** — stations that show no visible 57 kHz hump often decode perfectly.
Build a table of PI code, station name and PTY for your area. It takes an evening and it turns
the FM band from noise into a map.

---

## Going deeper

- **Extend Lab 08** to decode group types 4A (clock/date), 8A (traffic), and 14A (other networks)
- **Decode the SCA subcarrier** at 67 kHz — same technique as RDS, different centre frequency
- **Compare an HD Radio station's analog and digital audio** and measure the delay between them
- **Use DVB-T as a passive radar illuminator** — see [Radar & Sensing](./11_radar_and_sensing.md)

---

[← Catalogue index](./README.md) · [Next: Aviation →](./02_aviation.md)
