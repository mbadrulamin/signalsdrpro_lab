#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 08 - RDS Decoder: Reading Data Off the FM Broadcast Band
# Author: SignalSDR Pro Lab
# Description: Decode Programme Service name and RadioText from the 57 kHz RDS subcarrier
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
import math
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import lab08_rds_decoder_rds_decoder as rds_decoder  # embedded python block
import sip



class lab08_rds_decoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 08 - RDS Decoder: Reading Data Off the FM Broadcast Band", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 08 - RDS Decoder: Reading Data Off the FM Broadcast Band")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "lab08_rds_decoder")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2000000
        self.mpx_rate = mpx_rate = int(samp_rate/8)
        self.rds_rate = rds_rate = int(mpx_rate/25)
        self.chip_rate = chip_rate = 2375.0
        self.sps = sps = rds_rate/chip_rate
        self.nfilts = nfilts = 32
        self.volume = volume = 0.5
        self.rf_gain = rf_gain = 45
        self.rds_taps = rds_taps = firdes.low_pass(1.0, mpx_rate, 2400,800, window.WIN_HAMMING, 6.76)
        self.rds_mf_taps = rds_mf_taps = firdes.root_raised_cosine(nfilts, nfilts*sps, 1.0, 1.0, int(11*sps*nfilts))
        self.offset_freq = offset_freq = 0
        self.loop_bw = loop_bw = 0.010
        self.freq = freq = 100.0e6
        self.fm_taps = fm_taps = firdes.low_pass(1.0, samp_rate, 110e3,30e3, window.WIN_HAMMING, 6.76)
        self.audio_rate = audio_rate = int(mpx_rate/5)

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 5, 0.1, 0.5, 250)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._rf_gain_range = qtgui.Range(0, 76, 1, 45, 250)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rf_gain_win)
        self._offset_freq_range = qtgui.Range(-800e3, 800e3, 10e3, 0, 350)
        self._offset_freq_win = qtgui.RangeWidget(self._offset_freq_range, self.set_offset_freq, "Channel Offset (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._offset_freq_win)
        self._loop_bw_range = qtgui.Range(0.002, 0.050, 0.001, 0.010, 350)
        self._loop_bw_win = qtgui.RangeWidget(self._loop_bw_range, self.set_loop_bw, "Sync Loop Bandwidth", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._loop_bw_win)
        self._freq_range = qtgui.Range(87.5e6, 108e6, 100e3, 100.0e6, 350)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "FM Station (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self.xlating_fm = filter.freq_xlating_fir_filter_ccf(8, fm_taps, offset_freq, samp_rate)
        self.wbfm_rcv = analog.wfm_rcv(
        	quad_rate=mpx_rate,
        	audio_decimation=5,
        )
        self.volume_control = blocks.multiply_const_ff(volume)
        self.usrp_source = uhd.usrp_source(
            ",".join(('', '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.usrp_source.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.usrp_source.set_center_freq(freq, 0)
        self.usrp_source.set_antenna('TX/RX', 0)
        self.usrp_source.set_bandwidth(samp_rate, 0)
        self.usrp_source.set_gain(rf_gain, 0)
        self.to_real = blocks.complex_to_real(1)
        self.sym_sync = digital.symbol_sync_cc(
            digital.TED_GARDNER,
            sps,
            loop_bw,
            1.0,
            1.0,
            1.5,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_PFB_MF,
            nfilts,
            rds_mf_taps)
        self.rds_xlate = filter.freq_xlating_fir_filter_fcf(25, rds_taps, 57000, mpx_rate)
        self.rds_decoder = rds_decoder.blk(verbose=True, reacquire_chips=20000)
        self.rds_agc = analog.agc2_cc(0.1, 0.01, 0.5, 1.0, 65536)
        self.quad_demod = analog.quadrature_demod_cf((mpx_rate/(2*math.pi*75000)))
        self.mpx_sink = qtgui.freq_sink_f(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            mpx_rate, #bw
            'MPX Baseband - look for pilot at 19k, stereo at 38k, RDS at 57k', #name
            1,
            None # parent
        )
        self.mpx_sink.set_update_time(0.10)
        self.mpx_sink.set_y_axis((-120), 0)
        self.mpx_sink.set_y_label('Relative Gain', 'dB')
        self.mpx_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.mpx_sink.enable_autoscale(False)
        self.mpx_sink.enable_grid(True)
        self.mpx_sink.set_fft_average(1.0)
        self.mpx_sink.enable_axis_labels(True)
        self.mpx_sink.enable_control_panel(False)
        self.mpx_sink.set_fft_window_normalized(False)


        self.mpx_sink.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.mpx_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.mpx_sink.set_line_label(i, labels[i])
            self.mpx_sink.set_line_width(i, widths[i])
            self.mpx_sink.set_line_color(i, colors[i])
            self.mpx_sink.set_line_alpha(i, alphas[i])

        self._mpx_sink_win = sip.wrapinstance(self.mpx_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._mpx_sink_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.group_sink = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.group_sink.set_update_time(0.25)
        self.group_sink.set_title('Valid RDS groups decoded')

        labels = ['groups', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.group_sink.set_min(i, 0)
            self.group_sink.set_max(i, 1000)
            self.group_sink.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.group_sink.set_label(i, "Data {0}".format(i))
            else:
                self.group_sink.set_label(i, labels[i])
            self.group_sink.set_unit(i, units[i])
            self.group_sink.set_factor(i, factor[i])

        self.group_sink.enable_autoscale(True)
        self._group_sink_win = sip.wrapinstance(self.group_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._group_sink_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.costas = digital.costas_loop_cc(loop_bw, 2, False)
        self.const_sink = qtgui.const_sink_c(
            512, #size
            'RDS Constellation', #name
            1, #number of inputs
            None # parent
        )
        self.const_sink.set_update_time(0.10)
        self.const_sink.set_y_axis((-2), 2)
        self.const_sink.set_x_axis((-2), 2)
        self.const_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.const_sink.enable_autoscale(True)
        self.const_sink.enable_grid(True)
        self.const_sink.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.const_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.const_sink.set_line_label(i, labels[i])
            self.const_sink.set_line_width(i, widths[i])
            self.const_sink.set_line_color(i, colors[i])
            self.const_sink.set_line_style(i, styles[i])
            self.const_sink.set_line_marker(i, markers[i])
            self.const_sink.set_line_alpha(i, alphas[i])

        self._const_sink_win = sip.wrapinstance(self.const_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._const_sink_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.chip_sink = qtgui.time_sink_f(
            256, #size
            chip_rate, #samp_rate
            'Recovered chips (2375/s)', #name
            1, #number of inputs
            None # parent
        )
        self.chip_sink.set_update_time(0.10)
        self.chip_sink.set_y_axis(-2, 2)

        self.chip_sink.set_y_label('Amplitude', "")

        self.chip_sink.enable_tags(True)
        self.chip_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.chip_sink.enable_autoscale(True)
        self.chip_sink.enable_grid(True)
        self.chip_sink.enable_axis_labels(True)
        self.chip_sink.enable_control_panel(False)
        self.chip_sink.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.chip_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.chip_sink.set_line_label(i, labels[i])
            self.chip_sink.set_line_width(i, widths[i])
            self.chip_sink.set_line_color(i, colors[i])
            self.chip_sink.set_line_style(i, styles[i])
            self.chip_sink.set_line_marker(i, markers[i])
            self.chip_sink.set_line_alpha(i, alphas[i])

        self._chip_sink_win = sip.wrapinstance(self.chip_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._chip_sink_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.audio_sink = audio.sink(audio_rate, '', True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.costas, 0), (self.const_sink, 0))
        self.connect((self.costas, 0), (self.to_real, 0))
        self.connect((self.quad_demod, 0), (self.mpx_sink, 0))
        self.connect((self.quad_demod, 0), (self.rds_xlate, 0))
        self.connect((self.rds_agc, 0), (self.sym_sync, 0))
        self.connect((self.rds_decoder, 0), (self.group_sink, 0))
        self.connect((self.rds_xlate, 0), (self.rds_agc, 0))
        self.connect((self.sym_sync, 0), (self.costas, 0))
        self.connect((self.to_real, 0), (self.chip_sink, 0))
        self.connect((self.to_real, 0), (self.rds_decoder, 0))
        self.connect((self.usrp_source, 0), (self.xlating_fm, 0))
        self.connect((self.volume_control, 0), (self.audio_sink, 0))
        self.connect((self.wbfm_rcv, 0), (self.volume_control, 0))
        self.connect((self.xlating_fm, 0), (self.quad_demod, 0))
        self.connect((self.xlating_fm, 0), (self.wbfm_rcv, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab08_rds_decoder")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_mpx_rate(int(self.samp_rate/8))
        self.set_fm_taps(firdes.low_pass(1.0, self.samp_rate, 110e3, 30e3, window.WIN_HAMMING, 6.76))
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.usrp_source.set_bandwidth(self.samp_rate, 0)

    def get_mpx_rate(self):
        return self.mpx_rate

    def set_mpx_rate(self, mpx_rate):
        self.mpx_rate = mpx_rate
        self.set_rds_rate(int(self.mpx_rate/25))
        self.set_audio_rate(int(self.mpx_rate/5))
        self.set_rds_taps(firdes.low_pass(1.0, self.mpx_rate, 2400, 800, window.WIN_HAMMING, 6.76))
        self.quad_demod.set_gain((self.mpx_rate/(2*math.pi*75000)))
        self.mpx_sink.set_frequency_range(0, self.mpx_rate)

    def get_rds_rate(self):
        return self.rds_rate

    def set_rds_rate(self, rds_rate):
        self.rds_rate = rds_rate
        self.set_sps(self.rds_rate/self.chip_rate)

    def get_chip_rate(self):
        return self.chip_rate

    def set_chip_rate(self, chip_rate):
        self.chip_rate = chip_rate
        self.set_sps(self.rds_rate/self.chip_rate)
        self.chip_sink.set_samp_rate(self.chip_rate)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rds_mf_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sps, 1.0, 1.0, int(11*self.sps*self.nfilts)))
        self.sym_sync.set_sps(self.sps)

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_rds_mf_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sps, 1.0, 1.0, int(11*self.sps*self.nfilts)))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.volume_control.set_k(self.volume)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.usrp_source.set_gain(self.rf_gain, 0)

    def get_rds_taps(self):
        return self.rds_taps

    def set_rds_taps(self, rds_taps):
        self.rds_taps = rds_taps
        self.rds_xlate.set_taps(self.rds_taps)

    def get_rds_mf_taps(self):
        return self.rds_mf_taps

    def set_rds_mf_taps(self, rds_mf_taps):
        self.rds_mf_taps = rds_mf_taps

    def get_offset_freq(self):
        return self.offset_freq

    def set_offset_freq(self, offset_freq):
        self.offset_freq = offset_freq
        self.xlating_fm.set_center_freq(self.offset_freq)

    def get_loop_bw(self):
        return self.loop_bw

    def set_loop_bw(self, loop_bw):
        self.loop_bw = loop_bw
        self.sym_sync.set_loop_bandwidth(self.loop_bw)
        self.costas.set_loop_bandwidth(self.loop_bw)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.usrp_source.set_center_freq(self.freq, 0)

    def get_fm_taps(self):
        return self.fm_taps

    def set_fm_taps(self, fm_taps):
        self.fm_taps = fm_taps
        self.xlating_fm.set_taps(self.fm_taps)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate




def main(top_block_cls=lab08_rds_decoder, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
