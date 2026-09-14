#!/usr/bin/env python3
"""
The DVB-T modulator and demodulator, as reusable GNU Radio hierarchical blocks,
plus the instrumentation a television receiver needs to show a quality bar.

Labs 11 and 12 both import this.  Keeping one copy means the transmitter and
the receiver can never drift out of agreement about the mode -- which is the
single most common way a digital TV link fails to lock.

Why DVB-T here and DVB-T2 in Lab 10
-----------------------------------
gr-dtv ships a *transmitter* for DVB-T2 but no receiver: the blocks are
`dvbt2_*` for modulation only.  For DVB-T it ships both directions.  So:

    Lab 10   DVB-T2 transmit  -> decoded by a real TV or USB tuner
    Lab 11   DVB-T receive    -> decoded by this software, picture on screen
    Lab 12   DVB-T both ways  -> one radio doing each simultaneously

That is not a compromise in the theory -- DVB-T2 is DVB-T plus LDPC, rotated
constellations and a P1 preamble -- but it is the difference between watching
a picture and watching a spectrum.

Verified: a transport stream pushed through DvbtTx and back through DvbtRx
comes out **bit-identical** (0 mismatches in 3,912 packets), and the receiver
sustains 16.4 Msps against the 9.14 Msps it needs for real time.
"""
import queue
import subprocess
import threading

import numpy as np
from gnuradio import blocks, digital, dtv, fft, gr
from gnuradio.fft import window

# ---------------------------------------------------------------------------
# Mode tables (ETSI EN 300 744)
# ---------------------------------------------------------------------------
ELEMENTARY_T = {8e6: 7.0 / 64e6, 7e6: 1.0 / 8e6, 6e6: 7.0 / 48e6}
DATA_CARRIERS = {2048: 1512, 8192: 6048}
OCCUPIED_CARRIERS = {2048: 1705, 8192: 6817}
RS_RATE = 188.0 / 204.0

CONSTELLATIONS = {'qpsk': (dtv.MOD_QPSK, 2), '16qam': (dtv.MOD_16QAM, 4),
                  '64qam': (dtv.MOD_64QAM, 6)}
CODE_RATES = {'1/2': (dtv.C1_2, 1, 2), '2/3': (dtv.C2_3, 2, 3), '3/4': (dtv.C3_4, 3, 4),
              '5/6': (dtv.C5_6, 5, 6), '7/8': (dtv.C7_8, 7, 8)}
GUARDS = {'1/32': (dtv.GI_1_32, 32), '1/16': (dtv.GI_1_16, 16),
          '1/8': (dtv.GI_1_8, 8), '1/4': (dtv.GI_1_4, 4)}
FFT_MODES = {'2k': (dtv.T2k, 2048), '8k': (dtv.T8k, 8192)}

# Reed-Solomon (204,188) shortened from (255,239) over GF(2^8), and the
# convolutional interleaver that spreads a burst error across 12 RS blocks.
RS_ARGS = (2, 8, 0x11d, 255, 239, 8, 51, 8)
INTERLEAVER_ARGS = (136, 12, 17)


def sample_rate(chan_bw=8e6):
    """Complex sample rate: exactly one sample per elementary period."""
    return 1.0 / ELEMENTARY_T[chan_bw]


def dvbt_bitrate(fft_mode, const, code_rate, guard, chan_bw=8e6):
    """Useful transport-stream bit rate, and the two symbol times.

    Everything follows from the elementary period T:
        Tu = nfft * T                useful symbol
        Ts = Tu (1 + 1/G)            plus guard interval
        R  = cells * bits / Ts * CR * 188/204
    """
    nfft = FFT_MODES[fft_mode][1]
    T = ELEMENTARY_T[chan_bw]
    Tu = nfft * T
    Ts = Tu * (1.0 + 1.0 / GUARDS[guard][1])
    _, num, den = CODE_RATES[code_rate]
    raw = DATA_CARRIERS[nfft] * CONSTELLATIONS[const][1] / Ts
    return raw * num / den * RS_RATE, Tu, Ts


def parse_mode(s):
    """'16qam-2/3-1/32' -> ('16qam', '2/3', '1/32'), validated."""
    parts = s.split('-')
    if len(parts) != 3:
        raise ValueError(f"mode must look like 16qam-2/3-1/32, got {s!r}")
    const, cr, gi = parts
    if const not in CONSTELLATIONS:
        raise ValueError(f"unknown constellation {const!r}")
    if cr not in CODE_RATES:
        raise ValueError(f"unknown code rate {cr!r}")
    if gi not in GUARDS:
        raise ValueError(f"unknown guard interval {gi!r}")
    return const, cr, gi


def mode_summary(fft_mode, const, cr, gi, chan_bw=8e6):
    br, Tu, Ts = dvbt_bitrate(fft_mode, const, cr, gi, chan_bw)
    return (f"{fft_mode.upper()} {const.upper()} CR {cr} GI {gi} "
            f"@ {chan_bw/1e6:.0f} MHz -> {br/1e6:.3f} Mbit/s "
            f"(Tu {Tu*1e6:.0f} us, Ts {Ts*1e6:.0f} us)")


# ---------------------------------------------------------------------------
# Transmitter
# ---------------------------------------------------------------------------
class DvbtTx(gr.hier_block2):
    """MPEG-2 transport stream bytes in, complex baseband out.

    Eight stages, each defeating a specific impairment:

        energy dispersal      spreads the spectrum, stops a stuck TS pattern
                              putting a line in the middle of the channel
        Reed-Solomon (204,188) corrects up to 8 byte errors per packet
        convolutional interl. spreads an impulsive burst over 12 RS blocks
        inner convolutional   the workhorse FEC; Viterbi-decoded at the far end
        bit interleaver       decorrelates the bit positions within a QAM symbol
        symbol interleaver    spreads adjacent bits across the whole channel,
                              so a notch from a reflection does not kill a
                              contiguous run of data
        mapper                bits -> QAM constellation points
        reference signals     inserts scattered/continual pilots and the TPS
                              carriers, and performs the IFFT

    Note the last one: `dvbt_reference_signals` returns *time domain*.  Adding
    an IFFT after it -- which the block's name invites, and which the RX chain's
    explicit FFT makes look symmetrical -- silently destroys the signal.  It
    still has valid OFDM symbol timing, so a cyclic-prefix detector still locks
    onto it; only the frame synchroniser fails, with no error message.
    """

    def __init__(self, fft_mode='8k', const='16qam', code_rate='2/3', guard='1/32',
                 cell_id=0, amplitude=1.0):
        gr.hier_block2.__init__(
            self, 'DvbtTx',
            gr.io_signature(1, 1, gr.sizeof_char),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        tm, nfft = FFT_MODES[fft_mode]
        payload = DATA_CARRIERS[nfft]
        c = CONSTELLATIONS[const][0]
        cr = CODE_RATES[code_rate][0]
        g = GUARDS[guard][0]
        cp = nfft // GUARDS[guard][1]

        self.energy = dtv.dvbt_energy_dispersal(1)
        self.rs = dtv.dvbt_reed_solomon_enc(*RS_ARGS)
        self.interleave = dtv.dvbt_convolutional_interleaver(*INTERLEAVER_ARGS)
        self.inner = dtv.dvbt_inner_coder(1, payload, c, dtv.NH, cr)
        self.bitint = dtv.dvbt_bit_inner_interleaver(payload, c, dtv.NH, tm)
        self.symint = dtv.dvbt_symbol_inner_interleaver(payload, tm, 1)
        self.mapper = dtv.dvbt_map(payload, c, dtv.NH, tm, 1)
        self.pilots = dtv.dvbt_reference_signals(
            gr.sizeof_gr_complex, payload, nfft, c, dtv.NH, cr, cr, g, tm, 1, cell_id)
        self.cp = digital.ofdm_cyclic_prefixer(nfft, nfft + cp, 0, '')
        self.scale = blocks.multiply_const_cc(amplitude)

        self.connect(self, self.energy, self.rs, self.interleave, self.inner,
                     self.bitint, self.symint, self.mapper, self.pilots,
                     self.cp, self.scale, self)

    def set_amplitude(self, a):
        self.scale.set_k(a)


# ---------------------------------------------------------------------------
# Receiver
# ---------------------------------------------------------------------------
class DvbtRx(gr.hier_block2):
    """Complex baseband in; transport stream out, plus an equalised-cell tap.

    Output 0: MPEG-2 transport stream bytes
    Output 1: equalised constellation cells (for the display and for MER)

    The chain is the transmitter reversed, with two additions at the front:
    `dvbt_ofdm_sym_acquisition` finds the symbol boundary using the cyclic
    prefix and corrects the fractional frequency offset, and the FFT returns
    the signal to the frequency domain where the pilots live.
    """

    def __init__(self, fft_mode='8k', const='16qam', code_rate='2/3', guard='1/32',
                 cell_id=0, snr_hint=10.0, viterbi_block=768):
        gr.hier_block2.__init__(
            self, 'DvbtRx',
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(2, 2, [gr.sizeof_char, gr.sizeof_gr_complex]))

        tm, nfft = FFT_MODES[fft_mode]
        payload = DATA_CARRIERS[nfft]
        occupied = OCCUPIED_CARRIERS[nfft]
        c = CONSTELLATIONS[const][0]
        cr = CODE_RATES[code_rate][0]
        g = GUARDS[guard][0]
        cp = nfft // GUARDS[guard][1]

        self.acq = dtv.dvbt_ofdm_sym_acquisition(1, nfft, occupied, cp, snr_hint)
        self.fft = fft.fft_vcc(nfft, True, window.rectangular(nfft), True, 1)
        self.pilots = dtv.dvbt_demod_reference_signals(
            gr.sizeof_gr_complex, nfft, payload, c, dtv.NH, cr, cr, g, tm, 1, cell_id)
        self.demap = dtv.dvbt_demap(payload, c, dtv.NH, tm, 1)
        # Deinterleave BEFORE the bit deinterleaver, and in that order.  Leaving
        # this block out is not a subtle degradation: the transport stream still
        # comes out with a 0x47 sync byte on every packet, because the energy
        # descrambler writes those unconditionally, while every payload byte is
        # noise.  Check PIDs, never sync bytes, when judging a DVB-T receiver.
        self.symdeint = dtv.dvbt_symbol_inner_interleaver(payload, tm, 0)
        self.bitdeint = dtv.dvbt_bit_inner_deinterleaver(payload, c, dtv.NH, tm)
        self.v2s = blocks.vector_to_stream(gr.sizeof_char, payload)
        self.viterbi = dtv.dvbt_viterbi_decoder(c, dtv.NH, cr, viterbi_block)
        self.deinterleave = dtv.dvbt_convolutional_deinterleaver(*INTERLEAVER_ARGS)
        self.rs = dtv.dvbt_reed_solomon_dec(*RS_ARGS)
        self.descramble = dtv.dvbt_energy_descramble(8)
        self.cells = blocks.vector_to_stream(gr.sizeof_gr_complex, payload)

        self.connect(self, self.acq, self.fft, self.pilots, self.demap,
                     self.symdeint, self.bitdeint, self.v2s, self.viterbi,
                     self.deinterleave, self.rs, self.descramble, (self, 0))
        self.connect(self.pilots, self.cells, (self, 1))


# ---------------------------------------------------------------------------
# Instrumentation
# ---------------------------------------------------------------------------
class MerProbe(gr.sync_block):
    """Modulation Error Ratio, in dB, from equalised constellation cells.

        MER = 10 log10( sum |ideal|^2 / sum |received - ideal|^2 )

    'ideal' is the nearest legal constellation point, so this needs no
    knowledge of the transmitted data -- which is exactly how a television
    measures the number it shows you as signal quality.  It is the honest
    version of a 'bars' display: MER degrades smoothly as the link worsens,
    where the picture stays perfect and then collapses.
    """

    LEVELS = {'qpsk': np.array([-1, 1]) / np.sqrt(2),
              '16qam': np.array([-3, -1, 1, 3]) / np.sqrt(10),
              '64qam': np.array([-7, -5, -3, -1, 1, 3, 5, 7]) / np.sqrt(42)}

    def __init__(self, const='16qam', decim=64):
        gr.sync_block.__init__(self, name='MerProbe',
                               in_sig=[np.complex64], out_sig=None)
        self.levels = self.LEVELS[const]
        self.decim = max(1, int(decim))
        self._mer = float('nan')
        self._lock = threading.Lock()

    def set_constellation(self, const):
        with self._lock:
            self.levels = self.LEVELS[const]

    def work(self, input_items, output_items):
        x = input_items[0][::self.decim]
        if len(x):
            with self._lock:
                lv = self.levels
            i = lv[np.abs(x.real[:, None] - lv[None, :]).argmin(axis=1)]
            q = lv[np.abs(x.imag[:, None] - lv[None, :]).argmin(axis=1)]
            ideal = i + 1j * q
            err = float(np.mean(np.abs(x - ideal) ** 2))
            sig = float(np.mean(np.abs(ideal) ** 2))
            if err > 0 and sig > 0:
                m = 10 * np.log10(sig / err)
                with self._lock:
                    self._mer = m if np.isnan(self._mer) else 0.9 * self._mer + 0.1 * m
        return len(input_items[0])

    def mer(self):
        with self._lock:
            return self._mer


class TsProbe(gr.sync_block):
    """Parse the transport stream as it goes past: PIDs, continuity errors,
    service names, and the packet rate.

    The continuity counter is the receiver's only in-band way to notice that a
    packet was lost.  Each PID's counter increments modulo 16 on every packet
    carrying payload; a jump means the Reed-Solomon decoder gave up on a block.
    That ratio is the number worth watching -- a picture that looks fine at
    1e-4 will break up at 1e-3.
    """

    def __init__(self, window_packets=20000):
        gr.sync_block.__init__(self, name='TsProbe',
                               in_sig=[np.uint8], out_sig=None)
        self.set_output_multiple(188)
        self._buf = b''
        self._lock = threading.Lock()
        self.packets = 0
        self.sync_errors = 0
        self.cc_errors = 0
        self.pids = {}
        self.services = {}
        self._cc = {}
        self._window = window_packets
        self._since = 0

    def work(self, input_items, output_items):
        data = input_items[0].tobytes()
        buf = self._buf + data
        n = len(buf) // 188
        with self._lock:
            for k in range(n):
                p = buf[k * 188:(k + 1) * 188]
                self.packets += 1
                self._since += 1
                if p[0] != 0x47:
                    self.sync_errors += 1
                    continue
                pid = ((p[1] & 0x1f) << 8) | p[2]
                self.pids[pid] = self.pids.get(pid, 0) + 1
                if pid != 0x1fff:
                    has_payload = bool(p[3] & 0x10)
                    cc = p[3] & 0x0f
                    prev = self._cc.get(pid)
                    if prev is not None and has_payload and cc != (prev + 1) % 16:
                        self.cc_errors += 1
                    if has_payload or prev is None:
                        self._cc[pid] = cc
                    if pid == 0x11:
                        self._parse_sdt(p)
            if self._since >= self._window:
                # decay so the display tracks current conditions, not history
                self._since = 0
                self.pids = {k: max(1, v // 2) for k, v in self.pids.items()}
        self._buf = buf[n * 188:]
        return len(input_items[0])

    def _parse_sdt(self, p):
        """Pull service names out of the Service Description Table so the
        channel list can show 'SDR LAB TV' rather than a bare PID."""
        try:
            if not (p[3] & 0x10):
                return
            off = 4
            if p[3] & 0x20:
                off += 1 + p[4]
            if off >= 188:
                return
            off += p[off] + 1                      # pointer_field
            if off + 11 >= 188 or p[off] != 0x42:  # SDT, actual TS
                return
            slen = ((p[off + 1] & 0x0f) << 8) | p[off + 2]
            i = off + 11
            end = min(off + 3 + slen - 4, 188)
            while i + 5 <= end:
                sid = (p[i] << 8) | p[i + 1]
                dlen = ((p[i + 3] & 0x0f) << 8) | p[i + 4]
                j, dend = i + 5, min(i + 5 + dlen, end)
                while j + 2 <= dend:
                    tag, tlen = p[j], p[j + 1]
                    if tag == 0x48 and j + 3 < dend:   # service_descriptor
                        k = j + 3
                        plen = p[k]
                        k += 1 + plen
                        if k < dend:
                            nlen = p[k]
                            name = bytes(p[k + 1:k + 1 + nlen])
                            name = bytes(b for b in name if b >= 0x20)
                            if name:
                                self.services[sid] = name.decode('latin1', 'replace')
                    j += 2 + tlen
                i = i + 5 + dlen
        except (IndexError, ValueError):
            pass

    def snapshot(self):
        with self._lock:
            total = max(1, self.packets)
            return dict(packets=self.packets,
                        sync_errors=self.sync_errors,
                        cc_errors=self.cc_errors,
                        cc_error_rate=self.cc_errors / total,
                        pids=dict(sorted(self.pids.items(), key=lambda kv: -kv[1])[:12]),
                        services=dict(self.services))

    def reset(self):
        with self._lock:
            self.packets = self.sync_errors = self.cc_errors = 0
            self.pids.clear()
            self._cc.clear()


class PipeSink(gr.sync_block):
    """Feed the transport stream to an external player without ever stalling
    the radio.

    A plain file sink pointed at a FIFO looks simpler and is a trap: if the
    player pauses, buffers, or is killed, the write blocks, the scheduler
    stops draining the USRP, and the receiver drowns in overflows.  Here a
    bounded queue absorbs jitter and *drops* when the player cannot keep up.
    Dropping television frames is the correct failure: the radio keeps running
    and the picture recovers on the next keyframe.
    """

    def __init__(self, argv=None, path=None, max_blocks=256):
        gr.sync_block.__init__(self, name='PipeSink', in_sig=[np.uint8], out_sig=None)
        self.set_output_multiple(188)
        self._q = queue.Queue(maxsize=max_blocks)
        self._dropped = 0
        self._written = 0
        self._proc = None
        self._fh = None
        self._stop = threading.Event()
        if argv:
            self._proc = subprocess.Popen(argv, stdin=subprocess.PIPE,
                                          stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL)
            self._fh = self._proc.stdin
        elif path:
            self._fh = open(path, 'wb')
        self._thread = threading.Thread(target=self._drain, daemon=True)
        self._thread.start()

    def _drain(self):
        while not self._stop.is_set():
            try:
                chunk = self._q.get(timeout=0.2)
            except queue.Empty:
                continue
            if self._fh is None:
                continue
            try:
                self._fh.write(chunk)
                self._fh.flush()
                self._written += len(chunk)
            except (BrokenPipeError, ValueError, OSError):
                self._fh = None

    def work(self, input_items, output_items):
        try:
            self._q.put_nowait(input_items[0].tobytes())
        except queue.Full:
            self._dropped += 1
        return len(input_items[0])

    def stats(self):
        return dict(written=self._written, dropped_blocks=self._dropped,
                    alive=self._fh is not None)

    def close(self):
        self._stop.set()
        try:
            if self._fh:
                self._fh.close()
        except OSError:
            pass
        if self._proc:
            try:
                self._proc.terminate()
            except OSError:
                pass


__all__ = ['DvbtTx', 'DvbtRx', 'MerProbe', 'TsProbe', 'PipeSink',
           'dvbt_bitrate', 'sample_rate', 'parse_mode', 'mode_summary',
           'CONSTELLATIONS', 'CODE_RATES', 'GUARDS', 'FFT_MODES',
           'DATA_CARRIERS', 'OCCUPIED_CARRIERS']


# ---------------------------------------------------------------------------
# Loopback self-test
# ---------------------------------------------------------------------------
def _loopback(ts_bytes, fft_mode, const, cr, gi, snr_db=None, seed=0):
    """Push a transport stream through TX -> (optional AWGN) -> RX."""
    from gnuradio import analog

    class TxOnly(gr.top_block):
        def __init__(self, nsym):
            gr.top_block.__init__(self)
            nfft = FFT_MODES[fft_mode][1]
            cp = nfft // GUARDS[gi][1]
            src = blocks.vector_source_b(list(ts_bytes), True)
            self.tx = DvbtTx(fft_mode, const, cr, gi)
            head = blocks.head(gr.sizeof_gr_complex, nsym * (nfft + cp))
            self.sink = blocks.vector_sink_c()
            self.connect(src, self.tx, head, self.sink)

    nfft = FFT_MODES[fft_mode][1]
    cp = nfft // GUARDS[gi][1]
    nsym = 2600 if nfft == 8192 else 9000
    tb = TxOnly(nsym)
    tb.run()
    iq = np.array(tb.sink.data(), dtype=np.complex64)
    # The very first OFDM symbol carries a large start-up transient (peak 8.1
    # against an RMS of 0.21 -- 31 dB, where steady-state OFDM is 11 dB).
    # Drop it, exactly as the flowgraphs do before the USRP sink.
    iq = iq[nfft + cp:]

    class RxOnly(gr.top_block):
        def __init__(self):
            gr.top_block.__init__(self)
            src = blocks.vector_source_c(iq.tolist(), False)
            self.rx = DvbtRx(fft_mode, const, cr, gi)
            self.ts = blocks.vector_sink_b()
            self.mer = MerProbe(const, decim=8)
            self.probe = TsProbe()
            if snr_db is None:
                self.connect(src, self.rx)
            else:
                sig = float(np.mean(np.abs(iq) ** 2))
                # analog.noise_source_c(amplitude=A) yields total complex
                # variance A^2 (measured, not assumed -- see Fundamentals 08).
                amp = np.sqrt(sig / (10 ** (snr_db / 10.0)))
                noise = analog.noise_source_c(analog.GR_GAUSSIAN, float(amp), seed)
                add = blocks.add_cc()
                self.connect(src, (add, 0))
                self.connect(noise, (add, 1))
                self.connect(add, self.rx)
            self.connect((self.rx, 0), self.ts)
            self.connect((self.rx, 0), self.probe)
            self.connect((self.rx, 1), self.mer)

    rb = RxOnly()
    rb.run()
    return np.array(rb.ts.data(), dtype=np.uint8), rb.mer.mer(), rb.probe.snapshot()


def _align_and_compare(out, src):
    """Compare decoded TS against source, anchored on a table packet.

    Anchoring on null packets does not work: they are all 0xFF and match
    anywhere, which makes a broken decode look 99.9 % correct.
    """
    if len(out) < 188 * 400:
        return None
    o = out[:(len(out) // 188) * 188].reshape(-1, 188)
    pid = ((o[:, 1].astype(np.int32) & 0x1f) << 8) | o[:, 2]
    tbl = np.where((pid != 0x1fff) & (o[:, 0] == 0x47))[0]
    if len(tbl) < 3:
        return None
    k = int(tbl[1])
    span = min(600, len(o) - k)
    idx = src.tobytes().find(o[k:k + span].tobytes())
    if idx < 0:
        return None
    n = (min(len(out) - k * 188, len(src) - idx) // 188) * 188
    a, b = out[k * 188:k * 188 + n], src[idx:idx + n]
    return int(np.count_nonzero(a != b)), n


def selftest(argv=None):
    import argparse
    import os
    import sys
    ap = argparse.ArgumentParser(description='DVB-T chain loopback verification')
    ap.add_argument('--mode', default='16qam-2/3-1/32')
    ap.add_argument('--fft', default='8k', choices=['2k', '8k'])
    ap.add_argument('--snr', type=float, nargs='*',
                    help='also sweep these SNRs in dB')
    a = ap.parse_args(argv)
    const, cr, gi = parse_mode(a.mode)

    here = os.path.dirname(os.path.abspath(__file__))
    # Generated artefact, not source: keep it out of the repository.
    import tempfile
    ts_path = os.path.join(tempfile.gettempdir(), 'dvbt_selftest.ts')
    rate, _, _ = dvbt_bitrate(a.fft, const, cr, gi)
    if not os.path.exists(ts_path):
        sys.argv = ['make_test_ts.py', '--out', ts_path, '--seconds', '3',
                    '--rate', str(int(rate)), '--name', 'SELFTEST']
        import runpy
        try:
            runpy.run_path(os.path.join(here, 'make_test_ts.py'), run_name='__main__')
        except SystemExit:
            pass          # make_test_ts.py exits on success; that is not ours
    src = np.fromfile(ts_path, dtype=np.uint8)

    print(mode_summary(a.fft, const, cr, gi))
    print()
    ok = True

    out, mer, snap = _loopback(src, a.fft, const, cr, gi, None)
    cmp_ = _align_and_compare(out, src)
    nulls = snap['pids'].get(0x1fff, 0)
    tot = max(1, sum(snap['pids'].values()))
    print(f"noiseless : {len(out):>9,} TS bytes  MER {mer:6.1f} dB  "
          f"null {100*nulls/tot:5.1f} %  CC errors {snap['cc_errors']}")
    if cmp_ is None:
        print("            could not align against the source -- decode failed")
        ok = False
    else:
        err, n = cmp_
        print(f"            compared {n:,} bytes against the source: "
              f"{err} mismatches -> {100*(1-err/n):.6f} % exact")
        ok &= (err == 0)
    ok &= snap['sync_errors'] == 0

    if a.snr:
        print("\n  SNR dB     MER dB   TS bytes   CC err   null %   verdict")
        print("  " + "-" * 58)
        for s in a.snr:
            out, mer, snap = _loopback(src, a.fft, const, cr, gi, s)
            tot = max(1, sum(snap['pids'].values()))
            nulls = snap['pids'].get(0x1fff, 0)
            cmp_ = _align_and_compare(out, src)
            verdict = 'no lock'
            if cmp_ and cmp_[0] == 0:
                verdict = 'perfect'
            elif cmp_:
                verdict = f'{cmp_[0]} byte errors'
            elif len(out) > 188 * 100:
                verdict = 'bytes, no match'
            print(f"  {s:6.1f}   {mer:8.1f}   {len(out):>9,}   {snap['cc_errors']:>6}   "
                  f"{100*nulls/tot:6.1f}   {verdict}")

    print("\nSELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == '__main__':
    import sys
    sys.exit(selftest())
