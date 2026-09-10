# 📱 09 — Cellular

> The most heavily engineered signals you will ever receive, and the most legally constrained.
> Read the boundary section before anything else.
>
> [← IoT & ISM](./08_iot_ism_and_short_range.md) · [Catalogue index](./README.md) · [Next: Navigation & Timing →](./10_navigation_and_timing.md)

---

## ⛔ The legal boundary, stated plainly

Cellular is the one domain in this catalogue where **the default assumption should be "not
allowed"**, and where the consequences are criminal rather than administrative.

**Generally acceptable, and genuinely educational:**

- 🟢 Receiving **broadcast** channels that every handset in the cell receives anyway — the
  synchronisation signals, the MIB and SIBs, cell identity, and the network's own configuration
  parameters. This is how a phone finds a network; it is public by design.
- 🟢 **Measuring** signal strength, cell coverage, and spectrum occupancy.
- 🟢 Running your **own** small cell on your **own** licensed or lab-shielded spectrum.

**Not acceptable, anywhere:**

- ⛔ Decrypting or attempting to decrypt user traffic — voice, SMS, data.
- ⛔ Capturing IMSIs or otherwise tracking individuals.
- ⛔ Operating a base station on live spectrum without a licence, including "just to see".
- ⛔ Anything resembling an IMSI catcher.

In the USA the ECPA specifically prohibits intercepting cellular communications, with no hobbyist
exemption. Most other jurisdictions are stricter. **A shielded lab enclosure and your own SIMs is
the only fully safe way to experiment**, and it is genuinely how professionals do it.

---

## Bands (region-dependent)

| Band | Uplink | Downlink | Common in |
|---|---|---|---|
| GSM-850 | 824–849 | 869–894 MHz | Americas |
| GSM-900 | 890–915 | 935–960 MHz | Europe, Asia, Africa |
| DCS-1800 | 1710–1785 | 1805–1880 MHz | Europe, Asia |
| PCS-1900 | 1850–1910 | 1930–1990 MHz | Americas |
| LTE B1 | 1920–1980 | 2110–2170 MHz | worldwide |
| LTE B3 | 1710–1785 | 1805–1880 MHz | worldwide |
| LTE B7 | 2500–2570 | 2620–2690 MHz | worldwide |
| LTE B20 | 832–862 | 791–821 MHz | Europe (coverage band) |
| LTE B28 | 703–748 | 758–803 MHz | APAC, Europe |
| 5G n78 | 3300–3800 MHz (TDD) | | worldwide mid-band |
| 5G mmWave | 24–40 GHz 🔺 | | limited deployment |

**Downlink is what you receive.** All of the above except mmWave is within your SDR's tuning
range, though wide LTE and 5G carriers exceed its practical instantaneous bandwidth.

---

## GSM (2G)

Old, well documented, and the only cellular generation a hobbyist can realistically follow
end-to-end.

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **FCCH (frequency correction burst)** | downlink ARFCNs | pure tone burst | ⭐⭐⭐ | ✅ | 🟢 A constant frequency offset — easy to spot, and how you find a cell |
| **SCH (synchronisation burst)** | downlink | GMSK with training sequence | ⭐⭐⭐ | ✅ | 🟢 Gives frame number and base station identity |
| **BCCH (broadcast control)** | downlink | GMSK 270.833 kbit/s | ⭐⭐⭐⭐ | ✅ | 🟢 Network identity, cell parameters, neighbour lists |
| **CCCH / paging** | downlink | GMSK | ⭐⭐⭐⭐ | ✅ | 🟡 Paging messages; TMSIs rather than IMSIs on modern networks |
| **SDCCH / TCH traffic** | downlink | GMSK, A5/x encrypted | ⭐⭐⭐⭐⭐ | ✅ | ⛔ **Do not** |
| **GPRS / EDGE** | downlink | GMSK / 8PSK | ⭐⭐⭐⭐⭐ | ✅ | ⛔ |
| **Cell survey / ARFCN scan** | 900/1800 MHz | power measurement | ⭐⭐ | ✅ | 🟢 Map which channels are in use near you |

**Tooling:** `gr-gsm` (the successor to `airprobe`) does FCCH/SCH/BCCH cleanly and is a
genuinely good GNU Radio codebase to read.

---

## UMTS (3G)

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **P-SCH / S-SCH** | 2110–2170 MHz | 256-chip codes | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Primary/secondary synchronisation |
| **CPICH (pilot)** | downlink | 3.84 Mchip/s CDMA | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Scrambling code identifies the cell |
| **BCH / SIB** | downlink | CDMA | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟢 |
| **Traffic channels** | downlink | CDMA, encrypted | ⭐⭐⭐⭐⭐ | ✅🖥️ | ⛔ |

UMTS needs ~5 MHz of bandwidth and CDMA despreading. It is the least rewarding cellular target —
harder than GSM, less documented than LTE.

---

## LTE (4G)

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **PSS / SSS** | downlink centre 6 RBs | Zadoff-Chu sequences | ⭐⭐⭐ | ✅🖥️ | 🟢 **Only 1.08 MHz wide, regardless of carrier bandwidth.** Fits easily in 2 MSPS |
| **Cell ID detection** | downlink | from PSS+SSS | ⭐⭐⭐ | ✅ | 🟢 A very satisfying, entirely legal decode |
| **PBCH / MIB** | downlink centre | QPSK, tail-biting convolutional | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Bandwidth, frame number, antenna count |
| **PDSCH SIB1/SIB2** | downlink | needs full bandwidth | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟢 Network configuration, still broadcast |
| **Cell reference signals (CRS)** | downlink | known pilots | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Used for channel estimation — and for **passive radar** |
| **User plane traffic** | downlink | encrypted | ⭐⭐⭐⭐⭐ | ✅🖥️ | ⛔ |
| **NB-IoT** | 180 kHz in-band or guard | OFDM | ⭐⭐⭐⭐ | ✅ | 🟢 **Narrow enough to be genuinely tractable** |
| **LTE-M / CAT-M1** | 1.4 MHz | OFDM | ⭐⭐⭐⭐ | ✅ | 🟢 |

**Tooling:** `srsRAN` (formerly srsLTE) includes `srsue --rat.eutra` cell search, and
`LTE-Cell-Scanner` does PSS/SSS/MIB with modest bandwidth. Both are legal to run in receive-only
cell-search mode.

---

## 5G NR

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **SSB (PSS/SSS/PBCH block)** | n78 3.3–3.8 GHz etc. | OFDM, 3.6 MHz | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 The 5G equivalent of LTE's PSS/SSS |
| **SIB1 / RMSI** | downlink | OFDM | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟢 |
| **Beam sweeping observation** | mid-band | SSB burst set | ⭐⭐⭐⭐ | ✅🖥️ | 🟢 Watch the beams sweep in time — visually striking |
| **mmWave** | 24–40 GHz | OFDM, huge bandwidth | ⭐⭐⭐⭐⭐ | 🔺🖥️ | 🟢 Needs specialised hardware |

---

## Adjacent and legacy

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **TETRA / P25** | see [Land Mobile](./06_land_mobile_and_professional.md) | | | | |
| **DECT** | 1880–1900 MHz | GFSK TDMA | ⭐⭐⭐⭐ | ✅ | ⛔ Cordless phones |
| **CDMA2000 / EV-DO** | 850, 1900 MHz | CDMA | ⭐⭐⭐⭐⭐ | ✅🖥️ | ⛔ Largely retired |
| **iDEN** | 800 MHz | TDMA | ⭐⭐⭐⭐⭐ | ✅ | ⛔ Retired |
| **Cellular repeaters / boosters** | any band | amplify | ⭐⭐ | ✅ | 🟡 Illegal in many countries if unapproved |
| **Femtocell / small cell downlink** | LTE bands | as LTE | ⭐⭐⭐⭐ | ✅ | 🟢 Same signals, much lower power |

---

## Try this first: find every LTE cell around you

This is **completely legal**, genuinely useful, and a beautiful piece of DSP.

LTE's synchronisation signals occupy only the **centre 1.08 MHz** of a carrier no matter how wide
that carrier is — so a 2 MSPS capture is enough, and your SDR handles it comfortably.

```
1. Tune to an LTE downlink centre frequency (e.g. 1842.5 MHz for a B3 carrier)
2. Correlate against the three possible PSS Zadoff-Chu sequences
   -> gives you N_ID^(2) (0,1,2) and symbol timing
3. Decode SSS at the known offset -> gives N_ID^(1) (0..167)
4. Physical Cell ID = 3 * N_ID^(1) + N_ID^(2)
```

Zadoff-Chu sequences have **perfect autocorrelation** — the correlation peak is enormous and
unmistakable, which makes this one of the most satisfying correlation exercises in radio. It is
the same principle as ADS-B's non-uniform preamble in
[Lab 09](../02_flowgraphs/lab09_adsb_receiver/README.md), executed with much more mathematical
elegance.

Map the cell IDs and signal strengths around your neighbourhood and you have built a coverage
survey tool — a real professional instrument, from a $300 radio.

---

## Then: NB-IoT, because it is narrow

If full LTE feels out of reach, **NB-IoT occupies only 180 kHz** — narrower than an FM broadcast
station. It uses the same OFDM principles at a scale your hardware and your CPU can actually
handle, and it is increasingly what smart meters and city sensors use. It is the most tractable
doorway into modern cellular physical layers.

---

[← IoT & ISM](./08_iot_ism_and_short_range.md) · [Catalogue index](./README.md) · [Next: Navigation & Timing →](./10_navigation_and_timing.md)
