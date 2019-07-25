from PyQt5 import QtCore, QtGui, QtWidgets

class WorkerObject(QtCore.QObject):
    doneSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    @QtCore.pyqtSlot()
    def startWork(self, list):
        self.doneSignal.emit(subjects)