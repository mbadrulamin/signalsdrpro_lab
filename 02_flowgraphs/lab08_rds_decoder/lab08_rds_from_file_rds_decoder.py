import numpy as np
from gnuradio import gr

POLY = 0b10110111001
OFFSETS = {'A': 0b0011111100, 'B': 0b0110011000, 'C': 0b0101101000,
           'Cp': 0b1101010000, 'D': 0b0110110100}
SYN = {v: k for k, v in OFFSETS.items()}
PTY_EU = ['None','News','Current Affairs','Information','Sport','Education','Drama',
          'Culture','Science','Varied','Pop Music','Rock Music','Easy Listening',
          'Light Classical','Serious Classical','Other Music','Weather','Finance',
          "Children's",'Social Affairs','Religion','Phone In','Travel','Leisure',
          'Jazz Music','Country Music','National Music','Oldies Music','Folk Music',
          'Documentary','Alarm Test','Alarm']


def syndrome(w):
    reg = w & 0x3FFFFFF
    for i in range(25, 9, -1):
        if reg & (1 << i):
            reg ^= POLY << (i - 10)
    return reg & 0x3FF


class blk(gr.sync_block):
    """RDS Decoder.

    Input : one float per CHIP (2375 chips/s), real part after the Costas loop.
    Output: cumulative count of successfully CRC-checked RDS groups.

    Pipeline, all of it explained in Fundamentals 10:
      1. biphase pairing   two chips per data bit; bit = sign(c0 - c1)
      2. differential decode   b[n] = d[n] XOR d[n-1]
      3. block sync via CRC    the (26,16) code's syndrome equals the offset word,
                               so finding the alignment and identifying the block
                               are the same operation - no preamble needed
      4. group parsing         0A -> Programme Service name, 2A -> RadioText
    """

    def __init__(self, verbose=True, reacquire_chips=20000):
        gr.sync_block.__init__(self, name="RDS Decoder",
                               in_sig=[np.float32], out_sig=[np.float32])
        self.verbose = bool(verbose)
        self.reacquire = int(reacquire_chips)
        self.chipbuf = np.zeros(0, dtype=np.float32)
        self.phase = None
        self.prev_d = 0
        self.bits = []
        self.pos = 0
        self.groups = 0
        self.blocks_bad = 0
        self.since_group = 0
        self.pi = None
        self.pty = None
        self.tp = None
        self.ps = [' '] * 8
        self.rt = [' '] * 64
        self.rt_ab = None
        self._last_ps = None
        self._last_rt = None

    # --------------------------------------------------------------- work --
    def work(self, input_items, output_items):
        n = len(input_items[0])
        self.chipbuf = np.concatenate([self.chipbuf, input_items[0]])

        if self.phase is None:
            if len(self.chipbuf) < 4096:
                output_items[0][:] = np.float32(self.groups)
                return n
            self.phase = self._best_phase(self.chipbuf[:4096])

        c = self.chipbuf[self.phase:]
        npairs = len(c) // 2
        if npairs:
            c0, c1 = c[0:2 * npairs:2], c[1:2 * npairs:2]
            d = ((c0 - c1) > 0).astype(np.uint8)
            self._feed_bits(d)
            self.chipbuf = c[2 * npairs:].copy()
            self.phase = 0
            self.since_group += npairs
            if self.since_group > self.reacquire:      # lost? try the other pairing
                self.since_group = 0
                self.phase = 1
                self.bits, self.pos = [], 0
                if self.verbose:
                    print("[RDS] no valid groups - flipping biphase pairing", flush=True)

        output_items[0][:] = np.float32(self.groups)
        return n

    @staticmethod
    def _best_phase(c):
        """Within a biphase symbol the two chips are always opposite, so the
        correct pairing has a strongly negative chip-to-chip product."""
        scores = []
        for p in (0, 1):
            x = c[p:]
            m = len(x) // 2
            scores.append(-float(np.mean(x[0:2 * m:2] * x[1:2 * m:2])))
        return int(np.argmax(scores))

    # ------------------------------------------------------------- decode --
    def _feed_bits(self, dbits):
        for b in dbits:
            self.bits.append(int(b) ^ self.prev_d)     # differential decode
            self.prev_d = int(b)
        while self.pos + 104 <= len(self.bits):
            w = [self._word(self.pos + 26 * k) for k in range(4)]
            s = [SYN.get(syndrome(x)) for x in w]
            if s[0] == 'A' and s[1] == 'B' and s[2] in ('C', 'Cp') and s[3] == 'D':
                self._group([x >> 10 for x in w], s[2] == 'Cp')
                self.groups += 1
                self.since_group = 0
                self.pos += 104
            else:
                self.blocks_bad += 1
                self.pos += 1
        if self.pos > 4096:
            self.bits = self.bits[self.pos:]
            self.pos = 0

    def _word(self, i):
        v = 0
        for b in self.bits[i:i + 26]:
            v = (v << 1) | b
        return v

    def _group(self, info, version_b):
        a, b, c, d = info
        self.pi = a
        gtype = (b >> 12) & 0xF
        self.tp = (b >> 10) & 1
        self.pty = (b >> 5) & 0x1F
        if gtype == 0:
            addr = b & 0x3
            self.ps[2 * addr] = self._ch(d >> 8)
            self.ps[2 * addr + 1] = self._ch(d & 0xFF)
        elif gtype == 2:
            ab = (b >> 4) & 1
            if self.rt_ab is not None and ab != self.rt_ab:
                self.rt = [' '] * 64
            self.rt_ab = ab
            addr = b & 0xF
            chars = ([c >> 8, c & 0xFF, d >> 8, d & 0xFF] if not version_b
                     else [d >> 8, d & 0xFF])
            base = 4 * addr if not version_b else 2 * addr
            for i, ch in enumerate(chars):
                if base + i < 64:
                    self.rt[base + i] = self._ch(ch)
        self._announce()

    @staticmethod
    def _ch(c):
        return chr(c) if 32 <= c < 127 else ' '

    def _announce(self):
        if not self.verbose:
            return
        ps = ''.join(self.ps)
        rt = ''.join(self.rt).rstrip()
        if ps != self._last_ps and ps.strip():
            self._last_ps = ps
            print(f"[RDS] PI=0x{self.pi:04X}  PS='{ps}'  "
                  f"PTY={PTY_EU[self.pty]}  TP={self.tp}  groups={self.groups}", flush=True)
        if rt != self._last_rt and rt.strip():
            self._last_rt = rt
            print(f"[RDS] RadioText: {rt}", flush=True)
