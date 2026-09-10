# 🔐 13 — Security Research

> Radio security is a legitimate and valuable discipline. It is also the fastest way in this
> catalogue to commit a serious offence by accident. **Read the boundary first — it is not
> boilerplate.**
>
> [← Science](./12_science_and_radio_astronomy.md) · [Catalogue index](./README.md) · [Next: Test & Measurement →](./14_test_measurement_and_infrastructure.md)

---

## ⚖️ The boundary, in one page

### The single rule

> **You may test only systems you own, or systems whose owner has given you written permission
> to test.**

That is not a formality. In practice it is the entire difference between security research and a
criminal offence, and it is the line prosecutors actually use.

### Legal, useful, and where you should spend your time

- ✅ Analysing **your own** car key, garage door, doorbell, alarm, smart meter, thermostat
- ✅ Buying a device specifically to take it apart
- ✅ Testing in a **shielded enclosure** or into a **dummy load**, where nothing radiates
- ✅ Reverse-engineering a **protocol** and publishing the format
- ✅ Passive observation of unencrypted signals you are permitted to receive
- ✅ Responsible disclosure to a vendor, with a reasonable embargo

### Not legal, regardless of intent

- ⛔ **Transmitting anything at a device you do not own.** Including "just once, to see". This is
  where replay attacks cross from research into offence
- ⛔ **Decrypting** encrypted traffic — no research exemption exists in most jurisdictions
- ⛔ **Jamming or denial of service.** A criminal offence essentially everywhere, with no defence
- ⛔ **Interfering with safety systems**: aviation, maritime, rail, medical, emergency services
- ⛔ **Injecting false data** into ADS-B, AIS or GNSS. Prosecuted as endangerment
- ⛔ **Tracking individuals** — TPMS IDs, BLE MACs, IMSIs — without consent. This is surveillance,
  and increasingly it is also a data-protection offence

### The uncomfortable middle

Passively **recording** your neighbour's sensors, or logging TPMS identifiers from passing cars,
is often technically legal and ethically indefensible. The test that has never failed anyone:
**would you be comfortable explaining this to the person whose device it is?**

---

## Protocol reverse engineering

The core skill of this domain, and entirely legal on your own devices.

| Technique | Diff | Notes |
|---|---|---|
| **Signal identification** | ⭐⭐ | Bandwidth, modulation, symbol rate from a waterfall. `sigidwiki.com` as a reference |
| **OOK/ASK frame recovery** | ⭐⭐ | Envelope → threshold → pulse widths. See [IoT](./08_iot_ism_and_short_range.md) |
| **FSK deviation measurement** | ⭐⭐ | Quadrature demod and measure the two levels |
| **Symbol rate estimation** | ⭐⭐⭐ | Autocorrelation of the magnitude, or the cyclostationary spectrum |
| **Preamble and sync-word discovery** | ⭐⭐⭐ | Look for a repeating prefix across many captures |
| **Manchester / NRZI detection** | ⭐⭐⭐ | Test both interpretations and see which yields structure |
| **Checksum identification** | ⭐⭐⭐⭐ | CRC brute-force over polynomial, init and reflection. `CRC RevEng` |
| **Field mapping by differential capture** | ⭐⭐⭐ | Change **one** thing on the device, capture again, diff the frames. **The most effective technique there is** |
| **Whitening / scrambler recovery** | ⭐⭐⭐⭐ | Common in CC1101-class radios; usually a short LFSR |
| **FEC identification** | ⭐⭐⭐⭐⭐ | Convolutional, Reed-Solomon or LDPC — the hardest layer to reverse |
| **Frequency-hopping sequence recovery** | ⭐⭐⭐⭐⭐ | Requires wideband capture and pattern analysis |
| **Firmware correlation** | ⭐⭐⭐⭐ | Dump the device firmware and find the radio config registers. Often faster than pure RF work |

---

## Classes of weakness (study on your own devices)

| Weakness | Where it appears | Diff | Notes |
|---|---|---|---|
| **Fixed-code replay** | Old gates, doorbells, cheap remotes | ⭐⭐ | Capture and retransmit works. **Only against your own device** |
| **Rolling-code desync** | KeeLoq-era remotes | ⭐⭐⭐⭐ | "RollJam"-class techniques; well documented publicly |
| **Relay attacks** | Passive keyless entry | ⭐⭐⭐⭐ | Extends the LF link, not the UHF one. Studied extensively |
| **Missing authentication** | Industrial and building control | ⭐⭐⭐ | Very common; commands accepted from anyone |
| **Predictable identifiers** | Sensors, meters, tags | ⭐⭐⭐ | Enables tracking and spoofing |
| **Unencrypted telemetry** | Medical, industrial, drone links | ⭐⭐⭐ | Confidentiality failure rather than integrity |
| **Weak or absent integrity check** | Simple OOK devices | ⭐⭐ | A 4-bit checksum is not protection |
| **Downgrade to legacy mode** | Multi-protocol devices | ⭐⭐⭐⭐ | |
| **Side-channel via RF emission** | Any electronics | ⭐⭐⭐⭐⭐ | Unintentional emissions leaking state |
| **GNSS spoofing susceptibility** | Anything trusting GPS | ⭐⭐⭐⭐⭐ | ⛔ **Study only in a shielded chamber.** Radiating GNSS spoofing is a serious crime |

---

## Emissions security (TEMPEST-style)

Passive, and legal, because you are receiving your **own** equipment's unintentional emissions.

| Project | Frequency | Diff | Notes |
|---|---|---|---|
| **Video cable emissions** | 50–800 MHz | ⭐⭐⭐⭐⭐ | `TempestSDR` can reconstruct a screen image from HDMI/VGA leakage |
| **Keyboard emissions** | 20–200 MHz | ⭐⭐⭐⭐⭐ | Keystroke timing from unintentional radiation |
| **Power supply / SMPS signatures** | 100 kHz–30 MHz | ⭐⭐⭐ | Device identification from switching harmonics |
| **CPU / DRAM activity leakage** | broadband | ⭐⭐⭐⭐⭐ | Cryptographic side channels have been demonstrated |
| **Deliberate soft-TEMPEST transmission** | any | ⭐⭐⭐⭐ | Modulating a screen to transmit data — a classic demonstration |

---

## Defensive and forensic work

The other half of the discipline, and often the more employable half.

| Project | Diff | Notes |
|---|---|---|
| **RF fingerprinting** | ⭐⭐⭐⭐⭐ | Identify individual transmitters by turn-on transients and oscillator imperfections |
| **Rogue transmitter detection** | ⭐⭐⭐ | Spectrum baselining and change detection |
| **Jamming detection and characterisation** | ⭐⭐⭐ | Recognising interference rather than causing it |
| **GNSS spoofing detection** | ⭐⭐⭐⭐⭐ | Consistency of angle of arrival, C/N₀ and clock behaviour |
| **Drone detection and identification** | ⭐⭐⭐⭐ | Remote ID broadcasts plus control-link signatures |
| **IMSI-catcher detection** | ⭐⭐⭐⭐ | Anomalous cell parameters, missing neighbours, forced downgrades |
| **Wireless site survey** | ⭐⭐⭐ | Documenting what actually transmits in a building |
| **Spectrum baselining for a facility** | ⭐⭐⭐ | Know normal so you can recognise abnormal |
| **Direction finding a rogue emitter** | ⭐⭐⭐⭐ | See [Test & Measurement](./14_test_measurement_and_infrastructure.md) |

---

## Try this first: your own doorbell

A wireless doorbell is the ideal first target. You own it, it is harmless, it transmits only when
you press it, and its protocol is usually trivial.

```
1. Capture 433.92 MHz (or 315 MHz) with Lab 05 while pressing the button
2. Plot |x| and find the burst
3. Zoom in: you will see OOK pulses of two distinct widths
4. Transcribe them by hand into 1s and 0s
5. Press again. Capture again. Compare -> identical means a fixed code
6. Try a second button or a second unit -> find which bits are the ID
```

You will have reverse-engineered a real protocol **without any tools at all** — just a capture and
your eyes. That is the whole discipline in miniature, and it teaches the mindset better than any
framework.

**Then stop.** Do not transmit it back at anything except your own doorbell, and do not do this
to a car.

---

## A note on publishing

If you find a genuine vulnerability in a product:

1. **Contact the vendor first.** Many now have a `security.txt` or a disclosure policy
2. **Give a reasonable embargo** — 90 days is the common norm
3. **Publish the protocol and the class of flaw, not a weaponised tool**
4. **Do not publish anything that only enables theft**, such as a working attack against a
   current vehicle

The community's credibility — and the continued legality of this hobby — rests on researchers
behaving better than the law strictly requires.

---

[← Science](./12_science_and_radio_astronomy.md) · [Catalogue index](./README.md) · [Next: Test & Measurement →](./14_test_measurement_and_infrastructure.md)
