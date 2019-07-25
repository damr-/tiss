from EntryWidget import EntryWidget
from PyQt5.QtWidgets import QLabel

class CourseWidget(EntryWidget):
    def __init__(self, number, courseType, semester, name, hours, credits, link):
        self.number = number
        self.courseType = courseType
        self.semester = semester
        self.name = name
        self.hours = hours
        self.credits = credits
        self.link = link
        self.t = "         " + self.number + " " + self.courseType + " " + self.semester + " " + self.name + " " + \
                            str(self.hours) + "h " + str(self.credits) + "c " + self.link
        super().__init__()

    def initUI(self):
        super().initUI()
        self.numberLabel = QLabel(self)
        self.numberLabel.setText(self.number)
        self.numberLabel.resize(10, 30)
        self.horizontalLayout.addWidget(self.numberLabel)
        
        self.typeLabel = QLabel(self)
        self.typeLabel.setText(self.courseType)
        self.typeLabel.resize(10, 30)
        self.horizontalLayout.addWidget(self.typeLabel)

        self.tmpLabel = QLabel(self)
        x = self.semester + " " + self.name + " " + str(self.hours) + "h " + str(self.credits) + "c " + self.link
        self.tmpLabel.setText(x)
        #self.tmpLabel.resize(100, 30)
        self.horizontalLayout.addWidget(self.tmpLabel)
        