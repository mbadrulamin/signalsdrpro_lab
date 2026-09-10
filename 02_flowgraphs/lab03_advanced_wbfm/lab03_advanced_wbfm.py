#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 03 - Advanced WBFM with AGC, Squelch, Volume (SignalSDR Pro)
# Author: SignalSDR Pro Lab
# Description: Production-quality FM receiver with filtering, AGC, squelch, volume
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
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
import sip



class lab03_advanced_wbfm(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 03 - Advanced WBFM with AGC, Squelch, Volume (SignalSDR Pro)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 03 - Advanced WBFM with AGC, Squelch, Volume (SignalSDR Pro)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab03_advanced_wbfm")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 1.0
        self.squelch_threshold = squelch_threshold = -50
        self.samp_rate = samp_rate = 2000000
        self.rf_gain = rf_gain = 40
        self.quad_rate = quad_rate = 384000
        self.freq = freq = 100.0e6
        self.audio_rate = audio_rate = 48000

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 5, 0.1, 1.0, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._rf_gain_range = qtgui.Range(0, 76, 1, 40, 200)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rf_gain_win)
        self._freq_range = qtgui.Range(87.5e6, 108e6, 100e3, 100.0e6, 200)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "FM Station (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self.wbfm_rcv = analog.wfm_rcv(
        	quad_rate=quad_rate,
        	audio_decimation=8,
        )
        self.waterfall_sink = qtgui.waterfall_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate, #bw
            "Waterfall", #name
            1, #number of inputs
            None # parent
        )
        self.waterfall_sink.set_update_time(0.10)
        self.waterfall_sink.enable_grid(False)
        self.waterfall_sink.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.waterfall_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.waterfall_sink.set_line_label(i, labels[i])
            self.waterfall_sink.set_color_map(i, colors[i])
            self.waterfall_sink.set_line_alpha(i, alphas[i])

        self.waterfall_sink.set_intensity_range(-140, 10)

        self._waterfall_sink_win = sip.wrapinstance(self.waterfall_sink.qwidget(), Qt.QWidget)

        self.top_layout.addWidget(self._waterfall_sink_win)
        self.volume_control = blocks.multiply_const_ff(volume)
        self.usrp_source = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.usrp_source.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.usrp_source.set_center_freq(freq, 0)
        self.usrp_source.set_antenna("TX/RX", 0)
        self.usrp_source.set_bandwidth(samp_rate, 0)
        self.usrp_source.set_gain(rf_gain, 0)
        self._squelch_threshold_range = qtgui.Range(-80, 0, 1, -50, 200)
        self._squelch_threshold_win = qtgui.RangeWidget(self._squelch_threshold_range, self.set_squelch_threshold, "Squelch (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._squelch_threshold_win)
        self.squelch = analog.pwr_squelch_cc(squelch_threshold, 0.01, 0, False)
        self.rational_resampler = filter.rational_resampler_ccc(
                interpolation=24,
                decimation=125,
                taps=[],
                fractional_bw=0)
        self.pre_filter = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                100000,
                20000,
                window.WIN_HAMMING,
                6.76))
        self.freq_sink = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate, #bw
            "Spectrum", #name
            1,
            None # parent
        )
        self.freq_sink.set_update_time(0.10)
        self.freq_sink.set_y_axis((-140), 10)
        self.freq_sink.set_y_label('Relative Gain', 'dB')
        self.freq_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink.enable_autoscale(False)
        self.freq_sink.enable_grid(False)
        self.freq_sink.set_fft_average(1.0)
        self.freq_sink.enable_axis_labels(True)
        self.freq_sink.enable_control_panel(False)
        self.freq_sink.set_fft_window_normalized(False)



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
                self.freq_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.freq_sink.set_line_label(i, labels[i])
            self.freq_sink.set_line_width(i, widths[i])
            self.freq_sink.set_line_color(i, colors[i])
            self.freq_sink.set_line_alpha(i, alphas[i])

        self._freq_sink_win = sip.wrapinstance(self.freq_sink.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._freq_sink_win)
        self.audio_sink = audio.sink(audio_rate, "", True)
        self.agc = analog.agc2_cc(0.01, 0.001, 0.5, 1.0, 65536)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.agc, 0), (self.squelch, 0))
        self.connect((self.pre_filter, 0), (self.freq_sink, 0))
        self.connect((self.pre_filter, 0), (self.rational_resampler, 0))
        self.connect((self.pre_filter, 0), (self.waterfall_sink, 0))
        self.connect((self.rational_resampler, 0), (self.agc, 0))
        self.connect((self.squelch, 0), (self.wbfm_rcv, 0))
        self.connect((self.usrp_source, 0), (self.pre_filter, 0))
        self.connect((self.volume_control, 0), (self.audio_sink, 0))
        self.connect((self.wbfm_rcv, 0), (self.volume_control, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab03_advanced_wbfm")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.volume_control.set_k(self.volume)

    def get_squelch_threshold(self):
        return self.squelch_threshold

    def set_squelch_threshold(self, squelch_threshold):
        self.squelch_threshold = squelch_threshold
        self.squelch.set_threshold(self.squelch_threshold)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.usrp_source.set_bandwidth(self.samp_rate, 0)
        self.pre_filter.set_taps(firdes.low_pass(1, self.samp_rate, 100000, 20000, window.WIN_HAMMING, 6.76))
        self.freq_sink.set_frequency_range(self.freq, self.samp_rate)
        self.waterfall_sink.set_frequency_range(self.freq, self.samp_rate)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.usrp_source.set_gain(self.rf_gain, 0)

    def get_quad_rate(self):
        return self.quad_rate

    def set_quad_rate(self, quad_rate):
        self.quad_rate = quad_rate

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.usrp_source.set_center_freq(self.freq, 0)
        self.freq_sink.set_frequency_range(self.freq, self.samp_rate)
        self.waterfall_sink.set_frequency_range(self.freq, self.samp_rate)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate




def main(top_block_cls=lab03_advanced_wbfm, options=None):

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
