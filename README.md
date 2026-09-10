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

**Read 01–04 before Lab 01.** Documents 05–10 are referenced by the labs that need them, and
each lab's header tells you which.

| # | Document | What You'll Learn | Needed by |
|---|---|---|---|
| 01 | [Signals & Systems Basics](./01_fundamentals/01_signals_basics.md) | Time vs frequency, amplitude, phase, bandwidth | Lab 01 |
| 02 | [IQ Sampling](./01_fundamentals/02_iq_sampling.md) | Why SDRs use I/Q, complex numbers, negative frequencies | Lab 01 |
| 03 | [RF Basics](./01_fundamentals/03_rf_basics.md) | What is RF, spectrum, mixers, filters | Lab 01 |
| 04 | [FM Modulation Theory](./01_fundamentals/04_fm_theory.md) | How FM works, deviation, bandwidth, Carson's rule | Lab 01 |
| 05 | [Sampling, Filters & Resampling](./01_fundamentals/05_sampling_and_filters.md) | Nyquist, aliasing, FIR design, the tap-count equation, decimation, xlating filters | Labs 05–09 |
| 06 | [Noise, SNR, Gain & Dynamic Range](./01_fundamentals/06_noise_snr_and_gain.md) | kTB, noise figure, Friis, dBm/dBFS, AGC, squelch, link budgets | Labs 05, 06, 08, 09 |
| 07 | [AM, SSB & Narrowband FM](./01_fundamentals/07_am_and_narrowband_fm.md) | Envelope vs coherent detection, DSB-SC, SSB in IQ, modulation index | Lab 06 |
| 08 | [Digital Modulation](./01_fundamentals/08_digital_modulation.md) | Constellations, RRC pulse shaping, Eb/N0, BER, PPM | Labs 07–09 |
| 09 | [Synchronization](./01_fundamentals/09_synchronization.md) | PLLs, Costas loops, timing recovery, loop bandwidth | Labs 07, 08 |
| 10 | [Error Detection & Framing](./01_fundamentals/10_error_detection_and_framing.md) | GF(2) arithmetic, CRC, self-synchronising codes, FEC | Labs 08, 09 |

### Part 2 — Hands-On Flowgraphs (Progressive Labs)
Each lab builds on the previous one. **Do not skip.**

| Lab | Flowgraph | Concept | Blocks | Hardware? |
|---|---|---|---|---|
| 01 | [Simplest WBFM Receiver](./02_flowgraphs/lab01_simple_wbfm/README.md) | Minimum viable FM radio. 3 blocks total. | 7 | yes |
| 02 | [Enhanced WBFM + Visualization](./02_flowgraphs/lab02_enhanced_wbfm/README.md) | Spectrum, waterfall, resampling, GUI sliders. | 13 | yes |
| 03 | [Advanced WBFM with AGC & Squelch](./02_flowgraphs/lab03_advanced_wbfm/README.md) | Real receiver: filtering, AGC, squelch, volume. | 18 | yes |
| 04 | [Stereo WBFM — Full MPX Decoding](./02_flowgraphs/lab04_stereo_wbfm/README.md) | Manual stereo: pilot, PLL, L+R, L−R, de-emphasis. | 30 | yes |
| 05 | [IQ Recording & Playback](./02_flowgraphs/lab05_iq_record_playback/README.md) | Capture to disk, replay, retune inside a recording. | 19 | record only |
| 06 | [Multimode Receiver](./02_flowgraphs/lab06_multimode_receiver/README.md) | AM / NBFM / WBFM, channel selection, S-meter, squelch. | 35 | yes |
| 07 | [BPSK Link Simulation](./02_flowgraphs/lab07_bpsk_link_sim/README.md) | A full digital link with **measured BER vs theory**. | 34 | **none** |
| 08 | [RDS Decoder](./02_flowgraphs/lab08_rds_decoder/README.md) | Station name & RadioText off the 57 kHz subcarrier. | 34 | optional |
| 09 | [ADS-B Aircraft Receiver](./02_flowgraphs/lab09_adsb_receiver/README.md) | 1090 MHz Mode S: identity, altitude, position. | 14 | optional |

**Labs 07, 08b and 09b run with no radio attached.** Labs 08 and 09 each ship a second
flowgraph that reads a recorded or synthetic IQ file, so you can build and debug the whole
decoder before you ever fight an antenna.

### The arc

```
  01 ─▶ 02 ─▶ 03 ─▶ 04        analog: one signal, growing sophistication
                    │
                    ▼
                   05         stop needing the radio
                    │
                    ▼
                   06         one tuner, many channels and many modes
                    │
                    ▼
                   07         cross into digital, in a controlled simulation
                    │
                    ▼
                   08         apply it to real data hidden in an FM broadcast
                    │
                    ▼
                   09         a different band, a different modulation, aircraft
```

### Part 3 — Scripts & Tools
| Script | Purpose |
|---|---|
| [validate_flowgraph.py](./03_scripts/validate_flowgraph.py) | Validate `.grc` files against the **installed** GNU Radio block library — block ids, parameter expressions, port types, connections. `--compile` also generates the Python. |
| [simulate_bpsk_ber.py](./03_scripts/simulate_bpsk_ber.py) | Run Lab 07's link at a sweep of Eb/N0 and compare the measured BER against closed-form theory. |
| [simulate_rds_decode.py](./03_scripts/simulate_rds_decode.py) | Generate a synthetic FM+RDS signal with known contents for Lab 08, and self-test the RDS codec. |
| [simulate_adsb_decode.py](./03_scripts/simulate_adsb_decode.py) | Generate a synthetic 1090 MHz capture for Lab 09, and self-test the Mode S decoder against published reference frames. |
| [simulate_stereo_decode.py](./03_scripts/simulate_stereo_decode.py) · [_pure](./03_scripts/simulate_stereo_decode_pure.py) | Mathematical verification of Lab 04's stereo matrix. |

Run everything at once:

```bash
cd 03_scripts
python3 validate_flowgraph.py ../02_flowgraphs --compile
python3 simulate_rds_decode.py  --selftest
python3 simulate_adsb_decode.py --selftest
python3 simulate_bpsk_ber.py    --calibrate --ebno 2 4 6
```

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
│   ├── 06_fix_uhd_version_conflict.md  ← UHD version mismatch guide
│   └── fix_uhd_version_conflict.sh     ← Automated fix script
├── 01_fundamentals/                ← Theory
│   ├── 01_signals_basics.md            ┐
│   ├── 02_iq_sampling.md               │ read before Lab 01
│   ├── 03_rf_basics.md                 │
│   ├── 04_fm_theory.md                 ┘
│   ├── 05_sampling_and_filters.md      ┐
│   ├── 06_noise_snr_and_gain.md        │
│   ├── 07_am_and_narrowband_fm.md      │ read as the labs call for them
│   ├── 08_digital_modulation.md        │
│   ├── 09_synchronization.md           │
│   └── 10_error_detection_and_framing.md ┘
├── 02_flowgraphs/                  ← Hands-on labs
│   ├── lab01_simple_wbfm/
│   ├── lab02_enhanced_wbfm/
│   ├── lab03_advanced_wbfm/
│   ├── lab04_stereo_wbfm/
│   ├── lab05_iq_record_playback/       ← record + playback flowgraphs
│   ├── lab06_multimode_receiver/
│   ├── lab07_bpsk_link_sim/            ← no hardware needed
│   ├── lab08_rds_decoder/              ← live + from-file flowgraphs
│   └── lab09_adsb_receiver/            ← live + from-file flowgraphs
└── 03_scripts/
    ├── validate_flowgraph.py           ← deep .grc validation
    ├── simulate_bpsk_ber.py            ← BER vs theory
    ├── simulate_rds_decode.py          ← RDS signal generator + self-test
    ├── simulate_adsb_decode.py         ← ADS-B generator + self-test
    ├── simulate_stereo_decode.py
    └── simulate_stereo_decode_pure.py
```

Each lab folder contains a `README.md`, one or more `.grc` flowgraphs, and the `.py` that
`grcc` generates from them (byte-for-byte what GRC produces when you press F5).


---

## 🔬 About Verification

Claims in this repository are checked, and the checks are in the repo so you can re-run them.

### What is verified, and how

| Level | What it proves | How to run it |
|---|---|---|
| **Structural** | The `.grc` YAML is well-formed and self-consistent | `validate_flowgraph.py --structural-only` |
| **Deep** | Every block id, parameter expression and port type is valid against the **installed** GNU Radio 3.10 block library | `validate_flowgraph.py <dir>` |
| **Compile** | `grcc` generates Python, and that Python compiles | `validate_flowgraph.py <dir> --compile` |
| **Numerical** | The DSP produces the mathematically correct answer | the `simulate_*.py` scripts |
| **Execution** | The generated flowgraph actually runs and produces the right output | headless runs against synthetic captures |

All 12 flowgraphs pass structural + deep + compile.

### Results that were measured, not asserted

- **Lab 07** — the generated flowgraph was executed headlessly at Eb/N0 = 8 dB and converged to
  a BER of **3.9 × 10⁻⁴**; differentially-encoded BPSK theory predicts **3.82 × 10⁻⁴**.
- **Lab 08** — the generated flowgraph was executed against a synthetic FM+RDS capture and
  recovered the correct PI code, PS name, PTY and RadioText, decoding **90 CRC-valid groups**
  from 8 seconds against a theoretical maximum of ~91.
- **Lab 09** — the generated flowgraph was executed against a synthetic 1090 MHz capture and
  recovered **80 of 80** frames, with ICAO address, callsign, altitude, velocity and CPR
  position all matching the published Mode S reference vectors.
- **Fundamentals 05** — the tap-count equation is the one `firdes` uses internally; the doc's
  worked examples were checked against `firdes.low_pass()` directly.
- **Fundamentals 08** — the Eb/N0-to-`noise_voltage` formula was calibrated empirically against
  `analog.noise_source_c`, not assumed. (An earlier draft had a spurious factor of 2, which
  would have shifted every BER curve by 3 dB.)

### What is *not* verified

> **Honest note from the author:** **no over-the-air RF testing has been done** — the
> SignalSDR Pro was not connected to the authoring machine. Everything above is simulation,
> static analysis and headless execution against synthetic signals.
>
> That is a real limitation, and it is exactly why Labs 05, 08 and 09 ship file-based
> flowgraphs and synthetic signal generators: when a lab does not work on your hardware, run
> the offline version first. If the offline version works, the problem is RF — antenna, gain,
> placement, or simply nothing on the air — and not the flowgraph. If it fails, you have a
> deterministic, reproducible bug you can actually chase.
>
> Please run these against real hardware and report what you find. That is the spirit of this
> lab.

---

## 🚀 What's Next?

By the end of Lab 09 you will have built, from first principles: a wideband FM receiver, a
stereo MPX decoder, an AM/NBFM/WBFM multimode receiver, a synchronised BPSK link you measured
against theory, an RDS data decoder, and an aircraft transponder receiver. That covers analog
and digital, broadcast and packet, audio and data.

Where to go from here, roughly in order of difficulty:

- 🛰️ **NOAA APT weather satellites** (137 MHz) — Doppler tracking, AM-on-FM, image decoding
- 📟 **POCSAG / FLEX pagers** (150/450 MHz) — very simple FSK, still in service
- 🌦️ **Meteor-M LRPT** (137 MHz) — QPSK with Viterbi FEC and image reconstruction
- 📶 **LoRa** (868/915 MHz) — chirp spread spectrum, a genuinely different modulation
- 📱 **GSM / LTE signalling** — `gr-gsm`, srsRAN, LTESniffer
- 🛰️ **GPS** — the deepest of all: 20 dB *below* the noise floor, recovered by correlation
- 📻 **Transmitting** — legal only on bands you are licensed for. Check before you key up.

Each one reuses the same method this repo teaches: read the theory, plan the sample rates
backwards from the sink, build the chain, **validate against a signal you control**, and only
then point it at the sky.

---

## 🧠 The Mindset

SDR is not just "running a flowgraph". It's about understanding what happens **between every pair of blocks**:
- What is the sample rate at this point?
- What is the data type (complex, float, short)?
- What does the frequency spectrum look like?
- Why did we choose this specific decimation / filter tap count?

**Every block has a reason. Every parameter has a meaning.** This lab will teach you to ask
those questions — and every flowgraph here answers them in the `comment` field of every block,
which GRC shows on the canvas.

Three habits worth taking from this repo:

1. **Plan sample rates backwards from the sink.** 48 kHz audio × 8 = 384 kHz quadrature rate;
   × 125/24 = 2 MSPS at the radio. Everything falls out cleanly, and nothing aliases.
2. **Filter before you decimate, and filter before you AGC.** Both rules follow from one
   equation each, in Fundamentals 05 and 06.
3. **Validate against a signal you control before you blame the antenna.** It converts
   "why doesn't this work?" into a reproducible test.

Enjoy the journey! 🎧

---

*Target hardware: SignalSDR Pro (Signalens) as USRP B210 • Target software: GNU Radio 3.10.9.2 + UHD 4.6*
*10 theory documents · 9 labs · 12 flowgraphs · all structurally, deeply and compile-validated against GNU Radio 3.10.9.2*
