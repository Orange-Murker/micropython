from PyQt5.QtWidgets import *


def on_button_clicked():
    alert = QMessageBox()
    alert.setText('You clicked the button!')
    alert.exec_()


app = QApplication([])

button = QPushButton('Click')

button.clicked.connect(on_button_clicked)
button.show()
app.exec_()
