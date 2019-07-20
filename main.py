import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextBrowser, QPushButton, QDesktopWidget
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from tiss import Subject
from workerobj import WorkerObject
import functools

class App(QWidget):
    #signalStatus = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupWorkerThread()
        #self.connectSignals()
    
    def initUI(self):
        self.semester = "2019W"
        self.DEBUG_LOG = False
        height = 600
        width = 800
        
        self.button = QPushButton("do", self)
        self.button.move(0, 0)
        self.button.resize(50, 50)
        #button.clicked.connect(self.fillself.textEdit)

        self.textEdit = QTextBrowser(self)
        self.textEdit.move(70, 70)
        self.textEdit.resize(width * 0.8, height * 0.8)
        self.textEdit.setReadOnly(False)
        self.textEdit.setOpenExternalLinks(True)

        self.resize(width,height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")
        self.show()

    def setupWorkerThread(self):
        # Setup the worker object and the worker_thread.
        worker = WorkerObject()
        worker_thread = QtCore.QThread(self)
        worker.moveToThread(worker_thread)
        worker_thread.start()

        # Connect any worker signals
        worker.signalStatus.connect(self.updateStatus)
        self.button.clicked.connect(functools.partial(worker.startWork, self.semester, self.DEBUG_LOG))

        #def connectSignals(self):
            #self.gui.button_cancel.clicked.connect(self.forceWorkerReset)
            #self.signalStatus.connect(self.updateStatus)
            #self.aboutToQuit.connect(self.forceWorkerQuit)

        """def forceWorkerQuit(self):
            if worker_thread.isRunning():
                worker_thread.terminate()
                worker_thread.wait()"""

    @QtCore.pyqtSlot(object)
    def updateStatus(self, subjects):
        text = "" 
        for s in subjects:
            text += s.name + "\n"
            for m in s.modules:
                text += "  " + m.name + "\n"
                for c in m.catalogues:
                    text += "    " + c.name + "\n"
                    for co in c.courses:
                        text += "      " + co.name + "\n"
                        for ci in co.courseInfos:
                            text += "        " + ci.number + " " + ci.courseType + " " + ci.semester + " " + ci.name + " " + str(ci.hours) + "h " + str(ci.credits) + "c " + ci.link + "\n"
                for co2 in m.courses:
                    text += "      " + co2.name + "\n"
                    for ci2 in co2.courseInfos:
                        text += "        " + ci2.number + " " + ci2.courseType + " " + ci2.semester + " " + ci2.name + " " + str(ci2.hours) + "h " + str(ci2.credits) + "c " + ci2.link + "\n"
        self.textEdit.setText(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())