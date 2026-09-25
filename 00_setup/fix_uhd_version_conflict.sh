#!/bin/bash
# fix_uhd_version_conflict.sh
#
# Makes every installed UHD version find the B200/B210 image files, so that
# GNU Radio works whether it is started from a terminal or from the app menu.
#
# Why: GNU Radio from Ubuntu uses UHD 4.6.0. If a newer UHD (4.10, 4.11, ...)
# was also installed from the Ettus PPA, each version looks for images in its
# own folder, /usr/share/uhd/<version>/images/. Images downloaded by one
# version are invisible to the other. This script puts one copy of the images
# where every version will look for it.
#
# It works out the versions itself - nothing is hard-coded.
#
# Usage:
#     ./fix_uhd_version_conflict.sh            # do it (asks for your password)
#     ./fix_uhd_version_conflict.sh --dry-run  # only show what it would do
#
# Safe to run more than once.

set -e

DRY=0
[ "$1" = "--dry-run" ] && DRY=1

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
say()  { echo -e "${YELLOW}==> $*${NC}"; }
ok()   { echo -e "${GREEN}[OK] $*${NC}"; }
fail() { echo -e "${RED}[ERROR] $*${NC}"; exit 1; }
run()  { if [ $DRY = 1 ]; then echo "     would run: $*"; else "$@"; fi; }

FW=usrp_b200_fw.hex

# version string like "4.6.0.0+ds1-5..." or "UHD 4.11.0.0-0ubuntu1" -> "4.6.0" / "4.11.0"
short_version() { echo "$1" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1; }

# ------------------------------------------------------------------ 1. versions
say "Finding the installed UHD versions..."
GR_VER=$(short_version "$(python3 -c 'from gnuradio import uhd; print(uhd.get_version_string())' 2>/dev/null || true)")
CLI_VER=$(short_version "$(uhd_config_info --version 2>/dev/null || true)")
[ -n "$GR_VER" ]  && echo "     GNU Radio uses UHD      : $GR_VER"   || echo "     GNU Radio's UHD         : not found (is GNU Radio installed?)"
[ -n "$CLI_VER" ] && echo "     command-line tools use  : $CLI_VER" || echo "     command-line UHD tools  : not found"
[ -z "$GR_VER$CLI_VER" ] && fail "No UHD found. Install it first: see 00_setup/01_install_uhd.md"

if [ -n "$GR_VER" ] && [ "$GR_VER" = "$CLI_VER" ]; then
    ok "Only one UHD version ($GR_VER). There is no version conflict."
    echo "     If you still see 'Could not find path for image', just download the images:"
    echo "         sudo uhd_images_downloader -t b2xx"
    exit 0
fi

# ------------------------------------------------------------------ 2. images
find_images() {
    for d in /usr/share/uhd/*/images /usr/share/uhd/images; do
        if [ -f "$d/$FW" ]; then readlink -f "$d"; return; fi
    done
}

say "Looking for the image files ($FW)..."
SRC=$(find_images)
if [ -z "$SRC" ]; then
    say "Not found. Downloading the B200/B210 images (about 20 MB)..."
    run sudo uhd_images_downloader -t b2xx
    SRC=$(find_images)
    [ $DRY = 1 ] && [ -z "$SRC" ] && SRC="/usr/share/uhd/$CLI_VER/images (after download)"
    [ -z "$SRC" ] && fail "The download did not produce $FW. Check your internet connection."
fi
ok "Images are in: $SRC"

# ------------------------------------------------------------------ 3. links
# Give every version's own images folder a link to the one real copy.
say "Making sure every UHD version can find them..."
for v in $GR_VER $CLI_VER; do
    target="/usr/share/uhd/$v/images"
    if [ -f "$target/$FW" ]; then
        ok "UHD $v already finds them ($target)"
    elif [ -e "$target" ] && [ ! -L "$target" ]; then
        # a real folder without the file: do not replace it, put a link inside
        say "UHD $v has an empty images folder - linking the files into it"
        for f in "$SRC"/*; do run sudo ln -sfn "$f" "$target/$(basename "$f")"; done
    else
        run sudo mkdir -p "/usr/share/uhd/$v"
        run sudo ln -sfn "$SRC" "$target"
        ok "UHD $v: $target -> $SRC"
    fi
done
# the old version-less location, used by some older UHD builds
if [ ! -e /usr/share/uhd/images ] || [ -L /usr/share/uhd/images ]; then
    run sudo ln -sfn "$SRC" /usr/share/uhd/images
fi

# ------------------------------------------------------------------ 4. environment
# Not needed once the links exist, but an old, wrong value would override them.
if grep -q '^UHD_IMAGES_DIR=' /etc/environment 2>/dev/null; then
    CUR=$(grep '^UHD_IMAGES_DIR=' /etc/environment | tail -1 | cut -d= -f2- | tr -d '"')
    if [ -f "$CUR/$FW" ]; then
        ok "/etc/environment sets UHD_IMAGES_DIR=$CUR (valid)"
    else
        echo -e "${RED}[WARN] /etc/environment sets UHD_IMAGES_DIR=$CUR, which has no $FW.${NC}"
        echo "       Edit /etc/environment and remove that line, then log out and in."
    fi
fi

# ------------------------------------------------------------------ 5. check
if [ $DRY = 1 ]; then
    say "Dry run only - nothing was changed."
    exit 0
fi
say "Checking GNU Radio can now find the images (without any environment variable)..."
OUT=$(env -u UHD_IMAGES_DIR python3 -c "from gnuradio import uhd; uhd.usrp_source('', uhd.stream_args('fc32', '', [0]))" 2>&1 || true)
if echo "$OUT" | grep -q "Could not find path for image"; then
    fail "GNU Radio still cannot find the images. Output:\n$OUT"
elif echo "$OUT" | grep -q "Detected Device"; then
    ok "GNU Radio found the radio and loaded the images."
else
    ok "No image errors. (No radio was found - plug it in to test fully.)"
fi
echo -e "${GREEN}==> Done. GNU Radio should now work from the terminal and from the app menu.${NC}"
