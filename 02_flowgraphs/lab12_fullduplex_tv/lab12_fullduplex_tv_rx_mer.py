"""Modulation Error Ratio, the number a television calls "signal quality".

    MER = 10 log10( mean |ideal|^2 / mean |received - ideal|^2 )

`ideal` is the nearest legal constellation point, so no knowledge of the
transmitted data is needed.  Measured against a calibrated AWGN channel this
tracks true SNR to within about 0.9 dB.

Watch this rather than the picture.  MER falls smoothly as the link degrades,
while the picture stays flawless and then collapses: for 16QAM CR 2/3 this
receiver decodes perfectly at 13 dB and fails completely at 12 dB.  By the
time the picture breaks up you have already lost all your margin.
"""
import numpy as np
from gnuradio import gr

LEVELS = {2: np.array([-1., 1.]) / np.sqrt(2),
          4: np.array([-3., -1., 1., 3.]) / np.sqrt(10),
          6: np.array([-7., -5., -3., -1., 1., 3., 5., 7.]) / np.sqrt(42)}


class blk(gr.decim_block):
    def __init__(self, bits_per_symbol=4, decim=4096):
        gr.decim_block.__init__(self, name='MER (dB)',
                                in_sig=[np.complex64], out_sig=[np.float32],
                                decim=int(decim))
        self.levels = LEVELS[int(bits_per_symbol)]
        self.mer = 0.0

    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)
        x = input_items[0][:n * self.decimation()]
        if len(x) > 8192:                      # a measurement, not a filter:
            x = x[::len(x) // 8192]            # sub-sampling costs nothing
        if len(x):
            lv = self.levels
            i = lv[np.abs(x.real[:, None] - lv[None, :]).argmin(axis=1)]
            q = lv[np.abs(x.imag[:, None] - lv[None, :]).argmin(axis=1)]
            ideal = i + 1j * q
            err = float(np.mean(np.abs(x - ideal) ** 2))
            sig = float(np.mean(np.abs(ideal) ** 2))
            if err > 0 and sig > 0:
                m = 10 * np.log10(sig / err)
                self.mer = m if self.mer == 0.0 else 0.9 * self.mer + 0.1 * m
        out[:] = self.mer
        return n
