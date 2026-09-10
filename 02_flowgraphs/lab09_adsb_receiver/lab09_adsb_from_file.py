#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 09b - ADS-B Decoder from a Recorded IQ File (no hardware)
# Author: SignalSDR Pro Lab
# Description: The same ADS-B decoder fed from disk, for development and verification
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import lab09_adsb_from_file_adsb_decoder as adsb_decoder  # embedded python block
import sip



class lab09_adsb_from_file(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 09b - ADS-B Decoder from a Recorded IQ File (no hardware)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 09b - ADS-B Decoder from a Recorded IQ File (no hardware)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab09_adsb_from_file")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.threshold = threshold = 0.25
        self.samp_rate = samp_rate = 2000000
        self.rec_file = rec_file = '/tmp/adsb_test_2Msps_fc32.iq'
        self.pulse_ratio = pulse_ratio = 3.0

        ##################################################
        # Blocks
        ##################################################

        self._threshold_range = qtgui.Range(0.01, 1.0, 0.01, 0.25, 350)
        self._threshold_win = qtgui.RangeWidget(self._threshold_range, self.set_threshold, "Preamble threshold", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._threshold_win)
        self._pulse_ratio_range = qtgui.Range(1.5, 10.0, 0.1, 3.0, 350)
        self._pulse_ratio_win = qtgui.RangeWidget(self._pulse_ratio_range, self.set_pulse_ratio, "Pulse/gap ratio", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._pulse_ratio_win)
        self.to_mag = blocks.complex_to_mag(1)
        self.throttle = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.spectrum = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            1090e6, #fc
            samp_rate, #bw
            '1090 MHz spectrum', #name
            1,
            None # parent
        )
        self.spectrum.set_update_time(0.10)
        self.spectrum.set_y_axis((-120), 0)
        self.spectrum.set_y_label('Relative Gain', 'dB')
        self.spectrum.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spectrum.enable_autoscale(False)
        self.spectrum.enable_grid(True)
        self.spectrum.set_fft_average(0.1)
        self.spectrum.enable_axis_labels(True)
        self.spectrum.enable_control_panel(False)
        self.spectrum.set_fft_window_normalized(False)



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
                self.spectrum.set_line_label(i, "Data {0}".format(i))
            else:
                self.spectrum.set_line_label(i, labels[i])
            self.spectrum.set_line_width(i, widths[i])
            self.spectrum.set_line_color(i, colors[i])
            self.spectrum.set_line_alpha(i, alphas[i])

        self._spectrum_win = sip.wrapinstance(self.spectrum.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._spectrum_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.pulse_sink = qtgui.time_sink_f(
            512, #size
            samp_rate, #samp_rate
            'Signal magnitude - look for 120 us bursts', #name
            1, #number of inputs
            None # parent
        )
        self.pulse_sink.set_update_time(0.05)
        self.pulse_sink.set_y_axis(0, 1.0)

        self.pulse_sink.set_y_label('Magnitude', "")

        self.pulse_sink.enable_tags(True)
        self.pulse_sink.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.2, 0, 0, "")
        self.pulse_sink.enable_autoscale(True)
        self.pulse_sink.enable_grid(True)
        self.pulse_sink.enable_axis_labels(True)
        self.pulse_sink.enable_control_panel(False)
        self.pulse_sink.enable_stem_plot(False)


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
                self.pulse_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.pulse_sink.set_line_label(i, labels[i])
            self.pulse_sink.set_line_width(i, widths[i])
            self.pulse_sink.set_line_color(i, colors[i])
            self.pulse_sink.set_line_style(i, styles[i])
            self.pulse_sink.set_line_marker(i, markers[i])
            self.pulse_sink.set_line_alpha(i, alphas[i])

        self._pulse_sink_win = sip.wrapinstance(self.pulse_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._pulse_sink_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.frame_sink = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.frame_sink.set_update_time(0.25)
        self.frame_sink.set_title('CRC-valid frames')

        labels = ['frames', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.frame_sink.set_min(i, 0)
            self.frame_sink.set_max(i, 10000)
            self.frame_sink.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.frame_sink.set_label(i, "Data {0}".format(i))
            else:
                self.frame_sink.set_label(i, labels[i])
            self.frame_sink.set_unit(i, units[i])
            self.frame_sink.set_factor(i, factor[i])

        self.frame_sink.enable_autoscale(True)
        self._frame_sink_win = sip.wrapinstance(self.frame_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._frame_sink_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.file_source = blocks.file_source(gr.sizeof_gr_complex*1, rec_file, True, 0, 0)
        self.file_source.set_begin_tag(pmt.PMT_NIL)
        self.adsb_decoder = adsb_decoder.blk(threshold=threshold, ratio=pulse_ratio, verbose=True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.adsb_decoder, 0), (self.frame_sink, 0))
        self.connect((self.file_source, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.spectrum, 0))
        self.connect((self.throttle, 0), (self.to_mag, 0))
        self.connect((self.to_mag, 0), (self.adsb_decoder, 0))
        self.connect((self.to_mag, 0), (self.pulse_sink, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab09_adsb_from_file")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.adsb_decoder.threshold = self.threshold

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.throttle.set_sample_rate(self.samp_rate)
        self.pulse_sink.set_samp_rate(self.samp_rate)
        self.spectrum.set_frequency_range(1090e6, self.samp_rate)

    def get_rec_file(self):
        return self.rec_file

    def set_rec_file(self, rec_file):
        self.rec_file = rec_file
        self.file_source.open(self.rec_file, True)

    def get_pulse_ratio(self):
        return self.pulse_ratio

    def set_pulse_ratio(self, pulse_ratio):
        self.pulse_ratio = pulse_ratio
        self.adsb_decoder.ratio = self.pulse_ratio




def main(top_block_cls=lab09_adsb_from_file, options=None):

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
