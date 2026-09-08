# Fix UHD Version Conflict (GNU Radio vs Command Line)

## 🚨 Problem Description

**Symptoms:**
- `uhd_find_devices` works and shows UHD 4.10.0.0
- GNU Radio flowgraphs fail with: `Could not find path for image: usrp_b200_fw.hex`
- GNU Radio shows UHD 4.6.0.0 in logs

**Error Message:**
```
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
Using images directory: <no images directory located>
```

---

## 🔍 Root Cause

Your system has **TWO different UHD installations**:

| Component | Version | Source | Used By |
|-----------|---------|--------|---------|
| `uhd_find_devices` | **UHD 4.10.0.0** | PPA (`ppa:ettusresearch/uhd`) | Command line |
| GNU Radio | **UHD 4.6.0.0** | Ubuntu repos | GRC flowgraphs |

### How This Happened

1. You installed GNU Radio from Ubuntu's default repositories
2. Ubuntu's GNU Radio 3.10.9.2 was compiled against UHD 4.6.0
3. Later, you installed UHD 4.10.0 from the Ettus PPA
4. Now you have two UHD versions:
   - UHD 4.10.0: Used by command-line tools (newer, in PATH)
   - UHD 4.6.0: Used by GNU Radio (compiled against it)

### Why It Fails

- You downloaded firmware images to: `/usr/share/uhd/4.10.0/images/`
- GNU Radio's UHD 4.6.0 looks for images in: `/usr/share/uhd/4.6.0/images/`
- That directory doesn't exist, so UHD 4.6.0 can't find the firmware

### Verification

Run these commands to confirm the issue:

```bash
# Check which UHD version command-line tools use
uhd_find_devices
# Look for: UHD_4.10.0.0

# Check which UHD library GNU Radio uses
ldd /usr/lib/x86_64-linux-gnu/libgnuradio-uhd.so.3.10.9 | grep uhd
# Expected: libuhd.so.4.6.0

# Check installed UHD packages
dpkg -l | grep uhd
# You'll see both 4.6.0 and 4.10.0 packages
```

---

## 🚀 Solutions

### **Solution 1: Quick Fix (Recommended for Testing)**

Set the `UHD_IMAGES_DIR` environment variable to point UHD 4.6.0 to the 4.10.0 images.

#### Steps

```bash
# 1. Export the environment variable
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images

# 2. Test immediately
gnuradio-companion

# 3. If it works, make it permanent
echo 'export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images' >> ~/.bashrc

# 4. Reload your shell
source ~/.bashrc
```

#### Why This Works

- The `UHD_IMAGES_DIR` environment variable overrides UHD's default search path
- UHD 4.6.0 will now look in `/usr/share/uhd/4.10.0/images/` for firmware
- The B210 firmware format is compatible across UHD versions (4.6.0 → 4.10.0)

#### Pros and Cons

✅ **Pros:**
- Fastest solution (takes 10 seconds)
- No system changes required
- Works immediately

❌ **Cons:**
- Requires setting environment variable in every new terminal
- Two UHD versions still exist (potential for future conflicts)

---

### **Solution 2: Download Images for UHD 4.6.0**

Download firmware images specifically for UHD 4.6.0.

#### Steps

```bash
# 1. Run the UHD 4.6.0 image downloader
sudo /usr/bin/uhd_images_downloader

# 2. Verify images are in the correct location
ls -la /usr/share/uhd/4.6.0/images/ | grep b2
# Expected: usrp_b200_fw.hex and usrp_b210_fpga.bin

# 3. Test GNU Radio
gnuradio-companion
```

#### Why This Works

- The downloader fetches B210 firmware compatible with UHD 4.6.0
- Images are placed in `/usr/share/uhd/4.6.0/images/`
- GNU Radio's UHD 4.6.0 finds the images in the expected location

#### Pros and Cons

✅ **Pros:**
- Clean solution (each UHD has its own images)
- No environment variable needed
- Follows UHD's expected directory structure

❌ **Cons:**
- Downloads firmware twice (wastes ~20 MB)
- Two UHD versions still exist

---

### **Solution 3: Clean Install (Best Long-term)**

Remove conflicting UHD 4.6.0 and use only UHD 4.10.0 from the PPA.

#### Steps

```bash
# 1. Remove all UHD and GNU Radio packages
sudo apt remove --purge 'libuhd*' uhd-host gnuradio gnuradio-dev
sudo apt autoremove

# 2. Update package lists
sudo apt update

# 3. Install only PPA UHD (4.10.0)
sudo apt install libuhd-dev uhd-host

# 4. Download images for UHD 4.10.0
sudo uhd_images_downloader -t b2xx

# 5. Verify UHD 4.10.0 is the only version
uhd_find_devices
# Should show: UHD_4.10.0.0

# 6. Reinstall GNU Radio
sudo apt install gnuradio

# 7. Verify GNU Radio now uses UHD 4.10.0
gnuradio-companion
# Check log for: UHD_4.10.0.0
```

#### Why This Works

- Eliminates the version conflict entirely
- GNU Radio will now use UHD 4.10.0 (if recompiled) or you'll need to build GNU Radio from source

#### Pros and Cons

✅ **Pros:**
- Cleanest solution (only one UHD version)
- Eliminates potential future conflicts
- Uses latest UHD features and bug fixes

❌ **Cons:**
- Requires reinstalling GNU Radio
- Ubuntu's GNU Radio package might still pull in UHD 4.6.0 dependencies
- May need to build GNU Radio from source or use PyBOMBS

#### Alternative: Build GNU Radio from Source

If Ubuntu's GNU Radio still uses UHD 4.6.0 after Solution 3:

```bash
# Install PyBOMBS (Python package manager for GNU Radio)
sudo pip3 install pybombs

# Configure PyBOMBS
pybombs recipes add gr-recipes git+https://github.com/gnuradio/gr-recipes.git
pybombs recipes add gr-etcetera git+https://github.com/gnuradio/gr-etcetera.git

# Install GNU Radio from source (will use UHD 4.10.0)
pybombs prefix ~/gnuradio
pybombs install gnuradio

# Activate the prefix
source ~/gnuradio/setup_env.sh

# Test
gnuradio-companion
```

---

## 🧪 Testing the Fix

After applying any solution, verify it works:

### Test 1: Command Line

```bash
# With SignalSDR Pro connected
uhd_find_devices

# Expected output:
[INFO] [UHD] linux; GNU C++ version 13.3.0; Boost_108300; UHD_4.10.0.0-0ubuntu1~noble1
[INFO] [B200] Detected device: USRP B210
```

### Test 2: GNU Radio Companion

```bash
# With environment variable set (Solution 1)
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images

# Or without (Solutions 2 and 3)
gnuradio-companion

# Open any flowgraph and run
# Expected log:
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
[INFO] [B200] Detected device: USRP B210
```

### Test 3: Python Script

```bash
# Create a test script
cat > test_uhd.py << 'EOF'
from gnuradio import uhd

try:
    usrp = uhd.usrp_source("num_recv_frames=960", uhd.stream_args(cpu_format="fc32"))
    print("✓ UHD initialized successfully")
    print(f"Device detected: {usrp.get_pp_string()}")
except Exception as e:
    print(f"✗ Error: {e}")
EOF

# Run the test
python3 test_uhd.py
```

---

## 📊 Solution Comparison

| Solution | Time | Complexity | Cleanliness | Recommendation |
|----------|------|------------|-------------|----------------|
| **Solution 1** (Environment Variable) | 10 sec | Easy | Temporary | ⭐⭐⭐⭐⭐ For quick testing |
| **Solution 2** (Download Images) | 5 min | Easy | Moderate | ⭐⭐⭐⭐ For stable use |
| **Solution 3** (Clean Install) | 30 min | Medium | Clean | ⭐⭐⭐⭐⭐ For production |

---

## 🔧 Advanced Troubleshooting

### If Solution 1 Doesn't Work

**Problem:** UHD 4.6.0 rejects UHD 4.10.0 images

**Fix:** Try Solution 2 or 3

### If Solution 2 Fails

**Problem:** The downloader script is missing

**Fix:**
```bash
# Find the downloader script
find /usr -name "uhd_images_downloader*" 2>/dev/null

# If not found, reinstall uhd-host
sudo apt install --reinstall uhd-host
```

### If Solution 3 Breaks GNU Radio

**Problem:** Ubuntu's GNU Radio package has hard dependency on UHD 4.6.0

**Fix:** Build GNU Radio from source (see Alternative in Solution 3)

### If You See "Permission Denied"

**Problem:** USB permissions not set up

**Fix:**
```bash
# Create udev rules
sudo cp /usr/lib/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to plugdev group
sudo usermod -a -G plugdev $USER

# Re-login or reboot
```

---

## 📚 Understanding the Architecture

### Why Two UHD Versions?

1. **Ubuntu's Repositories:**
   - Provide stable, tested packages
   - Update slowly (UHD 4.6.0 released in 2023)
   - Optimized for Ubuntu's release cycle

2. **Ettus PPA:**
   - Provides latest UHD versions
   - Updates frequently (UHD 4.10.0 released in 2024)
   - Includes latest features and bug fixes

3. **The Conflict:**
   - GNU Radio was compiled against UHD 4.6.0 (Ubuntu version)
   - Command-line tools use UHD 4.10.0 (PPA version)
   - Each looks for firmware in its own directory

### UHD Firmware Architecture

```
UHD Installation
├── libuhd.so (shared library)
│   ├── Version 4.6.0 (Ubuntu)
│   └── Version 4.10.0 (PPA)
├── uhd_find_devices (command-line tool)
└── /usr/share/uhd/
    ├── 4.6.0/
    │   └── images/ (empty or missing)
    └── 4.10.0/
        └── images/
            ├── usrp_b200_fw.hex (FX3 USB firmware)
            └── usrp_b210_fpga.bin (Zynq FPGA bitstream)
```

**Every time you power on a USRP:**
1. UHD uploads `usrp_b200_fw.hex` to the Cypress FX3 chip
2. UHD uploads `usrp_b210_fpga.bin` to the Xilinx Zynq-7020 FPGA
3. The device is now ready to receive/transmit

**If images are missing:**
- UHD can't initialize the device
- You get the "Could not find path for image" error
- The device appears as "not found"

---

## 📖 References

- [Ettus Research: Installing UHD](https://files.ettus.com/manual/page_install_binary.html)
- [GNU Radio Wiki: UHD Installation](https://wiki.gnuradio.org/index.php?title=UHD_Installation)
- [Ubuntu PPA for UHD](https://launchpad.net/~ettusresearch/+archive/ubuntu/uhd)
- [USRP B210 Hardware Page](https://www.ettus.com/all-products/b210/)

---

## 🎯 Next Steps

1. **Choose a solution** (start with Solution 1 for quick testing)
2. **Verify the fix** using the test procedures above
3. **Connect your SignalSDR Pro** and proceed to the next lab
4. **Document your choice** in `00_setup/CHOSEN_SOLUTION.md` for future reference

---

## 📝 Notes

- **This is a common issue** when mixing PPA and Ubuntu packages
- **Not a bug** in GNU Radio or UHD, just a configuration issue
- **Easily fixable** with any of the three solutions
- **Won't affect** your SignalSDR Pro or flowgraphs once resolved
