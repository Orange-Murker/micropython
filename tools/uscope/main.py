import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtCore import pyqtSlot, QIODevice, pyqtSignal
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import pyqtgraph as pg
import numpy as np
import json

from plot_decoder import PlotDecoder


class ComboBox(QComboBox):
    """Extend QComboBox widget to handle click event"""

    popupAboutToBeShown = pyqtSignal()

    def showPopup(self):
        """Fire event first, then call parent popup method"""
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()


class MainWindow(QMainWindow):
    """Class for running the application window"""

    LINECOLORS = ['y', 'm', 'r', 'g', 'c', 'w', 'b']

    def __init__(self, *args, **kwargs):
        """Constructor"""

        super(MainWindow, self).__init__(*args, **kwargs)  # Run parent constructor

        layout_main = QVBoxLayout()  # Main vertical layout
        layout_top = QHBoxLayout()  # Layout for top buttons
        layout_bottom = QVBoxLayout()  # Layout for channels

        # Port control
        layout_port = QFormLayout()
        self.input_port = ComboBox()
        self.input_port.popupAboutToBeShown.connect(self.find_devices)
        self.find_devices()
        layout_port.addRow(QLabel("Serial port:"), self.input_port)
        self.button_port = QPushButton(
            "Connect",
            checkable=True,
            toggled=self.on_connect_toggle
        )

        # Data size
        self.input_size = QLineEdit()
        self.input_size.setValidator(QIntValidator(5, 1000000))
        self.input_size.setText("200")
        layout_port.addRow(QLabel("Samples:"), self.input_size)

        # Overlay
        self.input_overlay = QCheckBox()
        layout_port.addRow(QLabel("Overlay channels:"), self.input_overlay)

        layout_top.addLayout(layout_port)
        layout_top.addWidget(self.button_port)

        layout_main.addLayout(layout_top)

        # Plots
        self.layout_plots = pg.GraphicsLayoutWidget()
        layout_bottom.addWidget(self.layout_plots)

        self.plots = []  # Start with empty plots
        self.curves = []

        layout_main.addLayout(layout_bottom)

        # Main window widget
        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

        self.setWindowTitle("uScope")
        self.show()

        # Initialize serial
        self.serial = QSerialPort(baudRate=QSerialPort.Baud115200, readyRead=self.on_serial_receive)
        self.decoder = PlotDecoder()

        # Prepare data structure
        self.channels = 0  # Wait for serial data, resize on the fly
        self.data = None  # Received data, each row is a channel
        self.time = None  # Timestamps of each data column
        self.data_points = 0  # Number of points recorded
        self.data_size = 1  # Number of points in history
        self.time_offset = None  # Time offset in microseconds
        self.overlay = False  # When true, all plots should be combined in one plot

        self.set_channels(self.channels)

        # Load previous settings
        self.load_settings()

    @pyqtSlot(bool)
    def on_connect_toggle(self, checked):
        """When the serial `connect` button is pressed"""

        self.button_port.setText("Disconnect" if checked else "Connect")

        self.serial.close()

        if checked:
            port = self.input_port.currentData()
            self.serial.setPortName(port)
            if self.serial.open(QIODevice.ReadOnly):  # If serial opened successfully
                self.input_port.setDisabled(True)
                self.input_size.setDisabled(True)
                self.input_overlay.setDisabled(True)
                self.start_recording()
            else:
                self.button_port.setChecked(False)  # Undo toggle
                QMessageBox.warning(self, 'Serial connection', 'Could not connect to device', QMessageBox.Ok)
        else:
            self.input_port.setDisabled(False)
            self.input_size.setDisabled(False)
            self.input_overlay.setDisabled(False)

    @pyqtSlot()
    def on_serial_receive(self):
        """"
        Callback for serial data, already triggered by data

        It's important all available bytes are consumed, because this call-back cannot keep up with incoming streams
        at real-time!
        """

        new_bytes = self.serial.readAll()

        for byte in new_bytes:
            if self.decoder.receive_byte(byte):
                self.update_data(self.decoder.channel_size, self.decoder.time, self.decoder.data)

    def load_settings(self):
        """Load settings from file"""
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                if 'port' in settings and settings['port']:
                    self.input_port.setCurrentIndex(
                        self.input_port.findData(settings['port'])
                    )
                if 'size' in settings and settings['size'] > 0:
                    self.input_size.setText(str(settings['size']))
                if 'overlay' in settings:
                    self.input_overlay.setChecked(settings['overlay'])
        except FileNotFoundError:
            return  # Do nothing
        except json.decoder.JSONDecodeError:
            return  # DO nothing

    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'port': self.serial.portName(),
            'size': self.data_size,
            'overlay': self.overlay
        }
        with open("settings.json", "w") as file:
            file.write(json.dumps(settings))

    def closeEvent(self, event):
        """When main window is closed"""
        self.serial.close()
        self.save_settings()

    def find_devices(self):
        """Set found serial devices into dropdown"""
        ports = QSerialPortInfo.availablePorts()

        self.input_port.clear()

        for port in ports:

            label = port.portName()
            if port.description:
                label += " - " + port.description()

            self.input_port.addItem(label, port.portName())

    def start_recording(self):
        """Called when recording should start (e.g. when `connect` was hit)"""
        self.channels = 0  # Force an update on the next data point
        self.data_points = 0
        self.data_size = int(self.input_size.text())
        self.overlay = self.input_overlay.isChecked()

        self.serial.clear()  # Get rid of data in buffer

    def update_data(self, channels, time, new_data):
        """Called when new row was received"""

        if self.channels != channels:
            self.set_channels(channels)

        col = np.array(new_data, dtype=float)
        self.data = np.roll(self.data, -1, axis=1)  # Rotate backwards
        self.data[:, -1] = col[:, 0]  # Set new column at the end

        self.time = np.roll(self.time, -1)  # Rotate backwards

        if self.time_offset is None:
            self.time_offset = time

        self.time[0, -1] = (time - self.time_offset) / 1000000

        self.data_points += 1

        self.update_plots()

    def update_plots(self):
        """With data already updated, update plots"""

        if self.data_points < self.data_size:
            data_x = self.time[:, -self.data_points:]
            data_y = self.data[:, -self.data_points:]
        else:
            data_x = self.time
            data_y = self.data

        for i, curve in enumerate(self.curves):
            curve.setData(x=data_x[0, :], y=data_y[i, :])

    def set_channels(self, channels):
        """
        Resize number of channels

        Also functions as a reset between recordings, also sets new plot windows and curves
        """

        self.channels = channels
        self.data = np.zeros((channels, self.data_size))
        self.time = np.zeros((1, self.data_size))
        self.time_offset = None
        self.data_points = 0

        self.create_plots()

    def create_plots(self):
        """Create the desired plots and curves"""

        # Clear old
        for plot in self.plots:
            plot.clear()
            self.layout_plots.removeItem(plot)

        self.plots = []
        self.curves = []

        if self.overlay:
            new_plot = self.layout_plots.addPlot(row=0, col=0, title="Channels")

            for i in range(self.channels):
                new_curve = new_plot.plot()
                self.curves.append(new_curve)

            self.plots.append(new_plot)

        else:
            for i in range(self.channels):
                new_plot = self.layout_plots.addPlot(row=i, col=0, title="Ch{}".format(i))
                new_plot.showGrid(False, True)

                new_curve = new_plot.plot()

                self.plots.append(new_plot)
                self.curves.append(new_curve)

        # Set style
        for plot in self.plots:
            plot.showGrid(False, True)

        for i, curve in enumerate(self.curves):
            c = self.LINECOLORS[i % len(self.LINECOLORS)]  # Set automatic colors
            pen = pg.mkPen(c, width=2)
            curve.setPen(pen)


# Run window when file was called as executable
if __name__ == '__main__':

    app = QApplication([])
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon('logo.ico'))
    window = MainWindow()
    sys.exit(app.exec())
