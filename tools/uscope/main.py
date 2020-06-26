import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, QIODevice
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtSerialPort import QSerialPort
import pyqtgraph as pg
import numpy as np

from plot_decoder import PlotDecoder

# Basic PyQtGraph settings
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class MainWindow(QMainWindow):
    """Class for running the application window"""

    def __init__(self, *args, **kwargs):
        """Constructor"""

        super(MainWindow, self).__init__(*args, **kwargs)  # Run parent constructor

        layout_main = QVBoxLayout()  # Main vertical layout
        layout_top = QHBoxLayout()  # Layout for top buttons

        # Port control
        layout_port = QFormLayout()
        self.input_port = QLineEdit()
        self.input_port.setText("COM3")
        layout_port.addRow(QLabel("Serial port:"), self.input_port)
        self.button_port = QPushButton(
            "Connect",
            checkable=True,
            toggled=self.on_connect_toggle
        )

        layout_top.addLayout(layout_port)
        layout_top.addWidget(self.button_port)

        layout_main.addLayout(layout_top)

        # Plots
        self.plot = pg.PlotWidget()
        self.plot.showGrid(True, True)

        self.p1 = self.plot.getPlotItem()

        self.console = QTextEdit(readOnly=True)

        layout_main.addWidget(self.plot)
        layout_main.addWidget(self.console)

        # Main window widget
        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

        self.setLayout(layout_main)

        self.setWindowTitle("uScope")
        self.show()

        # Initialize serial
        self.serial = self.serial = QSerialPort(baudRate=QSerialPort.Baud115200, readyRead=self.on_serial_receive)
        self.decoder = PlotDecoder()

        # Prepare data structure
        self.channels = 0  # Wait for serial data, resize on the fly
        self.data = None

        self.set_channels(self.channels)

    @pyqtSlot(bool)
    def on_connect_toggle(self, checked):
        """When the serial `connect` button is pressed"""

        self.button_port.setText("Disconnect" if checked else "Connect")

        self.serial.close()

        if checked:
            port = self.input_port.text()
            self.serial.setPortName(port)
            if self.serial.open(QIODevice.ReadOnly):
                self.input_port.setDisabled(True)
            else:
                self.button_port.setChecked(False)  # Undo toggle
                QMessageBox.warning(self, 'Serial connection', 'Could not connect to device', QMessageBox.Ok)
        else:
            self.input_port.setDisabled(False)

    @pyqtSlot()
    def on_serial_receive(self):
        """"Callback for serial data, already triggered by data"""

        byte = self.serial.read(1)
        if self.decoder.receive(byte):
            self.update_data(self.decoder.channel_size, self.decoder.time, self.decoder.data)

    def update_data(self, channels, time, new_data):
        """Called when new row was received"""

        if self.channels != channels:
            self.set_channels(channels)

        col = np.array(new_data, dtype=float)

        self.data = np.concatenate((self.data, col))

        print(self.data)

    def set_channels(self, channels):
        """Resize number of channels"""

        self.data = np.ndarray([channels, 1], dtype=float)


# Run window when file was called as executable
if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec())
