# 📡 08 — IoT, ISM & Short Range

> The densest, noisiest, most varied part of the spectrum — and the easiest place to find a real
> signal you can fully reverse-engineer in an afternoon. Your own house is transmitting right now.
>
> [← Amateur Radio](./07_amateur_radio.md) · [Catalogue index](./README.md) · [Next: Cellular →](./09_cellular.md)

---

## The ISM bands

**ISM** = Industrial, Scientific and Medical — bands where licence-exempt devices may transmit
under power and duty-cycle limits. They differ by region, which is the first thing to get right:

| Band | Region | Typical use |
|---|---|---|
| 13.56 MHz | worldwide 🔻 | NFC, RFID |
| 40.68 MHz | worldwide 🔻 | Legacy remote control |
| **315 MHz** | **Americas, Japan** | Key fobs, TPMS |
| **433.05–434.79 MHz** | **Europe, most of world** | Remotes, sensors, LoRa |
| 902–928 MHz | **Americas** | LoRa, smart meters, Zigbee |
| **863–870 MHz** | **Europe** | LoRa, wM-Bus, sensors |
| 920–925 MHz | Japan, parts of Asia | LoRa |
| 2.400–2.500 GHz | worldwide | Wi-Fi, BLE, Zigbee, microwave ovens |
| 5.725–5.875 GHz | worldwide | Wi-Fi, drones |

> ⚠️ **Check your region before you conclude a band is empty.** A European reader finds nothing
> at 915 MHz; an American finds nothing at 868 MHz. Both are correct.

---

## Sensors and telemetry

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Weather station sensors** | 433.92, 868, 915 MHz | OOK/FSK, PWM framing | ⭐⭐ | ✅ | 🟢 `rtl_433` supports 200+ protocols. **The best first data project in SDR** |
| **Indoor thermometers / hygrometers** | 433.92, 868 MHz | OOK | ⭐ | ✅ | 🟢 Often no checksum at all |
| **Soil moisture / agricultural** | 868/915 MHz | LoRa/FSK | ⭐⭐⭐ | ✅ | 🟢 |
| **Pool / spa monitors** | 433 MHz | OOK | ⭐ | ✅ | 🟢 |
| **Water leak detectors** | 433, 868 MHz | FSK | ⭐⭐ | ✅ | 🟢 |
| **Refrigeration / cold-chain loggers** | 433, 868 MHz | FSK | ⭐⭐⭐ | ✅ | 🟡 |
| **Livestock and beehive monitors** | 868/915 MHz | LoRa | ⭐⭐⭐ | ✅ | 🟢 |
| **Rain gauges and anemometers** | 433/915 MHz | OOK | ⭐⭐ | ✅ | 🟢 |

---

## Metering

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Wireless M-Bus** | 868.95, 868.3 MHz | FSK, modes S/T/C | ⭐⭐⭐ | ✅ | 🟡 European water, gas, heat meters. Often encrypted per-meter |
| **Itron / ERT (AMR)** | 910–920 MHz | OOK/FSK | ⭐⭐⭐ | ✅ | 🟡 North American utility meters. `rtlamr` |
| **Elster / Landis+Gyr** | 900 MHz | proprietary FSK | ⭐⭐⭐⭐ | ✅ | 🟡 |
| **Mesh AMI networks** | 900 MHz | frequency-hopping | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟡 Hard: hops across the band |
| **Gas meter pulse transmitters** | 433/868 MHz | OOK | ⭐⭐ | ✅ | 🟡 |
| **District heating meters** | 868 MHz | wM-Bus | ⭐⭐⭐ | ✅ | 🟡 |

---

## Vehicles

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **TPMS (tyre pressure)** | 315 MHz (NA), 433.92 MHz (EU) | FSK/OOK, Manchester | ⭐⭐ | ✅ | 🟡 Each sensor has a unique ID. **Drive-by vehicle fingerprinting is a real privacy concern** |
| **Key fobs (fixed code)** | 315, 433.92 MHz | OOK | ⭐⭐ | ✅ | 🟡 Older gates and garages |
| **Key fobs (rolling code)** | 315, 433.92, 868 MHz | OOK/FSK, KeeLoq etc. | ⭐⭐⭐ | ✅ | 🟡 **Never replay against a vehicle you do not own** |
| **Passive keyless entry (PKE)** | 125 kHz + 433/868 MHz | LF wake + UHF reply | ⭐⭐⭐⭐ | 🔻+✅ | 🟡 The target of relay attacks |
| **Remote start systems** | 433, 868 MHz | FSK | ⭐⭐⭐ | ✅ | 🟡 |
| **Immobiliser transponders** | 125 kHz | LF inductive | ⭐⭐⭐ | 🔻📡 | 🟡 |
| **V2X / DSRC** | 5.9 GHz | 802.11p | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟢 Vehicle-to-everything safety messaging |
| **Toll transponders** | 915 MHz, 5.8 GHz | backscatter | ⭐⭐⭐⭐ | ✅ | 🟡 |
| **Truck/fleet telematics** | 400–900 MHz | FSK | ⭐⭐⭐⭐ | ✅ | 🟡 |

---

## Home and building

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Doorbells** | 433.92 MHz | OOK | ⭐ | ✅ | 🟢 Often literally a fixed 24-bit code |
| **Garage door openers** | 315, 433.92, 868 MHz | OOK, rolling | ⭐⭐ | ✅ | 🟡 |
| **Alarm system sensors** | 433, 868 MHz | OOK/FSK | ⭐⭐⭐ | ✅ | 🟡 Door/window contacts, PIRs |
| **Smoke detector interlinks** | 433, 868 MHz | FSK | ⭐⭐ | ✅ | 🟢 |
| **Wireless light switches** | 433, 868 MHz | OOK, EnOcean | ⭐⭐ | ✅ | 🟢 EnOcean devices are battery-free |
| **Blinds and shutters** | 433, 868 MHz | OOK/FSK | ⭐⭐ | ✅ | 🟢 Somfy RTS and similar |
| **Weather-compensated heating controls** | 868 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 |
| **Baby monitors (analog)** | 864, 900 MHz | NBFM | ⭐ | ✅ | 🟡 Older units are plain FM |
| **DECT cordless phones** | 1880–1900 MHz | GFSK, TDMA | ⭐⭐⭐⭐ | ✅ | ⛔ Encrypted; interception prohibited |
| **Wireless doorbell cameras** | 2.4 GHz | Wi-Fi | ⭐⭐⭐ | ✅ | 🟡 |

---

## Standard short-range protocols

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **LoRa** | 433, 868, 915 MHz | **chirp spread spectrum** | ⭐⭐⭐⭐ | ✅ | 🟢 Genuinely new DSP — up/down chirps, not PSK. `gr-lora_sdr` |
| **LoRaWAN** | same | LoRa + network layer | ⭐⭐⭐⭐ | ✅ | 🟢 Payloads encrypted; metadata is not |
| **Sigfox** | 868, 902 MHz | ultra-narrowband DBPSK | ⭐⭐⭐⭐ | ✅ | 🟢 100 Hz wide |
| **Zigbee / 802.15.4** | 2.4 GHz (also 868/915) | O-QPSK DSSS | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 `gr-ieee802-15-4` |
| **Thread / Matter** | 2.4 GHz | 802.15.4 based | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 |
| **Z-Wave** | 868.42 (EU), 908.42 MHz (US) | GFSK | ⭐⭐⭐ | ✅ | 🟢 `gr-zwave` |
| **Bluetooth Classic** | 2.4 GHz | GFSK, 79-channel hopping | ⭐⭐⭐⭐⭐ | ✅🖥️ | ⛔ Hopping makes capture hard |
| **Bluetooth LE advertising** | 2402, 2426, 2480 MHz | GFSK 1 Mbit/s | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 **Only three channels** — far more tractable than Classic |
| **BLE data channels** | 2.4 GHz | hopping | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟡 |
| **Wi-Fi 802.11b** | 2.4 GHz | DSSS | ⭐⭐⭐⭐ | ✅🖥️ | 🟡 The only Wi-Fi variant realistically decodable at 2 MSPS-class rates |
| **Wi-Fi 802.11a/g/n** | 2.4, 5 GHz | OFDM 20 MHz | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟡 `gr-ieee802-11`; needs 20 MHz bandwidth |
| **ANT+** | 2.4 GHz | GFSK | ⭐⭐⭐⭐ | ✅ | 🟢 Fitness sensors |
| **NFC / HF RFID** | 13.56 MHz | ASK/load modulation | ⭐⭐⭐ | 🔻📡 | 🟡 Needs a loop antenna |
| **UHF RFID (EPC Gen2)** | 860–960 MHz | backscatter | ⭐⭐⭐⭐ | ✅📡 | 🟢 Reader is easy to see; tag backscatter is faint |
| **EnOcean** | 868.3, 902 MHz | ASK | ⭐⭐ | ✅ | 🟢 Energy-harvesting switches |
| **Wireless HART / ISA100** | 2.4 GHz | 802.15.4 | ⭐⭐⭐⭐ | ✅ | 🟡 Industrial process control |

---

## Toys, drones and hobby

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **RC transmitters (2.4 GHz)** | 2.4 GHz | FHSS (DSM2/X, FrSky, etc.) | ⭐⭐⭐⭐ | ✅🖥️ | 🟡 Fast frequency hopping |
| **RC transmitters (legacy)** | 27, 35, 40, 72 MHz | PPM/PCM | ⭐⭐ | 🔻 | 🟢 Simple and readable |
| **Drone telemetry** | 433, 868, 915 MHz | MAVLink over FSK | ⭐⭐⭐ | ✅ | 🟡 Often unencrypted |
| **Drone video (analog FPV)** | 5.8 GHz | FM video | ⭐⭐⭐ | ✅📡 | 🟡 |
| **Drone Remote ID** | 2.4 GHz | BLE / Wi-Fi beacon | ⭐⭐⭐⭐ | ✅ | 🟢 Regulatory broadcast of drone identity and position |
| **Model telemetry (S.Port, etc.)** | 2.4 GHz | proprietary | ⭐⭐⭐⭐ | ✅ | 🟡 |
| **Wireless game controllers** | 2.4 GHz | proprietary FHSS | ⭐⭐⭐⭐ | ✅ | 🟡 |

---

## Try this first: capture your own house

Point the SDR at **433.92 MHz** (Europe/Asia) or **315 MHz** (Americas) and record five minutes
with [Lab 05](../02_flowgraphs/lab05_iq_record_playback/README.md). Then look at the magnitude in
NumPy:

```python
import numpy as np
d = np.fromfile('capture.iq', dtype=np.complex64)
m = np.abs(d)
bursts = np.flatnonzero((m[1:] > 0.05) & (m[:-1] <= 0.05))
print(f"{len(bursts)} bursts in {len(d)/2e6:.1f} s")
```

Every burst is a device. Zoom into one, look at the pulse widths, and you will usually find
**OOK with pulse-width encoding**: a long pulse is a 1, a short pulse is a 0, and there is a
preamble of alternating bits followed by a device ID and a checksum.

Decoding one from scratch — no library, just your eyes and NumPy — is the single most empowering
exercise in this catalogue. There is no synchronisation loop, no FEC, nothing hidden. And once
you have done one, `rtl_433`'s source code stops looking like magic and starts looking like a
list of the same idea 200 times.

---

## Then: LoRa, because it is genuinely different

Everything else in this repo has been amplitude, frequency or phase modulation. **LoRa is chirp
spread spectrum**: each symbol is a linear frequency sweep, and the symbol *value* is encoded in
where the sweep starts. Demodulation is a dechirp (multiply by a conjugate chirp) followed by an
FFT — the peak bin *is* the symbol.

It is the first modulation in this catalogue that your Lab 07 toolkit does not directly cover,
and working out why it achieves such extraordinary range at such low power is a genuine
education in spread spectrum.

---

[← Amateur Radio](./07_amateur_radio.md) · [Catalogue index](./README.md) · [Next: Cellular →](./09_cellular.md)
