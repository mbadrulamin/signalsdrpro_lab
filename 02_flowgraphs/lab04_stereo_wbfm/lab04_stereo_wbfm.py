#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 04 - Stereo WBFM with Full MPX Decoding (SignalSDR Pro)
# Author: SignalSDR Pro Lab
# Description: Manual stereo FM decoding: pilot extraction, PLL, L+R/L-R matrix
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
import math
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



class lab04_stereo_wbfm(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 04 - Stereo WBFM with Full MPX Decoding (SignalSDR Pro)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 04 - Stereo WBFM with Full MPX Decoding (SignalSDR Pro)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab04_stereo_wbfm")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.deemph_tau = deemph_tau = 50e-6
        self.audio_rate = audio_rate = 48000
        self.volume = volume = 1.0
        self.samp_rate = samp_rate = 2000000
        self.rf_gain = rf_gain = 40
        self.mpx_rate = mpx_rate = 240000
        self.freq = freq = 100.0e6
        self.deemph_alpha = deemph_alpha = 1 - __import__("math").exp(-1/(audio_rate * deemph_tau))

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 3, 0.1, 1.0, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._rf_gain_range = qtgui.Range(0, 76, 1, 40, 200)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rf_gain_win)
        self._freq_range = qtgui.Range(87.5e6, 108e6, 100e3, 100.0e6, 200)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "FM Station (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
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
        self.usrp_source.set_gain(rf_gain, 0)
        self.subcarrier_to_real = blocks.complex_to_real(1)
        self.subcarrier_doubler = blocks.multiply_vcc(1)
        self.spectrum_sink = qtgui.freq_sink_f(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            mpx_rate, #bw
            "MPX Spectrum", #name
            1,
            None # parent
        )
        self.spectrum_sink.set_update_time(0.10)
        self.spectrum_sink.set_y_axis((-100), 10)
        self.spectrum_sink.set_y_label('Relative Gain', 'dB')
        self.spectrum_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spectrum_sink.enable_autoscale(False)
        self.spectrum_sink.enable_grid(False)
        self.spectrum_sink.set_fft_average(1.0)
        self.spectrum_sink.enable_axis_labels(True)
        self.spectrum_sink.enable_control_panel(False)
        self.spectrum_sink.set_fft_window_normalized(False)


        self.spectrum_sink.set_plot_pos_half(not True)

        labels = ["MPX (L+R @ 0-15k, pilot @ 19k, L-R @ 23-53k)", '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.spectrum_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.spectrum_sink.set_line_label(i, labels[i])
            self.spectrum_sink.set_line_width(i, widths[i])
            self.spectrum_sink.set_line_color(i, colors[i])
            self.spectrum_sink.set_line_alpha(i, alphas[i])

        self._spectrum_sink_win = sip.wrapinstance(self.spectrum_sink.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._spectrum_sink_win)
        self.scale_right = blocks.multiply_const_ff((volume * 0.5))
        self.scale_lr_minus = blocks.multiply_const_ff(2.0)
        self.scale_left = blocks.multiply_const_ff((volume * 0.5))
        self.right_subtract = blocks.sub_ff(1)
        self.rf_lowpass = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                100000,
                20000,
                window.WIN_HAMMING,
                6.76))
        self.resampler = filter.rational_resampler_ccc(
                interpolation=12,
                decimation=100,
                taps=[],
                fractional_bw=0)
        self.quad_demod = analog.quadrature_demod_cf((mpx_rate / (2 * 3.141592653589793 * 75000)))
        self.pilot_pll = analog.pll_refout_cc(0.05, (2 * 3.141592653589793 * 19500 / mpx_rate), (2 * 3.141592653589793 * 18500 / mpx_rate))
        self.pilot_float_to_complex = blocks.float_to_complex(1)
        self.pilot_bandpass = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                mpx_rate,
                18500,
                19500,
                500,
                window.WIN_HAMMING,
                6.76))
        self.lrmix = blocks.multiply_vff(1)
        self.lr_plus_lowpass = filter.fir_filter_fff(
            5,
            firdes.low_pass(
                1,
                mpx_rate,
                15000,
                1500,
                window.WIN_HAMMING,
                6.76))
        self.lr_minus_lowpass = filter.fir_filter_fff(
            5,
            firdes.low_pass(
                1,
                mpx_rate,
                15000,
                1500,
                window.WIN_HAMMING,
                6.76))
        self.left_add = blocks.add_vff(1)
        self.l_plus_r_deemph = filter.single_pole_iir_filter_ff(deemph_alpha, 1)
        self.l_minus_r_deemph = filter.single_pole_iir_filter_ff(deemph_alpha, 1)
        self.audio_sink = audio.sink(audio_rate, "", True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.l_minus_r_deemph, 0), (self.left_add, 1))
        self.connect((self.l_minus_r_deemph, 0), (self.right_subtract, 1))
        self.connect((self.l_plus_r_deemph, 0), (self.left_add, 0))
        self.connect((self.l_plus_r_deemph, 0), (self.right_subtract, 0))
        self.connect((self.left_add, 0), (self.scale_left, 0))
        self.connect((self.lr_minus_lowpass, 0), (self.scale_lr_minus, 0))
        self.connect((self.lr_plus_lowpass, 0), (self.l_plus_r_deemph, 0))
        self.connect((self.lrmix, 0), (self.lr_minus_lowpass, 0))
        self.connect((self.pilot_bandpass, 0), (self.pilot_float_to_complex, 0))
        self.connect((self.pilot_float_to_complex, 0), (self.pilot_pll, 0))
        self.connect((self.pilot_pll, 0), (self.subcarrier_doubler, 1))
        self.connect((self.pilot_pll, 0), (self.subcarrier_doubler, 0))
        self.connect((self.quad_demod, 0), (self.lr_plus_lowpass, 0))
        self.connect((self.quad_demod, 0), (self.lrmix, 0))
        self.connect((self.quad_demod, 0), (self.pilot_bandpass, 0))
        self.connect((self.quad_demod, 0), (self.spectrum_sink, 0))
        self.connect((self.resampler, 0), (self.quad_demod, 0))
        self.connect((self.rf_lowpass, 0), (self.resampler, 0))
        self.connect((self.right_subtract, 0), (self.scale_right, 0))
        self.connect((self.scale_left, 0), (self.audio_sink, 0))
        self.connect((self.scale_lr_minus, 0), (self.l_minus_r_deemph, 0))
        self.connect((self.scale_right, 0), (self.audio_sink, 1))
        self.connect((self.subcarrier_doubler, 0), (self.subcarrier_to_real, 0))
        self.connect((self.subcarrier_to_real, 0), (self.lrmix, 1))
        self.connect((self.usrp_source, 0), (self.rf_lowpass, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab04_stereo_wbfm")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_deemph_tau(self):
        return self.deemph_tau

    def set_deemph_tau(self, deemph_tau):
        self.deemph_tau = deemph_tau
        self.set_deemph_alpha(1 - __import__("math").exp(-1/(self.audio_rate * self.deemph_tau)))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.set_deemph_alpha(1 - __import__("math").exp(-1/(self.audio_rate * self.deemph_tau)))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.scale_left.set_k((self.volume * 0.5))
        self.scale_right.set_k((self.volume * 0.5))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.rf_lowpass.set_taps(firdes.low_pass(1, self.samp_rate, 100000, 20000, window.WIN_HAMMING, 6.76))

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.usrp_source.set_gain(self.rf_gain, 0)

    def get_mpx_rate(self):
        return self.mpx_rate

    def set_mpx_rate(self, mpx_rate):
        self.mpx_rate = mpx_rate
        self.quad_demod.set_gain((self.mpx_rate / (2 * 3.141592653589793 * 75000)))
        self.spectrum_sink.set_frequency_range(0, self.mpx_rate)
        self.lr_plus_lowpass.set_taps(firdes.low_pass(1, self.mpx_rate, 15000, 1500, window.WIN_HAMMING, 6.76))
        self.pilot_bandpass.set_taps(firdes.band_pass(1, self.mpx_rate, 18500, 19500, 500, window.WIN_HAMMING, 6.76))
        self.pilot_pll.set_max_freq((2 * 3.141592653589793 * 19500 / self.mpx_rate))
        self.pilot_pll.set_min_freq((2 * 3.141592653589793 * 18500 / self.mpx_rate))
        self.lr_minus_lowpass.set_taps(firdes.low_pass(1, self.mpx_rate, 15000, 1500, window.WIN_HAMMING, 6.76))

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.usrp_source.set_center_freq(self.freq, 0)

    def get_deemph_alpha(self):
        return self.deemph_alpha

    def set_deemph_alpha(self, deemph_alpha):
        self.deemph_alpha = deemph_alpha
        self.l_plus_r_deemph.set_taps(self.deemph_alpha)
        self.l_minus_r_deemph.set_taps(self.deemph_alpha)




def main(top_block_cls=lab04_stereo_wbfm, options=None):

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
