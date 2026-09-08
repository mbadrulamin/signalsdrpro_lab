# 🚀 Quick Fix: UHD Version Conflict

**Time required:** 2 minutes  
**Difficulty:** Beginner  

---

## The Problem

Your system has **two UHD versions**:
- UHD 4.10.0 (used by `uhd_find_devices`) ✓ Works
- UHD 4.6.0 (used by GNU Radio) ✗ Fails with "Could not find path for image"

---

## The Solution

### Option 1: Quick Fix (Recommended)

Run this in your terminal:

```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
gnuradio-companion
```

**To make it permanent:**
```bash
echo 'export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: Automated Fix

```bash
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab/00_setup"
chmod +x fix_uhd_version_conflict.sh
./fix_uhd_version_conflict.sh
```

---

## Verify It Works

1. Connect your SignalSDR Pro
2. Open GNU Radio Companion
3. Load any flowgraph from `02_flowgraphs/`
4. Press F5 to run
5. You should see: `[INFO] [B200] Detected device: USRP B210`

---

## Why This Happens

- GNU Radio 3.10.9 from Ubuntu repos was compiled against UHD 4.6.0
- You later installed UHD 4.10.0 from the Ettus PPA
- Command-line tools use UHD 4.10.0 (newer, in PATH)
- GNU Radio uses UHD 4.6.0 (compiled against it)
- Each looks for firmware in its own directory

**Fix:** Tell UHD 4.6.0 to look in the UHD 4.10.0 directory for firmware images.

---

## More Information

For a complete explanation and alternative solutions, see:
[06_fix_uhd_version_conflict.md](06_fix_uhd_version_conflict.md)

---

## Need Help?

Check the full troubleshooting guide:
[05_troubleshooting.md](05_troubleshooting.md)
