# 📡 SignalSDR Pro Lab — Learn Software-Defined Radio from Zero

> A step-by-step course for the **SignalSDR Pro** (made by Signalens) using **GNU Radio**.
> You start knowing nothing about radio. You finish able to build a TV transmitter.

---

## 👋 What is this?

A **software-defined radio (SDR)** is a radio where the computer does most of the work.
The hardware catches radio waves and turns them into numbers. Software then turns those
numbers into sound, pictures or data.

This means **one device can be many radios**. Today it is an FM radio. Tomorrow it tracks
aircraft. Next week it is a television transmitter. You only change the software.

This repository teaches you how to do that, one small step at a time.

| You will use | What it is |
|---|---|
| **SignalSDR Pro** | The radio hardware. It pretends to be a well-known radio called the **USRP B210**, so lots of existing software works with it. |
| **GNU Radio 3.10** | Free software for building radios. You connect blocks on screen, like drawing a diagram. |
| **UHD** | The driver. It lets GNU Radio talk to the radio over USB. |
| **Ubuntu Linux** | The operating system. Version 24.04 (22.04 also works). |

---

## 🚀 Start here — three steps

| Step | Page | Time |
|---|---|---|
| **1** | **[Your First 30 Minutes](./QUICKSTART.md)** — plug in, install, and hear a real FM station. No theory. | 30 min |
| **2** | **[Introduction to SDR](./01_fundamentals/00_introduction_to_sdr.md)** — what you just did, and why it works. | 45 min |
| **3** | **[Lab 01](./02_flowgraphs/lab01_simple_wbfm/README.md)** — build that FM radio yourself, from three blocks. | 30 min |

After that, follow the learning path below in order.

> 💡 **Stuck on a word?** Every term used in this repository is explained in the
> **[Glossary](./05_reference/01_glossary.md)**. Keep it open in another tab.

---

## 🗺️ The learning path

The course has six parts. Do Part 0 once. Then move between Part 1 (theory) and Part 2 (labs).
Each lab tells you which theory page to read before it.

```
  Part 0  Setup          install and test          ── once
     │
  Part 1  Fundamentals   the ideas you need        ─┐
     │                                              ├─ take turns
  Part 2  Labs           build real radios         ─┘
     │
  Part 4  Applications   589 more things to try
  Part 5  Reference      look things up
  Part 6  Teaching       run a class with this
```

### Part 0 — Setup

Do this before any lab. Most people only need pages 01, 03 and 04.

| # | Page | What it covers |
|---|---|---|
| 01 | [Install the UHD driver](./00_setup/01_install_uhd.md) | The software that talks to the radio |
| 02 | [Prepare the SignalSDR Pro](./00_setup/02_flash_b210_firmware.md) | The microSD card, the switches, the cables, the start-up order |
| 03 | [Install GNU Radio](./00_setup/03_install_gnuradio.md) | The software you build radios in |
| 04 | [Check that everything works](./00_setup/04_verify_setup.md) | Three commands that prove the setup is good |
| 05 | [Troubleshooting](./00_setup/05_troubleshooting.md) | Fixes for common problems |
| 06 | [Fix the "two UHD versions" problem](./00_setup/06_fix_uhd_version_conflict.md) | Only if you see `Could not find path for image` |

### Part 1 — Fundamentals (the theory)

Short chapters that explain the ideas. **Read 00–04 before Lab 01.** Read the others when a
lab asks for them.

| # | Page | In one line | Needed by |
|---|---|---|---|
| **00** | **[Introduction to SDR](./01_fundamentals/00_introduction_to_sdr.md)** | **What an SDR is, the SignalSDR Pro, the software, Malaysian radio bands** | **Everyone** |
| 01 | [Signals basics](./01_fundamentals/01_signals_basics.md) | What a signal is: frequency, amplitude, phase, bandwidth, decibels | Lab 01 |
| 02 | [IQ sampling](./01_fundamentals/02_iq_sampling.md) | Why an SDR gives you *two* numbers per sample, called I and Q | Lab 01 |
| 03 | [RF basics](./01_fundamentals/03_rf_basics.md) | Radio waves, the spectrum, and how a radio tunes | Lab 01 |
| 04 | [How FM works](./01_fundamentals/04_fm_theory.md) | How music rides on a radio wave, and how we get it back | Lab 01 |
| 05 | [Sampling and filters](./01_fundamentals/05_sampling_and_filters.md) | Keeping the signal you want and throwing away the rest | Labs 05–09 |
| 06 | [Noise, gain and signal strength](./01_fundamentals/06_noise_snr_and_gain.md) | Why "more gain" is not always better | Labs 05, 06, 08, 09 |
| 07 | [AM, SSB and narrow FM](./01_fundamentals/07_am_and_narrowband_fm.md) | The other voice modes: aircraft, marine, amateur | Lab 06 |
| 08 | [Digital modulation](./01_fundamentals/08_digital_modulation.md) | How radios send ones and zeros | Labs 07–09 |
| 09 | [Synchronisation](./01_fundamentals/09_synchronization.md) | How a receiver locks on to a transmitter's timing | Labs 07, 08 |
| 10 | [Error detection](./01_fundamentals/10_error_detection_and_framing.md) | How a receiver knows the data arrived correctly | Labs 08, 09 |
| 11 | [OFDM and digital TV](./01_fundamentals/11_ofdm_and_broadcast_systems.md) | How TV and Wi-Fi send many signals side by side | Lab 10 |
| 12 | [Video over the air](./01_fundamentals/12_video_over_the_air.md) | How a video file becomes a TV broadcast, and back | Labs 11, 12 |

### Part 2 — The labs (hands-on)

Each lab adds **one or two new ideas** to the one before. Please do them in order.

| Lab | What you build | New idea | Needs the radio? |
|---|---|---|---|
| 01 | [The simplest FM radio](./02_flowgraphs/lab01_simple_wbfm/README.md) | Three blocks make a radio | ✅ yes |
| 02 | [FM radio with a spectrum display](./02_flowgraphs/lab02_enhanced_wbfm/README.md) | Seeing signals; sliders; changing sample rate | ✅ yes |
| 03 | [An FM radio that sounds good](./02_flowgraphs/lab03_advanced_wbfm/README.md) | Filters, automatic volume, mute when no signal | ✅ yes |
| 04 | [Stereo FM](./02_flowgraphs/lab04_stereo_wbfm/README.md) | Separating left and right channels by hand | ✅ yes |
| 05 | [Record and play back radio](./02_flowgraphs/lab05_iq_record_playback/README.md) | Save the radio signal to a file, replay it later | only to record |
| 06 | [One radio, many modes](./02_flowgraphs/lab06_multimode_receiver/README.md) | AM, narrow FM and wide FM; a signal meter | ✅ yes |
| 07 | [A digital link, simulated](./02_flowgraphs/lab07_bpsk_link_sim/README.md) | Sending bits; counting errors | ❌ no |
| 08 | [Read a station's name (RDS)](./02_flowgraphs/lab08_rds_decoder/README.md) | Decoding hidden data inside an FM broadcast | optional |
| 09 | [Track aircraft (ADS-B)](./02_flowgraphs/lab09_adsb_receiver/README.md) | Decoding aircraft position messages at 1090 MHz | optional |
| 10 | [**Build a TV transmitter**](./02_flowgraphs/lab10_dvbt2_tx_rx/README.md) | Digital TV (DVB-T2) that a real TV can receive | 🚨 **transmits** |
| 11 | [**Build a TV receiver**](./02_flowgraphs/lab11_tv_receiver/README.md) | Scan for channels, tune, and watch | ✅ yes |
| 12 | [**Send and receive video at once**](./02_flowgraphs/lab12_fullduplex_tv/README.md) | Transmit and receive on one radio at the same time | 🚨 **transmits** |

> 💡 **No radio yet?** Labs 07, 08 and 09 can run with **no radio attached**. Labs 08 and 09
> each include a second version that reads a recorded file instead of the antenna.

**How the labs build on each other:**

```
  01 → 02 → 03 → 04     FM radio: from 3 blocks to full stereo
                  │
                 05     record the signal, so you can work without the radio
                  │
                 06     one radio for many kinds of signal
                  │
                 07     digital signals, in a safe simulation
                  │
                 08     real digital data hidden inside FM
                  │
                 09     a new band and a new signal: aircraft
                  │
                 10     now TRANSMIT: a digital TV station
                  │
                 11     receive TV: scan, tune, watch
                  │
                 12     transmit and receive together, on one radio
```

> 🚨 **Labs 10 and 12 transmit radio waves.** They use TV frequencies that are licensed to
> broadcasters. Only do them inside a **shielded box (Faraday cage)** or with a **cable and an
> attenuator** instead of an antenna. Both labs start with the power set to zero, but you are
> responsible for what you transmit. Read each lab's safety section first.

### Part 4 — The Applications Catalogue

Ideas for what to do next: **589 signals and projects** in 16 areas. Each entry lists the
frequency, how hard it is, what extra hardware it needs, and which labs prepare you for it.

| # | Area | Examples |
|---|---|---|
| — | **[Start here: index and difficulty ladder](./04_applications/README.md)** | What to try first, the law, antennas |
| 01 | [Broadcast and media](./04_applications/01_broadcast_and_media.md) | FM, AM, shortwave, digital radio, TV |
| 02 | [Aviation](./04_applications/02_aviation.md) | Aircraft tracking, airband voice |
| 03 | [Maritime](./04_applications/03_maritime.md) | Ship tracking (AIS), marine weather |
| 04 | [Satellites and space](./04_applications/04_satellite_and_space.md) | Weather satellite pictures, small satellites |
| 05 | [Weather and environment](./04_applications/05_weather_and_environment.md) | Weather balloons, lightning, meteors |
| 06 | [Land mobile and professional](./04_applications/06_land_mobile_and_professional.md) | Digital two-way radio, pagers |
| 07 | [Amateur (ham) radio](./04_applications/07_amateur_radio.md) | FT8, APRS, slow-scan TV pictures |
| 08 | [IoT and short range](./04_applications/08_iot_ism_and_short_range.md) | LoRa, tyre sensors, weather stations |
| 09 | [Cellular](./04_applications/09_cellular.md) | 2G, 4G, 5G |
| 10 | [Navigation and timing](./04_applications/10_navigation_and_timing.md) | GPS, time signals |
| 11 | [Radar and sensing](./04_applications/11_radar_and_sensing.md) | Passive radar, Doppler |
| 12 | [Science and radio astronomy](./04_applications/12_science_and_radio_astronomy.md) | Hearing the Milky Way's hydrogen |
| 13 | [Security research](./04_applications/13_security_research.md) | Understanding wireless protocols safely |
| 14 | [Test and measurement](./04_applications/14_test_measurement_and_infrastructure.md) | Using the SDR as a lab instrument |
| 15 | [Transmit projects](./04_applications/15_transmit_projects.md) | Beacons, your own links |
| 16 | [Oddities and history](./04_applications/16_oddities_and_historical.md) | Numbers stations, weather fax |

### Part 5 — Reference

For looking things up, not for reading from start to end.

| Page | Open it when… |
|---|---|
| [Glossary](./05_reference/01_glossary.md) | A word or acronym stops you. **202 terms**, explained simply. |
| [Signal identification](./05_reference/02_signal_identification.md) | You see something on the screen and want to know what it is. |
| [Antennas](./05_reference/03_antennas.md) | Always. The antenna matters more than anything else you can buy. |
| [Malaysia](./05_reference/04_malaysia.md) | You want local frequencies, the law, licences and clubs. |

### Part 6 — Teaching this course

| Page | Use it when… |
|---|---|
| [4-hour session plan](./06_training/SESSION_PLAN.md) | You are teaching a class. Timings, speaker notes, what to do if a demo fails. |
| [Slide deck](./06_training/intro_to_sdr.html) | 63 slides with speaker notes and a timer. Opens in any browser, no internet needed. |

### Part 3 — Scripts and tools

Helper programs in [`03_scripts/`](./03_scripts/). You do not need these to start. The labs
tell you when to use them.

| Script | What it does |
|---|---|
| [validate_flowgraph.py](./03_scripts/validate_flowgraph.py) | Checks that a `.grc` flowgraph is correct for the installed GNU Radio. `--compile` also turns it into Python. |
| [simulate_bpsk_ber.py](./03_scripts/simulate_bpsk_ber.py) | Runs Lab 07 at many noise levels and compares the error count with theory. |
| [simulate_rds_decode.py](./03_scripts/simulate_rds_decode.py) | Makes a test FM signal with known RDS data for Lab 08, and tests the decoder. |
| [simulate_adsb_decode.py](./03_scripts/simulate_adsb_decode.py) | Makes a test aircraft signal for Lab 09, and tests the decoder against known messages. |
| [make_test_ts.py](./03_scripts/make_test_ts.py) | Makes a simple test TV stream for Labs 10–12. No extra software needed. |
| [make_video_ts.py](./03_scripts/make_video_ts.py) | Turns your own video file into a TV stream a real TV will accept. Needs `ffmpeg`. |
| [dvbt_chain.py](./03_scripts/dvbt_chain.py) | The DVB-T transmitter and receiver as reusable parts, plus a self-test. |
| [scan_tv_band.py](./03_scripts/scan_tv_band.py) | Scans the TV band and tells you which channels have a TV signal. |
| [tv_playout.py](./03_scripts/tv_playout.py) | Plays a video in a loop, non-stop, like a real TV station. |
| [verify_tv_link.py](./03_scripts/verify_tv_link.py) | Sends a test stream and checks every byte came back correctly. 🚨 transmits. |
| [analyze_dvbt2.py](./03_scripts/analyze_dvbt2.py) | Measures a DVB-T2 signal file and checks it matches the standard. |
| [make_diagrams.py](./03_scripts/make_diagrams.py) | Redraws the pictures used in the Introduction. |
| [test_labs_offline.py](./03_scripts/test_labs_offline.py) | Runs the **real** lab flowgraphs on test signals with known answers, and checks the results (audio rate, squelch, stereo separation). No radio needed. |
| [run_offline.py](./03_scripts/run_offline.py) | Runs any lab's `.py` with a recorded file instead of the radio, and saves the audio instead of playing it. |
| [make_fm_test_iq.py](./03_scripts/make_fm_test_iq.py) | Makes a test FM station (mono or stereo, with a different tone in each ear) as an IQ file. |
| [check_links.py](./03_scripts/check_links.py) | Checks every link between the pages of this repository. |

To run all the self-tests at once:

```bash
cd 03_scripts
python3 validate_flowgraph.py ../02_flowgraphs --compile
python3 test_labs_offline.py
python3 check_links.py
python3 simulate_rds_decode.py  --selftest
python3 simulate_adsb_decode.py --selftest
python3 simulate_bpsk_ber.py    --calibrate --ebno 2 4 6
```

---

## 🛠️ What you need

| Item | Recommended |
|---|---|
| **Computer** | Ubuntu 24.04 or 22.04 (or DragonOS). At least 8 GB of memory. |
| **USB ports** | One **USB 3.0** port (usually blue) for data. One more port or a phone charger for power. |
| **microSD card** | 8 GB or bigger, Class 10. It holds the radio's start-up software. |
| **Cables** | USB 3.0 Type-B to Type-A (data). USB-C to Type-A (power). |
| **Antenna** | Anything with an SMA plug that covers 70 MHz – 6 GHz. A telescopic whip is fine to start. |

> ⚠️ **Plug the data cable straight into the computer**, not through a hub or a laptop dock.
> The SignalSDR Pro needs a lot of data and power. Many hubs and docks cannot supply enough,
> and then the radio does not appear at all.

---

## 🆘 Common first problems

| You see | Do this |
|---|---|
| `No UHD Devices Found` | Check the power, wait 30 seconds, use a USB 3.0 port on the computer itself. See [Troubleshooting](./00_setup/05_troubleshooting.md). |
| `Could not find path for image: usrp_b200_fw.hex` | Two versions of the driver are installed. Run the fix below. |
| Only hiss, no station | Move to another frequency, check the antenna is screwed on. |
| Loud, harsh, distorted sound | Turn the **gain** down. |

**The fix for `Could not find path for image`:**

```bash
cd "00_setup"
./fix_uhd_version_conflict.sh
```

The full explanation is in [Setup 06](./00_setup/06_fix_uhd_version_conflict.md).

---

## 🔬 Is it tested?

Yes. Every flowgraph is checked automatically, and most labs were run on a real
SignalSDR Pro receiving real stations.

- **All 17 flowgraphs** pass the automatic checks against the installed GNU Radio.
- **Labs 01, 03, 04, 05, 06 and 08** were run on real hardware, receiving BFM 89.9 MHz in
  Kuala Lumpur.
- **Labs 10, 11 and 12** sent and received digital TV. A real TV found the station and played
  the video. Lab 12 sent **79 million bytes** of video and received every single byte correctly.

We also wrote down what is **not** tested yet, and the lessons we learned from real hardware
that simulation could not show us. Read them in **[VERIFICATION.md](./VERIFICATION.md)**.

---

## 📁 What is in each folder

```
signalsdrpro_lab/
├── README.md              ← you are here
├── QUICKSTART.md          ← your first 30 minutes
├── VERIFICATION.md        ← what was tested, how, and what we learned
├── STYLE_GUIDE.md         ← how pages in this repo are written
├── 00_setup/              ← Part 0: install and test
├── 01_fundamentals/       ← Part 1: theory, chapters 00–12
├── 02_flowgraphs/         ← Part 2: the labs, one folder each
├── 03_scripts/            ← Part 3: helper and test programs
├── 04_applications/       ← Part 4: 589 things to try next
├── 05_reference/          ← Part 5: glossary, antennas, Malaysia
├── 06_training/           ← Part 6: slides and plan for teaching
└── images/                ← diagrams used by the pages
```

Each lab folder has:

- a `README.md` — the lab instructions. **Start here.**
- one or more `.grc` files — open these in GNU Radio Companion.
- a `.py` file for each `.grc` — the same flowgraph as a Python program. GNU Radio made it
  from the `.grc`. You can run it directly with `python3`.

---

## 🚨 The one rule

> **Listening is allowed almost everywhere. Transmitting is not.**
>
> The SignalSDR Pro can transmit from 70 MHz to 6 GHz. That includes aircraft, ship-safety and
> mobile-phone frequencies. Transmitting on them without a licence is against the law (in
> Malaysia, the Communications and Multimedia Act 1998). Ten of the twelve labs only listen.
> Before you transmit anything, read [Law and ethics](./04_applications/README.md#-law--ethics)
> and, in Malaysia, [how to get a licence](./05_reference/04_malaysia.md#3-getting-licensed-to-transmit).
