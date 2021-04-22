from PyQt5 import QtCore, QtWidgets, QtSerialPort


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.portname_comboBox = QtWidgets.QComboBox()
        self.baudrate_comboBox = QtWidgets.QComboBox()

        for info in QtSerialPort.QSerialPortInfo.availablePorts():
            self.portname_comboBox.addItem(info.portName())

        for baudrate in QtSerialPort.QSerialPortInfo.standardBaudRates():
            self.baudrate_comboBox.addItem(str(baudrate), baudrate)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        lay = QtWidgets.QFormLayout(self)
        lay.addRow("Port Name:", self.portname_comboBox)
        lay.addRow("BaudRate:", self.baudrate_comboBox)
        lay.addRow(buttonBox)
        self.setFixedSize(self.sizeHint())

    def get_results(self):
        return self.portname_comboBox.currentText(), self.baudrate_comboBox.currentData()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.lcd_StartBtn = QtWidgets.QPushButton(
            "Send",
            clicked=self.send
        )
        self.lcd_lineEdit = QtWidgets.QLineEdit()
        self.light_lineEdit = QtWidgets.QLineEdit(readOnly=True)

        self.connect_btn = QtWidgets.QPushButton(
            "Connect",
            clicked=self.connectToPort
        )
        self.disconnect_btn = QtWidgets.QPushButton(
            "Disconnect",
            clicked=self.disconnectFromPort
        )
        self.configure_btn = QtWidgets.QPushButton(
            "Configure",
            clicked=self.open_dialog
        )
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QFormLayout(central_widget)
        lay.addRow(self.connect_btn)
        lay.addRow(self.disconnect_btn)
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.lcd_lineEdit)
        hlay.addWidget(self.lcd_StartBtn)
        lay.addRow(hlay)
        lay.addWidget(self.light_lineEdit)
        lay.addRow(self.configure_btn)

        self.serial = QtSerialPort.QSerialPort(
            self,
            readyRead=self.receive
        )

    @QtCore.pyqtSlot()
    def open_dialog(self):
        dialog = Dialog()
        if dialog.exec_():
            portname, baudrate = dialog.get_results()
            self.serial.setPortName(portname)
            self.serial.setBaudRate(baudrate)

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            self.light_lineEdit.setText(text)
            print(text)

    @QtCore.pyqtSlot()
    def send(self):
        self.serial.write(self.lcd_lineEdit.text().encode())

    @QtCore.pyqtSlot()
    def connectToPort(self):
        self.serial.open(QtCore.QIODevice.ReadWrite)

    @QtCore.pyqtSlot(bool)
    def disconnectFromPort(self):
        self.serial.close()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())