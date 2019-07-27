from EntryWidget import EntryWidget
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QSizePolicy, QLayout

class CategoryWidget(EntryWidget):
    # CategoryTypes
    SUBJECT = 1
    MODULE = 2
    CATALOGUE = 3
    COURSE = 4

    MinHeight = 20

    def __init__(self, categoryName, categoryType):
        self.categoryName = categoryName
        self.categoryType = categoryType
        super().__init__()

    def initUI(self):
        super().initUI()

        self.label = QLabel(self)
        #self.label.setGeometry(QtCore.QRect(0, 0, 500, 16))
        self.label.setText(self.categoryName)
        
        if self.categoryType == CategoryWidget.SUBJECT:
            self.setStyleSheet("background-color: orange; color: white; font-weight: bold;");
            self.label.setMinimumSize(QtCore.QSize(self.layout.parent().size().width(), CategoryWidget.MinHeight))
        elif self.categoryType == CategoryWidget.MODULE:
            self.setStyleSheet("background-color: lightgrey; font-weight: bold;");
            self.label.setMinimumSize(QtCore.QSize(self.layout.parent().size().width(), CategoryWidget.MinHeight))
        elif self.categoryType == CategoryWidget.CATALOGUE:
            self.setStyleSheet("font-weight: bold;");
        elif self.categoryType == CategoryWidget.COURSE:
            pass
        else:
            print("Undefined category-type " + str(self.categoryType))
        self.layout.addWidget(self.label)

    def updateMinimumSize(self):
        if self.categoryType == CategoryWidget.SUBJECT or \
            self.categoryType == CategoryWidget.MODULE:
            self.label.resize(self.layout.parent().size().width(), self.label.size().height())