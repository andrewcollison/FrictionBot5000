from PyQt5.QtWidgets import QMessageBox, QWidget


class eMessage():
    def critErrorBox(errMsg):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(errMsg)
        msg.setWindowTitle("Error")
        msg.exec_()  
