# 🧰 03 — Installing GNU Radio

> **Estimated time:** 10–20 minutes  
> **Difficulty:** Easy  
> **Prerequisites:** UHD installed

---

## What Is GNU Radio?

**GNU Radio** is the leading open-source toolkit for software-defined radio. It provides:

- Hundreds of ready-to-use signal processing **blocks** (filters, modulators, demodulators, visualizers, etc.)
- A Python and C++ API for building custom radio applications
- **GNU Radio Companion (GRC)** — a visual block-diagram editor that generates Python code

GNU Radio is the standard in academia, industry, and the hobbyist community. Almost every SDR tutorial you'll ever find assumes GNU Radio.

**Version we target:** GNU Radio 3.10.x (the stable series for Ubuntu 24.04).

---

## Method 1 — Install from Ubuntu Repositories (Recommended)

On Ubuntu 24.04, GNU Radio 3.10.9 is available directly from apt:

```bash
sudo apt update
sudo apt install -y gnuradio gnuradio-dev
```

### What gets installed

| Component | Description |
|---|---|
| `gnuradio-companion` | The visual flowgraph editor (GUI) |
| `grcc` | Command-line flowgraph compiler |
| `gnuradio-config-info` | Prints version and build info |
| Python modules | `gnuradio`, `pmt`, various block libraries |
| Documentation | Block help, examples |

### Verify

```bash
gnuradio-config-info --version
# Expected: "3.10.9.2" (or similar 3.10.x)

gnuradio-companion --version
# Expected: "grcc (GNU Radio Companion) 3.10.x.x"
```

Launch GRC to test the GUI:

```bash
gnuradio-companion &
```

A window should open showing the block library on the left and an empty canvas.

---

## Method 2 — Install via PyBOMBS (for the latest version)

**PyBOMBS** (Python Build Overlay for GNU Radio) is a package manager that can install GNU Radio from source with custom configuration. Use this if you need features from GNU Radio 3.11 / `main` branch.

```bash
# Install pybombs
sudo apt install -y python3-pip git
pip3 install --user pybombs

# Configure and install GNU Radio
pybombs recipes add gr-recipes git+https://github.com/gnuradio/gr-recipes.git
pybombs recipes add gr-etcetera git+https://github.com/gnuradio/gr-etcetera.git
pybombs prefix init ~/gnuradio-prefix -R gnuradio-default
pybombs -p ~/gnuradio-prefix install gnuradio
```

Activate the prefix:

```bash
. ~/gnuradio-prefix/setup_env.sh
gnuradio-config-info --version
```

---

## Method 3 — Install from PPA (for Ubuntu 22.04)

If you're on Ubuntu 22.04 and want 3.10 instead of the default 3.10.x:

```bash
sudo add-apt-repository ppa:gnuradio/gnuradio-releases
sudo apt update
sudo apt install -y gnuradio
```

---

## Essential Add-ons

For the best experience, install these optional packages:

```bash
# QT GUI support (required for all visual sinks)
sudo apt install -y python3-pyqt5 python3-pyqtgraph

# Audio support
sudo apt install -y pulseaudio-utils alsa-utils

# UHD integration (already done in 01)
sudo apt install -y uhd-host

# Optional: gr-osmosdr (for RTL-SDR, HackRF, BladeRF, etc.)
sudo apt install -y gr-osmosdr

# Optional: useful analysis tools
sudo apt install -y gqrx-sdr inspectrum
```

---

## 🧪 Test Your Installation with a Minimal Flowgraph

Let's build a 3-block flowgraph that generates a 1 kHz sine wave and plays it through your speakers.

1. Launch GRC: `gnuradio-companion`
2. Drag in these blocks from the left library:
   - **Analog → Signal Source** (sine wave generator)
   - **Audio → Sink** (speaker output)
3. Connect the output of Signal Source to the input of Audio Sink.
4. Double-click Signal Source and set:
   - Waveform: Sine
   - Frequency: 1000
   - Amplitude: 0.5
   - Sample Rate: 48000
5. Double-click Audio Sink:
   - Sample Rate: 48000
6. Click the ▶ **Execute** button.

You should hear a 1 kHz tone. 🎵 If you do, GNU Radio is working perfectly.

---

## 📝 Summary Checklist

- [ ] `gnuradio-config-info --version` returns `3.10.x`
- [ ] `gnuradio-companion` launches and shows the GUI
- [ ] A minimal tone-generating flowgraph runs
- [ ] You can hear audio through the Audio Sink

If any step fails, check [Troubleshooting](./05_troubleshooting.md).

---

**Next:** [04 — Verifying the Full Setup →](./04_verify_setup.md)
