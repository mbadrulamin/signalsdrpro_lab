# 📦 Setup 01 — Install the UHD Driver

> **What you will do:** install **UHD**, the driver that lets GNU Radio talk to the SignalSDR
> Pro, and download the radio's start-up files ("images").
> **Before this:** Ubuntu 24.04 or 22.04, and an internet connection.
> **Time:** about 15–30 minutes. **Difficulty:** easy.

---

## 1. What is UHD?

**UHD** (USRP Hardware Driver) is the driver for **USRP** radios, made by Ettus Research
(now part of NI). A **driver** is the software that lets programs on your computer control a
piece of hardware.

The SignalSDR Pro, set up in B210 mode ([Setup 02](./02_flash_b210_firmware.md)),
**pretends to be a USRP B210**. So UHD treats it exactly like a real B210. It never needs to
know that it is really a Signalens device.

UHD does these jobs:

- sends the radio its start-up files (firmware and FPGA image) each time it is plugged in,
- tunes the radio, and sets its gain, bandwidth and antenna port,
- carries the IQ samples over USB 3.0 to your program.

```
   Your GNU Radio flowgraph        ← what you build
            │
         UHD driver                ← what this page installs
            │  USB 3.0
      SignalSDR Pro (as a B210)    ← the hardware
```

**Without UHD, GNU Radio cannot talk to the SignalSDR Pro.**

---

## 2. The one rule: use ONE version of UHD

UHD can be installed from two places:

| Source | UHD version on Ubuntu 24.04 | Matches GNU Radio from Ubuntu? |
|---|---|---|
| **Ubuntu's own packages** | 4.6.0 | ✅ **Yes** — GNU Radio 3.10.9 is built for exactly this one |
| The Ettus "PPA" (an extra package source) | 4.10, 4.11, … (newer) | ❌ No — GNU Radio still uses 4.6.0 |

If you install GNU Radio from Ubuntu **and** UHD from the Ettus PPA, your computer ends up with
**two** UHD versions. The command-line tools use the new one; GNU Radio uses the old one. Then
`uhd_find_devices` works, but every flowgraph fails with:

```
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
```

This is the most common setup problem with this course.
**[Setup 06](./06_fix_uhd_version_conflict.md)** fixes it if it has already happened to you.

> ✅ **For this course, use Option A below: Ubuntu's own packages.** Everything then matches,
> and the problem above cannot happen. This is also what [QUICKSTART](../QUICKSTART.md) does.

---

## 3. Option A — Ubuntu's own packages (recommended)

### Step 1 — Install

```bash
sudo apt update
sudo apt install -y uhd-host libuhd-dev
```

| Package | What it is |
|---|---|
| `uhd-host` | The UHD driver, its Python part, and tools like `uhd_find_devices` and `uhd_images_downloader` |
| `libuhd-dev` | Files needed only if you compile your own C++ programs. Harmless to have |

You will install GNU Radio from the same place in [Setup 03](./03_install_gnuradio.md).

### Step 2 — Download the radio's start-up files ("images")

Every time the radio is plugged in, UHD must send it **two files**. They are called **images**:

| File | What it is for |
|---|---|
| `usrp_b200_fw.hex` | **Firmware** for the USB chip, so it can talk USB 3.0 |
| `usrp_b210_fpga.bin` | The **FPGA image**: the digital circuit that moves samples between the radio chip and USB |

These files are **not** in the package. Download them:

```bash
sudo uhd_images_downloader -t b2xx
```

`-t b2xx` downloads only the files for the B200/B210 family (about 20 MB). Without it, the tool
downloads files for every USRP model (about 200 MB). Either works.

You should see it finish with a line like `Images download complete.`

### Step 3 — Allow your user to use the radio

The `uhd-host` package installs a **udev rule** (`60-uhd-host.rules`). A udev rule tells Linux
who may use a USB device. Add yourself to the groups the rule uses:

```bash
sudo usermod -aG usrp,plugdev $USER
```

Then **log out and log back in** (or restart). Group changes only take effect on a new login.

### Step 4 — Check it

With the radio **not** plugged in:

```bash
uhd_find_devices
```

✅ You should see UHD's version line, then `No UHD Devices Found`. That is **correct** — the
driver works; there is just no radio yet.

```
[INFO] [UHD] linux; GNU C++ version ...; Boost_...; UHD_4.6.0...
No UHD Devices Found
```

Now go to [Setup 02](./02_flash_b210_firmware.md) to prepare the radio itself.

---

## 4. Option B — the Ettus PPA (newer UHD, for advanced users)

Only choose this if you need a feature from a newer UHD **and** you are ready to manage two
versions. The official instructions are
[here](https://files.ettus.com/manual/page_install_binary.html).

```bash
sudo add-apt-repository ppa:ettusresearch/uhd
sudo apt update
sudo apt install -y libuhd-dev uhd-host
sudo uhd_images_downloader -t b2xx
```

The images then go into a folder named after the version, for example
`/usr/share/uhd/4.10.0/images/`.

> ⚠️ **Then read [Setup 06](./06_fix_uhd_version_conflict.md) before you run any flowgraph.**
> GNU Radio from Ubuntu will still use UHD 4.6.0, which looks for images in a different folder.
> Setup 06 explains how to point it at the right one.

---

## 5. Option C — build from source (experts only)

Only if you need a specific UHD version, your own changes, or a Linux that is not Ubuntu. You
would then usually build GNU Radio from source too, so both use the same UHD. Follow the Ettus
guide:
[Building and installing UHD and GNU Radio on Linux](https://kb.ettus.com/Building_and_Installing_the_USRP_Open-Source_Toolchain_(UHD_and_GNU_Radio)_on_Linux).

---

## 6. Why does the radio need images every time?

A USRP B210 (and the SignalSDR Pro pretending to be one) does not keep its working firmware
permanently. Each time it is plugged in:

1. The USB chip starts in a basic mode, waiting.
2. UHD sends it the **firmware** (`usrp_b200_fw.hex`). Now it can do USB 3.0 properly.
3. UHD sends the **FPGA image** (`usrp_b210_fpga.bin`). This sets up the digital circuits that
   filter, tune and move the samples.
4. Only then can the radio tune, set gain and stream IQ samples.

This is why the first flowgraph after plugging in takes a few seconds to start, and prints
lines like `Loading firmware image` and `Loading FPGA image`.

> 💡 **The image files must match the UHD version.** `uhd_images_downloader` always fetches the
> right ones for the UHD it belongs to. That is another reason to have only one UHD.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `Could not find path for image: usrp_b200_fw.hex` | Images not downloaded: run `sudo uhd_images_downloader -t b2xx`. If `uhd_find_devices` works but GNU Radio fails, you have two UHD versions: see [Setup 06](./06_fix_uhd_version_conflict.md) |
| `No UHD Devices Found` with the radio plugged in | Try `sudo uhd_find_devices`. If that works, it is a permissions problem: redo Step 3 and log out/in. Otherwise see [Setup 05](./05_troubleshooting.md) |
| The radio is on USB 2.0 | Run `lsusb -t`. The radio's line should show `5000M` (USB 3.0), not `480M`. Use a blue USB 3.0 port on the computer itself, not a hub |
| `uhd_images_downloader` fails with a network error | Check the internet (`ping files.ettus.com`). Behind a proxy: `export https_proxy=http://your-proxy:port`, then try again |
| `uhd_images_downloader: command not found` | `uhd-host` is not installed. Redo Step 1 |

More problems and fixes: [Setup 05 — Troubleshooting](./05_troubleshooting.md).

---

## ✅ Summary

- **UHD** is the driver between GNU Radio and the SignalSDR Pro (which acts as a USRP B210).
- Install UHD **from Ubuntu**, like GNU Radio, so there is **only one version**.
- Download the images once: `sudo uhd_images_downloader -t b2xx`.
- Add yourself to the `usrp` and `plugdev` groups, then log out and in.
- `uhd_find_devices` with no radio should say `No UHD Devices Found` — that means success.

## 🧠 Check yourself

1. What two files does UHD send to the radio each time it is plugged in?
   <details><summary>Answer</summary>The USB chip firmware (<code>usrp_b200_fw.hex</code>)
   and the FPGA image (<code>usrp_b210_fpga.bin</code>).</details>
2. `uhd_find_devices` finds the radio, but GNU Radio says `Could not find path for image`. What
   is the likely cause?
   <details><summary>Answer</summary>Two UHD versions are installed. GNU Radio uses the older
   one, which looks for images in a different folder. See Setup 06.</details>
3. Why do you need to log out and back in after `usermod`?
   <details><summary>Answer</summary>Group membership is only read when you log in.</details>

**Next:** [Setup 02 — Prepare the SignalSDR Pro →](./02_flash_b210_firmware.md)

---

## 📚 References

- [Ettus Research — binary installation guide](https://files.ettus.com/manual/page_install_binary.html)
- [Ettus Knowledge Base — building UHD and GNU Radio on Linux](https://kb.ettus.com/Building_and_Installing_the_USRP_Open-Source_Toolchain_(UHD_and_GNU_Radio)_on_Linux)
- [uhd_images_downloader manual page](https://manpages.ubuntu.com/manpages/noble/man1/uhd_images_downloader.1.html)
- [UHD on GitHub](https://github.com/EttusResearch/uhd)
