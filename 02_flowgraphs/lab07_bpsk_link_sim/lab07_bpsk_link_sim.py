#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 07 - BPSK Link Simulation with Live BER Measurement
# Author: SignalSDR Pro Lab
# Description: A complete digital link in simulation: RRC shaping, AWGN, timing and carrier recovery, measured BER
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import channels
from gnuradio.filter import firdes
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import lab07_bpsk_link_sim_ber_monitor as ber_monitor  # embedded python block
import numpy as np
import sip



class lab07_bpsk_link_sim(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 07 - BPSK Link Simulation with Live BER Measurement", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 07 - BPSK Link Simulation with Live BER Measurement")
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

        self.settings = Qt.QSettings("GNU Radio", "lab07_bpsk_link_sim")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 4
        self.samp_rate = samp_rate = 400000
        self.nfilts = nfilts = 32
        self.excess_bw = excess_bw = 0.35
        self.ebno_db = ebno_db = 8
        self.timing_offset = timing_offset = 1.00005
        self.sym_rate = sym_rate = int(samp_rate/sps)
        self.rrc_tx_taps = rrc_tx_taps = firdes.root_raised_cosine(sps, sps, 1.0, excess_bw, 11*sps)
        self.pfb_mf_taps = pfb_mf_taps = firdes.root_raised_cosine(nfilts, nfilts*sps, 1.0, excess_bw, 11*sps*nfilts)
        self.pattern = pattern = [int(b) for b in np.random.RandomState(1).randint(0, 2, 1023)]
        self.noise_volt = noise_volt = float(np.sqrt(sps / (1.0 * 10.0**(ebno_db/10.0))))
        self.loop_bw = loop_bw = 0.010
        self.freq_offset = freq_offset = 0.0005

        ##################################################
        # Blocks
        ##################################################

        self._timing_offset_range = qtgui.Range(0.999, 1.001, 0.00001, 1.00005, 300)
        self._timing_offset_win = qtgui.RangeWidget(self._timing_offset_range, self.set_timing_offset, "Clock Ratio (epsilon)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._timing_offset_win)
        self._loop_bw_range = qtgui.Range(0.001, 0.080, 0.001, 0.010, 300)
        self._loop_bw_win = qtgui.RangeWidget(self._loop_bw_range, self.set_loop_bw, "Loop Bandwidth (both loops)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._loop_bw_win)
        self._freq_offset_range = qtgui.Range(-0.01, 0.01, 0.0005, 0.0005, 300)
        self._freq_offset_win = qtgui.RangeWidget(self._freq_offset_range, self.set_freq_offset, "Freq Offset (cycles/sample)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_offset_win)
        self.tx_bits = blocks.vector_source_b(pattern, True, 1, [])
        self.to_real = blocks.complex_to_real(1)
        self.throttle = blocks.throttle( gr.sizeof_char*1, sym_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * sym_rate) if "auto" == "time" else int(0.1), 1) )
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
            pfb_mf_taps)
        self.slicer = digital.binary_slicer_fb()
        self.rrc_tx = filter.interp_fir_filter_ccf(sps, rrc_tx_taps)
        self.rrc_tx.declare_sample_delay(0)
        self.eye = qtgui.eye_sink_c(
            1024, #size
            samp_rate, #samp_rate
            1, #number of inputs
            None
        )
        self.eye.set_update_time(0.10)
        self.eye.set_samp_per_symbol(sps)
        self.eye.set_y_axis(-2, 2)

        self.eye.set_y_label('Amplitude', "")

        self.eye.enable_tags(True)
        self.eye.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.eye.enable_autoscale(False)
        self.eye.enable_grid(True)
        self.eye.enable_axis_labels(True)
        self.eye.enable_control_panel(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'blue', 'blue', 'blue', 'blue',
            'blue', 'blue', 'blue', 'blue', 'blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.eye.set_line_label(i, "Eye [Re{{Data {0}}}]".format(round(i/2)))
                else:
                    self.eye.set_line_label(i, "Eye [Im{{Data {0}}}]".format(round((i-1)/2)))
            else:
                self.eye.set_line_label(i, labels[i])
            self.eye.set_line_width(i, widths[i])
            self.eye.set_line_color(i, colors[i])
            self.eye.set_line_style(i, styles[i])
            self.eye.set_line_marker(i, markers[i])
            self.eye.set_line_alpha(i, alphas[i])

        self._eye_win = sip.wrapinstance(self.eye.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._eye_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._ebno_db_range = qtgui.Range(0, 14, 0.5, 8, 300)
        self._ebno_db_win = qtgui.RangeWidget(self._ebno_db_range, self.set_ebno_db, "Eb/N0 (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ebno_db_win)
        self.diff_enc = digital.diff_encoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.diff_dec = digital.diff_decoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.costas_freq = qtgui.time_sink_f(
            1024, #size
            sym_rate, #samp_rate
            'Costas loop frequency estimate (rad/sample)', #name
            1, #number of inputs
            None # parent
        )
        self.costas_freq.set_update_time(0.10)
        self.costas_freq.set_y_axis(-0.1, 0.1)

        self.costas_freq.set_y_label('rad/sample', "")

        self.costas_freq.enable_tags(True)
        self.costas_freq.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.costas_freq.enable_autoscale(True)
        self.costas_freq.enable_grid(True)
        self.costas_freq.enable_axis_labels(True)
        self.costas_freq.enable_control_panel(False)
        self.costas_freq.enable_stem_plot(False)


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
                self.costas_freq.set_line_label(i, "Data {0}".format(i))
            else:
                self.costas_freq.set_line_label(i, labels[i])
            self.costas_freq.set_line_width(i, widths[i])
            self.costas_freq.set_line_color(i, colors[i])
            self.costas_freq.set_line_style(i, styles[i])
            self.costas_freq.set_line_marker(i, markers[i])
            self.costas_freq.set_line_alpha(i, alphas[i])

        self._costas_freq_win = sip.wrapinstance(self.costas_freq.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._costas_freq_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.costas = digital.costas_loop_cc(loop_bw, 2, False)
        self.const_rx = qtgui.const_sink_c(
            1024, #size
            'Constellation AFTER sync', #name
            1, #number of inputs
            None # parent
        )
        self.const_rx.set_update_time(0.10)
        self.const_rx.set_y_axis((-2), 2)
        self.const_rx.set_x_axis((-2), 2)
        self.const_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.const_rx.enable_autoscale(False)
        self.const_rx.enable_grid(True)
        self.const_rx.enable_axis_labels(True)


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
                self.const_rx.set_line_label(i, "Data {0}".format(i))
            else:
                self.const_rx.set_line_label(i, labels[i])
            self.const_rx.set_line_width(i, widths[i])
            self.const_rx.set_line_color(i, colors[i])
            self.const_rx.set_line_style(i, styles[i])
            self.const_rx.set_line_marker(i, markers[i])
            self.const_rx.set_line_alpha(i, alphas[i])

        self._const_rx_win = sip.wrapinstance(self.const_rx.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._const_rx_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.chunks_to_syms = digital.chunks_to_symbols_bc([-1+0j, 1+0j], 1)
        self.channel = channels.channel_model(
            noise_voltage=noise_volt,
            frequency_offset=freq_offset,
            epsilon=timing_offset,
            taps=[1.0 + 0.0j],
            noise_seed=0,
            block_tags=False)
        self.chan_spectrum = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            'Channel Spectrum (RRC shaped + noise)', #name
            1,
            None # parent
        )
        self.chan_spectrum.set_update_time(0.10)
        self.chan_spectrum.set_y_axis((-100), 10)
        self.chan_spectrum.set_y_label('Relative Gain', 'dB')
        self.chan_spectrum.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.chan_spectrum.enable_autoscale(False)
        self.chan_spectrum.enable_grid(True)
        self.chan_spectrum.set_fft_average(0.2)
        self.chan_spectrum.enable_axis_labels(True)
        self.chan_spectrum.enable_control_panel(False)
        self.chan_spectrum.set_fft_window_normalized(False)



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
                self.chan_spectrum.set_line_label(i, "Data {0}".format(i))
            else:
                self.chan_spectrum.set_line_label(i, labels[i])
            self.chan_spectrum.set_line_width(i, widths[i])
            self.chan_spectrum.set_line_color(i, colors[i])
            self.chan_spectrum.set_line_alpha(i, alphas[i])

        self._chan_spectrum_win = sip.wrapinstance(self.chan_spectrum.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._chan_spectrum_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.ber_time = qtgui.time_sink_f(
            2048, #size
            sym_rate, #samp_rate
            'BER convergence', #name
            1, #number of inputs
            None # parent
        )
        self.ber_time.set_update_time(0.25)
        self.ber_time.set_y_axis(0, 0.1)

        self.ber_time.set_y_label('BER', "")

        self.ber_time.enable_tags(True)
        self.ber_time.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.ber_time.enable_autoscale(True)
        self.ber_time.enable_grid(True)
        self.ber_time.enable_axis_labels(True)
        self.ber_time.enable_control_panel(False)
        self.ber_time.enable_stem_plot(False)


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
                self.ber_time.set_line_label(i, "Data {0}".format(i))
            else:
                self.ber_time.set_line_label(i, labels[i])
            self.ber_time.set_line_width(i, widths[i])
            self.ber_time.set_line_color(i, colors[i])
            self.ber_time.set_line_style(i, styles[i])
            self.ber_time.set_line_marker(i, markers[i])
            self.ber_time.set_line_alpha(i, alphas[i])

        self._ber_time_win = sip.wrapinstance(self.ber_time.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._ber_time_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.ber_number = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.ber_number.set_update_time(0.25)
        self.ber_number.set_title('Measured BER')

        labels = ['BER', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.ber_number.set_min(i, 0)
            self.ber_number.set_max(i, 0.5)
            self.ber_number.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.ber_number.set_label(i, "Data {0}".format(i))
            else:
                self.ber_number.set_label(i, labels[i])
            self.ber_number.set_unit(i, units[i])
            self.ber_number.set_factor(i, factor[i])

        self.ber_number.enable_autoscale(True)
        self._ber_number_win = sip.wrapinstance(self.ber_number.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._ber_number_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.ber_monitor = ber_monitor.blk(pattern=pattern, settle=100000, corr_threshold=0.4)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.ber_monitor, 0), (self.ber_number, 0))
        self.connect((self.ber_monitor, 0), (self.ber_time, 0))
        self.connect((self.channel, 0), (self.chan_spectrum, 0))
        self.connect((self.channel, 0), (self.eye, 0))
        self.connect((self.channel, 0), (self.sym_sync, 0))
        self.connect((self.chunks_to_syms, 0), (self.rrc_tx, 0))
        self.connect((self.costas, 0), (self.const_rx, 0))
        self.connect((self.costas, 1), (self.costas_freq, 0))
        self.connect((self.costas, 0), (self.to_real, 0))
        self.connect((self.diff_dec, 0), (self.ber_monitor, 0))
        self.connect((self.diff_enc, 0), (self.chunks_to_syms, 0))
        self.connect((self.rrc_tx, 0), (self.channel, 0))
        self.connect((self.slicer, 0), (self.diff_dec, 0))
        self.connect((self.sym_sync, 0), (self.costas, 0))
        self.connect((self.throttle, 0), (self.diff_enc, 0))
        self.connect((self.to_real, 0), (self.slicer, 0))
        self.connect((self.tx_bits, 0), (self.throttle, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab07_bpsk_link_sim")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_sym_rate(int(self.samp_rate/self.sps))
        self.set_rrc_tx_taps(firdes.root_raised_cosine(self.sps, self.sps, 1.0, self.excess_bw, 11*self.sps))
        self.set_pfb_mf_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sps, 1.0, self.excess_bw, 11*self.sps*self.nfilts))
        self.set_noise_volt(float(np.sqrt(self.sps / (1.0 * 10.0**(self.ebno_db/10.0)))))
        self.sym_sync.set_sps(self.sps)
        self.eye.set_samp_per_symbol(self.sps)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_sym_rate(int(self.samp_rate/self.sps))
        self.chan_spectrum.set_frequency_range(0, self.samp_rate)
        self.eye.set_samp_rate(self.samp_rate)

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts
        self.set_pfb_mf_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sps, 1.0, self.excess_bw, 11*self.sps*self.nfilts))

    def get_excess_bw(self):
        return self.excess_bw

    def set_excess_bw(self, excess_bw):
        self.excess_bw = excess_bw
        self.set_rrc_tx_taps(firdes.root_raised_cosine(self.sps, self.sps, 1.0, self.excess_bw, 11*self.sps))
        self.set_pfb_mf_taps(firdes.root_raised_cosine(self.nfilts, self.nfilts*self.sps, 1.0, self.excess_bw, 11*self.sps*self.nfilts))

    def get_ebno_db(self):
        return self.ebno_db

    def set_ebno_db(self, ebno_db):
        self.ebno_db = ebno_db
        self.set_noise_volt(float(np.sqrt(self.sps / (1.0 * 10.0**(self.ebno_db/10.0)))))

    def get_timing_offset(self):
        return self.timing_offset

    def set_timing_offset(self, timing_offset):
        self.timing_offset = timing_offset
        self.channel.set_timing_offset(self.timing_offset)

    def get_sym_rate(self):
        return self.sym_rate

    def set_sym_rate(self, sym_rate):
        self.sym_rate = sym_rate
        self.throttle.set_sample_rate(self.sym_rate)
        self.ber_time.set_samp_rate(self.sym_rate)
        self.costas_freq.set_samp_rate(self.sym_rate)

    def get_rrc_tx_taps(self):
        return self.rrc_tx_taps

    def set_rrc_tx_taps(self, rrc_tx_taps):
        self.rrc_tx_taps = rrc_tx_taps
        self.rrc_tx.set_taps(self.rrc_tx_taps)

    def get_pfb_mf_taps(self):
        return self.pfb_mf_taps

    def set_pfb_mf_taps(self, pfb_mf_taps):
        self.pfb_mf_taps = pfb_mf_taps

    def get_pattern(self):
        return self.pattern

    def set_pattern(self, pattern):
        self.pattern = pattern
        self.tx_bits.set_data(self.pattern, [])

    def get_noise_volt(self):
        return self.noise_volt

    def set_noise_volt(self, noise_volt):
        self.noise_volt = noise_volt
        self.channel.set_noise_voltage(self.noise_volt)

    def get_loop_bw(self):
        return self.loop_bw

    def set_loop_bw(self, loop_bw):
        self.loop_bw = loop_bw
        self.sym_sync.set_loop_bandwidth(self.loop_bw)
        self.costas.set_loop_bandwidth(self.loop_bw)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.channel.set_frequency_offset(self.freq_offset)




def main(top_block_cls=lab07_bpsk_link_sim, options=None):

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
