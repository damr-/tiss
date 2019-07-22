from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel, QSizePolicy

class EntryWidget(QWidget):

    def __init__(self, text):
        super().__init__()
        self.text = text

        self.initUI()

    def initUI(self):
        self.setObjectName("CourseWidget")
        self.resize(400, 30)
        self.setMinimumSize(QtCore.QSize(1000, 30))
        self.setMaximumSize(QtCore.QSize(1000, 30))

        self.line = QFrame(self)
        self.line.setGeometry(QtCore.QRect(0, 0, 1000, 30))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.layoutWidget = QWidget(self)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 4, 181, 22))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.label  = QLabel(self)
        self.label.setText(self.text)
        self.label.resize(1000, 30)
        self.horizontalLayout.addWidget(self.label)