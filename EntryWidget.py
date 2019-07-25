from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel, QSizePolicy

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(400, 30)
        #self.setMinimumSize(QtCore.QSize(1000, 30))
        self.setMaximumSize(QtCore.QSize(1000, 30))

        """
        self.frame = QFrame(self)
        self.frame.setGeometry(QtCore.QRect(0, 0, 1000, 30))
        self.frame.setFrameShape(QFrame.VLine)
        self.frame.setFrameShadow(QFrame.Sunken)"""

        self.layoutWidget = QWidget(self)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 4, 1000, 22))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(3)