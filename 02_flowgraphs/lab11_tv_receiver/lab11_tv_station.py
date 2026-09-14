#!/usr/bin/env python3
"""
Lab 11 - Television Receiver Station.

A complete receiver front end: scan the band, keep a channel list, tune
directly, watch signal quality, and see the picture.

    ./lab11_tv_station.py                       # start on UHF ch 21
    ./lab11_tv_station.py --channel 31
    ./lab11_tv_station.py --scan-on-start
    ./lab11_tv_station.py --no-video            # measure only

Live picture needs ffmpeg (`sudo apt install ffmpeg`).  Everything else --
scanning, locking, MER, the transport-stream analysis -- works without it.

Why the scan and the receiver are separate engines
--------------------------------------------------
There is one radio, so scanning and receiving cannot both own it.  Switching
tears one flowgraph down and builds the other, which costs a second or two.

Inside the scanner, the capture is gated by a `blocks.copy` that is disabled
between dwells.  A disabled copy block consumes and discards, so the USRP
keeps draining at full rate and never overflows; if the vector sink were
connected permanently it would try to store 9.14 million samples a second and
the receive buffer would overrun within a second.
"""
import argparse
import os
import sys
import time

import numpy as np
from PyQt5 import QtCore, QtWidgets

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, '03_scripts'))

from gnuradio import blocks, gr, qtgui, uhd                      # noqa: E402
from gnuradio import filter as gfilter                            # noqa: E402
from gnuradio.fft import window                                   # noqa: E402
import dvbt_chain                                                 # noqa: E402
from dvbt_chain import (DvbtRx, MerProbe, TsProbe, PipeSink,      # noqa: E402
                        parse_mode, sample_rate, dvbt_bitrate)
import scan_tv_band                                               # noqa: E402
from scan_tv_band import classify, uhf_channel_freq               # noqa: E402

PLAYER = ['ffplay', '-hide_banner', '-loglevel', 'error', '-fflags', 'nobuffer',
          '-flags', 'low_delay', '-framedrop', '-autoexit',
          '-window_title', 'SDR LAB TV', '-i', 'pipe:0']


# ---------------------------------------------------------------------------
class ScanEngine:
    """Keeps the radio open and captures a burst per channel on demand."""

    def __init__(self, fs, gain, antenna):
        self.fs, self.gain, self.antenna = fs, gain, antenna
        self.tb = gr.top_block('scan')
        self.src = uhd.usrp_source('num_recv_frames=512',
                                   uhd.stream_args(cpu_format='fc32', channels=[0]))
        self.src.set_samp_rate(fs)
        self.src.set_gain(gain, 0)
        self.src.set_antenna(antenna, 0)
        self.src.set_bandwidth(fs, 0)
        self.gate = blocks.copy(gr.sizeof_gr_complex)
        self.gate.set_enabled(False)
        self.sink = blocks.vector_sink_c()
        self.tb.connect(self.src, self.gate, self.sink)
        self.tb.start()

    def dwell(self, freq, seconds, settle=0.15):
        self.src.set_center_freq(uhd.tune_request(freq), 0)
        time.sleep(settle)
        self.sink.reset()
        self.gate.set_enabled(True)
        time.sleep(seconds)
        self.gate.set_enabled(False)
        time.sleep(0.02)
        return np.array(self.sink.data(), dtype=np.complex64)

    def close(self):
        try:
            self.tb.stop(); self.tb.wait()
        except Exception:
            pass


class ScanWorker(QtCore.QThread):
    result = QtCore.pyqtSignal(int, dict)
    finished_scan = QtCore.pyqtSignal()

    def __init__(self, engine, channels, dwell, bandwidth):
        super().__init__()
        self.engine, self.channels = engine, channels
        self.dwell, self.bandwidth = dwell, bandwidth
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        for ch in self.channels:
            if self._abort:
                break
            x = self.engine.dwell(uhf_channel_freq(ch), self.dwell)
            if len(x) < 100000:
                continue
            r = classify(x, self.engine.fs, None, self.bandwidth)
            r['channel'] = ch
            r['freq_mhz'] = uhf_channel_freq(ch) / 1e6
            self.result.emit(ch, r)
        self.finished_scan.emit()


# ---------------------------------------------------------------------------
class RxEngine:
    """The DVB-T receiver, with Qt display widgets and a video pipe."""

    def __init__(self, fs, freq, gain, antenna, fft_mode, const, cr, gi, video, ts_file):
        self.fs = fs
        self.tb = gr.top_block('rx')
        self.src = uhd.usrp_source('num_recv_frames=512',
                                   uhd.stream_args(cpu_format='fc32', channels=[0]))
        self.src.set_samp_rate(fs)
        self.src.set_center_freq(uhd.tune_request(freq), 0)
        self.src.set_gain(gain, 0)
        self.src.set_antenna(antenna, 0)
        self.src.set_bandwidth(fs, 0)

        self.rx = DvbtRx(fft_mode, const, cr, gi)
        self.probe = TsProbe()
        self.mer = MerProbe(const, decim=64)
        self.video = PipeSink(argv=PLAYER if video else None, path=None)
        self.cells = blocks.vector_to_stream(
            gr.sizeof_gr_complex, dvbt_chain.DATA_CARRIERS[
                dvbt_chain.FFT_MODES[fft_mode][1]])

        self.tb.connect(self.src, self.rx)
        self.tb.connect((self.rx, 0), self.probe)
        self.tb.connect((self.rx, 0), self.video)
        self.tb.connect((self.rx, 1), self.cells)
        self.tb.connect(self.cells, self.mer)
        if ts_file:
            self.file = blocks.file_sink(gr.sizeof_char, ts_file)
            self.file.set_unbuffered(False)
            self.tb.connect((self.rx, 0), self.file)

        self.level = blocks.probe_signal_f()
        self.tb.connect(self.src, blocks.complex_to_mag_squared(),
                        blocks.keep_one_in_n(gr.sizeof_float, 1024),
                        gfilter.single_pole_iir_filter_ff(0.005),
                        blocks.nlog10_ff(10, 1, 0), self.level)

        self.fsink = qtgui.freq_sink_c(4096, window.WIN_BLACKMAN_hARRIS,
                                       freq, fs, 'Channel spectrum', 1, None)
        self.fsink.set_update_time(0.10)
        self.fsink.set_y_axis(-110, -10)
        self.fsink.set_fft_average(0.2)
        self.fsink.enable_autoscale(False)
        self.tb.connect(self.src, self.fsink)

        self.csink = qtgui.const_sink_c(1024, 'Constellation', 1, None)
        self.csink.set_update_time(0.10)
        self.csink.set_x_axis(-2, 2)
        self.csink.set_y_axis(-2, 2)
        self.csink.enable_autoscale(False)
        self.tb.connect(self.cells, self.csink)

        self.tb.start()

    def widgets(self):
        return (sip_wrap(self.fsink.qwidget()), sip_wrap(self.csink.qwidget()))

    def retune(self, freq):
        self.src.set_center_freq(uhd.tune_request(freq), 0)
        self.fsink.set_frequency_range(freq, self.fs)
        self.probe.reset()

    def set_gain(self, g):
        self.src.set_gain(g, 0)

    def close(self):
        try:
            self.video.close()
        except Exception:
            pass
        try:
            self.tb.stop(); self.tb.wait()
        except Exception:
            pass


def sip_wrap(obj):
    import sip
    return sip.wrapinstance(obj, QtWidgets.QWidget)


# ---------------------------------------------------------------------------
class Station(QtWidgets.QMainWindow):
    def __init__(self, a):
        super().__init__()
        self.a = a
        self.fs = sample_rate(a.bandwidth)
        self.const, self.cr, self.gi = parse_mode(a.mode)
        self.rate, _, _ = dvbt_bitrate(a.fft, self.const, self.cr, self.gi, a.bandwidth)
        self.scan_engine = None
        self.rx_engine = None
        self.worker = None
        self.rows = {}
        self.setWindowTitle('Lab 11 - Television Receiver Station')
        self._build()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(400)
        if a.scan_on_start:
            QtCore.QTimer.singleShot(400, self.start_scan)
        else:
            QtCore.QTimer.singleShot(200, self.tune_current)

    # ---------------------------------------------------------------- layout
    def _build(self):
        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        grid = QtWidgets.QHBoxLayout(root)

        left = QtWidgets.QVBoxLayout()
        grid.addLayout(left, 0)

        box = QtWidgets.QGroupBox('Tune')
        f = QtWidgets.QGridLayout(box)
        self.chan_spin = QtWidgets.QSpinBox()
        self.chan_spin.setRange(5, 69)
        self.chan_spin.setValue(self.a.channel)
        self.freq_edit = QtWidgets.QLineEdit(f'{uhf_channel_freq(self.a.channel)/1e6:.3f}')
        btn_tune = QtWidgets.QPushButton('Tune')
        btn_tune.clicked.connect(self.tune_current)
        self.chan_spin.valueChanged.connect(
            lambda v: self.freq_edit.setText(f'{uhf_channel_freq(v)/1e6:.3f}'))
        f.addWidget(QtWidgets.QLabel('UHF channel'), 0, 0)
        f.addWidget(self.chan_spin, 0, 1)
        f.addWidget(QtWidgets.QLabel('MHz (direct)'), 1, 0)
        f.addWidget(self.freq_edit, 1, 1)
        f.addWidget(btn_tune, 2, 0, 1, 2)
        self.gain_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.gain_slider.setRange(0, 76)
        self.gain_slider.setValue(int(self.a.gain))
        self.gain_label = QtWidgets.QLabel(f'RX gain {self.a.gain:.0f} dB')
        self.gain_slider.valueChanged.connect(self._gain_changed)
        f.addWidget(self.gain_label, 3, 0, 1, 2)
        f.addWidget(self.gain_slider, 4, 0, 1, 2)
        left.addWidget(box)

        box2 = QtWidgets.QGroupBox('Channel list')
        v = QtWidgets.QVBoxLayout(box2)
        h = QtWidgets.QHBoxLayout()
        self.btn_scan = QtWidgets.QPushButton('Scan band')
        self.btn_scan.clicked.connect(self.start_scan)
        self.btn_stop = QtWidgets.QPushButton('Stop')
        self.btn_stop.clicked.connect(self.stop_scan)
        self.btn_stop.setEnabled(False)
        h.addWidget(self.btn_scan); h.addWidget(self.btn_stop)
        v.addLayout(h)
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ['CH', 'MHz', 'dBFS', 'Shldr', 'Standard', 'Detail'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._row_picked)
        self.table.setMinimumWidth(520)
        v.addWidget(self.table)
        self.scan_status = QtWidgets.QLabel('not scanned')
        v.addWidget(self.scan_status)
        left.addWidget(box2, 1)

        box3 = QtWidgets.QGroupBox('Signal quality')
        q = QtWidgets.QFormLayout(box3)
        self.lbl_lock = QtWidgets.QLabel('-')
        self.lbl_level = QtWidgets.QLabel('-')
        self.lbl_mer = QtWidgets.QLabel('-')
        self.bar_mer = QtWidgets.QProgressBar()
        self.bar_mer.setRange(0, 35)
        self.lbl_pkts = QtWidgets.QLabel('-')
        self.lbl_cc = QtWidgets.QLabel('-')
        self.lbl_svc = QtWidgets.QLabel('-')
        self.lbl_drop = QtWidgets.QLabel('-')
        for k, w in [('Lock', self.lbl_lock), ('Level', self.lbl_level),
                     ('MER', self.lbl_mer), ('', self.bar_mer),
                     ('Packets', self.lbl_pkts), ('Continuity errors', self.lbl_cc),
                     ('Services', self.lbl_svc), ('Video pipe', self.lbl_drop)]:
            q.addRow(k, w)
        left.addWidget(box3)

        self.plots = QtWidgets.QVBoxLayout()
        grid.addLayout(self.plots, 1)
        self.plot_holder = QtWidgets.QWidget()
        self.plot_layout = QtWidgets.QVBoxLayout(self.plot_holder)
        self.plots.addWidget(self.plot_holder)

        self.statusBar().showMessage(
            dvbt_chain.mode_summary(self.a.fft, self.const, self.cr, self.gi, self.a.bandwidth))

    def _gain_changed(self, v):
        self.gain_label.setText(f'RX gain {v} dB')
        if self.rx_engine:
            self.rx_engine.set_gain(float(v))
        if self.scan_engine:
            self.scan_engine.src.set_gain(float(v), 0)

    # ------------------------------------------------------------------ scan
    def start_scan(self):
        self._teardown_rx()
        if self.scan_engine is None:
            self.scan_engine = ScanEngine(self.fs, float(self.gain_slider.value()),
                                          self.a.antenna)
        chans = list(range(self.a.first, self.a.last + 1))
        self.table.setRowCount(0)
        self.rows.clear()
        self.btn_scan.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.scan_status.setText(f'scanning ch {chans[0]}-{chans[-1]} ...')
        self.worker = ScanWorker(self.scan_engine, chans, self.a.dwell, self.a.bandwidth)
        self.worker.result.connect(self._scan_result)
        self.worker.finished_scan.connect(self._scan_done)
        self.worker.start()

    def stop_scan(self):
        if self.worker:
            self.worker.abort()

    def _scan_result(self, ch, r):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.rows[ch] = r
        cells = [str(ch), f"{r['freq_mhz']:.1f}", f"{r['dbfs']:.1f}",
                 f"{r['shoulder_db']:.1f}", r['standard'], r['detail']]
        for c, t in enumerate(cells):
            it = QtWidgets.QTableWidgetItem(t)
            if r['standard'] in ('DVB-T', 'DVB-T2'):
                it.setBackground(QtCore.Qt.green)
            elif r['standard'] == 'burst':
                it.setBackground(QtCore.Qt.yellow)
            self.table.setItem(row, c, it)
        self.table.resizeColumnsToContents()
        self.scan_status.setText(f'scanning ... ch {ch}')

    def _scan_done(self):
        self.btn_scan.setEnabled(True)
        self.btn_stop.setEnabled(False)
        found = [c for c, r in self.rows.items() if r['standard'] in ('DVB-T', 'DVB-T2')]
        self.scan_status.setText(
            f"{len(found)} television signal(s) in {len(self.rows)} channels"
            + (f": ch {', '.join(map(str, found))}" if found else
               " - double-click any row to tune it anyway"))

    def _row_picked(self, row, _col):
        ch = int(self.table.item(row, 0).text())
        self.chan_spin.setValue(ch)
        self.tune_current()

    # --------------------------------------------------------------- receive
    def _teardown_scan(self):
        if self.worker and self.worker.isRunning():
            self.worker.abort()
            self.worker.wait(3000)
        if self.scan_engine:
            self.scan_engine.close()
            self.scan_engine = None

    def _teardown_rx(self):
        if self.rx_engine:
            while self.plot_layout.count():
                w = self.plot_layout.takeAt(0).widget()
                if w:
                    w.setParent(None)
            self.rx_engine.close()
            self.rx_engine = None

    def tune_current(self):
        """Tune directly, with no scan needed -- type a frequency or pick a
        channel number.  A scan is a convenience, never a prerequisite."""
        try:
            freq = float(self.freq_edit.text()) * 1e6
        except ValueError:
            freq = uhf_channel_freq(self.chan_spin.value())
        self._teardown_scan()
        if self.rx_engine:
            self.rx_engine.retune(freq)
            self.statusBar().showMessage(f'tuned {freq/1e6:.3f} MHz')
            return
        self.rx_engine = RxEngine(self.fs, freq, float(self.gain_slider.value()),
                                  self.a.antenna, self.a.fft, self.const, self.cr,
                                  self.gi, not self.a.no_video, self.a.ts_file)
        for w in self.rx_engine.widgets():
            self.plot_layout.addWidget(w)
        self.statusBar().showMessage(f'tuned {freq/1e6:.3f} MHz')

    # ------------------------------------------------------------------ tick
    def _tick(self):
        if not self.rx_engine:
            return
        s = self.rx_engine.probe.snapshot()
        mer = self.rx_engine.mer.mer()
        lvl = self.rx_engine.level.level()
        self.lbl_level.setText(f'{lvl:.1f} dBFS')
        self.lbl_mer.setText('-' if np.isnan(mer) else f'{mer:.1f} dB')
        self.bar_mer.setValue(0 if np.isnan(mer) else max(0, min(35, int(mer))))
        self.lbl_pkts.setText(f"{s['packets']:,}")
        rate = s['cc_error_rate']
        self.lbl_cc.setText(f"{s['cc_errors']:,}  ({rate:.1e})")
        if s['packets'] < 500:
            lock, colour = 'NO LOCK', 'red'
        elif rate < 1e-4:
            lock, colour = 'LOCKED', 'green'
        elif rate < 1e-2:
            lock, colour = 'MARGINAL', 'orange'
        else:
            lock, colour = 'BREAKING UP', 'red'
        self.lbl_lock.setText(f'<b style="color:{colour}">{lock}</b>')
        self.lbl_svc.setText(', '.join(s['services'].values()) or '-')
        v = self.rx_engine.video.stats()
        self.lbl_drop.setText(
            f"{v['written']/1e6:.1f} MB sent, {v['dropped_blocks']} blocks dropped"
            if v['alive'] else 'no player (install ffmpeg)')

    def closeEvent(self, e):
        self._teardown_scan()
        self._teardown_rx()
        e.accept()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--channel', type=int, default=21)
    ap.add_argument('--first', type=int, default=21)
    ap.add_argument('--last', type=int, default=48)
    ap.add_argument('--mode', default='16qam-2/3-1/32')
    ap.add_argument('--fft', default='8k', choices=['2k', '8k'])
    ap.add_argument('--bandwidth', type=float, default=8e6)
    ap.add_argument('--gain', type=float, default=30)
    ap.add_argument('--antenna', default='RX2')
    ap.add_argument('--dwell', type=float, default=0.4)
    ap.add_argument('--ts-file', default='', help='also record the stream here')
    ap.add_argument('--no-video', action='store_true')
    ap.add_argument('--scan-on-start', action='store_true')
    a = ap.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    w = Station(a)
    w.resize(1500, 900)
    w.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
