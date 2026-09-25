#!/usr/bin/env python3
"""
test_labs_live.py — check the FM labs on a REAL station, with the real radio.

RECEIVE ONLY. It runs the generated .py of Labs 01, 02, 03, 04 and 06 with the
SignalSDR Pro attached, records their audio instead of playing it, and measures:

  * audio SNR — the strongest point in the speech band (0.1-5 kHz) compared with
    the average level in a band where there should be no sound (0.40-0.48 x the
    audio rate). The same measurement VERIFICATION.md reports.
  * Lab 03's squelch — on an EMPTY channel the audio must be silent.

run_offline.py --live refuses any flowgraph that contains a transmitter.

Usage:
    python3 test_labs_live.py                         # BFM 89.9 MHz, empty 104.0 MHz
    python3 test_labs_live.py --station 98.8e6 --empty 104.0e6 --gain 40

Before trusting a result: tune the station in Lab 02 first and make sure it is
strong, and that the "empty" frequency really is empty where you are.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.join(HERE, '..', '02_flowgraphs')


def run_live(lab_py, workdir, seconds, sets=(), after=()):
    out = os.path.join(workdir, 'out')
    cmd = [sys.executable, os.path.join(HERE, 'run_offline.py'), os.path.join(LABS, lab_py),
           'unused', '--live', '--out', out, '--seconds', str(seconds)]
    for s in sets:
        cmd += ['--set', s]
    for s in after:
        cmd += ['--after', s]
    res = subprocess.run(cmd, capture_output=True, text=True, errors='replace', timeout=seconds + 120)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[-1500:])
    rate = None
    for line in res.stdout.splitlines():
        if line.startswith('channel 0:'):
            rate = float(line.split(' at ')[1].split(' Hz')[0])
    chans = {}
    for i in range(8):
        f = os.path.join(out, f'audio_ch{i}.f32')
        if os.path.exists(f):
            chans[i] = np.fromfile(f, np.float32)
            os.remove(f)
    return chans, rate, res.stdout + res.stderr


def audio_snr(x, rate):
    x = x[int(rate):]                               # skip the first second (start-up)
    if not np.any(x):
        return float('-inf')
    n = 1 << int(np.log2(min(len(x), 1 << 16)))
    segs = [x[i:i + n] for i in range(0, len(x) - n, n // 2)]
    spec = np.mean([np.abs(np.fft.rfft(s * np.hanning(n))) ** 2 for s in segs], axis=0)
    f = np.fft.rfftfreq(n, 1 / rate)
    band = spec[(f >= 100) & (f <= 5000)].max()
    quiet = spec[(f >= 0.40 * rate) & (f <= 0.48 * rate)].mean()
    return 10 * np.log10(band / quiet)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--station', type=float, default=89.9e6)
    ap.add_argument('--empty', type=float, default=104.0e6)
    ap.add_argument('--gain', type=float, default=40)
    ap.add_argument('--seconds', type=float, default=8)
    a = ap.parse_args()
    st, g = a.station, a.gain
    tests = [
        ('Lab 01', 'lab01_simple_wbfm/lab01_simple_wbfm.py', [f'freq={st}', f'gain={g}'], []),
        ('Lab 02', 'lab02_enhanced_wbfm/lab02_enhanced_wbfm.py', [f'freq={st}', f'gain={g}'], []),
        ('Lab 03', 'lab03_advanced_wbfm/lab03_advanced_wbfm.py', [f'freq={st}', f'rf_gain={g}'], []),
        ('Lab 04', 'lab04_stereo_wbfm/lab04_stereo_wbfm.py', [f'freq={st}', f'rf_gain={g}'], []),
        # Lab 06 tunes the hardware 200 kHz above and uses its -200 kHz software offset
        ('Lab 06', 'lab06_multimode_receiver/lab06_multimode_receiver.py', [f'freq={st + 200e3}', f'rf_gain={g}'], ['mode=2']),
    ]
    print(f'station {st / 1e6:.2f} MHz, gain {g} dB, {a.seconds:g} s each (receive only)\n')
    failed = 0
    for name, py, sets, after in tests:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                chans, rate, _ = run_live(py, tmp, a.seconds, sets, after)
                if 1 in chans:
                    # Lab 04's own 15 kHz filters empty the 'quiet' reference band, so the
                    # SNR figure would be meaningless. Report the stereo content instead.
                    x0, x1 = chans[0][int(rate):], chans[1][int(rate):]
                    lr, lpr = x0 - x1, x0 + x1
                    ratio = 10 * np.log10(np.mean(lr ** 2) / np.mean(lpr ** 2))
                    ok = np.std(x0) > 0.01 and -40 < ratio < 0
                    print(f'{"PASS" if ok else "FAIL"}  {name}  stereo decoded: L-R is {-ratio:.1f} dB below L+R '
                          f'(music is usually 3-20 dB; mono would be much lower)')
                else:
                    snr = audio_snr(chans[0], rate)
                    ok = snr > 30
                    print(f'{"PASS" if ok else "FAIL"}  {name}  audio SNR {snr:5.1f} dB (want > 30)')
            except Exception as e:
                ok = False
                print(f'FAIL  {name}  ERROR: {str(e)[-300:]}')
            failed += not ok
    with tempfile.TemporaryDirectory() as tmp:
        try:
            chans, rate, _ = run_live('lab03_advanced_wbfm/lab03_advanced_wbfm.py', tmp, a.seconds,
                                      [f'freq={a.empty}', f'rf_gain={g}'])
            rms = float(np.std(chans[0][int(rate):]))
            ok = rms < 1e-4
            print(f'{"PASS" if ok else "FAIL"}  Lab 03 squelch on empty {a.empty / 1e6:.2f} MHz: audio rms {rms:.2e} (want silence)'
                  + ('' if ok else '  - is the channel really empty? try raising the squelch slider default'))
        except Exception as e:
            ok = False
            print(f'FAIL  Lab 03 squelch  ERROR: {str(e)[-300:]}')
        failed += not ok
    print(f'\n{"all passed" if not failed else f"{failed} failed"}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
