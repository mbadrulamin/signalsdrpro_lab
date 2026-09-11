# 🇲🇾 Malaysia Reference

> Everything location-specific in one place: what is on the air here, which bands you may
> legally transmit in, how to get licensed, and where the community is.
>
> ⚠️ **This is orientation, not legal advice.** Rules change. The authoritative sources are
> linked throughout — check them before relying on anything here.

---

## 1. The regulator and its documents

Spectrum in Malaysia is administered by the **Malaysian Communications and Multimedia
Commission** (MCMC / SKMM) under the **Communications and Multimedia Act 1998**.

| Document | What it tells you | Link |
|---|---|---|
| **Spectrum Plan** | The Malaysian Table of Frequency Allocations — which service owns which band | [PDF](https://www.mcmc.gov.my/skmmgovmy/media/General/MCMC-Spectrum-Plan-2022.pdf) |
| **Class Assignment** | Bands you may transmit in **without an individual licence**, and the power limits. Revised periodically | [Page](https://www.mcmc.gov.my/en/spectrum/assignment-of-spectrum/class-assignment) |
| **Spectrum Assignment** | Who holds the licensed bands | [Page](https://www.mcmc.gov.my/en/spectrum/assignment-of-spectrum/spectrum-assignment) |
| **Amateur Radio Service in Malaysia** | Licensing, examinations, callsigns, band plan | [PDF](https://www.mcmc.gov.my/skmmgovmy/media/General/pdf2/Amateur-Radio-Service-in-Malaysia-3rd-Edition_v1.pdf) |
| **Call Sign Guidelines** | How callsigns are allocated | [PDF](https://www.mcmc.gov.my/skmmgovmy/media/General/pdf/Guideline-on-the-Allocation-of-Call-Sign-to-the-Amateur-Radio-Service.pdf) |
| **SEMS portal** | Where you register for the examination | [sems.skmm.gov.my](https://sems.skmm.gov.my/) |
| **AAIG portal** | Amateur apparatus assignment and callsign services | [aaig.mcmc.gov.my](https://aaig.mcmc.gov.my/) |

---

## 2. What is on the air here

![Radio spectrum in Malaysia](../images/malaysia_spectrum.svg)

### 2.1 Bands worth pointing an SDR at

| Band | Service | Notes |
|---|---|---|
| 526.5 – 1606.5 kHz | MW broadcast | 🔻 Needs an upconverter |
| 3.9 – 26.1 MHz | Shortwave broadcast | 🔻 Regional broadcasters, best at night |
| **87.5 – 108 MHz** | **FM broadcasting** | Where [Labs 01–08](../02_flowgraphs/lab01_simple_wbfm/README.md) live |
| 108 – 137 MHz | Aeronautical — AM voice, VOR/ILS | Busy near KLIA, Subang, Penang, Kota Kinabalu |
| 144 – 148 MHz | Amateur 2 m | Repeaters, APRS on 144.800 |
| 156 – 162 MHz | Maritime VHF and AIS | Excellent along the Straits of Malacca — one of the world's busiest shipping lanes |
| 400 – 406 MHz | Radiosondes | Launched from Malaysian Meteorological Department sites |
| **433 – 435 MHz** | **Licence-exempt SRD** | Remotes, sensors, TPMS |
| 430 – 440 MHz | Amateur 70 cm | |
| **470 – 694 MHz** | **DTT — DVB-T2 (MYTV / MyFreeview)** | [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md) |
| 703 – 803 MHz | Mobile 700 MHz (n28) | Refarmed after the 2019 analogue TV switch-off |
| 880 – 960 MHz | Mobile 900 | |
| **919 – 923 MHz** | **Licence-exempt SRD — LoRa AS923** | See the warning below |
| 1090 MHz | ADS-B | [Lab 09](../02_flowgraphs/lab09_adsb_receiver/README.md). Very busy — KL is a major hub |
| 1575.42 MHz | GPS L1 | |
| 1710 – 2170 MHz | Mobile 1800 / 2100 | |
| 2400 – 2500 MHz | **Licence-exempt** — Wi-Fi, Bluetooth | |
| 3.3 – 3.8 GHz | 5G mid-band (n78) | |

### 2.2 A measured FM band survey

This is **not** from a database — it is what this repository's own SignalSDR Pro actually heard,
scanning 88–108 MHz and testing every 100 kHz channel for a 19 kHz stereo pilot:

| Frequency | Pilot strength | RDS? |
|---|---|---|
| **89.90 MHz** | **23.2 dB** | ✅ **Yes** — decoded, see below |
| 91.50 MHz | 18.4 dB | ✗ none decoded |
| 92.90 MHz | 16.5 dB | — |
| 100.10 MHz | 14.1 dB | ✗ none decoded |
| 102.50 MHz | 10.8 dB | — |
| 90.40 MHz | 10.4 dB | — |
| 89.40 MHz | 9.1 dB | — |
| 97.60 MHz | 8.5 dB | — |
| 105.70 MHz | 8.4 dB | — |
| 106.70 MHz | 8.0 dB | — |

**89.9 MHz carries RDS**, and [Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md) decoded it:
287 CRC-valid groups in 30 seconds (84 % of the theoretical maximum), PI code `0x6000`, with a
**scrolling** programme-service name:

```
seg0 'BU'  seg1 'SI'  seg2 'NE'  seg3 'SS'   ->  "BUSINESS"
seg0 'BF'  seg1 'M '  seg2 '89'  seg3 '.9'   ->  "BFM 89.9"
seg0 'FI'  seg1 'NA'  seg2 'NC'  seg3 'E '   ->  "FINANCE "
```

Of five stations surveyed, only 89.9 yielded RDS groups here. **Your results will differ by
location** — run the survey yourself; it is a good first project.

> 📻 **Note for Lab 08:** BFM 89.9 uses a *dynamic* PS, so the 8-character name never settles.
> That is the station's choice, not a decoder fault.

---

## 3. Getting licensed to transmit

**Receiving is largely unrestricted. Transmitting is not.** The realistic and legitimate route
to transmitting is an **amateur radio licence**, and in Malaysia it is genuinely accessible.

### 3.1 The three classes

| Exam | Class | Callsign prefix | Notes |
|---|---|---|---|
| **RAE Class C** | Entry level | **9W3**xxx | Nationwide, valid across all regions |
| **RAE Class B** | Standard | **9W2** / 9W6 / 9W8 | |
| **RAE Class A** | Full / Advanced | **9M2** / 9M6 / 9M8 | Widest privileges |

The regional digit reflects where the licence was issued: **2** Peninsular Malaysia, **6** Sabah,
**8** Sarawak.

### 3.2 The process

1. **Study.** [MARTS](https://marts.org.my/) and other clubs run classes and publish materials.
   The syllabus covers regulations, operating practice and basic technical theory — much of
   which is in [Fundamentals 01–06](../01_fundamentals/01_signals_basics.md) of this repository.
2. **Register for the RAE** on the [SEMS portal](https://sems.skmm.gov.my/) and pay the fee.
3. **Sit the examination.**
4. **Apply for the ASAA** (Amateur Station Apparatus Assignment) and your callsign via the
   [AAIG portal](https://aaig.mcmc.gov.my/).
5. **Transmit**, within your class's privileges.

> 💡 **Why bother?** Because it converts your SignalSDR Pro from a receiver into a transceiver
> *legally*. [Part 4 §15 — Transmit Projects](../04_applications/15_transmit_projects.md) is
> largely locked behind this one step.

---

## 4. Licence-exempt bands (Class Assignment)

The only bands in which you may transmit **without** an individual assignment, and only within
these limits. **Verify against the current Class Assignment** — it is revised periodically.

| Band | Limit | Typical use |
|---|---|---|
| **433 – 435 MHz** | 100 mW EIRP | Remotes, sensors, TPMS |
| 916 – 919 MHz | 25 mW EIRP, duty cycle < 1 % or FHSS or LBT | Low-duty telemetry |
| **919 – 923 MHz** | 500 mW EIRP | **LoRa (AS923)**, IoT, metering |
| 923 – 924 MHz | 500 mW EIRP, duty cycle < 1 % or FHSS or LBT | |
| **2400 – 2500 MHz** | 500 mW EIRP | Wi-Fi, Bluetooth, Zigbee |
| 5 GHz RLAN | per Class Assignment | Wi-Fi 5/6 |

### ⚠️ The regional trap that catches everyone

> **Malaysia's 900 MHz band is 919–923 MHz.**
>
> - Europe uses **868 MHz**
> - The Americas use **915 MHz**
> - Malaysia and much of ASEAN use **AS923 → 919–923 MHz**
>
> A LoRa module ordered from a European supplier will be configured for 868 MHz and will be
> **transmitting out of band** here. Check the region setting before you power it up. This
> single mistake is probably the commonest unintentional licence breach among Malaysian makers.

---

## 5. Lab 10 and Malaysian television

Malaysia switched off analogue television on **31 October 2019** and runs DTT entirely on
**DVB-T2** (MYTV / MyFreeview) across **470–694 MHz**.

**What this means for you:** essentially every television sold in Malaysia has a **DVB-T2 tuner
built in** — which is exactly the receiver [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md)
needs. You do not need to buy anything.

> ⛔ **But you must still transmit only inside a Faraday cage or over a cable into a dummy
> load**, and never on a channel MYTV is using. A DVB-T2 signal is indistinguishable from a real
> broadcast, so interference from it looks to a viewer — and to MCMC — exactly like a
> broadcaster's own fault.

---

## 6. Community

| Organisation | What it is |
|---|---|
| **[MARTS](https://marts.org.my/)** | Malaysian Amateur Radio Transmitters' Society — the national society. Classes, examinations, repeaters, events |
| **MARES** | Malaysian Amateur Radio Emergency Service — emergency communications |
| **[hamradio.my](https://hamradio.my/)** | Active Malaysian amateur radio blog with practical getting-started guides |
| **[MY-HamCall](https://callsign.hamradio.my/)** | Malaysian callsign lookup |
| State and district clubs | Most states have one; MARTS can point you to the nearest |

**Online:** the Lowyat.NET forums have long-running amateur radio and digital TV threads with an
active Malaysian membership.

---

## 7. Getting hardware

| Source | Notes |
|---|---|
| **Local marketplaces** (Shopee, Lazada) | RTL-SDR dongles, antennas, SMA adapters, coax — cheap and fast. Beware counterfeit "RTL-SDR v3/v4" units; buy from sellers with a track record |
| **Specialist importers** | HackRF, Airspy, SDRplay, LimeSDR. Check import duty and that the seller ships to Malaysia |
| **[Signalens](https://signalens.com/)** | The SignalSDR Pro itself |
| **Hardware shops** | Brass rod, copper wire and SMA connectors for antennas. A coat hanger from any shop works for a V-dipole |
| **Club members** | Often the best source of used equipment and, more importantly, advice |

> 🛒 **Buy an RTL-SDR (~RM 150) even though you own a SignalSDR Pro.** A second receiver lets
> you compare, lend one to a friend, leave one running as a permanent ADS-B feeder, or use two
> at once. It is the best value in the hobby.

---

## 8. The short legal summary

| Activity | Status |
|---|---|
| Receiving broadcast radio and TV | ✅ Unrestricted |
| Receiving other services | 🟡 Generally tolerated; acting on, recording or sharing may not be |
| Decrypting encrypted traffic | ⛔ Prohibited |
| Transmitting in Class Assignment bands within limits | ✅ Permitted |
| Transmitting elsewhere with an amateur licence, within privileges | ✅ Permitted |
| Transmitting elsewhere without an assignment | ⛔ **An offence under the CMA 1998** |
| Transmitting on aviation, maritime distress or emergency frequencies | ⛔ **Never. People die** |
| Jamming or interfering | ⛔ **A criminal offence** |

> Your SignalSDR Pro can transmit from 70 MHz to 6 GHz. That includes aviation, maritime
> distress and cellular bands. **Nine of this repository's ten labs are receive-only for exactly
> this reason**, and [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md) ships with its
> amplitude and gain both set to zero.

---

## 9. Project ideas with a local flavour

| Project | Why it works well here |
|---|---|
| **AIS ship tracking** | The Straits of Malacca is one of the busiest shipping lanes on Earth |
| **ADS-B** | KL is a major hub; KLIA and Subang traffic is constant |
| **Survey the FM band for RDS** | Extend the table in §2.2 — very few Malaysian stations appear to run RDS, and a proper survey would be genuinely new information |
| **Radiosondes** | MMD launches balloons on a schedule; decode and go and find one |
| **Monitor the DTT multiplexes** | Measure MYTV's signal quality across your area with [Lab 10's analyser](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md) |
| **LoRa / AS923 survey** | Map what is actually using 919–923 MHz near you |
| **Tropospheric ducting across the Straits** | Watch Indonesian and Singaporean signals appear when conditions are right |

---

**See also:** [Glossary](./01_glossary.md) · [Antennas](./03_antennas.md) ·
[Introduction to SDR](../01_fundamentals/00_introduction_to_sdr.md) ·
[Applications catalogue](../04_applications/README.md) · [Reference index](./README.md)
