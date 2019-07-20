from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import random
from tiss import getData
from tiss import Subject

class WorkerObject(QtCore.QObject):
    signalStatus = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    @QtCore.pyqtSlot()        
    def startWork(self, semester, DEBUG_LOG):
        subjects = getData(semester, DEBUG_LOG)
        #TODO maybe move getData logic here and emit signals throughout the process for updating the user/UI
        self.signalStatus.emit(subjects)