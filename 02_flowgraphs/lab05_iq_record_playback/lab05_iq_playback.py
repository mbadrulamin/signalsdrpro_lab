#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 05b - IQ Playback & Offline Tuning (no hardware needed)
# Author: SignalSDR Pro Lab
# Description: Replay a recorded IQ file and retune inside it with a frequency-translating filter
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
import pmt
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
import sip



class lab05_iq_playback(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 05b - IQ Playback & Offline Tuning (no hardware needed)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 05b - IQ Playback & Offline Tuning (no hardware needed)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab05_iq_playback")

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
        self.chan_rate = chan_rate = int(samp_rate/5)
        self.volume = volume = 1.0
        self.rec_freq = rec_freq = 100.0e6
        self.rec_file = rec_file = "/tmp/capture_100M0_2Msps_fc32.iq"
        self.offset_freq = offset_freq = 0
        self.chan_taps = chan_taps = firdes.low_pass(1.0, samp_rate, 100e3,30e3, window.WIN_HAMMING, 6.76)
        self.audio_rate = audio_rate = int(chan_rate/8)

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 5, 0.1, 1.0, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._offset_freq_range = qtgui.Range(-900e3, 900e3, 10e3, 0, 400)
        self._offset_freq_win = qtgui.RangeWidget(self._offset_freq_range, self.set_offset_freq, "Offset from centre (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._offset_freq_win)
        self.wide_sink = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            rec_freq, #fc
            samp_rate, #bw
            "Recorded Spectrum (full file bandwidth)", #name
            1,
            None # parent
        )
        self.wide_sink.set_update_time(0.10)
        self.wide_sink.set_y_axis((-140), 10)
        self.wide_sink.set_y_label('Relative Gain', 'dB')
        self.wide_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.wide_sink.enable_autoscale(False)
        self.wide_sink.enable_grid(True)
        self.wide_sink.set_fft_average(0.2)
        self.wide_sink.enable_axis_labels(True)
        self.wide_sink.enable_control_panel(False)
        self.wide_sink.set_fft_window_normalized(False)



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
                self.wide_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.wide_sink.set_line_label(i, labels[i])
            self.wide_sink.set_line_width(i, widths[i])
            self.wide_sink.set_line_color(i, colors[i])
            self.wide_sink.set_line_alpha(i, alphas[i])

        self._wide_sink_win = sip.wrapinstance(self.wide_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._wide_sink_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.wbfm_rcv = analog.wfm_rcv(
        	quad_rate=chan_rate,
        	audio_decimation=8,
        )
        self.volume_control = blocks.multiply_const_ff(volume)
        self.throttle = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.file_source = blocks.file_source(gr.sizeof_gr_complex*1, rec_file, True, 0, 0)
        self.file_source.set_begin_tag(pmt.PMT_NIL)
        self.chan_sink = qtgui.freq_sink_c(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            chan_rate, #bw
            "Selected Channel (after xlating filter)", #name
            1,
            None # parent
        )
        self.chan_sink.set_update_time(0.10)
        self.chan_sink.set_y_axis((-140), 10)
        self.chan_sink.set_y_label('Relative Gain', 'dB')
        self.chan_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.chan_sink.enable_autoscale(False)
        self.chan_sink.enable_grid(True)
        self.chan_sink.set_fft_average(0.2)
        self.chan_sink.enable_axis_labels(True)
        self.chan_sink.enable_control_panel(False)
        self.chan_sink.set_fft_window_normalized(False)



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
                self.chan_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.chan_sink.set_line_label(i, labels[i])
            self.chan_sink.set_line_width(i, widths[i])
            self.chan_sink.set_line_color(i, colors[i])
            self.chan_sink.set_line_alpha(i, alphas[i])

        self._chan_sink_win = sip.wrapinstance(self.chan_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._chan_sink_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.chan_filter = filter.freq_xlating_fir_filter_ccf(5, chan_taps, offset_freq, samp_rate)
        self.audio_sink_gui = qtgui.time_sink_f(
            2048, #size
            audio_rate, #samp_rate
            "Demodulated Audio", #name
            1, #number of inputs
            None # parent
        )
        self.audio_sink_gui.set_update_time(0.10)
        self.audio_sink_gui.set_y_axis(-1.5, 1.5)

        self.audio_sink_gui.set_y_label('Amplitude', "")

        self.audio_sink_gui.enable_tags(True)
        self.audio_sink_gui.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.audio_sink_gui.enable_autoscale(False)
        self.audio_sink_gui.enable_grid(True)
        self.audio_sink_gui.enable_axis_labels(True)
        self.audio_sink_gui.enable_control_panel(False)
        self.audio_sink_gui.enable_stem_plot(False)


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
                self.audio_sink_gui.set_line_label(i, "Data {0}".format(i))
            else:
                self.audio_sink_gui.set_line_label(i, labels[i])
            self.audio_sink_gui.set_line_width(i, widths[i])
            self.audio_sink_gui.set_line_color(i, colors[i])
            self.audio_sink_gui.set_line_style(i, styles[i])
            self.audio_sink_gui.set_line_marker(i, markers[i])
            self.audio_sink_gui.set_line_alpha(i, alphas[i])

        self._audio_sink_gui_win = sip.wrapinstance(self.audio_sink_gui.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._audio_sink_gui_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.audio_sink = audio.sink(audio_rate, "", True)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.chan_filter, 0), (self.chan_sink, 0))
        self.connect((self.chan_filter, 0), (self.wbfm_rcv, 0))
        self.connect((self.file_source, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.chan_filter, 0))
        self.connect((self.throttle, 0), (self.wide_sink, 0))
        self.connect((self.volume_control, 0), (self.audio_sink, 0))
        self.connect((self.volume_control, 0), (self.audio_sink_gui, 0))
        self.connect((self.wbfm_rcv, 0), (self.volume_control, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab05_iq_playback")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_chan_rate(int(self.samp_rate/5))
        self.set_chan_taps(firdes.low_pass(1.0, self.samp_rate, 100e3, 30e3, window.WIN_HAMMING, 6.76))
        self.throttle.set_sample_rate(self.samp_rate)
        self.wide_sink.set_frequency_range(self.rec_freq, self.samp_rate)

    def get_chan_rate(self):
        return self.chan_rate

    def set_chan_rate(self, chan_rate):
        self.chan_rate = chan_rate
        self.set_audio_rate(int(self.chan_rate/8))
        self.chan_sink.set_frequency_range(0, self.chan_rate)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.volume_control.set_k(self.volume)

    def get_rec_freq(self):
        return self.rec_freq

    def set_rec_freq(self, rec_freq):
        self.rec_freq = rec_freq
        self.wide_sink.set_frequency_range(self.rec_freq, self.samp_rate)

    def get_rec_file(self):
        return self.rec_file

    def set_rec_file(self, rec_file):
        self.rec_file = rec_file
        self.file_source.open(self.rec_file, True)

    def get_offset_freq(self):
        return self.offset_freq

    def set_offset_freq(self, offset_freq):
        self.offset_freq = offset_freq
        self.chan_filter.set_center_freq(self.offset_freq)

    def get_chan_taps(self):
        return self.chan_taps

    def set_chan_taps(self, chan_taps):
        self.chan_taps = chan_taps
        self.chan_filter.set_taps(self.chan_taps)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.audio_sink_gui.set_samp_rate(self.audio_rate)




def main(top_block_cls=lab05_iq_playback, options=None):

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
