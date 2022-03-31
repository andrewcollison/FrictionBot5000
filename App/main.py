import csv
from socket import IPV6_MULTICAST_IF
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
import os
from PyQt5.QtWidgets import QMessageBox, QWidget
from motorInterface import motorInterface
from popUpMessage import eMessage

class startTestThread(QThread):
    updateTestStop = pyqtSignal(str)
    updateTestPause = pyqtSignal(str)
    updateTestStatus = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        
        self.testName = ''
        self.testWeightInput = ''
        self.testDwellInput = ''
        self.testFeetInput = ''
        self.testNCyclesInput = ''
        self.testTravelInput = ''
        self.testAuthorInput = ''
        self.testTempInput = ''
        self.homeP = 100
        self.minP = 75
        self.maxP = 3000

    def run(self):
        self._go = True
        print('Test Started')
        print(self.testName)
        print(self.testWeightInput)
        print(self.testDwellInput)
        print(self.testFeetInput)
        print(self.testNCyclesInput)

        # Save test paramaters 
        paramInputs = {'Param': ['test_Name', 'Author', 'Temp' ,'Weight', 'Dwell', 'Feet_Size', 'Num_Cycles', 'Travel_Len'],
                        'Value': [self.testName, self.testAuthorInput, self.testTempInput, self.testWeightInput, 
                                    self.testDwellInput, self.testFeetInput, self.testNCyclesInput, self.testTravelInput]}
        data = pd.DataFrame(data = paramInputs)
        
        paramFileName = str(self.testName) + '_params.csv'
        paramFilePath = str('./Results/') + str(self.testName)
        if not os.path.exists('Results'): os.makedirs(paramFilePath)
        if not os.path.exists(paramFilePath): os.makedirs(paramFilePath)


        paramPath = './Results/' + self.testName + '/' + paramFileName
        data.to_csv(paramPath, index = False)
        
        #### Start testing Cycle ####
        motor = motorInterface()

        # Move to home position aka Position One        
        motor.moveMotor(self.homeP)
        print("Moving Home")
        self.updateTestStatus.emit('Moving to home')
        time.sleep(30)


        nCycle = 0
        while self._go:
            if nCycle < int(self.testNCyclesInput):
                # Move to Position 1: should be the same as home position
                motor.moveMotor(self.homeP)
                time.sleep(5)
                self.updateTestStatus.emit('Dwell')
                print("Dwell process")
                time.sleep(int(self.testDwellInput))

                # Moving to position 2
                motor.moveMotor(self.maxP)
                self.updateTestStatus.emit('Moving to P2')
                self.updateTestPause.emit('False') # Starting data record
                time.sleep(30) # Time to move to P2                

                # Move back to Position 1
                motor.moveMotor(self.homeP)
                self.updateTestPause.emit('True')
                time.sleep(5)
                self.updateTestStatus.emit('Moving to home')
                
                

                nCycle = nCycle + 1

            else:
                self._go = False
                self.updateTestStop.emit('True')
                self.updateTestStatus.emit('Test Finished')
                print('Test Finished')                


        #         motorControl.motor2target(100) # home position


        #         # print('moving to home')
        #         # print(str(nCycle))
        #         # self.updateTestPause.emit('True')

        #         # time.sleep(5) # Dwell time
        #         # self.updateTestPause.emit('False')
        #         # motorControl.motor2Position(6666) # Target position
        #         # print('moving to target')
        #         # time.sleep(2.5) # Time to travel
        #         # nCycle = nCycle + 1

        #     else:
        #         self._go = False
        #         self.updateTestStop.emit('True')
        #         print('Test Finished')

    def stop(self):
        self._go = False

class serialThread(QThread): # Worker thread
    updateS1 = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.comPort = ""
        self.testName = ""
        self.cycleNum = 0         

    def run(self):
        ser = Serial(self.comPort)   
        self._go = True 
        self._paused = True
        listResults = []
        while self._go:
            if self._paused == False:
                ser_bytes = ser.readline()        
                decoded_bytes = str(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))                
                currTime = datetime.datetime.now()
                listResults = decoded_bytes[0:5]
                self.updateS1.emit(listResults)
                results =  str(currTime) + ', ' + str(decoded_bytes) + '\n'
                paramFileName = str(self.testName)
                paramPath = './Results/' + self.testName + '/' + paramFileName + '_' + str(self.cycleNum) + '_sg.csv'
                print(str(self.cycleNum))
                writeFile(paramPath, results)
            elif self._paused == True:
                results = [] # this clears the results buffer between cycles

    def pause(self):
        self._paused = True
        # print('test paused')

    def unPause(self):
        self._paused = False
        self.cycleNum = self.cycleNum +1

    def stop(self):
        self._go = False     

# Motor Interface thread
class motorThread(QThread): # Worker thread
    updateCurrP = pyqtSignal(str)
    updateCurrT = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.testName = ""
        self.cycleNum = 0         

    def run(self):
        self._go = True 
        self._paused = True
        self._target = None
        print("Motor Thread Started!!!")
        while self._go:
            if self._paused == False:
                currP = motorInterface.getPos(self)
                self.updateCurrP.emit(str(currP))
                currT = motorInterface.getTarget(self) 
                self.updateCurrT.emit(str(currT))               
                currTime = datetime.datetime.now()
                results =  str(currTime) + ', ' + str(currP) + ', '+ str(currT) + '\n'
                paramFileName = str(self.testName)
                paramPath = './Results/' + self.testName + '/' + paramFileName + '_' + str(self.cycleNum) + '_motor.csv'
                writeFile(paramPath, results) 

            elif self._paused == True:
                results = [] # this clears the results buffer between cycles

    def pause(self):
        self._paused = True
        # print('test paused')

    def unPause(self):
        self._paused = False
        self.cycleNum = self.cycleNum +1

    def stop(self):
        self._go = False 




class plotThread(QThread):
    def __init__(self):
        QThread.__init__(self)    
    
    def run(self):
        df = pd.read_csv("test1.csv", header = None, parse_dates=True, index_col = [0])
        print(df)        


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('serialTest.ui', self)        
        self.currTime = []
        self.reading = []
        # self.testStopFlag = False

        ###### Serial Line 1
        self.button = self.findChild(QtWidgets.QPushButton, 'serial_connect_1') # Find the button
        # self.button.clicked.connect(self.comThread) # Remember to pass the definition/method, not the return value!

        # Drop down
        self.comPortSelect = self.findChild(QtWidgets.QComboBox, 'com_select')        
        self.comPortSelect.addItems(serial_ports())
        self.comPortSelect.activated[str].connect(self.comSelect1Changed)    

        # Inputs
        self.comInput = self.findChild(QtWidgets.QLineEdit, 'serial_input_1')

        # Display Data
        self.lcdS1 = self.findChild(QtWidgets.QLabel, 's1_output')
        self.lcdCurrT = self.findChild(QtWidgets.QLabel, 'currT_out')
        self.lcdCurrP = self.findChild(QtWidgets.QLabel, 'currP_out')
        self.lcdCurrStat = self.findChild(QtWidgets.QLabel, 'stat_out')

        # Test Paramater Input
        self.testNameInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_1')
        self.testWeightInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_2')
        self.testDwellInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_3')
        self.testFeetInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_4')
        self.testNCyclesInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_5')
        self.testTravelInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_6')
        self.testAuthorInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_9')
        self.testTempInput = self.findChild(QtWidgets.QLineEdit, 'meta_input_8')
        

        # Start Test
        self.startTestButton = self.findChild(QtWidgets.QPushButton, 'start_test')
        self.startTestButton.clicked.connect(self.startTestThread)
        # self.startTestButton.clicked.connect(self.comThread)

        # Stop Test
        self.stopTestButton = self.findChild(QtWidgets.QPushButton, 'stop_test')
        self.stopTestButton.clicked.connect(self.stopTest)
        
        # Serial Coms
        self.comThread = serialThread()
        self.startTestThread = startTestThread() 
        self.mThread = motorThread()               

        # Plot Data
        self.visThread1 = plotThread()
        # self.plot([1,2,3,4,5,6,7,8,9,10], [30,32,34,32,33,31,29,32,35,45])

        self.dataLine = self.graphWidget.plot(self.currTime, self.reading)

        self.show()

    # Drop down selection boxes
    def comSelect1Changed(self, text):
        # print(text)
        self.comInput.setText(text)

   

    def visThread1(self):
        self.visThread1.start()

    # Update on screen displays
    def evt_updateS1(self, val):
        self.lcdS1.setText(str(val)) 
        self.currTime.append(time.time())
        self.reading.append(float(val))
        self.currTime = self.currTime[-100:]
        self.reading = self.reading[-100:]        
        self.dataLine.setData(self.currTime, self.reading)

    def evt_updateCurrT(self, val):
        self.lcdCurrT.setText(str(val)) 
        # self.currTime.append(time.time())
        # self.reading.append(float(val))
        # self.currTime = self.currTime[-100:]
        # self.reading = self.reading[-100:]        
        # self.dataLine.setData(self.currTime, self.reading)

    def evt_updateCurrP(self, val):
        self.lcdCurrP.setText(str(val))

    def evt_updateStat(self, val):
        self.lcdCurrStat.setText(str(val))

    def evt_updateTestStop(self, val):
        if str(val) == 'True':
            # print('Hold up mother fucker')
            self.stopTest()

    def evt_updateTestPause(self, val):
        if str(val) == 'True':
            print('Pause Bitch')
            self.pauseTest()
        
        elif str(val) == 'False':
            self.unPauseTest()
            
    
    def startTestThread(self):
        path = 'Results/'+str(self.testNameInput.text())
        print(self.comInput.text())
        if self.testNameInput.text() == '':
            eMessage.critErrorBox('No test name')
        elif os.path.exists(path): 
            print('you suck, file already exists')            
            eMessage.critErrorBox('Test name already exists')

        elif self.comInput.text() == '':
            print('com port fuckup')            
            eMessage.critErrorBox('Com port not selected')

        elif self.testNCyclesInput.text() == '':
            eMessage.critErrorBox('Num Cycles must be > 0')

        elif self.testDwellInput.text() == '':
            eMessage.critErrorBox('Dwell Time must be > 0')        
        else:
            # Start the test control thread
            self.startTestThread.testName = self.testNameInput.text()
            self.startTestThread.testWeightInput = self.testWeightInput.text()
            self.startTestThread.testDwellInput = self.testDwellInput.text()
            self.startTestThread.testFeetInput = self.testFeetInput.text()
            self.startTestThread.testNCyclesInput = self.testNCyclesInput.text()
            self.startTestThread.testTravelInput = self.testTravelInput.text()
            self.startTestThread.testAuthorInput = self.testAuthorInput.text()
            self.startTestThread.testTempInput = self.testTempInput.text()
            self.startTestThread.start()

            # Start the serial com thread for the strain gauge 
            self.comThread.comPort = self.comInput.text()
            self.comThread.testName = self.testNameInput.text()
            self.comThread._go = True
            self.comThread.start()
            self.comThread.updateS1.connect(self.evt_updateS1)
            self.startTestThread.updateTestStop.connect(self.evt_updateTestStop)
            self.startTestThread.updateTestPause.connect(self.evt_updateTestPause)
            self.startTestThread.updateTestStatus.connect(self.evt_updateStat)

            # Start the motorThread
            self.mThread.testName = self.testNameInput.text()
            self.mThread.start()
            self.mThread._go = True
            self.mThread.updateCurrT.connect(self.evt_updateCurrT) 
            self.mThread.updateCurrP.connect(self.evt_updateCurrP)
            

    def stopTest(self):
        # Stop com thread
        self.startTestThread.stop()
        self.comThread.stop()
        # Stop motor thread
        self.mThread.stop()


    def pauseTest(self):
        self.comThread.pause()
        self.mThread.pause()

    def unPauseTest(self):
        self.comThread.unPause()
        self.mThread.unPause()


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