#!/usr/bin/env bash
# Demo 6 fallback — the box sends television to itself and shows the picture.   🚨 TRANSMITS.
#
#   ./d6_fallback_loop.sh
#
# Use this if the TV box will not find the channel. No TV box needed:
# the radio transmits on TX/RX and receives on RX2 at the same time.
# UHF channel 31 (554 MHz). The transmitter starts at ZERO. In the window, slowly:
#   TX gain (dB) -> 80 to 89,  then  TX amplitude -> about 0.25.
#   Keep RX gain (dB) at 20. Aim for a level of -10 to -20 dBFS.
# The room sees: 16 tight dots, MER above 15 dB, [TV] LOCKED here,
# then a video window opens by itself.
#
# To stop: close the window. Then run ./stop_all.sh to be sure.

source "$(dirname "$0")/common.sh"
need_free_radio
restore bintang.ts || exit 1

say "Demo 6 fallback: Lab 12 loop on channel 31 (554 MHz). TRANSMITS. Starts at zero."
cd "$LABS/lab12_fullduplex_tv" || exit 1
python3 lab12_fullduplex_tv.py
"$(dirname "$0")/stop_all.sh" >/dev/null
ok "Stopped."
