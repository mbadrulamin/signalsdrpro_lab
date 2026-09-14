#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 11 - DVB-T Television Receiver
# Author: SignalSDR Pro Lab
# Description: Receive a DVB-T channel, measure its quality, and watch the picture
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import dtv
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import lab11_tv_receiver_mer as mer  # embedded python block
import lab11_tv_receiver_tv_out as tv_out  # embedded python block
import sip



class lab11_tv_receiver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 11 - DVB-T Television Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 11 - DVB-T Television Receiver")
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

        self.settings = Qt.QSettings("GNU Radio", "lab11_tv_receiver")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.fft_len = fft_len = 8192
        self.channel = channel = 31
        self.ts_file = ts_file = '/tmp/lab11_rx.ts'
        self.samp_rate = samp_rate = 64e6 / 7
        self.rx_gain = rx_gain = 45
        self.play_video = play_video = True
        self.payload = payload = 6048
        self.occupied = occupied = 6817
        self.cp_len = cp_len = fft_len // 32
        self.center_freq = center_freq = 474e6 + 8e6 * (channel - 21)

        ##################################################
        # Blocks
        ##################################################

        self._rx_gain_range = qtgui.Range(0, 76, 1, 45, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "RX gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.waterfall = qtgui.waterfall_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "Waterfall", #name
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

        self.waterfall.set_intensity_range(-110, -30)

        self._waterfall_win = sip.wrapinstance(self.waterfall.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._waterfall_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.viterbi = dtv.dvbt_viterbi_decoder(dtv.MOD_16QAM, dtv.NH, dtv.C2_3, 768)
        self.v2s = blocks.vector_to_stream(gr.sizeof_char*1, payload)
        self.usrp = uhd.usrp_source(
            ",".join(("num_recv_frames=512", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.usrp.set_samp_rate(samp_rate)
        self.usrp.set_time_unknown_pps(uhd.time_spec(0))

        self.usrp.set_center_freq(center_freq, 0)
        self.usrp.set_antenna('RX2', 0)
        self.usrp.set_bandwidth(samp_rate, 0)
        self.usrp.set_gain(rx_gain, 0)
        self.tv_out = tv_out.blk(play=play_video, ts_file=ts_file, report_every=20000)
        self.symdeint = dtv.dvbt_symbol_inner_interleaver(6048, dtv.T8k, 0)
        self.spectrum = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "Channel spectrum", #name
            1,
            None # parent
        )
        self.spectrum.set_update_time(0.10)
        self.spectrum.set_y_axis((-110), (-20))
        self.spectrum.set_y_label('Relative Gain', 'dB')
        self.spectrum.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.spectrum.enable_autoscale(False)
        self.spectrum.enable_grid(False)
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
        self.top_grid_layout.addWidget(self._spectrum_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rs = dtv.dvbt_reed_solomon_dec(2, 8, 0x11d, 255, 239, 8, 51, 8)
        self.pwr_dec = blocks.keep_one_in_n(gr.sizeof_float*1, 4096)
        self.pwr_db = blocks.nlog10_ff(10, 1, 0)
        self.pwr_avg = filter.single_pole_iir_filter_ff(0.02, 1)
        self.pwr = blocks.complex_to_mag_squared(1)
        self.pilots = dtv.dvbt_demod_reference_signals(
            gr.sizeof_gr_complex,
            8192,
            6048,
            dtv.MOD_16QAM,
            dtv.NH,
            dtv.C2_3,
            dtv.C2_3,
            dtv.GI_1_32,
            dtv.T8k,
            1,
            0)
        self.ofdm_fft = fft.fft_vcc(fft_len, True, window.rectangular(fft_len), True, 1)
        self.mer_display = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.mer_display.set_update_time(0.10)
        self.mer_display.set_title("Signal quality")

        labels = ["MER", '', '', '', '',
            '', '', '', '', '']
        units = ["dB", '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.mer_display.set_min(i, 0)
            self.mer_display.set_max(i, 40)
            self.mer_display.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.mer_display.set_label(i, "Data {0}".format(i))
            else:
                self.mer_display.set_label(i, labels[i])
            self.mer_display.set_unit(i, units[i])
            self.mer_display.set_factor(i, factor[i])

        self.mer_display.enable_autoscale(False)
        self._mer_display_win = sip.wrapinstance(self.mer_display.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._mer_display_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mer = mer.blk(bits_per_symbol=4, decim=4096)
        self.level_display = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.level_display.set_update_time(0.10)
        self.level_display.set_title("Level")

        labels = ["Level", '', '', '', '',
            '', '', '', '', '']
        units = ["dBFS", '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.level_display.set_min(i, -100)
            self.level_display.set_max(i, 0)
            self.level_display.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.level_display.set_label(i, "Data {0}".format(i))
            else:
                self.level_display.set_label(i, labels[i])
            self.level_display.set_unit(i, units[i])
            self.level_display.set_factor(i, factor[i])

        self.level_display.enable_autoscale(False)
        self._level_display_win = sip.wrapinstance(self.level_display.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._level_display_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.descramble = dtv.dvbt_energy_descramble(8)
        self.demap = dtv.dvbt_demap(6048, dtv.MOD_16QAM, dtv.NH, dtv.T8k, 1)
        self.convdeint = dtv.dvbt_convolutional_deinterleaver(136, 12, 17)
        self.constellation = qtgui.const_sink_c(
            2048, #size
            "Constellation", #name
            1, #number of inputs
            None # parent
        )
        self.constellation.set_update_time(0.10)
        self.constellation.set_y_axis((-2), 2)
        self.constellation.set_x_axis((-2), 2)
        self.constellation.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.constellation.enable_autoscale(False)
        self.constellation.enable_grid(False)
        self.constellation.enable_axis_labels(True)


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
                self.constellation.set_line_label(i, "Data {0}".format(i))
            else:
                self.constellation.set_line_label(i, labels[i])
            self.constellation.set_line_width(i, widths[i])
            self.constellation.set_line_color(i, colors[i])
            self.constellation.set_line_style(i, styles[i])
            self.constellation.set_line_marker(i, markers[i])
            self.constellation.set_line_alpha(i, alphas[i])

        self._constellation_win = sip.wrapinstance(self.constellation.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._constellation_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._channel_range = qtgui.Range(21, 48, 1, 31, 200)
        self._channel_win = qtgui.RangeWidget(self._channel_range, self.set_channel, "UHF channel", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._channel_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.cells = blocks.vector_to_stream(gr.sizeof_gr_complex*1, payload)
        self.bitdeint = dtv.dvbt_bit_inner_deinterleaver(6048, dtv.MOD_16QAM, dtv.NH, dtv.T8k)
        self.acq = dtv.dvbt_ofdm_sym_acquisition(1, fft_len, occupied, cp_len, 10)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.acq, 0), (self.ofdm_fft, 0))
        self.connect((self.bitdeint, 0), (self.v2s, 0))
        self.connect((self.cells, 0), (self.constellation, 0))
        self.connect((self.cells, 0), (self.mer, 0))
        self.connect((self.convdeint, 0), (self.rs, 0))
        self.connect((self.demap, 0), (self.symdeint, 0))
        self.connect((self.descramble, 0), (self.tv_out, 0))
        self.connect((self.mer, 0), (self.mer_display, 0))
        self.connect((self.ofdm_fft, 0), (self.pilots, 0))
        self.connect((self.pilots, 0), (self.cells, 0))
        self.connect((self.pilots, 0), (self.demap, 0))
        self.connect((self.pwr, 0), (self.pwr_dec, 0))
        self.connect((self.pwr_avg, 0), (self.pwr_db, 0))
        self.connect((self.pwr_db, 0), (self.level_display, 0))
        self.connect((self.pwr_dec, 0), (self.pwr_avg, 0))
        self.connect((self.rs, 0), (self.descramble, 0))
        self.connect((self.symdeint, 0), (self.bitdeint, 0))
        self.connect((self.usrp, 0), (self.acq, 0))
        self.connect((self.usrp, 0), (self.pwr, 0))
        self.connect((self.usrp, 0), (self.spectrum, 0))
        self.connect((self.usrp, 0), (self.waterfall, 0))
        self.connect((self.v2s, 0), (self.viterbi, 0))
        self.connect((self.viterbi, 0), (self.convdeint, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab11_tv_receiver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_cp_len(self.fft_len // 32)

    def get_channel(self):
        return self.channel

    def set_channel(self, channel):
        self.channel = channel
        self.set_center_freq(474e6 + 8e6 * (self.channel - 21))

    def get_ts_file(self):
        return self.ts_file

    def set_ts_file(self, ts_file):
        self.ts_file = ts_file

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.usrp.set_samp_rate(self.samp_rate)
        self.usrp.set_bandwidth(self.samp_rate, 0)
        self.spectrum.set_frequency_range(self.center_freq, self.samp_rate)
        self.waterfall.set_frequency_range(self.center_freq, self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.usrp.set_gain(self.rx_gain, 0)

    def get_play_video(self):
        return self.play_video

    def set_play_video(self, play_video):
        self.play_video = play_video

    def get_payload(self):
        return self.payload

    def set_payload(self, payload):
        self.payload = payload

    def get_occupied(self):
        return self.occupied

    def set_occupied(self, occupied):
        self.occupied = occupied

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.usrp.set_center_freq(self.center_freq, 0)
        self.spectrum.set_frequency_range(self.center_freq, self.samp_rate)
        self.waterfall.set_frequency_range(self.center_freq, self.samp_rate)




def main(top_block_cls=lab11_tv_receiver, options=None):

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
