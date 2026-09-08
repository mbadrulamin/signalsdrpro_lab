# 🚨 Quick Fix: Missing UHD Firmware Images

## Your Problem

You ran `uhd_find_devices` and got this error:

```
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
Using images directory: <no images directory located>
Set the environment variable 'UHD_IMAGES_DIR' appropriately or follow the below instructions to download the images package.
Please run: "/lib/x86_64-linux-gnu/uhd/utils/uhd_images_downloader.py"
No UHD Devices Found
```

## Why This Happens

You installed UHD 4.10.0.0 from the Ettus PPA, but the **firmware/FPGA images are NOT included** with the PPA package. UHD needs these binary files to upload to the SignalSDR Pro every time you power it on.

## The Fix (3 Commands)

Run these commands in order:

```bash
# 1. Download the B200/B210 firmware images (requires sudo)
sudo uhd_images_downloader -t b2xx

# 2. Verify the images were downloaded
ls /usr/share/uhd/4.10.0/images/ | grep b2

# Expected output:
#   usrp_b200_fw.hex
#   usrp_b210_fpga.bin

# 3. Test again
uhd_find_devices
```

## What Each Command Does

### Command 1: `sudo uhd_images_downloader -t b2xx`

This tool:
1. Connects to `https://files.ettus.com/binaries/cache/`
2. Downloads the firmware and FPGA bitstream files that match your UHD version (4.10.0.0)
3. Extracts them to `/usr/share/uhd/4.10.0/images/`
4. The `-t b2xx` flag tells it to download ONLY images for B200/B210 devices (faster, ~20 MB)

**Expected output:**
```
[INFO] Using base URL: https://files.ettus.com/binaries/cache/
[INFO] Images destination: /usr/share/uhd/4.10.0/images
[INFO] Downloading image package: b2xx-images-4.10.0.0.zip
[INFO] Extracting image package: b2xx-images-4.10.0.0.zip
[INFO] Images successfully installed
```

### Command 2: `ls /usr/share/uhd/4.10.0/images/ | grep b2`

This verifies the files exist. You should see:
- `usrp_b200_fw.hex` — Firmware for the Cypress FX3 USB 3.0 chip
- `usrp_b210_fpga.bin` — FPGA bitstream for the Xilinx Zynq-7020

### Command 3: `uhd_find_devices`

Now this should work without errors. With no SDR connected:
```
[INFO] [UHD] linux; GNU C++ version 13.3.0; Boost_108300; UHD_4.10.0.0-0ubuntu1~noble1
No UHD Devices Found
```

With your SignalSDR Pro (in B210 mode) connected via USB 3.0:
```
[INFO] [UHD] linux; GNU C++ version 13.3.0; Boost_108300; UHD_4.10.0.0-0ubuntu1~noble1
[INFO] [UHD] Mac OS; Clang version 14.0.0 ; Boost_108000; UHD_4.10.0.0
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: <your-serial-number>
    type: b200
    product: B 210
    name: B210
```

## Troubleshooting

### Problem: `sudo: command not found` or permission denied

You need sudo privileges. If you don't have sudo access, ask your system administrator.

### Problem: `uhd_images_downloader` fails with network error

**Possible causes:**
1. No internet connection — check with `ping files.ettus.com`
2. Firewall blocking — try `sudo uhd_images_downloader --proxy http://your-proxy:port`
3. Ettus servers temporarily down — wait a few minutes and retry

**Manual download workaround:**
```bash
# Download the image package manually
cd /tmp
wget https://files.ettus.com/binaries/cache/images/b2xx-images-4.10.0.0.zip

# Extract it
sudo mkdir -p /usr/share/uhd/4.10.0/images
sudo unzip b2xx-images-4.10.0.0.zip -d /usr/share/uhd/4.10.0/images/

# Verify
ls /usr/share/uhd/4.10.0/images/ | grep b2
```

### Problem: `uhd_images_downloader` not found

Try the alternative path:
```bash
sudo /usr/libexec/uhd/utils/uhd_images_downloader.py -t b2xx
```

Or find it:
```bash
find / -name "uhd_images_downloader*" 2>/dev/null
```

### Problem: Images downloaded but still getting the error

Set the environment variable manually:
```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
uhd_find_devices
```

To make it permanent, add to `~/.bashrc`:
```bash
echo 'export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images' >> ~/.bashrc
source ~/.bashrc
```

## Why Does UHD Need These Files?

The SignalSDR Pro (like a real USRP B210) is a **blank slate** when powered on:

1. The **Cypress FX3 USB chip** needs firmware (`usrp_b200_fw.hex`) to handle USB 3.0 communication
2. The **Xilinx Zynq FPGA** needs a bitstream (`usrp_b210_fpga.bin`) to configure its digital signal processing pipeline

UHD uploads these files every time the device powers on. This design allows the same hardware to be reconfigured for different purposes.

## Next Steps

Once `uhd_find_devices` works, proceed to:

1. [Flash the B210 firmware on your SignalSDR Pro](./00_setup/02_flash_b210_firmware.md)
2. [Verify the setup](./00_setup/04_verify_setup.md)

## Reference

- Updated documentation: [01_install_uhd.md](./00_setup/01_install_uhd.md)
- Official Ettus docs: https://files.ettus.com/manual/page_install_binary.html
