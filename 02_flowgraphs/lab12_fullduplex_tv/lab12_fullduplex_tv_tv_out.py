"""Transport-stream sink: statistics, an optional file, and live video.

Two things here are deliberate and worth copying.

**It never blocks the radio.**  Pointing a File Sink at a FIFO is the obvious
way to feed a player and it is a trap: if the player pauses or dies, the write
blocks, the scheduler stops draining the USRP, and the receiver drowns in
overflows.  A bounded queue absorbs jitter and *drops* when the player falls
behind.  Dropping television frames is the correct failure -- the radio keeps
running and the picture recovers at the next keyframe.

**It counts continuity errors, not sync bytes.**  Every packet leaving a DVB-T
receiver starts with 0x47 whether or not the decode worked, because the energy
descrambler writes that byte unconditionally.  The honest measure of link
health is the continuity counter: 4 bits per PID that increment on every
packet, so a jump means Reed-Solomon gave up on a block.
"""
import queue
import subprocess
import threading

import numpy as np
from gnuradio import gr

PLAYER = ['ffplay', '-hide_banner', '-loglevel', 'error', '-fflags', 'nobuffer',
          '-flags', 'low_delay', '-framedrop', '-autoexit',
          '-window_title', 'SDR LAB TV', '-i', 'pipe:0']


class blk(gr.sync_block):
    def __init__(self, play=True, ts_file='', report_every=20000):
        gr.sync_block.__init__(self, name='TV Output + TS Stats',
                               in_sig=[np.uint8], out_sig=None)
        self.set_output_multiple(188)
        self.report_every = int(report_every)
        self.packets = self.cc_errors = self.sync_errors = self.dropped = 0
        self.pids = {}
        self._cc = {}
        self._buf = b''
        self._since = 0
        self._q = queue.Queue(maxsize=256)
        self._fh = open(ts_file, 'wb') if ts_file else None
        self._proc = None
        if play:
            try:
                self._proc = subprocess.Popen(PLAYER, stdin=subprocess.PIPE,
                                              stdout=subprocess.DEVNULL,
                                              stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print('[TV] ffplay not found -- install ffmpeg for live video '
                      '(sudo apt install ffmpeg). Recording only.')
        threading.Thread(target=self._drain, daemon=True).start()

    def _drain(self):
        while True:
            chunk = self._q.get()
            for sink in (self._proc.stdin if self._proc else None, self._fh):
                if sink is None:
                    continue
                try:
                    sink.write(chunk)
                except (BrokenPipeError, ValueError, OSError):
                    pass

    def work(self, input_items, output_items):
        data = input_items[0].tobytes()
        try:
            self._q.put_nowait(data)
        except queue.Full:
            self.dropped += 1
        buf = self._buf + data
        n = len(buf) // 188
        for k in range(n):
            p = buf[k * 188:(k + 1) * 188]
            self.packets += 1
            self._since += 1
            if p[0] != 0x47:
                self.sync_errors += 1
                continue
            pid = ((p[1] & 0x1f) << 8) | p[2]
            self.pids[pid] = self.pids.get(pid, 0) + 1
            if pid != 0x1fff and (p[3] & 0x10):
                cc = p[3] & 0x0f
                prev = self._cc.get(pid)
                if prev is not None and cc != (prev + 1) % 16:
                    self.cc_errors += 1
                self._cc[pid] = cc
        self._buf = buf[n * 188:]
        if self._since >= self.report_every:
            self._since = 0
            self._report()
        return len(input_items[0])

    def _report(self):
        top = sorted(self.pids.items(), key=lambda kv: -kv[1])[:6]
        rate = self.cc_errors / max(1, self.packets)
        health = 'LOCKED  ' if rate < 1e-4 else ('marginal' if rate < 1e-2 else 'NO LOCK ')
        print(f'[TV] {health} {self.packets:>9,} pkts  '
              f'CC err {self.cc_errors:>7,} ({rate:.2e})  '
              f'sync err {self.sync_errors:>6,}  dropped {self.dropped:>4}')
        print('     PIDs: ' + '  '.join(
            f'{p}{"(null)" if p == 8191 else ""}:{c*100.0/max(1,self.packets):.1f}%'
            for p, c in top))
