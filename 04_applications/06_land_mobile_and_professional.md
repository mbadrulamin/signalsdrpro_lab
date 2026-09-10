# 📟 06 — Land Mobile & Professional

> Everything from a builder's walkie-talkie to a nationwide public-safety network. This is the
> busiest part of VHF/UHF and the domain where **legal restrictions bite hardest** — read the
> warning before you scan.
>
> [← Weather](./05_weather_and_environment.md) · [Catalogue index](./README.md) · [Next: Amateur Radio →](./07_amateur_radio.md)

---

## ⚖️ Read this first

Land mobile radio is where hobbyists most often cross a legal line without realising it.

- **Public safety** (police, fire, ambulance) is **explicitly protected** in many jurisdictions.
  In the UK, receiving it is an offence under the Wireless Telegraphy Act. In parts of the USA
  it is legal to listen but illegal to use a scanner in a vehicle. In Australia and Canada rules
  differ again, by state and province.
- **Encrypted traffic** — most modern P25 and TETRA systems — is ⛔ **off limits everywhere**.
  Not to decrypt, not to attempt, not "for research".
- **Business and utility traffic** is usually 🟡: technically restricted to the licensee, rarely
  enforced against passive listeners, but you have no right to it.

**The safe subset:** [NOAA Weather Radio](#public-information-and-utility), unlicensed PMR446 /
FRS, amateur repeaters, and anything explicitly broadcast to the public. Start there.

---

## Analog voice systems

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **PMR446** | 446.0–446.2 MHz | NBFM, 12.5 kHz | ⭐ | ✅ | 🟢 Licence-exempt in Europe. [Lab 06](../02_flowgraphs/lab06_multimode_receiver/README.md) handles it directly |
| **FRS / GMRS** | 462, 467 MHz | NBFM | ⭐ | ✅ | 🟢 North America. FRS is licence-free |
| **MURS** | 151–154 MHz | NBFM | ⭐ | ✅ | 🟢 USA, licence-free |
| **CB radio** | 26.965–27.405 MHz | AM / SSB | ⭐ | 🔻 | 🟢 Still busy in many countries |
| **Business band (VHF)** | 150–174 MHz | NBFM | ⭐ | ✅ | 🟡 Taxis, security, site crews |
| **Business band (UHF)** | 450–470 MHz | NBFM | ⭐ | ✅ | 🟡 |
| **CTCSS tone squelch** | 67.0–250.3 Hz sub-audible | tone under voice | ⭐⭐ | ✅ | 🟢 Decode it to identify user groups. High-pass at 300 Hz to remove it from audio |
| **DCS (digital coded squelch)** | 23-bit Golay code, ~134 baud | sub-audible data | ⭐⭐⭐ | ✅ | 🟢 The digital successor to CTCSS |
| **Two-tone sequential paging** | VHF/UHF | tone pairs | ⭐⭐ | ✅ | 🟡 Fire service alerting, especially volunteer departments |
| **Repeater tails and idents** | VHF/UHF | Morse or voice | ⭐ | ✅ | 🟢 Every repeater identifies itself periodically |

---

## Digital voice systems

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **DMR (Tier I/II/III)** | VHF/UHF | 4FSK, 2 timeslots, AMBE+2 | ⭐⭐⭐⭐ | ✅ | 🟡 Very widespread. Metadata decodes easily; audio needs a vocoder |
| **dPMR** | VHF/UHF | 4FSK, 6.25 kHz | ⭐⭐⭐⭐ | ✅ | 🟡 European narrowband digital |
| **NXDN** | VHF/UHF | 4FSK, 6.25/12.5 kHz | ⭐⭐⭐⭐ | ✅ | 🟡 Kenwood/Icom systems |
| **P25 Phase 1** | 136–174, 380–520, 700/800 MHz | C4FM, IMBE | ⭐⭐⭐⭐ | ✅ | 🟡/⛔ Public safety. **Often encrypted** |
| **P25 Phase 2** | 700/800 MHz | H-DQPSK, TDMA | ⭐⭐⭐⭐⭐ | ✅ | 🟡/⛔ |
| **TETRA** | 380–400, 410–430 MHz | π/4-DQPSK, TDMA | ⭐⭐⭐⭐ | ✅🖥️ | 🟡/⛔ European public safety and transport |
| **Tetrapol** | 380–400 MHz | GMSK | ⭐⭐⭐⭐ | ✅ | 🟡/⛔ France and others |
| **D-STAR** | amateur VHF/UHF | GMSK, AMBE | ⭐⭐⭐⭐ | ✅ | 🟢 Amateur — see [Amateur Radio](./07_amateur_radio.md) |
| **System Fusion (C4FM)** | amateur VHF/UHF | C4FM | ⭐⭐⭐⭐ | ✅ | 🟢 Amateur |
| **MotoTRBO trunking** | UHF | DMR Tier III | ⭐⭐⭐⭐⭐ | ✅ | 🟡 Follow the control channel to track calls |

---

## Trunked system control

Trunked networks assign a voice channel dynamically. To follow a conversation you must decode
the **control channel** and retune — which makes them an excellent multi-channel SDR project.

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Motorola SmartNet / SmartZone** | 800 MHz | 3600 baud control | ⭐⭐⭐⭐ | ✅🖥️ | 🟡 Classic analog trunking |
| **EDACS** | 800 MHz | GE/Ericsson control | ⭐⭐⭐⭐ | ✅🖥️ | 🟡 |
| **LTR** | UHF/800 MHz | sub-audible control | ⭐⭐⭐ | ✅ | 🟡 Simple, still in use |
| **P25 trunking control channel** | 700/800 MHz | C4FM data | ⭐⭐⭐⭐ | ✅🖥️ | 🟡 |
| **DMR Tier III control** | UHF | 4FSK data | ⭐⭐⭐⭐ | ✅🖥️ | 🟡 |
| **TETRA MCCH** | 380–430 MHz | main control channel | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟡 |

---

## Paging & messaging

**The best entry point in this whole domain** — paging is unencrypted by design, simple to
decode, and still widely used by hospitals and emergency services.

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **POCSAG** | 138–174, 450–470, 929 MHz | FSK 512/1200/2400 baud | ⭐⭐ | ✅ | 🟡 **The simplest real data decode there is.** Plain text messages |
| **FLEX** | 929–932 MHz | 4FSK 1600–6400 bps | ⭐⭐⭐ | ✅ | 🟡 Higher capacity American system |
| **ERMES** | 169 MHz | 4FSK | ⭐⭐⭐ | ✅ | 🟡 European, largely retired |
| **ReFLEX** | 900 MHz | two-way paging | ⭐⭐⭐⭐ | ✅ | 🟡 |

> ⚠️ **Pager traffic frequently contains patient names and addresses.** It is trivially
> decodable and that is precisely why decoding it responsibly matters. Decode it to learn FSK;
> do not store it, and never publish it.

---

## Public information and utility

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **NOAA Weather Radio** | 162.400–162.550 MHz (7 ch) | NBFM voice | ⭐ | ✅ | 🟢 **24/7, strong, unrestricted.** Ideal for testing an NBFM chain |
| **SAME / EAS alert headers** | on NWR and broadcast | AFSK 520.83 baud | ⭐⭐ | ✅ | 🟢 The digital burst before an emergency alert. Fully documented |
| **Environment Canada Weatheradio** | 162 MHz | NBFM | ⭐ | ✅ | 🟢 |
| **Traffic advisory (HAR)** | 530, 1610 kHz | AM | ⭐ | 🔻 | 🟢 Low-power roadside information stations |
| **Railway voice** | 160–161 MHz (AAR channels) | NBFM | ⭐ | ✅ | 🟡 |
| **End-of-Train (EOT/FRED)** | 452.9375, 457.9375 MHz | FSK bursts | ⭐⭐⭐ | ✅ | 🟡 Brake-pressure telemetry from the last wagon |
| **Hot box detectors** | 160 MHz | synthesised voice | ⭐ | ✅ | 🟡 Trackside axle-temperature announcements |
| **PTC (Positive Train Control)** | 220 MHz | digital | ⭐⭐⭐⭐ | ✅ | 🟡 |
| **SCADA / utility telemetry** | VHF/UHF, 450 MHz | FSK, proprietary | ⭐⭐⭐⭐ | ✅ | 🟡 Water, gas and power infrastructure |
| **AMR smart meters** | 900 MHz (ERT), 868 MHz (wM-Bus) | OOK/FSK | ⭐⭐⭐ | ✅ | 🟡 See [IoT](./08_iot_ism_and_short_range.md) |
| **Wireless alarm / telecare** | 169, 433, 868 MHz | FSK | ⭐⭐⭐ | ✅ | 🟡 |
| **Taxi / dispatch data** | VHF/UHF | FFSK | ⭐⭐⭐ | ✅ | 🟡 |

---

## Try this first: POCSAG

If [Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md) taught you RDS, POCSAG will take you an
hour. It is **simpler in every respect**: plain 2-FSK, no biphase coding, no differential
encoding, a 32-bit sync word instead of a self-synchronising CRC, and messages in readable ASCII.

```
NBFM demodulate → slice at zero → find 0x7CD215D8 sync word
  → 16 codewords per batch → BCH(31,21) check → 7-bit ASCII
```

The chain reuses your Lab 06 NBFM receiver verbatim; only the block after the demodulator is new.
It is the clearest possible demonstration that once you understand *one* framed digital protocol,
the rest are variations.

---

[← Weather](./05_weather_and_environment.md) · [Catalogue index](./README.md) · [Next: Amateur Radio →](./07_amateur_radio.md)
