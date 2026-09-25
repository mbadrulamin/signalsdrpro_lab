#!/usr/bin/env python3
"""
run_offline.py — run a lab's real flowgraph with no radio attached.

It loads the lab's generated .py file exactly as it is, but first swaps two things:

  * every USRP Source becomes a file source that reads IQ from a .cfile
    (complex64, the format Lab 05 records and `make_fm_test_iq` writes), and
  * every Audio Sink becomes a recorder that saves what would have been played.

Everything in between is the lab's own code, untouched. So this tests the real
flowgraph, not a copy of it.

Usage:
    python3 run_offline.py <lab.py> <input.cfile> [--out DIR] [--seconds N]
                           [--set name=value ...]

    --set freq=100e6     call the flowgraph's set_freq(100e6) before starting
    --seconds N          stop after N seconds (for flowgraphs that never end by
                         themselves, e.g. a File Source with repeat on)

Labs that read a file instead of the radio (the Lab 05 player, the Lab 08 and
09 "from file" versions) are handled too: every complex File Source is pointed
at <input.cfile>.

The recorded audio is written to DIR/audio_ch<N>.f32 (float32, one file per
channel) and the audio sample rate is printed.

Used by Labs 03, 04 and 06 checks in VERIFICATION.md. The Qt windows are created
off-screen, so this works over SSH too.
"""
import argparse
import importlib.util
import os
import re
import sys
import time

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import numpy as np
from gnuradio import gr, blocks, uhd, audio


_real_file_source = blocks.file_source


def _redirected_file_source(itemsize, filename, repeat=False, *rest):
    """Any complex File Source in the lab reads our test file instead."""
    if itemsize == gr.sizeof_gr_complex and _FakeUSRP.path:
        filename = _FakeUSRP.path
    return _real_file_source(itemsize, filename, repeat, *rest)


class _FakeUSRP(gr.hier_block2):
    """Looks enough like uhd.usrp_source for a generated flowgraph."""
    path = None

    def __init__(self, *args, **kwargs):
        gr.hier_block2.__init__(self, 'fake_usrp', gr.io_signature(0, 0, 0),
                                gr.io_signature(1, 1, gr.sizeof_gr_complex))
        src = _real_file_source(gr.sizeof_gr_complex, _FakeUSRP.path, False)
        self.connect(src, self)

    def __getattr__(self, name):
        if name.startswith(('set_', 'get_')):
            return lambda *a, **k: None
        raise AttributeError(name)


class _AudioRecorder(gr.hier_block2):
    """Replaces audio.sink: stores each channel instead of playing it."""
    instances = []
    port_counts = []      # filled from the lab's source before it is built

    def __init__(self, samp_rate, device_name='', ok_to_block=True):
        n = _AudioRecorder.port_counts[len(_AudioRecorder.instances)]
        gr.hier_block2.__init__(self, 'audio_recorder', gr.io_signature(n, n, gr.sizeof_float),
                                gr.io_signature(0, 0, 0))
        self.rate = samp_rate
        self.sinks = [blocks.vector_sink_f() for _ in range(n)]
        for i, snk in enumerate(self.sinks):
            self.connect((self, i), snk)
        _AudioRecorder.instances.append(self)


def count_audio_ports(src):
    """How many inputs each audio.sink in the generated code has, in creation order."""
    names = re.findall(r'self\.(\w+) = audio\.sink\(', src)
    counts = []
    for name in names:
        ports = re.findall(r'\(self\.' + name + r', (\d+)\)\)', src)
        counts.append(max(int(p) for p in ports) + 1 if ports else 1)
    return counts


def load(lab_py):
    spec = importlib.util.spec_from_file_location('lab_under_test', lab_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lab_py')
    ap.add_argument('cfile')
    ap.add_argument('--out', default='.')
    ap.add_argument('--set', action='append', default=[], metavar='name=value')
    ap.add_argument('--seconds', type=float, default=None)
    args = ap.parse_args()

    _FakeUSRP.path = os.path.abspath(args.cfile)
    uhd.usrp_source = _FakeUSRP
    audio.sink = _AudioRecorder
    blocks.file_source = _redirected_file_source

    from PyQt5 import Qt
    app = Qt.QApplication.instance() or Qt.QApplication(sys.argv)

    _AudioRecorder.port_counts = count_audio_ports(open(args.lab_py).read())
    mod = load(args.lab_py)
    cls = next(v for k, v in vars(mod).items()
               if isinstance(v, type) and issubclass(v, gr.top_block) and v is not gr.top_block)

    tb = cls()
    for k, v in (a.split('=', 1) for a in args.set):
        getattr(tb, 'set_' + k)(eval(v))
    t0 = time.time()
    tb.start()
    if args.seconds is None:
        tb.wait()
    else:
        time.sleep(args.seconds)
        tb.stop()
        tb.wait()
    dt = time.time() - t0

    os.makedirs(args.out, exist_ok=True)
    for rec in _AudioRecorder.instances:
        for i, s in enumerate(rec.sinks):
            data = np.array(s.data(), dtype=np.float32)
            if data.size:
                data.tofile(os.path.join(args.out, f'audio_ch{i}.f32'))
                print(f'channel {i}: {data.size} samples at {rec.rate} Hz '
                      f'({data.size / rec.rate:.2f} s)  rms {np.sqrt(np.mean(data**2)):.4f}')
    print(f'ran in {dt:.1f} s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
