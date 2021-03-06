from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QFrame, QLayout

class Catalogue:
    catalogueLetters = ['A', 'B', 'C', 'D']

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
        self.hours = float(hours)
        self.credits = float(credits)
        self.link = link

    def sameAs(self, otherCourse):
        return self.number == otherCourse.number and self.name == otherCourse.name and \
                self.courseType == otherCourse.courseType and self.semester == otherCourse.semester and \
                self.link == otherCourse.link and self.hours == otherCourse.hours and self.credits == otherCourse.credits

    def existsInCurriculum(self, curriculumCatalogue):
        reason = 0
        for course in curriculumCatalogue:
            if course.name == self.name:
                if course.courseType == self.courseType:
                    if course.credits == self.credits:
                        return -1
                    else:
                        reason = 2
                else:
                    reason = 1
        return reason
    
class CourseWidget(QWidget):

    HIDE_NUMBER = 0
    HIDE_HOURS = 1
    hiddenInfo = { HIDE_NUMBER: False, HIDE_HOURS: False }
    greyStyleSheet = "QLabel {color : grey}"

    def __init__(self, course, isPersonal):
        super().__init__()
        self.course = course
        self.hideableInfos = []
        self.isHighlit = self.isGreyedOut = False
        self.initUI(isPersonal)
        
    def initUI(self, isPersonal):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)

        self.feedbackLabel = QLabel("", self)
        self.layout.addWidget(self.feedbackLabel)

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
        
        self.linkLabel = QLabel("<a href=\"" + str(self.course.link) + "\">TISS</a>", self)
        self.linkLabel.setTextFormat(QtCore.Qt.RichText);
        self.linkLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction);
        self.linkLabel.setOpenExternalLinks(True);
        
        self.layout.setSizeConstraint(QLayout.SetFixedSize);
        self.layout.addWidget(self.linkLabel)

        self.hideableInfos.append(self.numberLabel)
        self.hideableInfos.append(self.hoursLabel)

        for idx,value in enumerate(CourseWidget.hiddenInfo.values()):
            if value:
                self.hideableInfos[idx].setVisible(False)

        if isPersonal:
            self.feedbackLabel.setVisible(False)

    def setGreyedOut(self, greyedOut):
        if self.isGreyedOut == greyedOut:
            return
        self.isGreyedOut = greyedOut

        if greyedOut:
            self.setHighlit(False)
            
        self.removeFeedback()
        ss = ""
        if greyedOut:
            ss = CourseWidget.greyStyleSheet
        self.setStyleSheet(ss)
        self.repaint()

    def setHighlit(self, highlit):
        if self.isHighlit == highlit:
            return
        self.isHighlit = highlit

        if highlit:
            self.setGreyedOut(False)

        self.setStyleSheet("")
        ss = ""
        if highlit:
            ss = "QLabel { background-color: yellow; }"
        self.feedbackLabel.setStyleSheet(ss)
        self.feedbackLabel.repaint()

    def setInfoHidden(self, infoIdx, hide):
        self.hideableInfos[infoIdx].setVisible(not hide)
        CourseWidget.hiddenInfo[infoIdx] = hide

    def setNegativeFeedback(self, reason):
        self.setHighlit(False)
        textStyle = "QLabel { color : red; }"
        color = "red"
        if reason == 1:
            self.typeLabel.setStyleSheet(textStyle)
            color = "orange"
        elif reason == 2:
            self.creditsLabel.setStyleSheet(textStyle)
            color = "orange"
        self.feedbackLabel.setStyleSheet("QLabel { background-color: " + color + "; }")
        self.feedbackLabel.repaint()

    def removeFeedback(self):
        self.feedbackLabel.setStyleSheet("")
        self.typeLabel.setStyleSheet("")
        self.creditsLabel.setStyleSheet("")
        self.repaint()