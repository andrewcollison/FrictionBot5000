from PyQt5 import QtWidgets, uic, QtGui
import sys
from serial import Serial
from PyQt5.QtCore import *
import glob
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from random import seed
from random import random

class serialThread(QThread): # Worker thread
    updateS1 = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.comPort = ""
    

    def run(self):
        ser = Serial(self.comPort)   
        while True:
            ser_bytes = ser.readline()        
            decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            
            currTime = datetime.datetime.now()
            listResults = decoded_bytes[0:5]
            # print(listResults)
            self.updateS1.emit(listResults)
            results =  str(currTime) + ', ' + str(decoded_bytes) + '\n'
            writeFile('test1.csv', results)
            # print(decoded_bytes) 
            
class serialThread2(QThread): # Worker thread
    updateS2 = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.comPort = ""    

    def run(self):
        ser = Serial(self.comPort)   
        while True:
            ser_bytes = ser.readline()        
            decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
            
            currTime = datetime.datetime.now()
            listResults = decoded_bytes[0:5]
            # print(listResults)
            self.updateS2.emit(listResults)
            results =  str(currTime) + ', ' + str(decoded_bytes) + '\n'
            writeFile('test2.csv', results)
            # print(decoded_bytes) 

class plotThread(QThread):
    def __init__(self):
        QThread.__init__(self)    
    
    def run(self):
        df = pd.read_csv("test1.csv", header = None, parse_dates=True, index_col = [0])
        print(df)
        
        # plt.plot(df.index, df[1])
        # plt.show()
        


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('serialTest.ui', self)        
        self.currTime = []
        self.reading = []
        self.currTime2 = []
        self.reading2 = []

        ###### Serial Line 2
        self.button2 = self.findChild(QtWidgets.QPushButton, 'serial_connect_2') # Find the button
        self.button2.clicked.connect(self.comThread2) # Remember to pass the definition/method, not the return value!

        # Drop down 2
        self.comPortSelect2 = self.findChild(QtWidgets.QComboBox, 'com_select_2')        
        self.comPortSelect2.addItems(serial_ports())
        self.comPortSelect2.activated[str].connect(self.comSelect2Changed)
        

        ###### Serial Line 1
        self.button = self.findChild(QtWidgets.QPushButton, 'serial_connect_1') # Find the button
        self.button.clicked.connect(self.comThread) # Remember to pass the definition/method, not the return value!

        # Graph button
        self.graphS1button = self.findChild(QtWidgets.QPushButton, 'graph_s1')
        self.graphS1button.clicked.connect(self.visThread1)

        # Drop down
        self.comPortSelect = self.findChild(QtWidgets.QComboBox, 'com_select')        
        self.comPortSelect.addItems(serial_ports())
        self.comPortSelect.activated[str].connect(self.comSelect1Changed)    

        # Inputs
        self.comInput = self.findChild(QtWidgets.QLineEdit, 'serial_input_1')
        self.comInput2 = self.findChild(QtWidgets.QLineEdit, 'serial_input_2')

        # Display Data
        self.lcdS1 = self.findChild(QtWidgets.QLabel, 's1_output')
        self.lcdS2 = self.findChild(QtWidgets.QLabel, 's2_output')
        
        # Serial Coms
        self.comThread = serialThread()
        self.comThread2 = serialThread2()

        # Plot Data
        self.visThread1 = plotThread()
        # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        self.dataLine = self.graphWidget.plot(self.currTime, self.reading)
        self.dataLine2 = self.graphWidget_2.plot(self.currTime, self.reading)

        self.show()


    # Drop down selection boxes
    def comSelect1Changed(self, text):
        # print(text)
        self.comInput.setText(text)

    def comSelect2Changed(self, text):
        # print(text)
        self.comInput2.setText(text)

    # Serial Com threads
    def comThread(self):
        self.comThread.comPort = self.comInput.text()
        self.comThread.start()
        self.comThread.updateS1.connect(self.evt_updateS1)

    def comThread2(self):
        self.comThread2.comPort2 = self.comInput2.text()
        self.comThread2.start()
        self.comThread2.updateS2.connect(self.evt_updateS2)

    def visThread1(self):
        self.visThread1.start()

    # Update on screen displays
    def evt_updateS1(self, val):
        self.lcdS1.setText(str(val)) 
        self.currTime.append(time.time())
        self.reading.append(float(val))
        self.currTime = self.currTime[-100:]
        self.reading = self.reading[-100:]
        # print(self.reading)
        self.dataLine.setData(self.currTime, self.reading)
        # self.dataLine2.setData(self.currTime, self.reading)

    def evt_updateS2(self, val):
        self.lcdS2.setText(str(val)) 
        self.currTime2.append(time.time())
        self.reading2.append(float(val))
        self.currTime2 = self.currTime2[-100:]
        self.reading2 = self.reading2[-100:]
        # print(self.reading)
        # self.dataLine.setData(self.currTime, self.reading)
        self.dataLine2.setData(self.currTime2, self.reading2)


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = Serial(port)
            s.close()
            result.append(port)
        except (OSError):
            pass
    return result

def writeFile(filename, data):
    file = open(filename, "a")
    file.write(data)
    file.close()



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()