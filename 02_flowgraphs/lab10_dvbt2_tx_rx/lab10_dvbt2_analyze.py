#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 10c - DVB-T2 Receiver-Side Analyzer
# Author: SignalSDR Pro Lab
# Description: Measure a DVB-T2 signal: spectrum, cyclic-prefix timing, amplitude statistics
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
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
import sip



class lab10_dvbt2_analyze(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 10c - DVB-T2 Receiver-Side Analyzer", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 10c - DVB-T2 Receiver-Side Analyzer")
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

        self.settings = Qt.QSettings("GNU Radio", "lab10_dvbt2_analyze")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.fft_len = fft_len = 1024
        self.samp_rate = samp_rate = (8000000.0 * 8) / 7
        self.iq_file = iq_file = '/tmp/dvbt2_signal_9M14_fc32.iq'
        self.cp_len = cp_len = fft_len // 8
        self.center_freq = center_freq = 474e6

        ##################################################
        # Blocks
        ##################################################

        self.waterfall = qtgui.waterfall_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            'Waterfall', #name
            1, #number of inputs
            None # parent
        )
        self.waterfall.set_update_time(0.10)
        self.waterfall.enable_grid(False)
        self.waterfall.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.waterfall.set_line_label(i, "Data {0}".format(i))
            else:
                self.waterfall.set_line_label(i, labels[i])
            self.waterfall.set_color_map(i, colors[i])
            self.waterfall.set_line_alpha(i, alphas[i])

        self.waterfall.set_intensity_range(-140, 10)

        self._waterfall_win = sip.wrapinstance(self.waterfall.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._waterfall_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.spectrum = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            'DVB-T2 spectrum - a flat-topped 7.6 MHz block, not a hump', #name
            1,
            None # parent
        )
        self.spectrum.set_update_time(0.10)
        self.spectrum.set_y_axis((-120), 0)
        self.spectrum.set_y_label('Relative Gain', 'dB')
        self.spectrum.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spectrum.enable_autoscale(False)
        self.spectrum.enable_grid(True)
        self.spectrum.set_fft_average(0.2)
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
        self.top_grid_layout.addWidget(self._spectrum_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mag = blocks.complex_to_mag(1)
        self.integrate = blocks.moving_average_cc(cp_len, 1.0/cp_len, 4096, 1)
        self.hist = qtgui.histogram_sink_f(
            2048,
            100,
            0,
            1,
            'Amplitude distribution - Rayleigh, because OFDM is Gaussian',
            1,
            None # parent
        )

        self.hist.set_update_time(0.10)
        self.hist.enable_autoscale(True)
        self.hist.enable_accumulate(False)
        self.hist.enable_grid(True)
        self.hist.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers= [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.hist.set_line_label(i, "Data {0}".format(i))
            else:
                self.hist.set_line_label(i, labels[i])
            self.hist.set_line_width(i, widths[i])
            self.hist.set_line_color(i, colors[i])
            self.hist.set_line_style(i, styles[i])
            self.hist.set_line_marker(i, markers[i])
            self.hist.set_line_alpha(i, alphas[i])

        self._hist_win = sip.wrapinstance(self.hist.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._hist_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.file_source = blocks.file_source(gr.sizeof_gr_complex*1, iq_file, True, 0, 0)
        self.file_source.set_begin_tag(pmt.PMT_NIL)
        self.delay_fft = blocks.delay(gr.sizeof_gr_complex*1, fft_len)
        self.correlate = blocks.multiply_vcc(1)
        self.corr_plot = qtgui.time_sink_f(
            4096, #size
            samp_rate, #samp_rate
            'Cyclic-prefix correlation - one peak per OFDM symbol (every 1152 samples)', #name
            1, #number of inputs
            None # parent
        )
        self.corr_plot.set_update_time(0.10)
        self.corr_plot.set_y_axis(0, 0.2)

        self.corr_plot.set_y_label('Correlation', "")

        self.corr_plot.enable_tags(True)
        self.corr_plot.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.corr_plot.enable_autoscale(True)
        self.corr_plot.enable_grid(True)
        self.corr_plot.enable_axis_labels(True)
        self.corr_plot.enable_control_panel(False)
        self.corr_plot.enable_stem_plot(False)


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
                self.corr_plot.set_line_label(i, "Data {0}".format(i))
            else:
                self.corr_plot.set_line_label(i, labels[i])
            self.corr_plot.set_line_width(i, widths[i])
            self.corr_plot.set_line_color(i, colors[i])
            self.corr_plot.set_line_style(i, styles[i])
            self.corr_plot.set_line_marker(i, markers[i])
            self.corr_plot.set_line_alpha(i, alphas[i])

        self._corr_plot_win = sip.wrapinstance(self.corr_plot.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._corr_plot_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.corr_mag = blocks.complex_to_mag(1)
        self.conj = blocks.conjugate_cc()


        ##################################################
        # Connections
        ##################################################
        self.connect((self.conj, 0), (self.correlate, 1))
        self.connect((self.corr_mag, 0), (self.corr_plot, 0))
        self.connect((self.correlate, 0), (self.integrate, 0))
        self.connect((self.delay_fft, 0), (self.conj, 0))
        self.connect((self.file_source, 0), (self.throttle, 0))
        self.connect((self.integrate, 0), (self.corr_mag, 0))
        self.connect((self.mag, 0), (self.hist, 0))
        self.connect((self.throttle, 0), (self.correlate, 0))
        self.connect((self.throttle, 0), (self.delay_fft, 0))
        self.connect((self.throttle, 0), (self.mag, 0))
        self.connect((self.throttle, 0), (self.spectrum, 0))
        self.connect((self.throttle, 0), (self.waterfall, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab10_dvbt2_analyze")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_cp_len(self.fft_len // 8)
        self.delay_fft.set_dly(int(self.fft_len))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.throttle.set_sample_rate(self.samp_rate)
        self.spectrum.set_frequency_range(self.center_freq, self.samp_rate)
        self.waterfall.set_frequency_range(self.center_freq, self.samp_rate)
        self.corr_plot.set_samp_rate(self.samp_rate)

    def get_iq_file(self):
        return self.iq_file

    def set_iq_file(self, iq_file):
        self.iq_file = iq_file
        self.file_source.open(self.iq_file, True)

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len
        self.integrate.set_length_and_scale(self.cp_len, 1.0/self.cp_len)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.spectrum.set_frequency_range(self.center_freq, self.samp_rate)
        self.waterfall.set_frequency_range(self.center_freq, self.samp_rate)




def main(top_block_cls=lab10_dvbt2_analyze, options=None):

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
