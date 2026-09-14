#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 12 - Full-Duplex DVB-T Video Link (TRANSMITS - contained environment only)
# Author: SignalSDR Pro Lab
# Description: Transmit a video file as DVB-T and receive it back on the same radio, simultaneously
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
import pmt
from gnuradio import digital
from gnuradio import dtv
from gnuradio import fft
from gnuradio.fft import window
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
import lab12_fullduplex_tv_rx_mer as rx_mer  # embedded python block
import lab12_fullduplex_tv_tv_out as tv_out  # embedded python block
import sip



class lab12_fullduplex_tv(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 12 - Full-Duplex DVB-T Video Link (TRANSMITS - contained environment only)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 12 - Full-Duplex DVB-T Video Link (TRANSMITS - contained environment only)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab12_fullduplex_tv")

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
        self.tx_gain = tx_gain = 0
        self.tx_amplitude = tx_amplitude = 0
        self.ts_out = ts_out = '/tmp/lab12_rx.ts'
        self.ts_in = ts_in = '/tmp/bintang.ts'
        self.samp_rate = samp_rate = 64e6 / 7
        self.rx_gain = rx_gain = 20
        self.play_video = play_video = True
        self.payload = payload = 6048
        self.occupied = occupied = 6817
        self.cp_len = cp_len = fft_len // 32
        self.center_freq = center_freq = 474e6 + 8e6 * (channel - 21)

        ##################################################
        # Blocks
        ##################################################

        self._tx_gain_range = qtgui.Range(0, 89, 1, 0, 200)
        self._tx_gain_win = qtgui.RangeWidget(self._tx_gain_range, self.set_tx_gain, "TX gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_gain_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = qtgui.Range(0, 76, 1, 20, 200)
        self._rx_gain_win = qtgui.RangeWidget(self._rx_gain_range, self.set_rx_gain, "RX gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 3, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.usrp_tx = uhd.usrp_sink(
            ",".join(("send_frame_size=8192,num_send_frames=256", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.usrp_tx.set_samp_rate(samp_rate)
        self.usrp_tx.set_time_unknown_pps(uhd.time_spec(0))

        self.usrp_tx.set_center_freq(center_freq, 0)
        self.usrp_tx.set_antenna('TX/RX', 0)
        self.usrp_tx.set_bandwidth(samp_rate, 0)
        self.usrp_tx.set_gain(tx_gain, 0)
        self.usrp_rx = uhd.usrp_source(
            ",".join(("num_recv_frames=512", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.usrp_rx.set_samp_rate(samp_rate)
        self.usrp_rx.set_time_unknown_pps(uhd.time_spec(0))

        self.usrp_rx.set_center_freq(center_freq, 0)
        self.usrp_rx.set_antenna('RX2', 0)
        self.usrp_rx.set_bandwidth(samp_rate, 0)
        self.usrp_rx.set_gain(rx_gain, 0)
        self.tx_spectrum = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "Transmitted spectrum", #name
            1,
            None # parent
        )
        self.tx_spectrum.set_update_time(0.10)
        self.tx_spectrum.set_y_axis((-120), 0)
        self.tx_spectrum.set_y_label('Relative Gain', 'dB')
        self.tx_spectrum.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.tx_spectrum.enable_autoscale(False)
        self.tx_spectrum.enable_grid(False)
        self.tx_spectrum.set_fft_average(0.2)
        self.tx_spectrum.enable_axis_labels(True)
        self.tx_spectrum.enable_control_panel(False)
        self.tx_spectrum.set_fft_window_normalized(False)



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
                self.tx_spectrum.set_line_label(i, "Data {0}".format(i))
            else:
                self.tx_spectrum.set_line_label(i, labels[i])
            self.tx_spectrum.set_line_width(i, widths[i])
            self.tx_spectrum.set_line_color(i, colors[i])
            self.tx_spectrum.set_line_alpha(i, alphas[i])

        self._tx_spectrum_win = sip.wrapinstance(self.tx_spectrum.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._tx_spectrum_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.tx_skip = blocks.skiphead(gr.sizeof_gr_complex*1, (fft_len + cp_len))
        self.tx_si = dtv.dvbt_symbol_inner_interleaver(6048, dtv.T8k, 1)
        self.tx_rs = dtv.dvbt_reed_solomon_enc(2, 8, 0x11d, 255, 239, 8, 51, 8)
        self.tx_pilots = dtv.dvbt_reference_signals(
            gr.sizeof_gr_complex,
            6048,
            8192,
            dtv.MOD_16QAM,
            dtv.NH,
            dtv.C2_3,
            dtv.C2_3,
            dtv.GI_1_32,
            dtv.T8k,
            1,
            0)
        self.tx_map = dtv.dvbt_map(6048, dtv.MOD_16QAM, dtv.NH, dtv.T8k, 1)
        self.tx_inner = dtv.dvbt_inner_coder(1, payload, dtv.MOD_16QAM, dtv.NH, dtv.C2_3)
        self.tx_energy = dtv.dvbt_energy_dispersal(1)
        self.tx_cp = digital.ofdm_cyclic_prefixer(
            fft_len,
            fft_len + cp_len,
            0,
            '')
        self.tx_ci = dtv.dvbt_convolutional_interleaver(136, 12, 17)
        self.tx_bi = dtv.dvbt_bit_inner_interleaver(6048, dtv.MOD_16QAM, dtv.NH, dtv.T8k)
        self._tx_amplitude_range = qtgui.Range(0, 1.0, 0.05, 0, 200)
        self._tx_amplitude_win = qtgui.RangeWidget(self._tx_amplitude_range, self.set_tx_amplitude, "TX amplitude (0 = off)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tx_amplitude_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.tx_amp = blocks.multiply_const_cc(tx_amplitude)
        self.tv_out = tv_out.blk(play=play_video, ts_file=ts_out, report_every=20000)
        self.ts_src = blocks.file_source(gr.sizeof_char*1, ts_in, True, 0, 0)
        self.ts_src.set_begin_tag(pmt.PMT_NIL)
        self.rx_viterbi = dtv.dvbt_viterbi_decoder(dtv.MOD_16QAM, dtv.NH, dtv.C2_3, 768)
        self.rx_v2s = blocks.vector_to_stream(gr.sizeof_char*1, payload)
        self.rx_spectrum = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "Received spectrum", #name
            1,
            None # parent
        )
        self.rx_spectrum.set_update_time(0.10)
        self.rx_spectrum.set_y_axis((-110), (-10))
        self.rx_spectrum.set_y_label('Relative Gain', 'dB')
        self.rx_spectrum.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.rx_spectrum.enable_autoscale(False)
        self.rx_spectrum.enable_grid(False)
        self.rx_spectrum.set_fft_average(0.2)
        self.rx_spectrum.enable_axis_labels(True)
        self.rx_spectrum.enable_control_panel(False)
        self.rx_spectrum.set_fft_window_normalized(False)



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
                self.rx_spectrum.set_line_label(i, "Data {0}".format(i))
            else:
                self.rx_spectrum.set_line_label(i, labels[i])
            self.rx_spectrum.set_line_width(i, widths[i])
            self.rx_spectrum.set_line_color(i, colors[i])
            self.rx_spectrum.set_line_alpha(i, alphas[i])

        self._rx_spectrum_win = sip.wrapinstance(self.rx_spectrum.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._rx_spectrum_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rx_si = dtv.dvbt_symbol_inner_interleaver(6048, dtv.T8k, 0)
        self.rx_rs = dtv.dvbt_reed_solomon_dec(2, 8, 0x11d, 255, 239, 8, 51, 8)
        self.rx_pilots = dtv.dvbt_demod_reference_signals(
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
        self.rx_mer_display = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.rx_mer_display.set_update_time(0.10)
        self.rx_mer_display.set_title("Signal quality")

        labels = ["MER", '', '', '', '',
            '', '', '', '', '']
        units = ["dB", '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.rx_mer_display.set_min(i, 0)
            self.rx_mer_display.set_max(i, 40)
            self.rx_mer_display.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.rx_mer_display.set_label(i, "Data {0}".format(i))
            else:
                self.rx_mer_display.set_label(i, labels[i])
            self.rx_mer_display.set_unit(i, units[i])
            self.rx_mer_display.set_factor(i, factor[i])

        self.rx_mer_display.enable_autoscale(False)
        self._rx_mer_display_win = sip.wrapinstance(self.rx_mer_display.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._rx_mer_display_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rx_mer = rx_mer.blk(bits_per_symbol=4, decim=4096)
        self.rx_fft = fft.fft_vcc(fft_len, True, window.rectangular(fft_len), True, 1)
        self.rx_desc = dtv.dvbt_energy_descramble(8)
        self.rx_demap = dtv.dvbt_demap(6048, dtv.MOD_16QAM, dtv.NH, dtv.T8k, 1)
        self.rx_const = qtgui.const_sink_c(
            2048, #size
            "Received constellation", #name
            1, #number of inputs
            None # parent
        )
        self.rx_const.set_update_time(0.10)
        self.rx_const.set_y_axis((-2), 2)
        self.rx_const.set_x_axis((-2), 2)
        self.rx_const.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.rx_const.enable_autoscale(False)
        self.rx_const.enable_grid(False)
        self.rx_const.enable_axis_labels(True)


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
                self.rx_const.set_line_label(i, "Data {0}".format(i))
            else:
                self.rx_const.set_line_label(i, labels[i])
            self.rx_const.set_line_width(i, widths[i])
            self.rx_const.set_line_color(i, colors[i])
            self.rx_const.set_line_style(i, styles[i])
            self.rx_const.set_line_marker(i, markers[i])
            self.rx_const.set_line_alpha(i, alphas[i])

        self._rx_const_win = sip.wrapinstance(self.rx_const.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._rx_const_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rx_cells = blocks.vector_to_stream(gr.sizeof_gr_complex*1, payload)
        self.rx_cd = dtv.dvbt_convolutional_deinterleaver(136, 12, 17)
        self.rx_bi = dtv.dvbt_bit_inner_deinterleaver(6048, dtv.MOD_16QAM, dtv.NH, dtv.T8k)
        self.rx_acq = dtv.dvbt_ofdm_sym_acquisition(1, fft_len, occupied, cp_len, 10)
        self._channel_range = qtgui.Range(21, 48, 1, 31, 200)
        self._channel_win = qtgui.RangeWidget(self._channel_range, self.set_channel, "UHF channel", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._channel_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.rx_acq, 0), (self.rx_fft, 0))
        self.connect((self.rx_bi, 0), (self.rx_v2s, 0))
        self.connect((self.rx_cd, 0), (self.rx_rs, 0))
        self.connect((self.rx_cells, 0), (self.rx_const, 0))
        self.connect((self.rx_cells, 0), (self.rx_mer, 0))
        self.connect((self.rx_demap, 0), (self.rx_si, 0))
        self.connect((self.rx_desc, 0), (self.tv_out, 0))
        self.connect((self.rx_fft, 0), (self.rx_pilots, 0))
        self.connect((self.rx_mer, 0), (self.rx_mer_display, 0))
        self.connect((self.rx_pilots, 0), (self.rx_cells, 0))
        self.connect((self.rx_pilots, 0), (self.rx_demap, 0))
        self.connect((self.rx_rs, 0), (self.rx_desc, 0))
        self.connect((self.rx_si, 0), (self.rx_bi, 0))
        self.connect((self.rx_v2s, 0), (self.rx_viterbi, 0))
        self.connect((self.rx_viterbi, 0), (self.rx_cd, 0))
        self.connect((self.ts_src, 0), (self.tx_energy, 0))
        self.connect((self.tx_amp, 0), (self.tx_spectrum, 0))
        self.connect((self.tx_amp, 0), (self.usrp_tx, 0))
        self.connect((self.tx_bi, 0), (self.tx_si, 0))
        self.connect((self.tx_ci, 0), (self.tx_inner, 0))
        self.connect((self.tx_cp, 0), (self.tx_skip, 0))
        self.connect((self.tx_energy, 0), (self.tx_rs, 0))
        self.connect((self.tx_inner, 0), (self.tx_bi, 0))
        self.connect((self.tx_map, 0), (self.tx_pilots, 0))
        self.connect((self.tx_pilots, 0), (self.tx_cp, 0))
        self.connect((self.tx_rs, 0), (self.tx_ci, 0))
        self.connect((self.tx_si, 0), (self.tx_map, 0))
        self.connect((self.tx_skip, 0), (self.tx_amp, 0))
        self.connect((self.usrp_rx, 0), (self.rx_acq, 0))
        self.connect((self.usrp_rx, 0), (self.rx_spectrum, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab12_fullduplex_tv")
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

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.usrp_tx.set_gain(self.tx_gain, 0)

    def get_tx_amplitude(self):
        return self.tx_amplitude

    def set_tx_amplitude(self, tx_amplitude):
        self.tx_amplitude = tx_amplitude
        self.tx_amp.set_k(self.tx_amplitude)

    def get_ts_out(self):
        return self.ts_out

    def set_ts_out(self, ts_out):
        self.ts_out = ts_out

    def get_ts_in(self):
        return self.ts_in

    def set_ts_in(self, ts_in):
        self.ts_in = ts_in
        self.ts_src.open(self.ts_in, True)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.usrp_tx.set_samp_rate(self.samp_rate)
        self.usrp_tx.set_bandwidth(self.samp_rate, 0)
        self.usrp_rx.set_samp_rate(self.samp_rate)
        self.usrp_rx.set_bandwidth(self.samp_rate, 0)
        self.rx_spectrum.set_frequency_range(self.center_freq, self.samp_rate)
        self.tx_spectrum.set_frequency_range(self.center_freq, self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.usrp_rx.set_gain(self.rx_gain, 0)

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
        self.usrp_tx.set_center_freq(self.center_freq, 0)
        self.usrp_rx.set_center_freq(self.center_freq, 0)
        self.rx_spectrum.set_frequency_range(self.center_freq, self.samp_rate)
        self.tx_spectrum.set_frequency_range(self.center_freq, self.samp_rate)




def main(top_block_cls=lab12_fullduplex_tv, options=None):

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
