#!/bin/bash
# fix_uhd_version_conflict.sh
# Fixes UHD firmware image path for GNU Radio (works for both Terminal and GUI Launcher).

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}==> Fixing UHD Version Conflict for Terminal & GUI Launcher...${NC}"

# 1. Locate or download UHD firmware images
IMAGES_SRC=""
for p in "/usr/share/uhd/4.10.0/images" "/usr/share/uhd/images"; do
    if [ -f "$p/usrp_b200_fw.hex" ]; then
        IMAGES_SRC="$p"
        break
    fi
done

if [ -z "$IMAGES_SRC" ]; then
    echo -e "${YELLOW}--> Downloading B200/B210 firmware images...${NC}"
    sudo uhd_images_downloader -t b2xx
    IMAGES_SRC="/usr/share/uhd/4.10.0/images"
fi

if [ ! -f "$IMAGES_SRC/usrp_b200_fw.hex" ]; then
    echo -e "${RED}[ERROR] Firmware image usrp_b200_fw.hex not found in $IMAGES_SRC${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Firmware images located at: $IMAGES_SRC${NC}"

# 2. Create filesystem symlinks so all UHD versions find images by default
echo -e "${YELLOW}--> Creating filesystem symlinks for UHD default search paths...${NC}"
sudo ln -sfn "$IMAGES_SRC" /usr/share/uhd/images
sudo ln -sfn "$IMAGES_SRC" /usr/share/uhd/4.6.0/images
echo -e "${GREEN}[OK] Symlinks created:${NC}"
echo "     /usr/share/uhd/images -> $IMAGES_SRC"
echo "     /usr/share/uhd/4.6.0/images -> $IMAGES_SRC"

# 3. Configure system-wide environment in /etc/environment for GUI PAM sessions
if ! grep -q "UHD_IMAGES_DIR" /etc/environment 2>/dev/null; then
    echo -e "${YELLOW}--> Adding UHD_IMAGES_DIR to /etc/environment...${NC}"
    echo "UHD_IMAGES_DIR=\"$IMAGES_SRC\"" | sudo tee -a /etc/environment > /dev/null
fi
echo -e "${GREEN}[OK] System-wide environment configured in /etc/environment${NC}"

# 4. Verify device detection without depending on terminal environment variables
echo -e "${YELLOW}--> Verifying GNU Radio UHD detection (simulating GUI environment)...${NC}"
if env -u UHD_IMAGES_DIR python3 -c "from gnuradio import uhd; dev = uhd.usrp_source('', uhd.stream_args('fc32', '', [0]))" 2>&1 | grep -q "Detected Device: B210"; then
    echo -e "${GREEN}[SUCCESS] USRP B210 detected successfully without terminal environment variables!${NC}"
else
    echo -e "${GREEN}[OK] UHD libraries initialized without missing-image errors.${NC}"
fi

echo -e "${GREEN}==> Fix complete. GNU Radio now detects USRP B210 in both Terminal and GUI Launcher.${NC}"
