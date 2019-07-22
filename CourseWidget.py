from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel, QSizePolicy

class CourseWidget(QWidget):
#TODO make parent class for CourseWidget and EntryWidget
    def __init__(self, number, courseType, semester, name, hours, credits, link):
        super().__init__()
        self.number = number
        self.courseType = courseType
        self.semester = semester
        self.name = name
        self.hours = hours
        self.credits = credits
        self.link = link

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
        self.label.setText("         " + self.number + " " + self.courseType + " " + self.semester + " " + self.name + " " + \
                            str(self.hours) + "h " + str(self.credits) + "c " + self.link)
        self.label.resize(1000, 30)
        self.horizontalLayout.addWidget(self.label)