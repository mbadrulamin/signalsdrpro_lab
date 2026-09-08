#!/bin/bash
#
# fix_uhd_version_conflict.sh
# Quick fix for UHD version conflict between GNU Radio and command-line tools
#
# Usage:
#   chmod +x fix_uhd_version_conflict.sh
#   ./fix_uhd_version_conflict.sh
#
# This script:
# 1. Detects which UHD versions are installed
# 2. Sets UHD_IMAGES_DIR to the correct path
# 3. Verifies the fix works
#

set -e

echo "=========================================="
echo "  UHD Version Conflict Fix"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Step 1: Detect installed UHD versions
echo "Step 1: Detecting installed UHD versions..."
echo ""

UHD_VERSIONS=$(dpkg -l | grep -E "^ii.*libuhd" | awk '{print $3}' | sort -u)

if [ -z "$UHD_VERSIONS" ]; then
    print_error "No UHD packages found!"
    exit 1
fi

echo "Found UHD versions:"
echo "$UHD_VERSIONS" | while read -r version; do
    echo "  - $version"
done
echo ""

# Step 2: Find UHD 4.10.0 images directory
echo "Step 2: Looking for UHD 4.10.0 images..."
echo ""

UHD_410_IMAGES="/usr/share/uhd/4.10.0/images"

if [ -f "$UHD_410_IMAGES/usrp_b200_fw.hex" ]; then
    print_success "Found UHD 4.10.0 images at: $UHD_410_IMAGES"
    UHD_IMAGES_DIR="$UHD_410_IMAGES"
else
    print_info "UHD 4.10.0 images not found, trying to download..."
    echo ""
    
    # Try to download images
    if command -v uhd_images_downloader &> /dev/null; then
        echo "Running: sudo uhd_images_downloader -t b2xx"
        sudo uhd_images_downloader -t b2xx
        
        if [ -f "$UHD_410_IMAGES/usrp_b200_fw.hex" ]; then
            print_success "Downloaded images successfully"
            UHD_IMAGES_DIR="$UHD_410_IMAGES"
        else
            print_error "Failed to download images"
            exit 1
        fi
    else
        print_error "uhd_images_downloader not found!"
        echo "Please install UHD first: sudo apt install uhd-host"
        exit 1
    fi
fi

# Step 3: Set environment variable
echo ""
echo "Step 3: Setting UHD_IMAGES_DIR environment variable..."
echo ""

export UHD_IMAGES_DIR="$UHD_IMAGES_DIR"
print_success "Set UHD_IMAGES_DIR=$UHD_IMAGES_DIR"

# Step 4: Verify the fix
echo ""
echo "Step 4: Verifying the fix..."
echo ""

# Test with uhd_find_devices
if command -v uhd_find_devices &> /dev/null; then
    echo "Testing uhd_find_devices..."
    if uhd_find_devices 2>&1 | grep -q "Could not find path for image"; then
        print_error "uhd_find_devices still can't find images!"
    else
        print_success "uhd_find_devices works"
    fi
    echo ""
fi

# Step 5: Make it permanent (optional)
echo "Step 5: Make the fix permanent?"
echo ""
read -p "Do you want to add UHD_IMAGES_DIR to your ~/.bashrc? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    BASHRC_LINE="export UHD_IMAGES_DIR=$UHD_IMAGES_DIR"
    
    # Check if it's already in .bashrc
    if grep -q "UHD_IMAGES_DIR" ~/.bashrc; then
        print_info "UHD_IMAGES_DIR already in ~/.bashrc, updating..."
        sed -i "/UHD_IMAGES_DIR/c\\$BASHRC_LINE" ~/.bashrc
    else
        echo "" >> ~/.bashrc
        echo "# UHD firmware images path (for UHD version conflict fix)" >> ~/.bashrc
        echo "$BASHRC_LINE" >> ~/.bashrc
    fi
    
    print_success "Added to ~/.bashrc"
    print_info "Run 'source ~/.bashrc' or open a new terminal to apply"
else
    print_info "Not adding to ~/.bashrc"
    print_info "You'll need to run: export UHD_IMAGES_DIR=$UHD_IMAGES_DIR"
    print_info "in every new terminal before using GNU Radio"
fi

# Step 6: Summary
echo ""
echo "=========================================="
echo "  Fix Complete!"
echo "=========================================="
echo ""
print_success "UHD_IMAGES_DIR set to: $UHD_IMAGES_DIR"
echo ""
echo "To test:"
echo "  1. Connect your SignalSDR Pro"
echo "  2. Run: gnuradio-companion"
echo "  3. Open a flowgraph and press F5"
echo ""
echo "For more information, see:"
echo "  /home/ubuntu/GNU Radio/signalsdrpro_lab/00_setup/06_fix_uhd_version_conflict.md"
echo ""
