from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLayout, QLabel, QSizePolicy

class EntryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)