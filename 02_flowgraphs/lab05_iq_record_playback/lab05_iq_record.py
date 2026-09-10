#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 05a - IQ Recorder (SignalSDR Pro as B210)
# Author: SignalSDR Pro Lab
# Description: Capture raw complex baseband to disk for offline, repeatable DSP work
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import blocks
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



class lab05_iq_record(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 05a - IQ Recorder (SignalSDR Pro as B210)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 05a - IQ Recorder (SignalSDR Pro as B210)")
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

        self.settings = Qt.QSettings("GNU Radio", "lab05_iq_record")

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
        self.recording = recording = 0
        self.rec_file = rec_file = "/tmp/capture_100M0_2Msps_fc32.iq"
        self.gain = gain = 40
        self.freq = freq = 100.0e6

        ##################################################
        # Blocks
        ##################################################

        # Create the options list
        self._recording_options = [0, 1]
        # Create the labels list
        self._recording_labels = ['OFF (monitor only)', 'ON (writing to disk)']
        # Create the combo box
        # Create the radio buttons
        self._recording_group_box = Qt.QGroupBox("Record" + ": ")
        self._recording_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._recording_button_group = variable_chooser_button_group()
        self._recording_group_box.setLayout(self._recording_box)
        for i, _label in enumerate(self._recording_labels):
            radio_button = Qt.QRadioButton(_label)
            self._recording_box.addWidget(radio_button)
            self._recording_button_group.addButton(radio_button, i)
        self._recording_callback = lambda i: Qt.QMetaObject.invokeMethod(self._recording_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._recording_options.index(i)))
        self._recording_callback(self.recording)
        self._recording_button_group.buttonClicked[int].connect(
            lambda i: self.set_recording(self._recording_options[i]))
        self.top_layout.addWidget(self._recording_group_box)
        self._gain_range = qtgui.Range(0, 76, 1, 40, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "RF Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
        self._freq_range = qtgui.Range(87.5e6, 108e6, 100e3, 100.0e6, 200)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "Centre Frequency (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self.waterfall_sink = qtgui.waterfall_sink_c(
            4096, #size
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

        self.top_grid_layout.addWidget(self._waterfall_sink_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.usrp_source = uhd.usrp_source(
            ",".join(("", "num_recv_frames=512")),
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
        self.usrp_source.set_gain(gain, 0)
        self.record_gate = blocks.copy(gr.sizeof_gr_complex*1)
        self.record_gate.set_enabled(bool(recording))
        self.power_sink = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.power_sink.set_update_time(0.10)
        self.power_sink.set_title("Wideband Level")

        labels = ["dBFS", '', '', '', '',
            '', '', '', '', '']
        units = ["dB", '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.power_sink.set_min(i, -90)
            self.power_sink.set_max(i, 0)
            self.power_sink.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.power_sink.set_label(i, "Data {0}".format(i))
            else:
                self.power_sink.set_label(i, labels[i])
            self.power_sink.set_unit(i, units[i])
            self.power_sink.set_factor(i, factor[i])

        self.power_sink.enable_autoscale(False)
        self._power_sink_win = sip.wrapinstance(self.power_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._power_sink_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.power_db = blocks.nlog10_ff(10, 1, 3.0103)
        self.power_average = blocks.moving_average_ff(100000, (1.0/100000), 100000, 1)
        self.mag_squared = blocks.complex_to_mag_squared(1)
        self.freq_sink = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate, #bw
            "Live Spectrum - check before recording", #name
            1,
            None # parent
        )
        self.freq_sink.set_update_time(0.10)
        self.freq_sink.set_y_axis((-140), 10)
        self.freq_sink.set_y_label('Relative Gain', 'dB')
        self.freq_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink.enable_autoscale(False)
        self.freq_sink.enable_grid(True)
        self.freq_sink.set_fft_average(0.2)
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
        self.top_grid_layout.addWidget(self._freq_sink_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.file_sink = blocks.file_sink(gr.sizeof_gr_complex*1, rec_file, False)
        self.file_sink.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.mag_squared, 0), (self.power_average, 0))
        self.connect((self.power_average, 0), (self.power_db, 0))
        self.connect((self.power_db, 0), (self.power_sink, 0))
        self.connect((self.record_gate, 0), (self.file_sink, 0))
        self.connect((self.usrp_source, 0), (self.freq_sink, 0))
        self.connect((self.usrp_source, 0), (self.mag_squared, 0))
        self.connect((self.usrp_source, 0), (self.record_gate, 0))
        self.connect((self.usrp_source, 0), (self.waterfall_sink, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab05_iq_record")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.usrp_source.set_bandwidth(self.samp_rate, 0)
        self.freq_sink.set_frequency_range(self.freq, self.samp_rate)
        self.waterfall_sink.set_frequency_range(self.freq, self.samp_rate)

    def get_recording(self):
        return self.recording

    def set_recording(self, recording):
        self.recording = recording
        self._recording_callback(self.recording)
        self.record_gate.set_enabled(bool(self.recording))

    def get_rec_file(self):
        return self.rec_file

    def set_rec_file(self, rec_file):
        self.rec_file = rec_file
        self.file_sink.open(self.rec_file)

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




def main(top_block_cls=lab05_iq_record, options=None):

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
