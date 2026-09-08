# 📦 01 — Installing the UHD Driver

> **Estimated time:** 15–30 minutes  
> **Difficulty:** Easy  
> **Prerequisites:** Ubuntu 22.04/24.04 LTS, internet connection

---

## What Is UHD?

**UHD** stands for **USRP Hardware Driver**. It is the official driver developed by **Ettus Research** (now part of NI) to communicate with USRP (Universal Software Radio Peripheral) devices.

When the SignalSDR Pro is configured with the USRP B210 firmware, it **pretends to be a USRP B210**. That means UHD doesn't need to know it's talking to a Signalens device — it just sees a USRP B210 with a Cypress FX3 USB 3.0 interface, an AD9361 RF front-end, and a Xilinx Zynq FPGA. UHD handles:

- USB 3.0 streaming of I/Q samples
- FPGA firmware uploads
- RF front-end control (frequency, gain, bandwidth, antenna selection)
- Clock and time synchronization
- Multi-device MIMO setups

**Without UHD, GNU Radio cannot talk to the SignalSDR Pro (in B210 mode).**

---

## Architecture — What Happens Under the Hood

```
┌─────────────────────────┐
│   GNU Radio Flowgraph   │   ← Your flowgraph
│  (uses uhd_usrp_source) │
└────────────┬────────────┘
             │ UHD C++ / Python API
┌────────────▼────────────┐
│        UHD Driver       │   ← This is what we install
│  (libuhd, uhd images)   │
└────────────┬────────────┘
             │ libusb / USB 3.0
┌────────────▼────────────┐
│    SignalSDR Pro        │   ← Hardware, configured as B210
│   (Cypress FX3 + Zynq   │
│    + AD9361)            │
└─────────────────────────┘
```

---

## Method 1 — Install from Ettus PPA (Recommended for Ubuntu 24.04)

This is the **officially recommended** method from Ettus Research for Ubuntu systems [[1]].

### Step 1 — Add the PPA and Install UHD

```bash
sudo apt update
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt update
sudo apt install -y libuhd-dev uhd-host
```

**What each package does:**

| Package | Purpose |
|---|---|
| `uhd-host` | The UHD driver binaries, Python bindings, and command-line tools (`uhd_find_devices`, `uhd_usrp_probe`, etc.) |
| `libuhd-dev` | C++ headers and static library (only needed if you compile your own SDR apps) |

> **⚠️ Important:** The `uhd-images` package is **NOT** available in the PPA for newer UHD versions (4.7+). You MUST manually download the firmware images (Step 2).

### Step 2 — Download the UHD Firmware/FPGA Images (CRITICAL)

UHD needs to upload **two binary images** to the USRP every time it powers on:

1. **Firmware** (`usrp_b200_fw.hex`) — runs on the Cypress FX3 USB chip
2. **FPGA bitstream** (`usrp_b210_fpga.bin`) — configures the Zynq FPGA

**These images are NOT included with the PPA installation.** You must download them:

```bash
# Download ALL images (all USRP models — ~200 MB)
sudo uhd_images_downloader

# OR: Download ONLY B200/B210 images (faster — ~20 MB)
sudo uhd_images_downloader -t b2xx
```

The `uhd_images_downloader` tool is located at `/usr/bin/uhd_images_downloader` on UHD 4.10.0+. It downloads the firmware/FPGA binaries from Ettus' servers and places them in the correct location.

**Where are the images stored?**

| UHD Version | Images Path |
|---|---|
| UHD 4.10.0+ | `/usr/share/uhd/<version>/images/` (e.g., `/usr/share/uhd/4.10.0/images/`) |
| UHD 4.6 and earlier | `/usr/share/uhd/images/` |

Verify the download succeeded:

```bash
ls /usr/share/uhd/4.10.0/images/ | grep b2
# Expected output:
#   usrp_b200_fw.hex
#   usrp_b210_fpga.bin
```

### Step 3 — Verify the Installation

```bash
uhd_find_devices
# With no SDR connected: "[INFO] No devices found." (SUCCESS — driver works)
# With SignalSDR Pro (in B210 mode) connected: a B200 device entry.
```

**Common error if you skip Step 2:**
```
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
Using images directory: <no images directory located>
Set the environment variable 'UHD_IMAGES_DIR' appropriately...
```

**Fix:** Run `sudo uhd_images_downloader -t b2xx` (as described in Step 2).

### Step 4 — USB Permissions (Important for USB-based devices)

The B210/SignalSDR Pro connects via USB 3.0. Without proper permissions, UHD cannot access the device even if the driver is installed.

```bash
# Find the uhd-usrp.rules file and copy it to the udev rules directory
sudo cp /usr/lib/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add your user to the 'usrp' group (if it exists) or 'plugdev'
sudo usermod -aG plugdev $USER

# Log out and log back in (or reboot) for group changes to take effect
```

---

## Method 2 — Install from Ubuntu Repositories (Older UHD)

This installs UHD from the official Ubuntu package archives. On Ubuntu 24.04, this gives you UHD 4.6.0 (not the latest).

```bash
sudo apt update
sudo apt install -y libuhd-dev uhd-host uhd-images
```

> **Note:** The `uhd-images` package **may or may not exist** depending on your Ubuntu version. If `apt` cannot find it, use Method 1 instead.

### Verify

```bash
uhd_find_devices
# Should work without needing uhd_images_downloader (uhd-images package included them)
```

**Limitation:** UHD 4.6.0 is older and may lack support for newer features or USRP models.

---

## Method 3 — Install from Source (Advanced)

Only do this if you need a specific UHD version, custom patches, or are on a non-Ubuntu distro.

### Step 1 — Install Dependencies (Ubuntu 24.04)

```bash
sudo apt-get -y install autoconf automake build-essential ccache cmake \
  cpufrequtils doxygen ethtool fort77 g++ gir1.2-gtk-3.0 git \
  gobject-introspection gpsd gpsd-clients inetutils-tools \
  libasound2-dev libboost-all-dev libcomedi-dev libcppunit-dev \
  libfftw3-bin libfftw3-dev libfftw3-doc libfontconfig1-dev \
  libgmp-dev libgps-dev libgsl-dev liblog4cpp5-dev libncurses6 \
  libncurses-dev libpulse-dev libqt5opengl5-dev libqwt-qt5-dev \
  libsdl1.2-dev libtool libudev-dev libusb-1.0-0 libusb-1.0-0-dev \
  libusb-dev libxi-dev libxrender-dev libzmq3-dev libzmq5 \
  ncurses-bin python3-cheetah python3-click python3-click-plugins \
  python3-click-threading python3-dev python3-docutils python3-gi \
  python3-gi-cairo python3-gps python3-lxml python3-mako \
  python3-numpy python3-opengl python3-pyqt5 python3-requests \
  python3-scipy python3-setuptools python3-six python3-sphinx \
  python3-yaml python3-zmq python3-ruamel.yaml swig wget \
  python3-pygccxml libjs-mathjax python3-pyqtgraph
```

### Step 2 — Clone and Build UHD

```bash
git clone https://github.com/EttusResearch/uhd.git
cd uhd/host
mkdir build && cd build
cmake -DENABLE_MANUAL=OFF -DENABLE_PYTHON_API=ON -DCMAKE_INSTALL_PREFIX=/usr/local ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

### Step 3 — Download Images

```bash
sudo /usr/local/lib/uhd/utils/uhd_images_downloader.py
```

### Step 4 — Verify

```bash
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
uhd_find_devices
```

---

## 📋 Understanding UHD Images — Deep Dive

### Why Does UHD Need External Firmware?

Unlike a webcam or a keyboard, a USRP doesn't come pre-programmed with its operating firmware. Instead:

1. **The device is a blank slate** when powered on. The Zynq FPGA has no logic loaded.
2. **UHD uploads the firmware** (`usrp_b200_fw.hex`) to the Cypress FX3 USB controller via USB.
3. **UHD uploads the FPGA bitstream** (`usrp_b210_fpga.bin`) to configure the Zynq FPGA as a DSP pipeline.
4. **Only then** does the USRP become functional — it can tune frequencies, set gains, and stream I/Q samples.

This design allows Ettus to ship a single hardware platform that can be reconfigured for different purposes (B210, E310, etc.) by uploading different firmware.

### What's in `usrp_b200_fw.hex`?

This is the firmware for the **Cypress EZ-USB FX3** chip. It handles:
- USB 3.0 SuperSpeed communication
- Bulk streaming of I/Q samples (up to 56 MS/s)
- USB control transfers (for configuring the FPGA and RF front-end)
- DMA engine management

### What's in `usrp_b210_fpga.bin`?

This is the **FPGA bitstream** for the Xilinx Zynq-7020. It contains:
- The radio DSP pipeline (DDC, DUC, filters, CORDIC for tuning)
- The DMA controller that moves samples between the AD9361 and the FX3
- The register map that UHD reads/writes to control the device

### Version Compatibility

The firmware and FPGA bitstream **must match** the UHD version. UHD 4.10.0 expects specific firmware/FPGA versions. The `uhd_images_downloader` automatically fetches the correct versions.

---

## 🐛 Troubleshooting Common Issues

### Issue 1: `Could not find path for image: usrp_b200_fw.hex`

**Cause:** The firmware images are missing.

**Fix:**
```bash
sudo uhd_images_downloader -t b2xx
```

If that fails, set the environment variable manually:
```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
uhd_find_devices
```

### Issue 2: `No devices found` even when SDR is plugged in

**Possible causes:**
1. **USB permissions:** Run `sudo uhd_find_devices`. If it works, the issue is permissions. Fix with udev rules (see Step 4 above).
2. **Firmware not flashed:** The SignalSDR Pro hasn't been flashed with B210 firmware yet. See [02_flash_b210_firmware.md](./02_flash_b210_firmware.md).
3. **USB 2.0 instead of USB 3.0:** The B210 requires USB 3.0 for full functionality. Check with `lsusb -t` — you should see `5000M` (5 Gbps) not `480M`.

### Issue 3: `uhd_images_downloader` fails with network errors

**Cause:** Firewall, proxy, or Ettus servers are temporarily down.

**Fix:**
- Check your internet connection: `ping files.ettus.com`
- If behind a proxy: `export https_proxy=http://your-proxy:port`
- Manual download: Visit https://files.ettus.com/binaries/cache/ and download the `b2xx` image archive manually, then extract to `/usr/share/uhd/<version>/images/`.

### Issue 4: `uhd_images_downloader` not found

**Cause:** UHD not properly installed, or installed to a non-standard path.

**Fix:**
```bash
# Try the alternative path
sudo /usr/libexec/uhd/utils/uhd_images_downloader.py -t b2xx

# Or find it
find / -name "uhd_images_downloader*" 2>/dev/null
```

---

## 📊 Version Compatibility Matrix

| UHD Version | Ubuntu 22.04 | Ubuntu 24.04 | B210 Support | Notes |
|---|---|---|---|---|
| 4.6.0 | ✅ `apt` | ✅ `apt` | ✅ | Old but stable |
| 4.10.0 | ✅ PPA | ✅ PPA | ✅ | Latest, recommended |
| 4.7.x | ✅ PPA | ⚠️ PPA | ✅ | Intermediate |

---

## 📝 Summary Checklist

- [ ] `uhd-host` and `libuhd-dev` are installed (`dpkg -l | grep uhd`)
- [ ] `sudo uhd_images_downloader -t b2xx` ran successfully
- [ ] `/usr/share/uhd/4.10.0/images/usrp_b200_fw.hex` exists
- [ ] `/usr/share/uhd/4.10.0/images/usrp_b210_fpga.bin` exists
- [ ] `uhd_find_devices` runs without "Could not find path" errors
- [ ] USB permissions are configured (udev rules installed)

If any step fails, go to [Troubleshooting](./05_troubleshooting.md).

---

## ⚠️ CRITICAL WARNING: UHD Version Conflict with GNU Radio

**This is the #2 most common issue after installing UHD and GNU Radio.**

If you install UHD from the PPA (Method 1) **AND** install GNU Radio from Ubuntu's default repositories, you may encounter a **version conflict**:

### The Problem

- **Command-line tools** (`uhd_find_devices`) will use **UHD 4.10.0** (from PPA) ✓ Works
- **GNU Radio** will use **UHD 4.6.0** (from Ubuntu repos, compiled against it) ✗ Fails
- **Result:** `uhd_find_devices` works, but GNU Radio flowgraphs fail with:
  ```
  [WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
  ```

### Why This Happens

- GNU Radio 3.10.9 from Ubuntu repos was compiled against UHD 4.6.0
- The PPA's UHD 4.10.0 is newer, but GNU Radio's shared library (`libgnuradio-uhd.so`) is linked to UHD 4.6.0
- Each UHD version looks for firmware in its own directory:
  - UHD 4.10.0 looks in: `/usr/share/uhd/4.10.0/images/`
  - UHD 4.6.0 looks in: `/usr/share/uhd/4.6.0/images/` (which doesn't exist)

### Quick Fix

```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
gnuradio-companion
```

This tells UHD 4.6.0 to look in the UHD 4.10.0 directory for firmware images.

### Full Solution

For a complete explanation, automated fix script, and alternative solutions, see:
**[06_fix_uhd_version_conflict.md](./06_fix_uhd_version_conflict.md)**

---

## 📚 References

- [Ettus Research — Binary Installation Guide](https://files.ettus.com/manual/page_install_binary.html)
- [Ettus Knowledge Base — Building UHD on Linux](https://kb.ettus.com/Building_and_Installing_the_USRP_Open-Source_Toolchain_(UHD_and_GNU_Radio)_on_Linux)
- [Ubuntu man page — uhd_images_downloader](https://manpages.ubuntu.com/manpages/noble/man1/uhd_images_downloader.1.html)
- [UHD GitHub Repository](https://github.com/EttusResearch/uhd)

---

**Next:** [02 — Flashing the B210 Firmware on SignalSDR Pro →](./02_flash_b210_firmware.md)
