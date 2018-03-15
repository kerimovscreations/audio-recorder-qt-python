from PyQt5.QtGui import QIcon
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QPointF
from dragdroparea import DragDropArea
import numpy as np
from scipy.io import wavfile
from scipy import fftpack


class ContentView(QWidget):

    def __init__(self):
        super().__init__()

        self.m_chart_1 = QChart()
        self.m_chart_2 = QChart()
        self.m_chart_3 = QChart()
        self.m_chart_4 = QChart()
        self.m_series_1 = QLineSeries()
        self.m_series_2 = QLineSeries()
        self.m_series_3 = QLineSeries()
        self.m_series_4 = QLineSeries()

        self.y_original = []
        self.x_data = []
        self.y_noisy = []
        self.sampling_rate = 0

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Drag&Drop area
        drag_drop = DragDropArea(parent=self)
        main_layout.addWidget(drag_drop)

        # Chart layout
        chart_layout_1 = QHBoxLayout()
        chart_layout_2 = QHBoxLayout()

        # Chart 1
        chart_view_1 = QChartView(self.m_chart_1)
        chart_view_1.setMinimumSize(400, 300)

        self.m_chart_1.addSeries(self.m_series_1)

        pen = self.m_series_1.pen()
        pen.setColor(Qt.red)
        pen.setWidthF(.1)
        self.m_series_1.setPen(pen)
        self.m_series_1.setUseOpenGL(True)

        axis_x = QValueAxis()
        axis_x.setRange(0, 100)
        axis_x.setLabelFormat("%g")
        axis_x.setTitleText("Samples")

        axis_y = QValueAxis()
        axis_y.setRange(-10, 10)
        axis_y.setTitleText("Audio level")

        self.m_chart_1.setAxisX(axis_x, self.m_series_1)
        self.m_chart_1.setAxisY(axis_y, self.m_series_1)
        self.m_chart_1.setTitle("Original signal time domain")

        chart_layout_1.addWidget(chart_view_1)

        # Chart 2
        chart_view_2 = QChartView(self.m_chart_2)
        chart_view_2.setMinimumSize(400, 300)

        self.m_chart_2.setTitle("Original signal frequency domain")

        pen = self.m_series_2.pen()
        pen.setColor(Qt.blue)
        pen.setWidthF(.1)
        self.m_series_2.setPen(pen)
        self.m_series_2.setUseOpenGL(True)

        self.m_chart_2.addSeries(self.m_series_2)

        chart_layout_1.addWidget(chart_view_2)

        # Chart 3
        chart_view_3 = QChartView(self.m_chart_3)
        chart_view_3.setMinimumSize(400, 300)

        self.m_chart_3.addSeries(self.m_series_3)

        pen = self.m_series_3.pen()
        pen.setColor(Qt.green)
        pen.setWidthF(.1)
        self.m_series_3.setPen(pen)
        self.m_series_3.setUseOpenGL(True)

        axis_x = QValueAxis()
        axis_x.setRange(0, 100)
        axis_x.setLabelFormat("%g")
        axis_x.setTitleText("Samples")

        axis_y = QValueAxis()
        axis_y.setRange(-10, 10)
        axis_y.setTitleText("Audio level")

        self.m_chart_3.setAxisX(axis_x, self.m_series_3)
        self.m_chart_3.setAxisY(axis_y, self.m_series_3)
        self.m_chart_3.setTitle("Noisy signal time domain")

        chart_layout_2.addWidget(chart_view_3)

        # Chart 4
        chart_view_4 = QChartView(self.m_chart_4)
        chart_view_4.setMinimumSize(400, 300)

        self.m_chart_4.setTitle("Noisy signal frequency domain")

        pen = self.m_series_4.pen()
        pen.setColor(Qt.magenta)
        pen.setWidthF(.1)
        self.m_series_4.setPen(pen)
        self.m_series_4.setUseOpenGL(True)

        self.m_chart_4.addSeries(self.m_series_4)

        chart_layout_2.addWidget(chart_view_4)

        main_layout.addLayout(chart_layout_1)
        main_layout.addLayout(chart_layout_2)

        # Action buttons
        player_layout = QHBoxLayout()

        noise_jc = QIcon('rate_ic.png')
        noise_btn = QPushButton('Add Noise')
        noise_btn.setIcon(noise_jc)
        noise_btn.clicked.connect(self.on_add_noise)

        player_layout.addWidget(noise_btn)

        play_jc = QIcon('play_ic.png')
        play_btn = QPushButton('Play')
        play_btn.setIcon(play_jc)
        play_btn.clicked.connect(self.on_play)

        player_layout.addWidget(play_btn)

        main_layout.addLayout(player_layout)

        self.setLayout(main_layout)

    def on_file_upload(self, file_url):
        print(file_url[7:])

        rate, data = wavfile.read(file_url[7:])

        self.show_info(rate, data)

    def on_add_noise(self):
        if len(self.y_original) > 0:
            noise = np.random.normal(0, self.y_original.max()/10, len(self.y_original))
            arr1 = np.array(self.y_original)
            self.y_noisy = arr1 + noise

            # Time domain
            y_data_scaled = np.interp(self.y_noisy, (self.y_noisy.min(), self.y_noisy.max()), (-10, +10))

            points_3 = []

            for k in range(len(y_data_scaled)):
                points_3.append(QPointF(self.x_data[k], y_data_scaled[k]))

            self.m_series_3.replace(points_3)

            # Frequency domain
            y_freq_data = np.abs(fftpack.fft(self.y_noisy))
            y_freq_data = np.interp(y_freq_data, (y_freq_data.min(), y_freq_data.max()), (0, +10))
            x_freq_data = fftpack.fftfreq(len(self.y_noisy)) * self.sampling_rate

            axis_x = QValueAxis()
            axis_x.setRange(0, self.sampling_rate / 2)
            axis_x.setLabelFormat("%g")
            axis_x.setTitleText("Frequency [Hz]")

            axis_y = QValueAxis()
            axis_y.setRange(np.min(y_freq_data), np.max(y_freq_data))
            axis_y.setTitleText("Magnitude")

            self.m_chart_4.setAxisX(axis_x, self.m_series_4)
            self.m_chart_4.setAxisY(axis_y, self.m_series_4)

            points_4 = []

            for k in range(len(y_freq_data)):
                points_4.append(QPointF(x_freq_data[k], y_freq_data[k]))

            self.m_series_4.replace(points_4)

    def on_play(self):
        print("on_play")

    def show_info(self, sampling_rate, data):
        print("sampling rate:", sampling_rate)
        print("shape:", data.shape)
        print("dtype:", data.dtype)
        print("min, max:", data.min(), data.max())

        self.sampling_rate = sampling_rate

        # Time domain
        self.y_original = data[:, 0]
        y_data_scaled = np.interp(self.y_original, (self.y_original.min(), self.y_original.max()), (-10, +10))

        sample_size = data.shape[0]
        self.x_data = np.linspace(0., 100., sample_size)

        points_1 = []

        for k in range(len(y_data_scaled)):
            points_1.append(QPointF(self.x_data[k], y_data_scaled[k]))

        self.m_series_1.replace(points_1)

        # Frequency domain
        y_freq_data = np.abs(fftpack.fft(self.y_original))
        y_freq_data = np.interp(y_freq_data, (y_freq_data.min(), y_freq_data.max()), (0, +10))
        x_freq_data = fftpack.fftfreq(len(self.y_original)) * self.sampling_rate

        axis_x = QValueAxis()
        axis_x.setRange(0, self.sampling_rate / 2)
        axis_x.setLabelFormat("%g")
        axis_x.setTitleText("Frequency [Hz]")

        axis_y = QValueAxis()
        axis_y.setRange(np.min(y_freq_data), np.max(y_freq_data))
        axis_y.setTitleText("Magnitude")

        self.m_chart_2.setAxisX(axis_x, self.m_series_2)
        self.m_chart_2.setAxisY(axis_y, self.m_series_2)

        points_2 = []

        for k in range(len(y_freq_data)):
            points_2.append(QPointF(x_freq_data[k], y_freq_data[k]))

        self.m_series_2.replace(points_2)