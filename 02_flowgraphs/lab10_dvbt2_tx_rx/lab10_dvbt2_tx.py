#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 10b - DVB-T2 Transmitter (RF - Faraday cage or dummy load ONLY)
# Author: SignalSDR Pro Lab
# Description: Transmit a standards-compliant DVB-T2 multiplex for a real TV or tuner to receive
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import blocks
import pmt
from gnuradio import digital
from gnuradio import dtv
from gnuradio import gr
from gnuradio.filter import firdes
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



class lab10_dvbt2_tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 10b - DVB-T2 Transmitter (RF - Faraday cage or dummy load ONLY)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 10b - DVB-T2 Transmitter (RF - Faraday cage or dummy load ONLY)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab10_dvbt2_tx")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.fft_len = fft_len = 32768
        self.tx_gain = tx_gain = 0
        self.tx_amplitude = tx_amplitude = 0.0
        self.ts_file = ts_file = '/tmp/tv.fifo'
        self.ti_blocks = ti_blocks = 3
        self.samp_rate = samp_rate = (8000000.0 * 8) / 7
        self.num_data_syms = num_data_syms = 59
        self.fec_blocks = fec_blocks = 202
        self.cp_len = cp_len = fft_len // 128
        self.center_freq = center_freq = 474e6

        ##################################################
        # Blocks
        ##################################################

        self._tx_gain_range = qtgui.Range(0, 89, 1, 0, 300)
        self._tx_gain_win = qtgui.RangeWidget(self._tx_gain_range, self.set_tx_gain, "TX RF gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tx_gain_win)
        self._tx_amplitude_range = qtgui.Range(0.0, 0.5, 0.01, 0.0, 300)
        self._tx_amplitude_win = qtgui.RangeWidget(self._tx_amplitude_range, self.set_tx_amplitude, "TX digital amplitude", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tx_amplitude_win)
        self.usrp_sink = uhd.usrp_sink(
            ",".join(("send_frame_size=8192,num_send_frames=1024", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.usrp_sink.set_samp_rate(samp_rate)
        # No synchronization enforced.

        self.usrp_sink.set_center_freq(center_freq, 0)
        self.usrp_sink.set_antenna('TX/RX', 0)
        self.usrp_sink.set_bandwidth(samp_rate, 0)
        self.usrp_sink.set_gain(tx_gain, 0)
        self.tx_scale = blocks.multiply_const_cc(tx_amplitude)
        self.tx_scale.set_min_output_buffer(4194304)
        self.ts_source = blocks.file_source(gr.sizeof_char*1, ts_file, False, 0, 0)
        self.ts_source.set_begin_tag(pmt.PMT_NIL)
        self.timeplot = qtgui.time_sink_c(
            2048, #size
            samp_rate, #samp_rate
            'Time domain - noise-like, with high peaks', #name
            1, #number of inputs
            None # parent
        )
        self.timeplot.set_update_time(0.10)
        self.timeplot.set_y_axis(-1, 1)

        self.timeplot.set_y_label('Amplitude', "")

        self.timeplot.enable_tags(True)
        self.timeplot.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.timeplot.enable_autoscale(True)
        self.timeplot.enable_grid(True)
        self.timeplot.enable_axis_labels(True)
        self.timeplot.enable_control_panel(False)
        self.timeplot.enable_stem_plot(False)


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


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.timeplot.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.timeplot.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.timeplot.set_line_label(i, labels[i])
            self.timeplot.set_line_width(i, widths[i])
            self.timeplot.set_line_color(i, colors[i])
            self.timeplot.set_line_style(i, styles[i])
            self.timeplot.set_line_marker(i, markers[i])
            self.timeplot.set_line_alpha(i, alphas[i])

        self._timeplot_win = sip.wrapinstance(self.timeplot.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._timeplot_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.spectrum = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            'DVB-T2 signal - should be a 7.6 MHz flat-topped block', #name
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
        self.pilotgenerator = dtv.dvbt2_pilotgenerator_cc(
            dtv.CARRIERS_EXTENDED,
            dtv.FFTSIZE_32K_T2GI,
            dtv.PILOT_PP7,
            dtv.GI_1_128,
            num_data_syms,
            dtv.PAPR_OFF,
            dtv.VERSION_111,
            dtv.PREAMBLE_T2_SISO,
            dtv.MISO_TX1,
            dtv.EQUALIZATION_OFF,
            dtv.BANDWIDTH_8_0_MHZ,
            32768
            )
        self.p1insertion = dtv.dvbt2_p1insertion_cc(
            dtv.CARRIERS_EXTENDED,
            dtv.FFTSIZE_32K_T2GI,
            dtv.GI_1_128,
            num_data_syms,
            dtv.PREAMBLE_T2_SISO,
            dtv.SHOWLEVELS_OFF,
            3.3
            )
        self.modulator = dtv.dvbt2_modulator_bc(dtv.FECFRAME_NORMAL, dtv.MOD_256QAM, dtv.ROTATION_ON)
        self.ldpc = dtv.dvb_ldpc_bb(
            dtv.STANDARD_DVBT2,
            dtv.FECFRAME_NORMAL,
            dtv.C2_3,
            dtv.MOD_OTHER)
        self.freqinterleaver = dtv.dvbt2_freqinterleaver_cc(
            dtv.CARRIERS_EXTENDED,
            dtv.FFTSIZE_32K_T2GI,
            dtv.PILOT_PP7,
            dtv.GI_1_128,
            num_data_syms,
            dtv.PAPR_OFF,
            dtv.VERSION_111,
            dtv.PREAMBLE_T2_SISO
            )
        self.framemapper = dtv.dvbt2_framemapper_cc(
            dtv.FECFRAME_NORMAL,
            dtv.C2_3,
            dtv.MOD_256QAM,
            dtv.ROTATION_ON,
            fec_blocks,
            ti_blocks,
            dtv.CARRIERS_EXTENDED,
            dtv.FFTSIZE_32K_T2GI,
            dtv.GI_1_128,
            dtv.L1_MOD_64QAM,
            dtv.PILOT_PP7,
            2,
            num_data_syms,
            dtv.PAPR_OFF,
            dtv.VERSION_111,
            dtv.PREAMBLE_T2_SISO,
            dtv.INPUTMODE_NORMAL,
            dtv.RESERVED_OFF,
            dtv.L1_SCRAMBLED_OFF,
            dtv.INBAND_OFF)
        self.cyclic_prefixer = digital.ofdm_cyclic_prefixer(
            fft_len,
            fft_len + cp_len,
            0,
            "")
        self.cellinterleaver = dtv.dvbt2_cellinterleaver_cc(dtv.FECFRAME_NORMAL, dtv.MOD_256QAM, fec_blocks, ti_blocks)
        self.bitinterleaver = dtv.dvbt2_interleaver_bb(dtv.FECFRAME_NORMAL, dtv.C2_3, dtv.MOD_256QAM)
        self.bch = dtv.dvb_bch_bb(
            dtv.STANDARD_DVBT2,
            dtv.FECFRAME_NORMAL,
            dtv.C2_3
            )
        self.bbscrambler = dtv.dvb_bbscrambler_bb(
            dtv.STANDARD_DVBT2,
            dtv.FECFRAME_NORMAL,
            dtv.C2_3
            )
        self.bbheader = dtv.dvb_bbheader_bb(
        dtv.STANDARD_DVBT2,
        dtv.FECFRAME_NORMAL,
        dtv.C2_3,
        dtv.RO_0_35,
        dtv.INPUTMODE_NORMAL,
        dtv.INBAND_OFF,
        168,
        4000000)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.bbheader, 0), (self.bbscrambler, 0))
        self.connect((self.bbscrambler, 0), (self.bch, 0))
        self.connect((self.bch, 0), (self.ldpc, 0))
        self.connect((self.bitinterleaver, 0), (self.modulator, 0))
        self.connect((self.cellinterleaver, 0), (self.framemapper, 0))
        self.connect((self.cyclic_prefixer, 0), (self.p1insertion, 0))
        self.connect((self.framemapper, 0), (self.freqinterleaver, 0))
        self.connect((self.freqinterleaver, 0), (self.pilotgenerator, 0))
        self.connect((self.ldpc, 0), (self.bitinterleaver, 0))
        self.connect((self.modulator, 0), (self.cellinterleaver, 0))
        self.connect((self.p1insertion, 0), (self.tx_scale, 0))
        self.connect((self.pilotgenerator, 0), (self.cyclic_prefixer, 0))
        self.connect((self.ts_source, 0), (self.bbheader, 0))
        self.connect((self.tx_scale, 0), (self.spectrum, 0))
        self.connect((self.tx_scale, 0), (self.timeplot, 0))
        self.connect((self.tx_scale, 0), (self.usrp_sink, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab10_dvbt2_tx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_cp_len(self.fft_len // 128)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.usrp_sink.set_gain(self.tx_gain, 0)

    def get_tx_amplitude(self):
        return self.tx_amplitude

    def set_tx_amplitude(self, tx_amplitude):
        self.tx_amplitude = tx_amplitude
        self.tx_scale.set_k(self.tx_amplitude)

    def get_ts_file(self):
        return self.ts_file

    def set_ts_file(self, ts_file):
        self.ts_file = ts_file
        self.ts_source.open(self.ts_file, False)

    def get_ti_blocks(self):
        return self.ti_blocks

    def set_ti_blocks(self, ti_blocks):
        self.ti_blocks = ti_blocks

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.spectrum.set_frequency_range(0, self.samp_rate)
        self.timeplot.set_samp_rate(self.samp_rate)
        self.usrp_sink.set_samp_rate(self.samp_rate)
        self.usrp_sink.set_bandwidth(self.samp_rate, 0)

    def get_num_data_syms(self):
        return self.num_data_syms

    def set_num_data_syms(self, num_data_syms):
        self.num_data_syms = num_data_syms

    def get_fec_blocks(self):
        return self.fec_blocks

    def set_fec_blocks(self, fec_blocks):
        self.fec_blocks = fec_blocks

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.usrp_sink.set_center_freq(self.center_freq, 0)




def main(top_block_cls=lab10_dvbt2_tx, options=None):

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
