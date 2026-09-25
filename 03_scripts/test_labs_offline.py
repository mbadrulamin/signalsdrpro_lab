#!/usr/bin/env python3
"""
test_labs_offline.py — check that the labs' real flowgraphs give the right answer.

No radio is needed. For each lab it:
  1. makes a test signal whose correct output is known (make_test_iq.py),
  2. runs the lab's generated .py on it, with the radio swapped for that file
     (run_offline.py), and
  3. measures the audio and compares it with what it should be.

This catches mistakes that "does it compile?" cannot: a squelch that never
closes, a stereo decoder that is really mono, a wrong audio rate.

Usage:
    python3 test_labs_offline.py            # all tests
    python3 test_labs_offline.py lab04      # only tests whose name contains "lab04"

Exit code 0 = all passed.
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.join(HERE, '..', '02_flowgraphs')
sys.path.insert(0, HERE)
from make_test_iq import make  # noqa: E402


LAST_OUTPUT = ''      # what the last lab printed (the RDS and ADS-B decoders print results)


def run_lab(lab_py, iq, workdir, sets=(), seconds=None, after=()):
    """Run a lab on IQ samples (an array, or the path of a .cfile).
    Returns {channel: audio array} and the audio rate."""
    global LAST_OUTPUT
    if isinstance(iq, str):
        cfile = iq
    else:
        cfile = os.path.join(workdir, 'in.cfile')
        iq.astype(np.complex64).tofile(cfile)
    out = os.path.join(workdir, 'out')
    cmd = [sys.executable, os.path.join(HERE, 'run_offline.py'), os.path.join(LABS, lab_py), cfile, '--out', out]
    for s in sets:
        cmd += ['--set', s.replace('{cfile}', cfile)]
    for s in after:
        cmd += ['--after', s]
    if seconds:
        cmd += ['--seconds', str(seconds)]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[-2000:])
    LAST_OUTPUT = res.stdout
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
    return chans, rate


def tone_level(x, rate, hz):
    x = x[len(x) // 3:]                      # skip the start-up transient
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1 / rate)
    k = np.argmin(abs(freqs - hz))
    return spec[max(k - 3, 0):k + 4].max()


def db(a, b):
    return 20 * np.log10(a / b)


# ---------------------------------------------------------------- the tests
# Each returns (passed, message).

def lab01_tone(tmp):
    chans, rate = run_lab('lab01_simple_wbfm/lab01_simple_wbfm.py',
                          make(rate=1e6, seconds=2, stereo=False), tmp)
    a = chans[0]
    ok = rate == 50000 and tone_level(a, rate, 1000) > 20 * tone_level(a, rate, 3000)
    return ok, f'audio rate {rate:g} Hz (want 50000); 1 kHz tone recovered, rms {np.std(a):.3f}'


def lab02_tone(tmp):
    chans, rate = run_lab('lab02_enhanced_wbfm/lab02_enhanced_wbfm.py',
                          make(rate=2e6, seconds=2, stereo=False), tmp)
    a = chans[0]
    ok = rate == 48000 and tone_level(a, rate, 1000) > 20 * tone_level(a, rate, 3000)
    return ok, f'audio rate {rate:g} Hz (want 48000); 1 kHz tone recovered, rms {np.std(a):.3f}'


def lab03_squelch(tmp):
    station, rate = run_lab('lab03_advanced_wbfm/lab03_advanced_wbfm.py',
                            make(rate=2e6, seconds=2, stereo=False, snr_db=40), tmp)
    rng = np.random.default_rng(2)
    n = int(2e6 * 2)
    noise = 0.001 * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)
    empty, _ = run_lab('lab03_advanced_wbfm/lab03_advanced_wbfm.py', noise, tmp)
    s_rms = np.std(station[0][len(station[0]) // 2:])
    e_rms = np.std(empty[0][len(empty[0]) // 2:])
    ok = s_rms > 0.05 and e_rms < 1e-6
    return ok, (f'station: audio rms {s_rms:.3f} (want > 0.05);  '
                f'empty channel at -60 dBFS: audio rms {e_rms:.2e} (want silence)')


def lab04_separation(tmp):
    chans, rate = run_lab('lab04_stereo_wbfm/lab04_stereo_wbfm.py',
                          make(rate=2e6, seconds=3, left_hz=1000, right_hz=1700, snr_db=40), tmp)
    left, right = chans[0], chans[1]
    sep_l = db(tone_level(left, rate, 1000), tone_level(left, rate, 1700))
    sep_r = db(tone_level(right, rate, 1700), tone_level(right, rate, 1000))
    ok = sep_l > 25 and sep_r > 25
    return ok, f'stereo separation: left {sep_l:.1f} dB, right {sep_r:.1f} dB (want > 25 dB each)'


def lab05_retune(tmp):
    # a recording with one station 300 kHz above centre; the player must find it
    # with its Offset slider, exactly as a student retunes inside a real capture.
    # The noise matters: with none, the empty channel still holds a faint leaked
    # copy of the station, and an FM decoder ignores how faint a signal is.
    iq = make(rate=2e6, seconds=4, stereo=False, offset=300e3, snr_db=40)
    on, rate = run_lab('lab05_iq_record_playback/lab05_iq_playback.py', iq, tmp,
                       sets=['offset_freq=300e3'], seconds=3)
    off, _ = run_lab('lab05_iq_record_playback/lab05_iq_playback.py', iq, tmp,
                     sets=['offset_freq=-300e3'], seconds=3)
    a, b = on[0], off[0]
    tone_on = tone_level(a, rate, 1000)
    tone_off = tone_level(b, rate, 1000)
    ok = rate == 50000 and db(tone_on, tone_off) > 20
    return ok, (f'audio rate {rate:g} Hz (want 50000); 1 kHz tone at offset +300 kHz is '
                f'{db(tone_on, tone_off):.0f} dB stronger than at -300 kHz (want > 20)')


LAB06 = 'lab06_multimode_receiver/lab06_multimode_receiver.py'


def _lab06(tmp, mode, iq):
    # mode can only be set on a running flowgraph (see VERIFICATION.md, Known issue)
    chans, rate = run_lab(LAB06, iq, tmp, after=[f'mode={mode}'])
    a = chans[0][len(chans[0]) // 2:]
    return a, rate


def lab06_modes(tmp):
    # the default tuning puts the channel 200 kHz below the hardware centre
    results, ok = [], True
    for name, mode, kind in (('AM', 0, 'am'), ('NBFM', 1, 'nbfm'), ('WBFM', 2, 'wbfm')):
        a, rate = _lab06(tmp, mode, make(rate=2e6, seconds=3, mode=kind, stereo=False,
                                         offset=-200e3, snr_db=40))
        clean = tone_level(a, rate, 1000) > 30 * tone_level(a, rate, 2500)
        no_dc = abs(a.mean()) < 0.02
        ok &= rate == 50000 and clean and no_dc and np.std(a) > 0.05
        results.append(f'{name} rms {np.std(a):.2f} dc {a.mean():+.3f}')
    return ok, '; '.join(results) + ' (want a clean 1 kHz tone, no DC offset)'


def lab06_squelch(tmp):
    rng = np.random.default_rng(3)
    n = int(2e6 * 3)
    noise = 0.001 * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)
    a, _ = _lab06(tmp, 1, noise)
    ok = np.std(a) < 1e-6
    return ok, f'NBFM on an empty channel: audio rms {np.std(a):.2e} (want silence)'


def _script(name, *args):
    subprocess.run([sys.executable, os.path.join(HERE, name), *args],
                   check=True, capture_output=True, timeout=600)


def lab08_rds(tmp):
    iq = os.path.join(tmp, 'rds.iq')
    _script('simulate_rds_decode.py', '--seconds', '8', '--snr', '30', '--ps', 'SDR LAB ',
            '--rt', 'Hello from the SignalSDR Pro lab', '--out', iq, '--quiet')
    run_lab('lab08_rds_decoder/lab08_rds_from_file.py', iq, tmp, seconds=12)
    ps = "PS='SDR LAB '" in LAST_OUTPUT
    rt = 'RadioText: Hello from the SignalSDR Pro lab' in LAST_OUTPUT
    return ps and rt, f'station name decoded: {ps}; RadioText decoded: {rt}'


def lab09_adsb(tmp):
    iq = os.path.join(tmp, 'adsb.iq')
    _script('simulate_adsb_decode.py', '--seconds', '2', '--snr', '20', '--out', iq)
    run_lab('lab09_adsb_receiver/lab09_adsb_from_file.py', iq, tmp, seconds=6)
    callsign = 'KLM1023' in LAST_OUTPUT
    position = '38000 ft' in LAST_OUTPUT and '52.25' in LAST_OUTPUT
    return callsign and position, f'callsign KLM1023 decoded: {callsign}; altitude and position decoded: {position}'


TESTS = [lab01_tone, lab02_tone, lab03_squelch, lab04_separation, lab05_retune,
         lab06_modes, lab06_squelch, lab08_rds, lab09_adsb]


def main():
    pick = sys.argv[1] if len(sys.argv) > 1 else ''
    failed = 0
    for test in TESTS:
        if pick not in test.__name__:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            try:
                ok, msg = test(tmp)
            except Exception as e:                       # report, keep going
                ok, msg = False, f'ERROR: {e}'
        failed += not ok
        print(f'{"PASS" if ok else "FAIL"}  {test.__name__:18s} {msg}')
    print(f'\n{"all passed" if not failed else f"{failed} failed"}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
