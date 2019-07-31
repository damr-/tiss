from EntryWidget import EntryWidget
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QFrame, QLayout

class CourseWidget(EntryWidget):
    def __init__(self, number, courseType, semester, name, hours, credits, link):
        self.number = number
        self.courseType = courseType
        self.semester = semester
        self.name = name
        self.hours = hours
        self.credits = credits
        self.link = link
        self.t = self.number + " " + self.courseType + " " + self.semester + " " + self.name + " " + \
                            str(self.hours) + "h " + str(self.credits) + "c"
        super().__init__()

    def initUI(self):
        super().initUI()

        self.label = QLabel(self.t, self)
        self.layout.addWidget(self.label)

        self.label2 = QLabel("<a href=\"" + self.link + "\">TISS</a>", self)
        self.label2.setTextFormat(QtCore.Qt.RichText);
        self.label2.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction);
        self.label2.setOpenExternalLinks(True);
        
        self.layout.setSizeConstraint(QLayout.SetFixedSize);
        self.layout.addWidget(self.label2)