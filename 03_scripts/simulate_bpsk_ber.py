#!/usr/bin/env python3
"""
simulate_bpsk_ber.py - Verify Lab 07's BPSK link against closed-form theory.

Runs a real GNU Radio flowgraph (the same blocks Lab 07 uses) at a series of
Eb/N0 values and compares the measured bit error rate against:

    BPSK       P_b = Q(sqrt(2 Eb/N0))
    DBPSK      P_b = 2 p (1 - p)          with p = the BPSK value

Two modes:

  --calibrate   open-loop: perfect timing, no sync loops, Noise Source + Add.
                This isolates the Eb/N0 calibration itself and should match
                BPSK theory to within statistical error.

  (default)     closed-loop: the full Lab 07 chain including Channel Model,
                Symbol Sync and the Costas loop, differentially encoded.
                Should match DBPSK theory - and will visibly FAIL at low
                Eb/N0 if the loop bandwidth is too wide, which is the point
                of Lab 07 Exercise 3.

Usage:
    python3 simulate_bpsk_ber.py                     # closed loop sweep
    python3 simulate_bpsk_ber.py --calibrate         # open loop sweep
    python3 simulate_bpsk_ber.py --loop-bw 0.045     # watch it break at 2 dB
    python3 simulate_bpsk_ber.py --ebno 2 4 6 --bits 2000000

Requires: gnuradio (3.10), numpy.
"""
import argparse
import sys
from math import erfc, sqrt

import numpy as np

try:
    from gnuradio import gr, blocks, analog, channels, digital
    from gnuradio import filter as gfilter
    from gnuradio.filter import firdes
except ImportError:                                          # pragma: no cover
    sys.exit("GNU Radio not found. Install gnuradio 3.10 (see 00_setup/03_install_gnuradio.md).")

SPS = 4
ALPHA = 0.35
NFILTS = 32
PATTERN_LEN = 1023


def q(x):
    return 0.5 * erfc(x / sqrt(2.0))


def theory_bpsk(ebno_db):
    return q(sqrt(2 * 10 ** (ebno_db / 10.0)))


def theory_dbpsk(ebno_db):
    p = theory_bpsk(ebno_db)
    return 2 * p * (1 - p)


def noise_voltage(ebno_db, sps=SPS, bits_per_symbol=1):
    """The calibration derived (and empirically checked) in Fundamentals 08.

    GNU Radio's noise_voltage is the TOTAL complex standard deviation, so
    there is no extra factor of two here.
    """
    return sqrt(sps / (bits_per_symbol * 10 ** (ebno_db / 10.0)))


def pattern(seed=1):
    return np.random.RandomState(seed).randint(0, 2, PATTERN_LEN).astype(np.uint8)


# --------------------------------------------------------------- open loop --
def run_calibrate(ebno_db, nbits, pat):
    """No sync loops: fixed matched filter, known delay, ideal sampling."""
    rrc_tx = firdes.root_raised_cosine(SPS, SPS, 1.0, ALPHA, 11 * SPS)
    rrc_mf = firdes.root_raised_cosine(1.0 / SPS, SPS, 1.0, ALPHA, 11 * SPS)
    bits = np.tile(pat, int(np.ceil(nbits / len(pat))))[:nbits]

    def once(amp, seed):
        tb = gr.top_block()
        vs = blocks.vector_source_b(bits.tolist(), False)
        c2s = digital.chunks_to_symbols_bc([-1 + 0j, 1 + 0j], 1)
        tx = gfilter.interp_fir_filter_ccf(SPS, rrc_tx)
        ns = analog.noise_source_c(analog.GR_GAUSSIAN, amp, seed)
        add = blocks.add_cc()
        mf = gfilter.fir_filter_ccf(SPS, rrc_mf)
        snk = blocks.vector_sink_c()
        tb.connect(vs, c2s, tx, (add, 0))
        tb.connect(ns, (add, 1))
        tb.connect(add, mf, snk)
        tb.run()
        return np.array(snk.data())

    ref = 2.0 * bits[:2000].astype(float) - 1.0
    clean = once(0.0, 0)
    delay = max(range(40), key=lambda d: abs(np.dot(clean[d:d + 2000].real, ref)))

    y = once(noise_voltage(ebno_db), 11)
    rx = y[delay:delay + nbits - delay]
    return float(np.mean((rx.real > 0).astype(np.uint8) != bits[:len(rx)]))


# ------------------------------------------------------------- closed loop --
def run_closed(ebno_db, nbits, pat, loop_bw, freq_off, eps, settle):
    rrc_tx = firdes.root_raised_cosine(SPS, SPS, 1.0, ALPHA, 11 * SPS)
    pfb_mf = firdes.root_raised_cosine(NFILTS, NFILTS * SPS, 1.0, ALPHA, 11 * SPS * NFILTS)

    tb = gr.top_block()
    vs = blocks.vector_source_b(pat.tolist(), True)
    enc = digital.diff_encoder_bb(2)
    c2s = digital.chunks_to_symbols_bc([-1 + 0j, 1 + 0j], 1)
    tx = gfilter.interp_fir_filter_ccf(SPS, rrc_tx)
    ch = channels.channel_model(noise_voltage=noise_voltage(ebno_db),
                                frequency_offset=freq_off, epsilon=eps,
                                taps=[1.0 + 0j], noise_seed=5)
    ss = digital.symbol_sync_cc(digital.TED_GARDNER, SPS, loop_bw, 1.0, 1.5, 1, 1,
                                digital.constellation_bpsk().base(),
                                digital.IR_PFB_MF, NFILTS, pfb_mf)
    cl = digital.costas_loop_cc(loop_bw, 2, False)
    head = blocks.head(gr.sizeof_char, settle + nbits)
    snk = blocks.vector_sink_b()
    tb.connect(vs, enc, c2s, tx, ch, ss, cl, blocks.complex_to_real(),
               digital.binary_slicer_fb(), digital.diff_decoder_bb(2), head, snk)
    tb.run()

    b = np.array(snk.data(), dtype=np.uint8)[settle:]
    return align_and_count(b, pat)


def align_and_count(b, pat):
    """Cyclically align the received bits to the reference and count errors."""
    n = len(pat)
    usable = (len(b) // n) * n
    if usable < 2 * n:
        return float('nan')
    b = b[:usable]
    a = 2.0 * b[:n].astype(float) - 1.0
    tiled = np.concatenate([2.0 * pat.astype(float) - 1.0] * 2)
    corr = np.correlate(tiled, a, mode='valid')[:n] / n
    s = int(np.argmax(np.abs(corr)))
    if abs(corr[s]) < 0.3:
        return float('nan')                       # never locked
    ref = np.tile(np.roll(pat, -s), usable // n)
    if corr[s] < 0:
        ref = 1 - ref
    return float(np.mean(b != ref))


# -------------------------------------------------------------------- main --
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ebno', type=float, nargs='+',
                    default=[2, 4, 6, 8, 10], help='Eb/N0 values in dB')
    ap.add_argument('--bits', type=int, default=400000, help='bits to measure per point')
    ap.add_argument('--loop-bw', type=float, default=0.010, help='sync loop bandwidth')
    ap.add_argument('--freq-offset', type=float, default=0.0005, help='cycles/sample')
    ap.add_argument('--epsilon', type=float, default=1.00005, help='TX/RX clock ratio')
    ap.add_argument('--settle', type=int, default=100000, help='bits to discard while locking')
    ap.add_argument('--calibrate', action='store_true',
                    help='open-loop Eb/N0 calibration instead of the full chain')
    args = ap.parse_args()

    pat = pattern()
    mode = 'OPEN LOOP (calibration)' if args.calibrate else \
           f'CLOSED LOOP (loop_bw={args.loop_bw}, freq_off={args.freq_offset}, eps={args.epsilon})'
    theory = theory_bpsk if args.calibrate else theory_dbpsk
    tname = 'BPSK' if args.calibrate else 'DBPSK'

    print(f"\nBPSK link verification - {mode}")
    print(f"sps={SPS}  alpha={ALPHA}  pattern={PATTERN_LEN} bits  measured bits={args.bits:,}\n")
    print(f"{'Eb/N0':>7} {'noise_v':>9} {'measured':>12} {tname+' theory':>14} {'ratio':>8}")
    print("-" * 55)

    worst = 0.0
    for e in args.ebno:
        meas = (run_calibrate(e, args.bits, pat) if args.calibrate else
                run_closed(e, args.bits, pat, args.loop_bw,
                           args.freq_offset, args.epsilon, args.settle))
        th = theory(e)
        if np.isnan(meas):
            print(f"{e:>7.1f} {noise_voltage(e):>9.4f} {'NO LOCK':>12} {th:>14.3e} {'--':>8}")
            worst = float('inf')
            continue
        if meas == 0.0:
            # zero errors observed: we can only bound the BER from above
            bound = 1.0 / args.bits
            note = 'too few bits' if bound > th else 'consistent'
            print(f"{e:>7.1f} {noise_voltage(e):>9.4f} {'<'+f'{bound:.1e}':>12} "
                  f"{th:>14.3e} {note:>18}")
            continue
        ratio = meas / th if th > 0 else float('nan')
        flag = '' if 0.5 <= ratio <= 2.0 else '   <-- off'
        worst = max(worst, abs(np.log10(ratio)))
        print(f"{e:>7.1f} {noise_voltage(e):>9.4f} {meas:>12.3e} {th:>14.3e} {ratio:>8.2f}{flag}")

    print("-" * 55)
    if worst == float('inf'):
        print("RESULT: at least one point never acquired lock.")
        print("        That is the Lab 07 Exercise 3 failure mode - try --loop-bw 0.010")
        return 1
    print("RESULT: measurement tracks theory." if worst < 0.35 else
          "RESULT: measurement deviates from theory - check the calibration.")
    print("Note: points with fewer than ~100 error events are dominated by")
    print("      counting statistics; raise --bits to tighten them.\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
