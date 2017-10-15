import sys
from mainwindow import Ui_MainWindow
from PyQt5.QtCore import QTimer
import os
import subprocess
import re
from PyQt5 import QtCore, QtGui, QtWidgets

class MyWin(QtWidgets.QMainWindow):
    sleepTimeOld = 0
    oldState = ""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connections
        self.ui.changeButton.clicked.connect(self.MyFunction)
        self.ui.sleepSlider.valueChanged.connect(self.refreshTime)

        #getting parametres from system
        powerDictionary = self.getParametres()
        self.sleepTimeOld = powerDictionary["Standby"]

        #getting parametres of battery
        batteryDictionary = self.getBatteryinfo()
        self.ui.batteryNameLabel.setText("Battery name: " + batteryDictionary["native-path"])
        self.ui.statusValueLabel.setText(batteryDictionary["state"])
        self.ui.percentageValueLabel.setText(batteryDictionary["percentage"])
        self.oldState = batteryDictionary["state"]

        self.ui.sleepDelayLabel.setText(str(0))


    #button_on_click action
    def MyFunction(self):
        self.changeSleep(str(self.ui.sleepSlider.value()))

    #action of refrehing time label form slider
    def refreshTime(self, p_int):
        self.ui.sleepDelayLabel.setText(str(p_int))

    #action of refreshing all window
    def refresh(self):
        batteryDictionary = self.getBatteryinfo()
        self.ui.batteryNameLabel.setText("Battery name: " + batteryDictionary["native-path"])
        self.ui.statusValueLabel.setText(batteryDictionary["state"])
        self.ui.percentageValueLabel.setText(batteryDictionary["percentage"] + " " + batteryDictionary["time to "])
        if batteryDictionary["state"] != self.oldState and batteryDictionary["state"] != "discharging":
            self.changeSleep(self.sleepTimeOld)
            print("not discharge")
        self.oldState = batteryDictionary["state"]

        sleepDict = self.getParametres()
        self.ui.sleepLabel.setText("Время до выключения: " + sleepDict["Standby"])

    #getting parametres of system (sleeping delay)
    def getParametres(self):
        subprocess.call("xset -q | grep Standby: > " + os.getcwd() + "/log.txt", shell=True)
        # open temp file "/log.txt"
        logfile = open(os.getcwd() + "/log.txt")
        powerDictionary = {(y.split(": ")[0])[1:]: y.split(": ")[1] for y in logfile.readline()[1:-1].split("   ")}
        logfile.close()
        return powerDictionary

    #getting parametres of battery
    def getBatteryinfo(self):
        subprocess.call("upower -i $(upower -e | grep 'BAT') > " + os.getcwd() + "/log.txt", shell=True)
        # open temp file "/log.txt"
        logfile = open(os.getcwd() + "/log.txt")
        # create keys of information about hd disk
        keys = ["native-path", "state", "time to ", "percentage", "technology"]
        # create dictianory with information about parameteres of hd disk
        batteryDictionary = {k: None for k in keys}
        for i in logfile:
            for j in keys:
                if (j in i):
                    if (j == "time to "):
                        a = (re.split(r" +",(i.split(j)[1])))
                        batteryDictionary[j] = a[1] + " " + a[2]
                    else:
                        list = re.split(r" +", (i.split(j + ":")[1])[:-1])
                        batteryDictionary[j] = list[1]
        logfile.close()
        return batteryDictionary

    #action for changing sleep delay
    def changeSleep(self, delay):
        subprocess.call("xset dpms " + delay, shell=True)

    #close action
    def closeEvent(self, event):
        self.changeSleep(self.sleepTimeOld)
        event.accept()


if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWin()

    window.show()
    
    #creating timer for refresh main window
    timer = QTimer()
    timer.timeout.connect(window.refresh)
    timer.start(1000)

    sys.exit(app.exec_())
