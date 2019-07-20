import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextBrowser, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from tiss import Subject
from workerobj import WorkerObject
import functools

class App(QWidget):
   #signalStatus = QtCore.pyqtSignal(object)
   semester = "2019W"
   DEBUG_LOG = False

   def __init__(self):
      super().__init__()
      self.initUI()
      self.createWorkerThread()
      #self.connectSignals()

   def initUI(self):
      height = 600
      width = 800

      rec = app.desktop().screenGeometry();
      screenHeight = rec.height();
      screenWidth = rec.width();

      self.button = QPushButton("do", self)
      self.button.move(0, 0)
      self.button.resize(50, 50)
      #self.button.clicked.connect(self.fillTextEdit)

      self.textEdit = QTextBrowser(self)
      self.textEdit.move(70, 70)
      self.textEdit.resize(width * 0.8, height * 0.8)
      self.textEdit.setReadOnly(False)
      self.textEdit.setOpenExternalLinks(True)

      self.setGeometry(screenWidth/2-width/2,screenHeight/2-height/2,width,height)
      self.setWindowTitle("Tiss Program")
      self.show()

   def createWorkerThread(self):
      # Setup the worker object and the worker_thread.
      self.worker = WorkerObject()
      self.worker_thread = QtCore.QThread()
      self.worker.moveToThread(self.worker_thread)
      self.worker_thread.start()

      # Connect any worker signals
      self.worker.signalStatus.connect(self.updateStatus)
      self.button.clicked.connect(functools.partial(self.worker.startWork, self.semester, self.DEBUG_LOG))

   #def connectSignals(self):
      #self.gui.button_cancel.clicked.connect(self.forceWorkerReset)
      #self.signalStatus.connect(self.updateStatus)
      #self.aboutToQuit.connect(self.forceWorkerQuit)

   """def forceWorkerQuit(self):
      if self.worker_thread.isRunning():
         self.worker_thread.terminate()
         self.worker_thread.wait()"""

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