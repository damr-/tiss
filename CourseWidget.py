from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QFrame, QLayout

class Catalogue:
    def __init__(self, name):
        self.name = name
        self.courses = []
    
    def isEmpty(self):
        return len(self.courses) == 0

class Course:
    def __init__(self, number, courseType, semester, name, hours, credits, link):
        self.number = number
        self.courseType = courseType
        self.semester = semester
        self.name = name
        self.hours = hours
        self.credits = credits
        self.link = link

    def sameAs(self, otherCourse):
        return self.number == otherCourse.number and self.name == otherCourse.name and \
                self.courseType == otherCourse.courseType and self.semester == otherCourse.semester and \
                self.link == otherCourse.link and self.hours == otherCourse.hours and self.credits == otherCourse.credits

    
class CourseWidget(QWidget):

    HIDE_NUMBER = 0
    HIDE_HOURS = 1
    hiddenInfo = { HIDE_NUMBER: False, HIDE_HOURS: False }

    def __init__(self, course):
        super().__init__()
        self.course = course
        self.hideableInfos = []
        self.initUI()
        
    def initUI(self):        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)

        self.numberLabel = QLabel(self.course.number, self)
        self.layout.addWidget(self.numberLabel)

        self.typeLabel = QLabel(self.course.courseType, self)
        self.layout.addWidget(self.typeLabel)

        self.semesterLabel = QLabel(self.course.semester, self)
        self.layout.addWidget(self.semesterLabel)

        self.nameLabel = QLabel(self.course.name, self)
        self.layout.addWidget(self.nameLabel)
        
        self.hoursLabel = QLabel(str(self.course.hours)+"h", self)
        self.layout.addWidget(self.hoursLabel)
        
        self.creditsLabel = QLabel(str(self.course.credits)+"c", self)
        self.layout.addWidget(self.creditsLabel)

        self.linkLabel = QLabel(self.course.link, self)
        self.layout.addWidget(self.linkLabel)
        
        self.label2 = QLabel("<a href=\"" + str(self.course.link) + "\">TISS</a>", self)
        self.label2.setTextFormat(QtCore.Qt.RichText);
        self.label2.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction);
        self.label2.setOpenExternalLinks(True);
        
        self.layout.setSizeConstraint(QLayout.SetFixedSize);
        self.layout.addWidget(self.label2)

        self.hideableInfos.append(self.numberLabel)
        self.hideableInfos.append(self.hoursLabel)

        for idx,value in enumerate(CourseWidget.hiddenInfo.values()):
            if value:
                self.hideableInfos[idx].setVisible(False)

    def setInfoHidden(self, infoIdx, hide):
        self.hideableInfos[infoIdx].setVisible(not hide)
        CourseWidget.hiddenInfo[infoIdx] = hide