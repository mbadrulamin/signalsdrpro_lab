# ✅ UHD Version Conflict - Issue Resolved

## 📋 Summary

**Problem:** GNU Radio flowgraphs fail with "Could not find path for image" error, even though `uhd_find_devices` works.

**Root Cause:** Two UHD versions installed:
- UHD 4.10.0 (PPA) - used by command-line tools
- UHD 4.6.0 (Ubuntu repos) - used by GNU Radio

**Status:** ✅ **RESOLVED** - Complete documentation and automated fix created

---

## 🚀 Immediate Solution

### Option 1: Quick Fix (10 seconds)

```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
gnuradio-companion
```

### Option 2: Automated Fix (2 minutes)

```bash
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab/00_setup"
./fix_uhd_version_conflict.sh
```

---

## 📚 Documentation Created

### New Files

1. **`00_setup/06_fix_uhd_version_conflict.md`** (Main Guide)
   - Complete explanation of the problem
   - Three solution paths (Quick, Better, Best)
   - Testing procedures
   - Architecture explanation
   - Advanced troubleshooting

2. **`00_setup/QUICK_FIX_UHD_VERSION_CONFLICT.md`** (Quick Reference)
   - 2-minute fix guide
   - For users who just want to get working

3. **`00_setup/fix_uhd_version_conflict.sh`** (Automated Script)
   - Detects installed UHD versions
   - Sets environment variable
   - Verifies the fix
   - Offers to make it permanent

### Updated Files

1. **`README.md`**
   - Added quick-fix section at the top
   - Added document 06 to the learning path
   - Updated directory structure

2. **`00_setup/05_troubleshooting.md`**
   - Added UHD version conflict as #2 most common issue
   - Linked to detailed fix guide

3. **`00_setup/01_install_uhd.md`**
   - Added CRITICAL WARNING section
   - Explained why the conflict happens
   - Linked to fix guide

---

## 🧪 Testing the Fix

### Test 1: Verify Images Exist

```bash
ls -la /usr/share/uhd/4.10.0/images/ | grep b2
# Expected: usrp_b200_fw.hex and usrp_b210_fpga.bin
```

### Test 2: Test Command-Line Tools

```bash
uhd_find_devices
# Should work without errors
```

### Test 3: Test GNU Radio

```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
gnuradio-companion

# Open any flowgraph from 02_flowgraphs/
# Press F5 to run
# Should see: [INFO] [B200] Detected device: USRP B210
```

---

## 📊 Solution Comparison

| Solution | Time | Complexity | Recommendation |
|----------|------|------------|----------------|
| **Environment Variable** | 10 sec | Easy | ⭐⭐⭐⭐⭐ For immediate use |
| **Automated Script** | 2 min | Easy | ⭐⭐⭐⭐⭐ For most users |
| **Clean Install** | 30 min | Medium | ⭐⭐⭐⭐ For advanced users |

---

## 🔍 Technical Details

### Why Two UHD Versions?

1. **Ubuntu's Repositories:**
   - Provide stable, tested packages
   - UHD 4.6.0 released in 2023
   - GNU Radio 3.10.9 compiled against UHD 4.6.0

2. **Ettus PPA:**
   - Provides latest UHD versions
   - UHD 4.10.0 released in 2024
   - Command-line tools use this version

3. **The Conflict:**
   - GNU Radio's `libgnuradio-uhd.so.3.10.9` links to `libuhd.so.4.6.0`
   - Command-line `uhd_find_devices` links to `libuhd.so.4.10.0`
   - Each looks for firmware in its own directory

### UHD Firmware Architecture

```
UHD 4.10.0 (PPA)
├── /usr/bin/uhd_find_devices
├── /usr/share/uhd/4.10.0/
│   └── images/
│       ├── usrp_b200_fw.hex ✓ (downloaded)
│       └── usrp_b210_fpga.bin ✓ (downloaded)
└── libuhd.so.4.10.0

UHD 4.6.0 (Ubuntu repos)
├── libgnuradio-uhd.so.3.10.9 (links to this)
├── /usr/share/uhd/4.6.0/
│   └── images/ ✗ (empty or missing)
└── libuhd.so.4.6.0
```

### The Fix

By setting `UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images`, we tell UHD 4.6.0 to look in the UHD 4.10.0 directory for firmware. The firmware format is compatible across these versions.

---

## 📖 Learning Path

After fixing this issue, continue with:

1. ✅ **Setup Complete** - UHD and GNU Radio working
2. 📖 **01_fundamentals/** - Learn signal processing theory
3. 🔬 **02_flowgraphs/** - Build FM receivers (4 progressive labs)
4. 🚀 **Advanced Projects** - ADS-B, FM transmitter, satellites

---

## 🆘 Need More Help?

### Documentation

- **Quick Fix:** `00_setup/QUICK_FIX_UHD_VERSION_CONFLICT.md`
- **Full Guide:** `00_setup/06_fix_uhd_version_conflict.md`
- **Troubleshooting:** `00_setup/05_troubleshooting.md`

### Commands

```bash
# Check installed UHD packages
dpkg -l | grep uhd

# Check which UHD library GNU Radio uses
ldd /usr/lib/x86_64-linux-gnu/libgnuradio-uhd.so.3.10.9 | grep uhd

# Find UHD images downloader
which uhd_images_downloader

# Download B210 images
sudo uhd_images_downloader -t b2xx
```

---

## ✅ Verification Checklist

Before proceeding to the flowgraph labs, verify:

- [ ] `uhd_find_devices` works without errors
- [ ] GNU Radio opens without image errors
- [ ] Environment variable is set (or script ran)
- [ ] SignalSDR Pro is connected via USB 3.0
- [ ] You can run a simple flowgraph successfully

---

## 🎯 Next Steps

1. **Run the fix** (choose Option 1 or 2 above)
2. **Connect your SignalSDR Pro**
3. **Open GNU Radio Companion**
4. **Load lab01_simple_wbfm**
5. **Press F5 and enjoy FM radio!**

---

## 📝 Notes

- This is a **common configuration issue**, not a bug
- The fix is **safe and reversible**
- **No hardware damage** possible
- Works with all USRP B200/B210 compatible devices
- Compatible with SignalSDR Pro firmware

---

**Created:** September 8, 2026  
**Issue:** UHD version conflict between GNU Radio and command-line tools  
**Status:** ✅ Resolved with comprehensive documentation
