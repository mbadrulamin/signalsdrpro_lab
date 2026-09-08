#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 02 - Enhanced WBFM with Visualization (SignalSDR Pro)
# Author: SignalSDR Pro Lab
# Description: FM receiver with spectrum, waterfall, time displays and 48 kHz audio
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
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



class lab02_enhanced_wbfm(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 02 - Enhanced WBFM with Visualization (SignalSDR Pro)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 02 - Enhanced WBFM with Visualization (SignalSDR Pro)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab02_enhanced_wbfm")

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
        self.quad_rate = quad_rate = 384000
        self.gain = gain = 40
        self.freq = freq = 100.0e6
        self.audio_rate = audio_rate = 48000

        ##################################################
        # Blocks
        ##################################################

        self._gain_range = qtgui.Range(0, 76, 1, 40, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "RF Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
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
        self.usrp_source.set_gain(gain, 0)
        self.time_sink = qtgui.time_sink_c(
            1024, #size
            samp_rate, #samp_rate
            "IQ Time Domain", #name
            1, #number of inputs
            None # parent
        )
        self.time_sink.set_update_time(0.10)
        self.time_sink.set_y_axis(-1, 1)

        self.time_sink.set_y_label('Amplitude', "")

        self.time_sink.enable_tags(True)
        self.time_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.time_sink.enable_autoscale(True)
        self.time_sink.enable_grid(False)
        self.time_sink.enable_axis_labels(True)
        self.time_sink.enable_control_panel(False)
        self.time_sink.enable_stem_plot(False)


        labels = ["I (real)", "Q (imag)", 'Signal 3', 'Signal 4', 'Signal 5',
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


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.time_sink.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.time_sink.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.time_sink.set_line_label(i, labels[i])
            self.time_sink.set_line_width(i, widths[i])
            self.time_sink.set_line_color(i, colors[i])
            self.time_sink.set_line_style(i, styles[i])
            self.time_sink.set_line_marker(i, markers[i])
            self.time_sink.set_line_alpha(i, alphas[i])

        self._time_sink_win = sip.wrapinstance(self.time_sink.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._time_sink_win)
        self.rational_resampler = filter.rational_resampler_ccc(
                interpolation=24,
                decimation=125,
                taps=[],
                fractional_bw=0)
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



        labels = ["Raw IQ", '', '', '', '',
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


        ##################################################
        # Connections
        ##################################################
        self.connect((self.rational_resampler, 0), (self.wbfm_rcv, 0))
        self.connect((self.usrp_source, 0), (self.freq_sink, 0))
        self.connect((self.usrp_source, 0), (self.rational_resampler, 0))
        self.connect((self.usrp_source, 0), (self.time_sink, 0))
        self.connect((self.usrp_source, 0), (self.waterfall_sink, 0))
        self.connect((self.wbfm_rcv, 0), (self.audio_sink, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab02_enhanced_wbfm")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.freq_sink.set_frequency_range(self.freq, self.samp_rate)
        self.waterfall_sink.set_frequency_range(self.freq, self.samp_rate)
        self.time_sink.set_samp_rate(self.samp_rate)

    def get_quad_rate(self):
        return self.quad_rate

    def set_quad_rate(self, quad_rate):
        self.quad_rate = quad_rate

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.usrp_source.set_gain(self.gain, 0)

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




def main(top_block_cls=lab02_enhanced_wbfm, options=None):

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
