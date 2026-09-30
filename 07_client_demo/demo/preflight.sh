#!/usr/bin/env bash
# Preflight — check everything the six demos need, in about a minute.
#
#   ./preflight.sh
#
# Every line should say OK. WARN means a demo will need its fallback.
# FAIL means fix it before the session. Nothing here transmits.

source "$(dirname "$0")/common.sh"
fails=0; warns=0
f() { bad "$*"; fails=$((fails+1)); }
w() { warn "$*"; warns=$((warns+1)); }

say "1. Programs"
for p in uhd_find_devices uhd_fft python3 ffmpeg ffplay; do
    command -v "$p" >/dev/null && ok "$p" || f "$p is not installed"
done
python3 -c "import gnuradio.gr" 2>/dev/null && ok "GNU Radio (Python)" || f "GNU Radio Python modules do not load"
command -v gqrx >/dev/null && ok "gqrx (bonus)" || echo "  --    gqrx not installed (optional: ../install_demo_tools.sh)"

say "2. The radio"
users="$(radio_users)"
if [ -n "$users" ]; then
    w "Something is already running (it may hold the radio). ./stop_all.sh stops it:"
    echo "$users" | sed 's/^/        /'
fi
found="$(timeout 30 uhd_find_devices 2>/dev/null)"
if echo "$found" | grep -q "type: b200"; then
    ok "Radio found: $(echo "$found" | grep -m1 -E 'serial' | xargs)"
    probe="$(timeout 60 uhd_usrp_probe 2>&1)"
    if echo "$probe" | grep -qi "USB 3"; then
        ok "Connected at USB 3"
    else
        w "Not clearly on USB 3. Use the blue USB port. Demo 6 needs USB 3"
    fi
else
    f "No radio found. Power cable first, wait 30 s, then the USB 3 data cable"
fi

say "3. Files (kept in $STORE, copied to /tmp for the labs)"
for n in bintang_dvbt2.ts bintang.ts; do
    if [ -s "$STORE/$n" ]; then
        restore "$n" && ok "$n  $(du -h "$STORE/$n" | cut -f1)"
    else
        f "$STORE/$n missing (Demo 6 needs it)"
    fi
done
n=capture_100M0_2Msps_fc32.iq
if [ -s "$STORE/$n" ]; then
    restore "$n" && ok "Demo 4 recording  $(du -h "$STORE/$n" | cut -f1)"
else
    w "No Demo 4 recording yet. Make it with ./d4_record.sh"
fi

say "4. Space and settings"
free_gb=$(df -BG --output=avail /tmp | tail -1 | tr -dc 0-9)
[ "${free_gb:-0}" -ge 5 ] && ok "/tmp has ${free_gb} GB free" || f "/tmp has only ${free_gb} GB free"
[ -n "${UHD_IMAGES_DIR:-}" ] && [ -d "$UHD_IMAGES_DIR" ] && ok "UHD_IMAGES_DIR=$UHD_IMAGES_DIR" \
    || w "UHD_IMAGES_DIR is not set in this terminal. Open a new terminal"
sink="$(pactl get-default-sink 2>/dev/null)"
if [ -n "$sink" ]; then
    case "$sink" in
        *hdmi*) w "Sound goes to HDMI ($sink). Settings -> Sound -> Output if the room cannot hear it" ;;
        *)      ok "Sound output: $sink" ;;
    esac
fi

say "5. Fallback recordings"
nfb=$(ls "$(dirname "$0")/../fallbacks" 2>/dev/null | grep -c -E '^d[1-6]_.*\.(png|webm|mp4)$')
if [ "$nfb" -ge 6 ]; then ok "$nfb fallback files in fallbacks/"
else w "Only $nfb fallback files in fallbacks/. Record them while the demos work"
fi

say "Result"
if [ "$fails" -eq 0 ] && [ "$warns" -eq 0 ]; then
    ok "Everything is ready."
elif [ "$fails" -eq 0 ]; then
    warn "$warns warning(s). The session can go ahead; check the lines above."
else
    bad "$fails problem(s) and $warns warning(s). Fix the FAIL lines first."
fi
exit "$fails"
