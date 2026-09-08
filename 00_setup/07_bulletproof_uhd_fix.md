# Bulletproof UHD Images Fix (System-Wide)

> **Use this guide if the automated fix script didn't work or if you keep getting:**
> ```
> [WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
> ```

---

## 🎯 The Problem in One Sentence

The `UHD_IMAGES_DIR` environment variable is **not set** in your current terminal session, so GNU Radio's UHD 4.6.0 library cannot find the B210 firmware images.

---

## 🔍 Diagnosing the Issue

Run these commands to confirm:

```bash
# Check if the variable is set
echo $UHD_IMAGES_DIR
# If output is empty ← THIS IS YOUR PROBLEM

# Check if images exist
ls /usr/share/uhd/4.10.0/images/usrp_b200_fw.hex
# If file exists ← images are fine, just the variable is missing

# Check ~/.bashrc
grep UHD_IMAGES_DIR ~/.bashrc
# If no output ← variable not configured permanently
```

---

## 🚀 The Bulletproof Fix (3 Commands)

### Command 1: Create a system-wide environment file

```bash
echo 'export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images' | sudo tee /etc/profile.d/uhd_images.sh
```

**What this does:**
- Creates `/etc/profile.d/uhd_images.sh`
- This file is sourced by **EVERY** shell session on the system
- Works in terminals, desktop launchers, cron jobs — everywhere

### Command 2: Make it executable

```bash
sudo chmod +x /etc/profile.d/uhd_images.sh
```

### Command 3: Load it in your CURRENT terminal

```bash
source /etc/profile.d/uhd_images.sh
```

---

## ✅ Verification

```bash
echo $UHD_IMAGES_DIR
```

**Expected output:**
```
/usr/share/uhd/4.10.0/images
```

---

## 🧪 Test GNU Radio

```bash
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab/02_flowgraphs/lab01_simple_wbfm"
gnuradio-companion lab01_simple_wbfm.grc
```

Press **F5**. You should see:

```
[INFO] [B200] Detected device: USRP B210
```

---

## 💡 Why Other Methods Fail

| Method | Why It Fails |
|--------|--------------|
| `export UHD_IMAGES_DIR=...` | Only works in the CURRENT terminal. Close it, and it's gone. |
| Adding to `~/.bashrc` | Only works for terminals. Desktop launchers (GNOME, KDE) don't source `~/.bashrc`. |
| Automated script + "no" to permanent | Variable only exists during script execution, then vanishes. |
| Automated script + "yes" to permanent | Works in terminals but NOT from desktop shortcuts. |

**The `/etc/profile.d/` method works everywhere** because it's part of the system-wide shell initialization.

---

## 🔄 If You Still See the Error After the Fix

### Scenario A: You opened GRC from desktop launcher AFTER applying fix

**Fix:** Reboot your computer. The `/etc/profile.d/` files are loaded at login.

```bash
sudo reboot
```

### Scenario B: You're in a non-login shell (rare)

**Fix:** Manually source the file:

```bash
source /etc/profile.d/uhd_images.sh
gnuradio-companion
```

### Scenario C: Using a non-bash shell (zsh, fish, etc.)

**For zsh:**
```bash
echo 'export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images' | sudo tee -a /etc/zsh/zprofile
```

**For fish:**
```bash
set -Ux UHD_IMAGES_DIR /usr/share/uhd/4.10.0/images
```

---

## 📊 Comparison: Fix Methods

| Method | Terminal | Desktop Launcher | Survives Reboot | Effort |
|--------|----------|------------------|-----------------|--------|
| `export` (temporary) | ✅ | ❌ | ❌ | 5 sec |
| `~/.bashrc` | ✅ | ❌ | ✅ | 10 sec |
| **`/etc/profile.d/`** | ✅ | ✅ | ✅ | **30 sec** |
| `~/.pam_environment` | ✅ | ✅ | ✅ | 1 min |

**Winner: `/etc/profile.d/`** — easiest, most reliable, works everywhere.

---

## 🧹 Undo the Fix

If you ever need to remove this:

```bash
sudo rm /etc/profile.d/uhd_images.sh
```

---

## 📚 References

- [Ubuntu Wiki: Environment Variables](https://help.ubuntu.com/community/EnvironmentVariables)
- [Linux Manual: profile.d](https://manpages.ubuntu.com/manpages/noble/man1/profile.1.html)
- [Ettus Research: UHD Troubleshooting](https://files.ettus.com/manual/page_troubleshooting.html)

---

## ✅ Success Checklist

- [ ] Ran `echo $UHD_IMAGES_DIR` — confirmed it was empty
- [ ] Created `/etc/profile.d/uhd_images.sh` with the export command
- [ ] Made the file executable with `chmod +x`
- [ ] Sourced the file with `source` command
- [ ] Verified `echo $UHD_IMAGES_DIR` now shows the path
- [ ] Launched GRC from terminal and ran a flowgraph successfully
- [ ] Flowgraph shows "Detected device: USRP B210" in logs
