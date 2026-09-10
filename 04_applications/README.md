# 🌍 Part 4 — The Applications Catalogue

> **What is actually out there, what it takes to receive it, and where to start.**
>
> Labs 01–09 taught you *how* to build a receiver. This part answers the question that
> naturally follows: **what should I point it at?**

---

## 🧭 How to Use This Catalogue

Every entry follows the same format so you can scan for something that matches your hardware,
your skill level and your patience:

| Column | Meaning |
|---|---|
| **Signal** | What it is |
| **Frequency** | Where to tune. Regional variants are noted |
| **Mode** | Modulation and coding |
| **Diff** | Difficulty, ⭐ to ⭐⭐⭐⭐⭐ (see below) |
| **Needs** | Hardware beyond the bare SDR |
| **Build on** | Which labs and fundamentals prepare you for it |

### Difficulty scale

| | Level | You are ready after | Typical effort |
|---|---|---|---|
| ⭐ | **Beginner** | Lab 03 | An afternoon |
| ⭐⭐ | **Intermediate** | Lab 05–06 | A weekend |
| ⭐⭐⭐ | **Advanced** | Lab 07–08 | Days; needs sync and framing |
| ⭐⭐⭐⭐ | **Expert** | Lab 09 | Weeks; custom DSP, FEC, hard RF |
| ⭐⭐⭐⭐⭐ | **Research** | — | Months; specialist hardware or genuinely open problems |

### Hardware symbols

| | Meaning |
|---|---|
| ✅ | Works directly with the SignalSDR Pro and a suitable antenna |
| 🔻 | **Below 70 MHz** — needs an upconverter (or a different SDR) |
| 🔺 | **Above 6 GHz** — needs a downconverter or LNB |
| 📡 | Needs a specific or directional antenna |
| 🔊 | Needs a low-noise amplifier, ideally at the antenna |
| 🧊 | Needs a filter to survive strong nearby transmitters |
| 🖥️ | Needs serious CPU, or wide instantaneous bandwidth |

### Legal symbols

| | Meaning |
|---|---|
| 🟢 | Reception generally unrestricted |
| 🟡 | Reception usually fine; **acting on, recording or sharing may not be** |
| 🔴 | Transmission requires a licence |
| ⛔ | Interception or decryption is prohibited in most jurisdictions |

> ⚖️ **These symbols are a prompt to think, not legal advice.** Radio law varies enormously —
> what is a normal hobby in one country is a criminal offence in another. Before you receive
> anything other than broadcast radio, look up your own regulator's rules. Before you
> *transmit* anything at all, get licensed. See [Law & Ethics](#-law--ethics) below.

---

## 📚 The Catalogue

| # | Domain | Entries | Highlights |
|---|---|---|---|
| 01 | [Broadcast & Media](./01_broadcast_and_media.md) | 32 | FM, AM, shortwave, DAB, DVB-T, HD Radio |
| 02 | [Aviation](./02_aviation.md) | 32 | ADS-B, ACARS, airband, VOR/ILS, CPDLC |
| 03 | [Maritime](./03_maritime.md) | 26 | AIS, NAVTEX, DSC, EPIRB, radar |
| 04 | [Satellite & Space](./04_satellite_and_space.md) | 40 | NOAA/Meteor imagery, GOES, Inmarsat, Iridium, cubesats |
| 05 | [Weather & Environment](./05_weather_and_environment.md) | 29 | Radiosondes, lightning, meteor scatter, ionosondes |
| 06 | [Land Mobile & Professional](./06_land_mobile_and_professional.md) | 42 | DMR, P25, TETRA, trunking, SCADA, railway |
| 07 | [Amateur Radio](./07_amateur_radio.md) | 39 | FT8, WSPR, APRS, SSTV, EME, packet |
| 08 | [IoT, ISM & Short Range](./08_iot_ism_and_short_range.md) | 59 | LoRa, TPMS, smart meters, key fobs, BLE, Zigbee |
| 09 | [Cellular](./09_cellular.md) | 29 | GSM, UMTS, LTE, 5G NR, NB-IoT |
| 10 | [Navigation & Timing](./10_navigation_and_timing.md) | 37 | GPS/GNSS, time stations, eLoran, beacons |
| 11 | [Radar & Sensing](./11_radar_and_sensing.md) | 35 | Passive radar, FMCW, Doppler, SAR, altimeters |
| 12 | [Science & Radio Astronomy](./12_science_and_radio_astronomy.md) | 29 | Hydrogen line, Jupiter, solar bursts, pulsars |
| 13 | [Security Research](./13_security_research.md) | 36 | Replay attacks, protocol RE, fingerprinting, jamming study |
| 14 | [Test, Measurement & Infrastructure](./14_test_measurement_and_infrastructure.md) | 42 | Spectrum monitoring, DF, antenna measurement, EMC |
| 15 | [Transmit Projects](./15_transmit_projects.md) | 39 | Beacons, repeaters, custom links, GNSS simulation |
| 16 | [Oddities & Historical](./16_oddities_and_historical.md) | 43 | Numbers stations, the Buzzer, NDBs, teletype, fax |
| | **Total** | **589** | |

---

## 📶 The Spectrum at a Glance

Where everything lives, and what your SignalSDR Pro can reach directly.

```
        ┌─────────────────────── needs an upconverter ───────────────────────┐
 3 kHz         30 kHz        300 kHz        3 MHz         30 MHz         70 MHz
   │             │              │             │              │              │
   │  VLF        │   LF         │   MF        │     HF       │    low VHF   │
   │  submarine  │  time sigs   │  AM broad-  │  shortwave   │  6 m ham     │
   │  lightning  │  NDB, eLoran │  cast, ham  │  ham, RTTY   │  meteor      │
   ├─────────────┴──────────────┴─────────────┴──────────────┴──────────────┤

        ┌──────────── SignalSDR Pro tunes here, 70 MHz – 6 GHz ─────────────┐
 70 MHz       108      137      174     400      1 GHz      2.4 GHz     6 GHz
   │           │        │        │       │         │           │           │
   │  VHF low  │  FM    │ sats   │  DAB  │  UHF    │  GPS      │  WiFi     │
   │  airband  │ broad- │ radio- │  DVB  │ pagers  │  ADS-B    │  Bluetooth│
   │  106-137  │ cast   │ sondes │  TETRA│ ISM 433 │  Inmarsat │  ISM 5.8  │
   │           │ 88-108 │ 137    │ P25   │ LoRa    │  Iridium  │  radar    │
   ├───────────┴────────┴────────┴───────┴─────────┴───────────┴───────────┤

        ┌──────────────── needs a downconverter / LNB ───────────────────────┐
  6 GHz          10 GHz          12 GHz          24 GHz            77 GHz
   │  C band       X band          Ku band         K band           W band
   │  satellite    weather radar   TV sats         motion sensors   car radar
   │                               Starlink        amateur 24 GHz
   └────────────────────────────────────────────────────────────────────────┘
```

**The practical consequence:** your hardware covers the busiest 85 % of what a hobbyist wants,
but **not HF**. Shortwave, amateur HF, NDBs, time stations and numbers stations all sit below
70 MHz. A cheap upconverter (or a second SDR with direct sampling) opens that up, and it is the
single best accessory purchase after an antenna.

---

## 🚀 Where to Start — A Suggested Path

You do not have to follow this, but it climbs steadily and each rung genuinely prepares the next.

### Rung 1 — Everything you can hear this week (⭐)

You already have the skills. Only the antenna changes.

| Signal | Why start here |
|---|---|
| [FM broadcast + RDS](./01_broadcast_and_media.md) | Labs 01–08 already did it |
| [NOAA Weather Radio](./06_land_mobile_and_professional.md) | 24/7, strong, trivially found (North America) |
| [Airband AM](./02_aviation.md) | Lab 06 handles it; teaches bursty-signal hunting |
| [Marine VHF](./03_maritime.md) | Same, if you are near water |
| [Pagers (POCSAG)](./06_land_mobile_and_professional.md) | Simplest real *data* decode there is |

### Rung 2 — Your first satellite (⭐⭐)

| Signal | Why |
|---|---|
| [NOAA APT weather images](./04_satellite_and_space.md) | **The best second project in all of SDR.** You get a picture of the Earth, taken minutes ago, from a $5 antenna |
| [ISS SSTV](./04_satellite_and_space.md) | Same skills, more novelty |
| [Radiosondes](./05_weather_and_environment.md) | Balloons launched twice daily worldwide; you can go and find them |

### Rung 3 — Real data links (⭐⭐⭐)

| Signal | Why |
|---|---|
| [ADS-B](./02_aviation.md) | Lab 09 already built the decoder |
| [AIS](./03_maritime.md) | Ships instead of planes; GMSK instead of PPM |
| [ACARS](./02_aviation.md) | Aircraft text messages; simple and readable |
| [LoRa](./08_iot_ism_and_short_range.md) | Chirp spread spectrum — genuinely new DSP |
| [FT8 / WSPR](./07_amateur_radio.md) | Weak-signal decoding far below the noise floor 🔻 |

### Rung 4 — Where it gets hard (⭐⭐⭐⭐)

| Signal | Why |
|---|---|
| [Meteor-M LRPT](./04_satellite_and_space.md) | QPSK + Viterbi + image reconstruction |
| [GOES HRIT](./04_satellite_and_space.md) | Full-disc Earth images, but needs a dish and an LNA |
| [GPS from scratch](./10_navigation_and_timing.md) | Correlate a signal 20 dB *below* the noise |
| [Passive radar](./11_radar_and_sensing.md) | Detect aircraft using a broadcast transmitter you do not own |
| [Hydrogen line](./12_science_and_radio_astronomy.md) | Measure the rotation of the Milky Way from your garden |

### Rung 5 — Transmit (⭐⭐⭐⭐⭐, and get licensed first)

| Project | Why |
|---|---|
| [Amateur beacon / WSPR TX](./15_transmit_projects.md) | Your signal, reported by strangers worldwide |
| [Custom digital link](./15_transmit_projects.md) | Lab 07, but over the air |
| [Your own repeater or gateway](./15_transmit_projects.md) | Infrastructure other people use |

---

## 🧰 What You Actually Need Beyond the SDR

In order of how much difference it makes:

| Priority | Item | Why | Rough cost |
|---|---|---|---|
| **1** | **The right antenna** | Nothing else comes close. A resonant antenna for *your* band beats any amount of gain or DSP | $0–40 |
| **2** | **Get it outside and high** | Every wall costs ~10 dB; every metre of height extends the horizon | $0 |
| **3** | **Short, decent coax** | RG-58 loses ~1 dB/m at 1 GHz. Use RG-6 or LMR-240 | $10–30 |
| **4** | **LNA at the antenna** | Friis: the first stage sets your noise figure ([Fund. 06](../01_fundamentals/06_noise_snr_and_gain.md)) | $15–40 |
| **5** | **Band-pass / FM-notch filter** | Strong broadcast stations desensitise everything else | $10–30 |
| **6** | **Upconverter** | Opens HF: shortwave, ham, NDBs, time signals, numbers stations | $30–60 |
| **7** | **Dish + LNB** | Geostationary satellites, GOES, Ku band | $50–150 |
| **8** | **GPS-disciplined clock** | Sub-ppm frequency accuracy. **Your SignalSDR Pro already has one built in** | — |

### Antenna quick reference

$$
\lambda = \frac{300}{f_{\text{MHz}}} \text{ metres}, \qquad
\text{quarter wave} = \frac{75}{f_{\text{MHz}}} \text{ metres} = \frac{75000}{f_{\text{MHz}}} \text{ mm}
$$

| Band | Frequency | ¼-wave element |
|---|---|---|
| Airband | 127 MHz | 590 mm |
| FM broadcast | 98 MHz | 765 mm |
| Weather satellites | 137 MHz | 547 mm |
| 2 m amateur / marine | 145–160 MHz | 470–517 mm |
| Radiosondes | 403 MHz | 186 mm |
| 70 cm amateur | 435 MHz | 172 mm |
| ISM | 868 MHz | 86 mm |
| ISM | 915 MHz | 82 mm |
| ADS-B | 1090 MHz | **69 mm** |
| GPS L1 | 1575 MHz | 48 mm |
| Wi-Fi / BLE | 2450 MHz | 31 mm |

```bash
python3 -c "
f = float(input('frequency in MHz: '))
print(f'wavelength     {300/f*1000:8.1f} mm')
print(f'quarter wave   {75/f*1000:8.1f} mm')
print(f'half wave      {150/f*1000:8.1f} mm')
print(f'5/8 wave       {187.5/f*1000:8.1f} mm')"
```

---

## ⚖️ Law & Ethics

This catalogue lists what exists. It is not permission to receive it.

### Three questions before you tune

1. **Am I allowed to receive this?** In most of Europe and the Commonwealth, receiving anything
   *not addressed to you* is technically restricted even if it is unencrypted. In the USA the
   ECPA permits receiving most unencrypted transmissions but forbids cellular and encrypted
   traffic. In some countries owning a scanner at all requires a permit. **Look it up.**
2. **Am I allowed to act on it, record it, or share it?** Very often the answer differs from
   question 1. Receiving an aircraft transmission may be legal while publishing it is not.
3. **Would I be comfortable explaining this to the operator?** A good instinct where the law is
   ambiguous.

### Bright lines that hold nearly everywhere

- ⛔ **Never decrypt encrypted traffic.** Not "for research", not "it was easy".
- ⛔ **Never transmit on emergency, aviation, maritime distress, or public-safety frequencies.**
  People die.
- ⛔ **Never inject false data** into a safety system — ADS-B, AIS, GNSS. This is prosecuted as
  endangerment, not as a computer offence.
- ⛔ **Never jam.** Deliberate interference is a criminal offence in every country.
- 🔴 **Do not transmit without a licence**, on any band, including "just a test". Your
  SignalSDR Pro can transmit from 70 MHz to 6 GHz — it will happily radiate into an air traffic
  control channel if you tell it to.
- 🟡 **Security research needs authorization.** Testing your own car key is fine. Testing your
  neighbour's is a crime.

### The one that catches people out

**Receiving is passive; transmitting is not.** A misconfigured flowgraph, a wrong digit in a
frequency box, or a stray `uhd_usrp_sink` can put you on the air by accident. When you start
Part 15, **use a dummy load or an attenuator until you are certain what is coming out.**

---

## 🤝 Contributing

This catalogue is intended to grow. If you receive something that is not listed, or find that a
frequency here is wrong for your region, add it:

- Keep the table format so it stays scannable
- State the **actual frequency you used**, not the nominal band
- Note the antenna and any extra hardware — that is usually the deciding factor
- Say what your success rate was, honestly. "Worked once at 3 a.m." is useful information
- Add the legal symbol for **your** jurisdiction and name the jurisdiction

---

**Start here:** [01 — Broadcast & Media →](./01_broadcast_and_media.md)

**Back to:** [Lab 09 — ADS-B](../02_flowgraphs/lab09_adsb_receiver/README.md) · [Repository home](../README.md)
