import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    """BER Monitor.

    Compares a received bit stream against a KNOWN repeating reference
    pattern and reports the running bit error rate.

    Acquisition: buffer two full periods, then cross-correlate the first
    period against every cyclic shift of the reference.  The shift with the
    largest |correlation| is the alignment; a negative correlation means the
    stream is inverted, which is exactly the 180-degree ambiguity a Costas
    loop leaves behind (see Fundamentals 09).

    Tracking: XOR against the rolled reference and accumulate.  Output is one
    float per input bit carrying the running BER, so it can drive a Number
    Sink or a Time Sink directly.
    """

    def __init__(self, pattern=[0, 1], settle=30000, corr_threshold=0.4):
        gr.sync_block.__init__(self, name="BER Monitor",
                               in_sig=[np.uint8], out_sig=[np.float32])
        self.ref = np.asarray(pattern, dtype=np.uint8)
        self.N = len(self.ref)
        self.settle = int(settle)
        self.thr = float(corr_threshold)
        # two concatenated periods of the bipolar reference: sliding a window
        # over this gives every cyclic shift in one np.correlate call
        refb = 2.0 * self.ref.astype(np.float64) - 1.0
        self.tiled = np.concatenate([refb, refb])
        self.reset()

    def reset(self):
        self.locked = False
        self.invert = False
        self.phase = 0
        self.errors = 0
        self.total = 0
        self.skipped = 0
        self.acq = np.zeros(0, dtype=np.uint8)
        self._last_report = 0

    def _align(self, seg):
        """Correlate one period against all N cyclic shifts of the reference."""
        a = 2.0 * seg.astype(np.float64) - 1.0
        corr = np.correlate(self.tiled, a, mode='valid')[:self.N] / self.N
        s = int(np.argmax(np.abs(corr)))
        if abs(corr[s]) < self.thr:
            return None, False
        return s, bool(corr[s] < 0)

    def _count(self, bits):
        idx = (self.phase + np.arange(len(bits))) % self.N
        ref = self.ref[idx]
        if self.invert:
            ref = 1 - ref
        self.errors += int(np.count_nonzero(bits != ref))
        self.total += len(bits)
        self.phase = int((self.phase + len(bits)) % self.N)

    def work(self, input_items, output_items):
        n = len(input_items[0])
        xs = input_items[0]

        # 1. let the sync loops settle before we judge anything
        if self.skipped < self.settle:
            take = min(len(xs), self.settle - self.skipped)
            self.skipped += take
            xs = xs[take:]

        # 2. acquire alignment
        if not self.locked and len(xs):
            self.acq = np.concatenate([self.acq, xs])
            xs = xs[:0]
            if len(self.acq) >= 2 * self.N:
                s, inv = self._align(self.acq[:self.N])
                if s is None:
                    self.acq = self.acq[self.N:]      # slide on, try again
                else:
                    self.locked, self.invert, self.phase = True, inv, s
                    self._count(self.acq)
                    self.acq = self.acq[:0]

        # 3. track
        if self.locked and len(xs):
            self._count(xs)

        self._report()
        output_items[0][:] = self.ber()
        return n

    def _report(self, every=200000):
        if self.total - self._last_report >= every:
            self._last_report = self.total
            print(f"[BER Monitor] bits={self.total:>10,}  errors={self.errors:>8,}  "
                  f"BER={self.ber():.3e}", flush=True)

    def ber(self):
        return np.float32(self.errors / self.total) if self.total else np.float32(0.5)
