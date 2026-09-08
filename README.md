# 📡 SignalSDR Pro Lab — A Complete SDR Learning Journey

> **Your comprehensive laboratory for learning Software-Defined Radio using the SignalSDR Pro (by Signalens) emulating a USRP B210, with GNU Radio.**

---

## 🚨 Quick Fix: "Could not find path for image" Error

If you're seeing this error when running GNU Radio flowgraphs:

```
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
```

**But** `uhd_find_devices` works fine, you have a **UHD version conflict**.

### ⚡ Quick Fix (Terminal & GUI Launcher)

```bash
# Automated fix:
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab/00_setup"
./fix_uhd_version_conflict.sh
```

Or manually create system symlinks:
```bash
sudo ln -sfn /usr/share/uhd/4.10.0/images /usr/share/uhd/images
sudo ln -sfn /usr/share/uhd/4.10.0/images /usr/share/uhd/4.6.0/images
echo 'UHD_IMAGES_DIR="/usr/share/uhd/4.10.0/images"' | sudo tee -a /etc/environment
```

**Full explanation:** [Fix UHD Version Conflict](./00_setup/06_fix_uhd_version_conflict.md)

---

## 🎯 What Is This Project?

This lab is a carefully structured learning path that takes you from **zero knowledge** to being able to build, understand, and modify sophisticated SDR flowgraphs. We use:

- **Hardware:** SignalSDR Pro (Signalens) — configured to emulate a **USRP B210**
- **Software:** **GNU Radio 3.10** (the leading open-source SDR toolkit)
- **Driver:** **UHD** (USRP Hardware Driver) by Ettus Research
- **OS:** Ubuntu 24.04 LTS (works on any modern Linux)

The SignalSDR Pro is a compact, credit-card-sized SDR built around the **Analog Devices AD9361** transceiver chip and a **Xilinx Zynq** FPGA. Thanks to its flexible firmware (loaded from an SD card), it can pretend to be a USRP B210 — the gold-standard hobbyist SDR — which means **all the existing UHD + GNU Radio tutorials and code work on it directly**.

---

## 📚 Learning Path (Read in Order)

### Part 0 — Setup (Do this first!)
Everything here is required before you can run any flowgraph.

| # | Document | What You'll Learn |
|---|---|---|
| 01 | [Installing UHD Driver](./00_setup/01_install_uhd.md) | What UHD is, how to install it, what `uhd_images_downloader` does |
| 02 | [Flashing the B210 Firmware](./00_setup/02_flash_b210_firmware.md) | SD card prep, jumper settings, power/data cables, boot sequence |
| 03 | [Installing GNU Radio](./00_setup/03_install_gnuradio.md) | Getting GRC (GNU Radio Companion) working |
| 04 | [Verifying the Setup](./00_setup/04_verify_setup.md) | `uhd_find_devices`, `uhd_usrp_probe`, first signal |
| 05 | [Troubleshooting](./00_setup/05_troubleshooting.md) | Common pitfalls with SignalSDR Pro + UHD |
| 06 | [Fix UHD Version Conflict](./00_setup/06_fix_uhd_version_conflict.md) | **CRITICAL:** Fix for dual UHD versions (Terminal & GUI Launcher) |

### Part 1 — Fundamentals (Theory from Zero)
You cannot build good SDR systems without understanding these.

| # | Document | What You'll Learn |
|---|---|---|
| 01 | [Signals & Systems Basics](./01_fundamentals/01_signals_basics.md) | Time vs frequency, amplitude, phase, bandwidth |
| 02 | [IQ Sampling](./01_fundamentals/02_iq_sampling.md) | Why SDRs use I/Q, complex numbers, negative frequencies |
| 03 | [RF Basics](./01_fundamentals/03_rf_basics.md) | What is RF, spectrum, mixers, filters |
| 04 | [FM Modulation Theory](./01_fundamentals/04_fm_theory.md) | How FM works, deviation, bandwidth, Carson's rule |

### Part 2 — Hands-On Flowgraphs (Progressive Labs)
Each lab builds on the previous one. **Do not skip.**

| Lab | Flowgraph | Concept |
|---|---|---|
| 01 | [Simplest WBFM Receiver](./02_flowgraphs/lab01_simple_wbfm/README.md) | Minimum viable FM radio. 3 blocks total. |
| 02 | [Enhanced WBFM + Visualization](./02_flowgraphs/lab02_enhanced_wbfm/README.md) | Add spectrum, waterfall, resampling, GUI sliders. |
| 03 | [Advanced WBFM with AGC & Squelch](./02_flowgraphs/lab03_advanced_wbfm/README.md) | Real-world receiver: filtering, AGC, squelch, volume. |
| 04 | [Stereo WBFM — Full MPX Decoding](./02_flowgraphs/lab04_stereo_wbfm/README.md) | Manual stereo extraction: pilot, PLL, L+R, L-R, de-emphasis. |

### Part 3 — Scripts & Tools
| Document | Purpose |
|---|---|
| [Flowgraph Validator](./03_scripts/validate_flowgraph.py) | Python script to check if your `.grc` files are well-formed |

---

## 🛠️ System Requirements

| Item | Recommendation |
|---|---|
| **OS** | Ubuntu 24.04 LTS (Noble), 22.04 LTS, or DragonOS |
| **RAM** | ≥ 8 GB (waterfall sinks use lots of memory) |
| **USB** | USB 3.0 port for data (Type-B), USB 2.0 for power (Type-C) |
| **SD card** | ≥ 8 GB, Class 10, for the SignalSDR Pro boot image |
| **Cables** | USB-B to USB-A 3.0 (data), USB-C to USB-A (power) |
| **Antenna** | Any 70 MHz – 6 GHz antenna (telescopic, SMA dipole, etc.) |

---

## 📦 What's In the Box

```
signalsdrpro_lab/
├── README.md                       ← You are here
├── 00_setup/                       ← Environment setup
│   ├── 01_install_uhd.md
│   ├── 02_flash_b210_firmware.md
│   ├── 03_install_gnuradio.md
│   ├── 04_verify_setup.md
│   ├── 05_troubleshooting.md
│   ├── 06_fix_uhd_version_conflict.md  ← UHD version mismatch guide (Terminal & GUI)
│   └── fix_uhd_version_conflict.sh     ← Automated fix script
├── 01_fundamentals/                ← Theory (read first!)
│   ├── 01_signals_basics.md
│   ├── 02_iq_sampling.md
│   ├── 03_rf_basics.md
│   └── 04_fm_theory.md
├── 02_flowgraphs/                  ← Hands-on labs
│   ├── lab01_simple_wbfm/
│   ├── lab02_enhanced_wbfm/
│   ├── lab03_advanced_wbfm/
│   └── lab04_stereo_wbfm/
└── 03_scripts/
    └── validate_flowgraph.py
```

---

## 🔬 About Verification

> **Honest note from the author:** The flowgraphs in this lab were built, structurally validated, and checked against the exact YAML schema used by GNU Radio 3.10. Their Python-equivalent outputs were syntax-checked with `python3 -m py_compile`. However, **physical RF testing was not possible** on the authoring machine because the SignalSDR Pro device is not currently connected. You are expected to run each flowgraph in **GNU Radio Companion** and confirm they work with your hardware. If you find a bug, please fix it and report back — that's the spirit of this lab.

---

## 🚀 What's Next?

After you finish all four labs, you will have built up the skills to tackle advanced projects such as:

- ✈️ **ADS-B Airplane Detection** (1090 MHz) — planned as Part 4
- 📻 **FM Transmitter** (be careful with local laws!)
- 📱 **LTE/5G Sniffing** (srsRAN, LTESniffer)
- 🛰️ **GPS Signal Simulation** (gps-sim-sdr)
- 📶 **GSM Base Station** (OpenBTS, YateBTS)
- 🌐 **WiFi Reverse Engineering** (OpenWiFi)

---

## 🧠 The Mindset

SDR is not just "running a flowgraph". It's about understanding what happens **between every pair of blocks**:
- What is the sample rate at this point?
- What is the data type (complex, float, short)?
- What does the frequency spectrum look like?
- Why did we choose this specific decimation / filter tap count?

**Every block has a reason. Every parameter has a meaning.** This lab will teach you to ask those questions.

Enjoy the journey! 🎧

---

*Created: September 2026 • Target hardware: SignalSDR Pro (Signalens) as USRP B210 • Target software: GNU Radio 3.10.9 + UHD 4.6*
