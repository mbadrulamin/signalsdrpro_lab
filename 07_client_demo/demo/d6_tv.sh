#!/usr/bin/env bash
# Demo 6 — Television from this box to a real TV.   🚨 TRANSMITS.
#
#   ./d6_tv.sh
#
# Sends DVB-T2 on UHF channel 21 (474 MHz). The transmitter starts at ZERO.
# In the window, slowly:
#   1. TX digital amplitude  -> 0.25
#   2. TX RF gain (dB)       -> raise from 0 until the TV box finds the channel.
#                       Use the lowest value that works.
# Then scan the TV box on channel 21 / 474 MHz.
#
# To stop: close the window, or press Ctrl+C here. Then run ./stop_all.sh to be sure.
# Never leave it running unattended.

source "$(dirname "$0")/common.sh"
need_free_radio
restore bintang_dvbt2.ts || exit 1

say "Demo 6: DVB-T2 on channel 21 (474 MHz). TRANSMITS. Starts at zero power."
echo "  TX digital amplitude -> 0.25, then raise TX RF gain slowly. TV box: channel 21 / 474 MHz."
cd "$SCRIPTS" || exit 1
# tv_playout splits --launch on spaces, and the repo path has one ("GNU Radio").
# %q escapes it, so the path reaches python3 in one piece.
printf -v launch 'python3 %q' "$LABS/lab10_dvbt2_tx_rx/lab10_dvbt2_tx.py"
python3 tv_playout.py /tmp/bintang_dvbt2.ts --copy \
    --standard dvbt2 --t2-fft 32k --t2-guard 1/128 --t2-rate 2/3 \
    --t2-fecblocks 202 --t2-datasyms 59 --fifo /tmp/tv.fifo \
    --launch "$launch"

say "Playout has stopped. Checking the transmitter is off:"
sleep 2
if ps -eo pid,args | grep -q "[l]ab10_dvbt2_tx"; then
    bad "The transmitter is STILL RUNNING:"
    ps -eo pid,args | grep "[l]ab10_dvbt2_tx" | sed 's/^/        /'
    echo "        Run ./stop_all.sh now."
    exit 1
fi
ok "Transmitter is off."
