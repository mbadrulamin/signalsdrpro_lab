# 💾 02 — Flashing the USRP B210 Firmware on SignalSDR Pro

> **Estimated time:** 10–15 minutes  
> **Difficulty:** Easy  
> **Prerequisites:** UHD installed, SignalSDR Pro board, SD card, USB-C + USB-B cables

---

## Overview

The SignalSDR Pro boots from an SD card and loads a complete SDR image: Linux kernel, FPGA bitstream, firmware, and configuration. Depending on which image you put on the SD card, the board can emulate:

- **USRP B210** (what we want for GNU Radio / UHD)
- **ADALM-PLUTO** (IIO-based, useful for some tools like GQRX)
- **Native Signalens firmware**

For this lab we will use the **USRP B210 image**. Once flashed, the SignalSDR Pro will behave identically to a real USRP B210 from the host's perspective.

---

## Step 1 — Prepare the SD Card

### Hardware requirements
- A microSD card (8 GB or larger, Class 10 recommended)
- A USB SD card reader (or built-in reader)

### Format the SD card

The SignalSDR Pro bootloader expects a **FAT32** partition. On Ubuntu:

```bash
# Identify your SD card (be CAREFUL — don't pick your hard drive!)
lsblk

# Unmount if auto-mounted (replace sdX1 with your partition)
sudo umount /dev/sdX1

# Format as FAT32
sudo mkfs.vfat -F 32 -n SIGNALSDR /dev/sdX1
```

### Download the B210 boot image

Signalens provides pre-compiled binaries on GitHub:

```bash
# Create a working directory
mkdir -p ~/signalsdr_fw && cd ~/signalsdr_fw

# Download BOOT.BIN (this is the combined image: u-boot + FSBL + FPGA + firmware)
wget https://github.com/signalens/signalsdrpro/raw/main/bin/b210/v3/BOOT.bin
```

> 📌 The `BOOT.BIN` file is a Xilinx Boot Image Format file. It bundles:
> - The First-Stage Bootloader (FSBL)
> - The FPGA bitstream for the B210-emulating design
> - The ARM firmware that runs on the Zynq's Cortex-A9 cores

### Copy BOOT.BIN to the SD card

```bash
# Mount the SD card
sudo mount /dev/sdX1 /mnt

# Copy the file (note: it must be named BOOT.BIN, in all caps)
sudo cp ~/signalsdr_fw/BOOT.BIN /mnt/BOOT.BIN

# Safely unmount
sync
sudo umount /mnt
```

**Important:** The filename must be exactly `BOOT.BIN` (all uppercase). The Zynq's BootROM is case-sensitive when searching the FAT partition.

---

## Step 2 — Set the Jumper on the SignalSDR Pro

The SignalSDR Pro has a boot-selection jumper that tells the Zynq where to load the image from:

- **Internal flash** (default): loads the factory image
- **SD card**: loads from the SD card

👉 **Move the jumper to "SD card" position.** Refer to the [Signalens layout diagram](https://github.com/signalens/signalsdrpro/blob/main/img/transform/layout.png) for exact jumper location.

---

## Step 3 — Insert the SD Card and Connect Cables

1. **Insert the SD card** into the SignalSDR Pro's SD slot.
2. **Connect the power cable:** USB-C to USB-A. Use a good quality cable (charge-only cables won't work).
3. **Connect the data cable:** USB-B (on the SDR) to USB-A 3.0 (blue port on your PC). **USB 3.0 is strongly recommended** — USB 2.0 works but bandwidth is limited to ~2 MSPS.
4. **Attach an antenna** to the SMA port labeled `TX/RX` or `RX2`.

---

## Step 4 — Power Cycle and Watch the Boot Sequence

Plug in the power cable. The SignalSDR Pro will boot in roughly 10 seconds.

### First enumeration — "WestBridge"

Right after power-on, the Cypress FX3 USB controller enumerates with its default identity:

```bash
dmesg -w | grep -i usb
```

You will see something like:

```
usb 3-3: New USB device found, idVendor=04b4, idProduct=00f3
usb 3-3: Product: WestBridge
usb 3-3: Manufacturer: Cypress
```

This is **normal**. The Cypress chip is waiting for the Zynq to upload the firmware.

### Second enumeration — "USRP B200"

After ~10–20 seconds, the Zynq uploads the B210 firmware to the Cypress chip, and the device re-enumerates as a USRP:

```
usb 4-3: New USB device found, idVendor=2500, idProduct=0020
usb 4-3: Product: USRP B200
usb 4-3: Manufacturer: Ettus Research LLC
```

**Now you're ready to use it!**

---

## Step 5 — Verify with UHD

```bash
uhd_find_devices
```

Expected output:

```
[INFO] [UHD] linux; GNU C++ version 13.x.x; UHD_4.6.0.0
[INFO] [USB] Opening device 2500:0020...
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: 194170
    name: MyB210
    product: 2
    type: b200
```

Then probe it for full details:

```bash
uhd_usrp_probe
```

This will show you:
- Motherboard: **B210**
- Serial number
- Firmware version and FPGA version
- RX/TX frontends (both `FE-RX1`, `FE-RX2`, `FE-TX1`, `FE-TX2`)
- Frequency range: **50 MHz – 6 GHz**
- Gain range: 0–76 dB (RX), 0–89.8 dB (TX)
- Bandwidth range: 200 kHz – 56 MHz
- Internal GPSDO (yes, SignalSDR Pro has one!)

---

## ⚠️ Important Notes

1. **Always do a full power cycle** between tests. Unplug both the USB-C (power) and USB-B (data) cables, wait 2 seconds, then reconnect. The Zynq needs to fully reset.

2. **If the device stays as "WestBridge" forever**, the B210 firmware failed to load. Common causes:
   - Corrupted SD card image — re-download and re-flash
   - Jumper not set correctly
   - Insufficient USB power — use a powered USB hub

3. **If `uhd_find_devices` returns nothing**, check:
   - USB 3.0 cable is properly seated
   - udev rules installed (usually auto-installed by `uhd-host`)
   - `dmesg | tail -20` for USB errors

4. **The SignalSDR Pro's internal GPSDO is detected as "GPSTCXO v3.2 for SDRPro"** by UHD. You can use it as a reference clock for improved frequency accuracy.

---

## 📝 Summary Checklist

- [ ] SD card formatted as FAT32
- [ ] `BOOT.BIN` copied to SD card root (uppercase filename)
- [ ] Jumper set to SD card boot
- [ ] Both USB cables connected (power + data)
- [ ] `dmesg` shows transition from "WestBridge" → "USRP B200"
- [ ] `uhd_find_devices` shows a B200 device
- [ ] `uhd_usrp_probe` returns full device info

If any step fails, go to [Troubleshooting](./05_troubleshooting.md).

---

**Next:** [03 — Installing GNU Radio →](./03_install_gnuradio.md)
