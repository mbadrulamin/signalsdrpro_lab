#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Lab 06 - Multimode Receiver: AM / NBFM / WBFM with Channel Selection
# Author: SignalSDR Pro Lab
# Description: One tuner, three demodulators, software channel selection, S-meter and squelch
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
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



class lab06_multimode_receiver(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Lab 06 - Multimode Receiver: AM / NBFM / WBFM with Channel Selection", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Lab 06 - Multimode Receiver: AM / NBFM / WBFM with Channel Selection")
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

        self.settings = Qt.QSettings("GNU Radio", "lab06_multimode_receiver")

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
        self.wide_rate = wide_rate = int(samp_rate/5)
        self.wide_taps = wide_taps = firdes.low_pass(1.0, samp_rate, 150e3,30e3, window.WIN_HAMMING, 6.76)
        self.volume = volume = 1.0
        self.squelch_threshold = squelch_threshold = -70
        self.rf_gain = rf_gain = 40
        self.offset_freq = offset_freq = -200e3
        self.narrow_rate = narrow_rate = int(wide_rate/8)
        self.narrow_bw = narrow_bw = 8000
        self.mode = mode = 2
        self.freq = freq = 100.1e6
        self.audio_rate = audio_rate = 50000

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 5, 0.1, 1.0, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._rf_gain_range = qtgui.Range(0, 76, 1, 40, 200)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rf_gain_win)
        self._offset_freq_range = qtgui.Range(-900e3, 900e3, 5e3, -200e3, 400)
        self._offset_freq_win = qtgui.RangeWidget(self._offset_freq_range, self.set_offset_freq, "Channel Offset (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._offset_freq_win)
        self._narrow_bw_range = qtgui.Range(3000, 18000, 500, 8000, 250)
        self._narrow_bw_win = qtgui.RangeWidget(self._narrow_bw_range, self.set_narrow_bw, "Narrow Channel BW (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._narrow_bw_win)
        # Create the options list
        self._mode_options = [0, 1, 2]
        # Create the labels list
        self._mode_labels = ['AM (airband, shortwave)', 'NBFM (marine, weather, PMR)', 'WBFM (broadcast 88-108)']
        # Create the combo box
        # Create the radio buttons
        self._mode_group_box = Qt.QGroupBox("Demodulator" + ": ")
        self._mode_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._mode_button_group = variable_chooser_button_group()
        self._mode_group_box.setLayout(self._mode_box)
        for i, _label in enumerate(self._mode_labels):
            radio_button = Qt.QRadioButton(_label)
            self._mode_box.addWidget(radio_button)
            self._mode_button_group.addButton(radio_button, i)
        self._mode_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mode_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._mode_options.index(i)))
        self._mode_callback(self.mode)
        self._mode_button_group.buttonClicked[int].connect(
            lambda i: self.set_mode(self._mode_options[i]))
        self.top_layout.addWidget(self._mode_group_box)
        self._freq_range = qtgui.Range(70e6, 6000e6, 100e3, 100.1e6, 400)
        self._freq_win = qtgui.RangeWidget(self._freq_range, self.set_freq, "Hardware Centre (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._freq_win)
        self.xlating_wide = filter.freq_xlating_fir_filter_ccf(5, wide_taps, offset_freq, samp_rate)
        self.wide_sink = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate, #bw
            "Full Span - pick a channel here", #name
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
        	quad_rate=wide_rate,
        	audio_decimation=8,
        )
        self.waterfall_sink = qtgui.waterfall_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate, #bw
            "Full Span Waterfall", #name
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
        self.volume_control = blocks.multiply_const_ff(volume)
        self.usrp_source = uhd.usrp_source(
            ",".join(("", "")),
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
        self.usrp_source.set_gain(rf_gain, 0)
        self._squelch_threshold_range = qtgui.Range(-90, 0, 1, -70, 250)
        self._squelch_threshold_win = qtgui.RangeWidget(self._squelch_threshold_range, self.set_squelch_threshold, "Squelch (dBFS)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._squelch_threshold_win)
        self.squelch = analog.pwr_squelch_cc(squelch_threshold, 0.01, 20, False)
        self.smeter_sink = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.smeter_sink.set_update_time(0.10)
        self.smeter_sink.set_title("Channel S-Meter")

        labels = ["Channel Power", '', '', '', '',
            '', '', '', '', '']
        units = ["dBFS", '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.smeter_sink.set_min(i, -100)
            self.smeter_sink.set_max(i, 0)
            self.smeter_sink.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.smeter_sink.set_label(i, "Data {0}".format(i))
            else:
                self.smeter_sink.set_label(i, labels[i])
            self.smeter_sink.set_unit(i, units[i])
            self.smeter_sink.set_factor(i, factor[i])

        self.smeter_sink.enable_autoscale(False)
        self._smeter_sink_win = sip.wrapinstance(self.smeter_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._smeter_sink_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.smeter_mag = blocks.complex_to_mag_squared(1)
        self.smeter_db = blocks.nlog10_ff(10, 1, 3.0103)
        self.smeter_avg = blocks.moving_average_ff(5000, (1.0/5000), 5000, 1)
        self.nbfm_rcv = analog.nbfm_rx(
        	audio_rate=audio_rate,
        	quad_rate=narrow_rate,
        	tau=(75e-6),
        	max_dev=5e3,
          )
        self.narrow_lpf = filter.fir_filter_ccf(
            8,
            firdes.low_pass(
                1,
                wide_rate,
                narrow_bw,
                2000,
                window.WIN_HAMMING,
                6.76))
        self.mode_selector = blocks.selector(gr.sizeof_float*1,mode,0)
        self.mode_selector.set_enabled(True)
        self.chan_sink = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            narrow_rate, #bw
            "Selected Narrow Channel", #name
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
        self.top_grid_layout.addWidget(self._chan_sink_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.audio_time_sink = qtgui.time_sink_f(
            2048, #size
            audio_rate, #samp_rate
            "Demodulated Audio", #name
            1, #number of inputs
            None # parent
        )
        self.audio_time_sink.set_update_time(0.10)
        self.audio_time_sink.set_y_axis(-1.5, 1.5)

        self.audio_time_sink.set_y_label('Amplitude', "")

        self.audio_time_sink.enable_tags(True)
        self.audio_time_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.audio_time_sink.enable_autoscale(False)
        self.audio_time_sink.enable_grid(True)
        self.audio_time_sink.enable_axis_labels(True)
        self.audio_time_sink.enable_control_panel(False)
        self.audio_time_sink.enable_stem_plot(False)


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
                self.audio_time_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.audio_time_sink.set_line_label(i, labels[i])
            self.audio_time_sink.set_line_width(i, widths[i])
            self.audio_time_sink.set_line_color(i, colors[i])
            self.audio_time_sink.set_line_style(i, styles[i])
            self.audio_time_sink.set_line_marker(i, markers[i])
            self.audio_time_sink.set_line_alpha(i, alphas[i])

        self._audio_time_sink_win = sip.wrapinstance(self.audio_time_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._audio_time_sink_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.audio_sink = audio.sink(audio_rate, "", True)
        self.am_demod = analog.am_demod_cf(
        	channel_rate=narrow_rate,
        	audio_decim=1,
        	audio_pass=5000,
        	audio_stop=5500,
        )
        self.agc_wide = analog.agc2_cc(0.01, 0.001, 0.5, 1.0, 4096)
        self.agc_narrow = analog.agc2_cc(0.02, 0.0005, 0.3, 1.0, 4096)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.agc_narrow, 0), (self.am_demod, 0))
        self.connect((self.agc_narrow, 0), (self.nbfm_rcv, 0))
        self.connect((self.agc_wide, 0), (self.wbfm_rcv, 0))
        self.connect((self.am_demod, 0), (self.mode_selector, 0))
        self.connect((self.mode_selector, 0), (self.volume_control, 0))
        self.connect((self.narrow_lpf, 0), (self.chan_sink, 0))
        self.connect((self.narrow_lpf, 0), (self.smeter_mag, 0))
        self.connect((self.narrow_lpf, 0), (self.squelch, 0))
        self.connect((self.nbfm_rcv, 0), (self.mode_selector, 1))
        self.connect((self.smeter_avg, 0), (self.smeter_db, 0))
        self.connect((self.smeter_db, 0), (self.smeter_sink, 0))
        self.connect((self.smeter_mag, 0), (self.smeter_avg, 0))
        self.connect((self.squelch, 0), (self.agc_narrow, 0))
        self.connect((self.usrp_source, 0), (self.waterfall_sink, 0))
        self.connect((self.usrp_source, 0), (self.wide_sink, 0))
        self.connect((self.usrp_source, 0), (self.xlating_wide, 0))
        self.connect((self.volume_control, 0), (self.audio_sink, 0))
        self.connect((self.volume_control, 0), (self.audio_time_sink, 0))
        self.connect((self.wbfm_rcv, 0), (self.mode_selector, 2))
        self.connect((self.xlating_wide, 0), (self.agc_wide, 0))
        self.connect((self.xlating_wide, 0), (self.narrow_lpf, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "lab06_multimode_receiver")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_wide_rate(int(self.samp_rate/5))
        self.set_wide_taps(firdes.low_pass(1.0, self.samp_rate, 150e3, 30e3, window.WIN_HAMMING, 6.76))
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.usrp_source.set_bandwidth(self.samp_rate, 0)
        self.wide_sink.set_frequency_range(self.freq, self.samp_rate)
        self.waterfall_sink.set_frequency_range(self.freq, self.samp_rate)

    def get_wide_rate(self):
        return self.wide_rate

    def set_wide_rate(self, wide_rate):
        self.wide_rate = wide_rate
        self.set_narrow_rate(int(self.wide_rate/8))
        self.narrow_lpf.set_taps(firdes.low_pass(1, self.wide_rate, self.narrow_bw, 2000, window.WIN_HAMMING, 6.76))

    def get_wide_taps(self):
        return self.wide_taps

    def set_wide_taps(self, wide_taps):
        self.wide_taps = wide_taps
        self.xlating_wide.set_taps(self.wide_taps)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.volume_control.set_k(self.volume)

    def get_squelch_threshold(self):
        return self.squelch_threshold

    def set_squelch_threshold(self, squelch_threshold):
        self.squelch_threshold = squelch_threshold
        self.squelch.set_threshold(self.squelch_threshold)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain
        self.usrp_source.set_gain(self.rf_gain, 0)

    def get_offset_freq(self):
        return self.offset_freq

    def set_offset_freq(self, offset_freq):
        self.offset_freq = offset_freq
        self.xlating_wide.set_center_freq(self.offset_freq)

    def get_narrow_rate(self):
        return self.narrow_rate

    def set_narrow_rate(self, narrow_rate):
        self.narrow_rate = narrow_rate
        self.chan_sink.set_frequency_range(0, self.narrow_rate)

    def get_narrow_bw(self):
        return self.narrow_bw

    def set_narrow_bw(self, narrow_bw):
        self.narrow_bw = narrow_bw
        self.narrow_lpf.set_taps(firdes.low_pass(1, self.wide_rate, self.narrow_bw, 2000, window.WIN_HAMMING, 6.76))

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode
        self._mode_callback(self.mode)
        self.mode_selector.set_input_index(self.mode)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.usrp_source.set_center_freq(self.freq, 0)
        self.wide_sink.set_frequency_range(self.freq, self.samp_rate)
        self.waterfall_sink.set_frequency_range(self.freq, self.samp_rate)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.audio_time_sink.set_samp_rate(self.audio_rate)




def main(top_block_cls=lab06_multimode_receiver, options=None):

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
