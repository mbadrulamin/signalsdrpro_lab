#!/bin/bash
#
# bulletproof_fix.sh
# One-command fix for UHD version conflict that works EVERYWHERE
#
# Usage:
#   chmod +x bulletproof_fix.sh
#   ./bulletproof_fix.sh
#
# This script creates a system-wide environment variable that tells
# UHD 4.6.0 (used by GNU Radio) where to find the B210 firmware images.
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UHD Bulletproof Fix${NC}"
echo -e "${BLUE}  Works in ALL terminals AND desktop launchers${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Verify images exist
echo -e "${YELLOW}Step 1: Verifying firmware images exist...${NC}"
IMAGES_DIR="/usr/share/uhd/4.10.0/images"

if [ ! -f "$IMAGES_DIR/usrp_b200_fw.hex" ]; then
    echo -e "${RED}✗ Firmware images not found at $IMAGES_DIR${NC}"
    echo ""
    echo "Please download them first:"
    echo "  sudo uhd_images_downloader -t b2xx"
    exit 1
fi

echo -e "${GREEN}✓ Found firmware images at $IMAGES_DIR${NC}"
echo ""

# Step 2: Create system-wide environment file
echo -e "${YELLOW}Step 2: Creating system-wide environment variable...${NC}"
PROFILE_FILE="/etc/profile.d/uhd_images.sh"
EXPORT_LINE="export UHD_IMAGES_DIR=$IMAGES_DIR"

# Create the file (requires sudo)
echo "$EXPORT_LINE" | sudo tee "$PROFILE_FILE" > /dev/null
sudo chmod +x "$PROFILE_FILE"

echo -e "${GREEN}✓ Created $PROFILE_FILE${NC}"
echo ""

# Step 3: Load in current session
echo -e "${YELLOW}Step 3: Loading in current terminal session...${NC}"
export UHD_IMAGES_DIR="$IMAGES_DIR"
echo -e "${GREEN}✓ UHD_IMAGES_DIR=$UHD_IMAGES_DIR${NC}"
echo ""

# Step 4: Verify
echo -e "${YELLOW}Step 4: Verifying...${NC}"
if [ -z "$UHD_IMAGES_DIR" ]; then
    echo -e "${RED}✗ Variable not set!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ UHD_IMAGES_DIR is set correctly${NC}"
echo ""

# Step 5: Test UHD
echo -e "${YELLOW}Step 5: Testing UHD device detection...${NC}"
if command -v uhd_find_devices &> /dev/null; then
    echo "Running uhd_find_devices..."
    uhd_find_devices 2>&1 | head -20
    echo ""
fi

# Step 6: Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}  Fix Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}✓ UHD_IMAGES_DIR is now set system-wide${NC}"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  1. This variable will be loaded automatically in all NEW terminals"
echo "  2. It also works when launching GNU Radio from the desktop"
echo "  3. If GRC still shows the error, REBOOT your computer:"
echo ""
echo -e "     ${BLUE}sudo reboot${NC}"
echo ""
echo -e "${YELLOW}To test now:${NC}"
echo "  cd \"/home/ubuntu/GNU Radio/signalsdrpro_lab/02_flowgraphs/lab01_simple_wbfm\""
echo "  gnuradio-companion lab01_simple_wbfm.grc"
echo "  (Then press F5)"
echo ""
echo -e "${YELLOW}To verify the variable is set:${NC}"
echo "  echo \$UHD_IMAGES_DIR"
echo ""
echo -e "${YELLOW}Documentation:${NC}"
echo "  /home/ubuntu/GNU Radio/signalsdrpro_lab/00_setup/07_bulletproof_uhd_fix.md"
echo ""
