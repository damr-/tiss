import sys, time, functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextBrowser, QTabWidget, \
                            QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, \
                            QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout, QComboBox, QVBoxLayout
from CourseFetcher import WorkerObject
from CourseFetcher import Catalogue
from CourseFetcher import Course
from CourseWidget import CourseWidget
from CategoryWidget import CategoryWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.entryListsWidth = 15
        self.entryListsHeight = 10
        self.personalWidth = 5
        self.personalHeight = 5
        self.timeout = 30
        self.fetchIncrement = 20
        self.height = 780
        self.width = 1400
        self.catalogues = []
        self.entryLists = []
        self.personalLists = []
        self.catalogueLetters = ['A', 'B', 'C', 'D']

        self.initUI()
        self.setupWorkerThread()
    
    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout()
        centralWidget.setLayout(gridLayout)

        self.semesterSelectBox = QComboBox(self)
        self.semesterSelectBox.addItem("2019S")
        self.semesterSelectBox.addItem("2019W")
        self.semesterSelectBox.setCurrentIndex(1)
        gridLayout.addWidget(self.semesterSelectBox, 0, 0)

        self.button = QPushButton("Fetch Courses", self)
        self.button.resize(50, 50)
        gridLayout.addWidget(self.button, 1, 0)

        self.label = QLabel("<Status output>", self)
        self.label.resize(250, 25)
        gridLayout.addWidget(self.label, 2, 0)

        self.progressBar = QProgressBar(self)
        self.progressBar.resize(250, 50)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        gridLayout.addWidget(self.progressBar, 3, 0)
    
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(0, 50))

        self.entryListA, self.entryListB, self.entryListC, self.entryListD = (QListWidget(self) for i in range(4))
        self.entryLists.append(self.entryListA)
        self.entryLists.append(self.entryListB)
        self.entryLists.append(self.entryListC)
        self.entryLists.append(self.entryListD)
        
        for index, l in enumerate(self.entryLists):
            l.setSizePolicy(sizePolicy)
            l.setMinimumSize(QtCore.QSize(50, 50))
            l.setObjectName("WFK " + self.catalogueLetters[index] + " list")
            #self.entryList.setSizeIncrement(QtCore.QSize(1, 1))
            #font =  QtGui.QFont()
            #font.setPointSize(10)
            #self.entryList.setFont(font)
            #self.entryList.setStyleSheet("selection-background-color: rgb(159, 181, 255);")
            l.setEditTriggers(QAbstractItemView.NoEditTriggers)
            l.setDropIndicatorShown(False)
            l.setDragEnabled(False)
            l.setDefaultDropAction(QtCore.Qt.IgnoreAction)
            l.setSelectionMode(QAbstractItemView.SingleSelection)
            l.itemDoubleClicked.connect(self.addPersonalItem)
            self.tabWidget.addTab(l, self.catalogueLetters[index])

        gridLayout.addWidget(self.tabWidget, 0, 1, self.entryListsWidth, self.entryListsHeight)

        self.personalListA, self.personalListB, self.personalListC, self.personalListD = (QListWidget(self) for i in range(4))
        self.personalLists.append(self.personalListA)
        self.personalLists.append(self.personalListB)
        self.personalLists.append(self.personalListC)
        self.personalLists.append(self.personalListD)
        for index, l in enumerate(self.personalLists):
            l.setSizePolicy(sizePolicy)
            l.setMinimumSize(QtCore.QSize(50, 50))
            l.setEditTriggers(QAbstractItemView.NoEditTriggers)
            l.setDropIndicatorShown(False)
            l.setDragEnabled(False)
            l.setDefaultDropAction(QtCore.Qt.IgnoreAction)
            l.setSelectionMode(QAbstractItemView.SingleSelection)
            l.itemDoubleClicked.connect(self.removePersonalItem)
            
            row = 0
            col = self.entryListsWidth + 1 + self.personalWidth
            if index > 1:
                row = self.personalHeight + 1
            if index % 2 == 0:
                col -= self.personalWidth

            vlayout = QVBoxLayout()
            titleLabel = QLabel("WFK " + self.catalogueLetters[index], self)
            #titleLabel.resize(250, 25)
            vlayout.addWidget(titleLabel)
            vlayout.addWidget(l)
            gridLayout.addLayout(vlayout, row, col, self.personalWidth, self.personalHeight)

        self.resize(self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")

        
        ca = Catalogue("TestA")
        cb = Catalogue("TestB")
        cc = Catalogue("TestC")
        cd = Catalogue("TestD")

        ca1 = Course("000.000", "VO", "2019W", "TestName1", 3.0, 3.0, "test.com")
        ca2 = Course("000.000", "VO", "2019W", "TestName11", 3.0, 3.0, "test.com")
        cb1 = Course("000.000", "VO", "2019W", "TestName2", 3.0, 3.0, "test.com")
        cc1 = Course("000.000", "VO", "2019W", "TestName3", 3.0, 3.0, "test.com")
        cd1 = Course("000.000", "VO", "2019W", "TestName4", 3.0, 3.0, "test.com")

        ca.courses.append(ca1)
        ca.courses.append(ca2)
        cb.courses.append(cb1)
        cc.courses.append(cc1)
        cd.courses.append(cd1)

        self.catalogues.append(ca)
        self.catalogues.append(cb)
        self.catalogues.append(cc)
        self.catalogues.append(cd)

        self.addNewCourseCopy(self.entryLists[0], ca1)
        self.addNewCourseCopy(self.entryLists[0], ca2)
        self.addNewCourseCopy(self.entryLists[1], cb1)
        self.addNewCourseCopy(self.entryLists[2], cc1)
        self.addNewCourseCopy(self.entryLists[3], cd1)


    def setupWorkerThread(self):
        # Setup the worker object and the worker_thread.
        worker = WorkerObject()
        worker_thread = QtCore.QThread(self)
        worker.moveToThread(worker_thread)
        worker_thread.start()

        # Connect any worker signals
        worker.doneSignal.connect(self.fetchingFinished)
        worker.updateSignal.connect(self.updateStatus)
        self.button.clicked.connect(self.prepareFetching)
        self.button.clicked.connect(functools.partial(worker.startWork, self.semesterSelectBox.currentText(), self.timeout))

        #def connectSignals(self):
            #self.gui.button_cancel.clicked.connect(self.forceWorkerReset)
            #self.signalStatus.connect(self.updateStatus)
            #self.aboutToQuit.connect(self.forceWorkerQuit)

        """def forceWorkerQuit(self):
            if worker_thread.isRunning():
                worker_thread.terminate()
                worker_thread.wait()"""

    def addNewCourseCopy(self, targetList, course):
        self.addNewCourse(targetList, course.number, course.courseType, course.semester, course.name, course.hours, course.credits, course.link)

    def addNewCourse(self, targetList, number, courseType, semester, name, hours, credits, link):
        itemWidget = CourseWidget(number, courseType, semester, name, hours, credits, link)
        item = QListWidgetItem()
        row = targetList.count()
        targetList.insertItem(row, item)
        targetList.setItemWidget(item, itemWidget)
        item.setSizeHint(QtCore.QSize(itemWidget.width(), itemWidget.height()))

    def getItemWidget(self, targetList, idx):
        item = targetList.item(idx)
        return targetList.itemWidget(item)

    def addPersonalItem(self, item):
        originList = self.sender()

        courseIdx = originList.indexFromItem(item).row()
        catalogueIdx = self.entryLists.index(originList)
        course = self.catalogues[catalogueIdx].courses[courseIdx]

        targetList = self.personalLists[catalogueIdx]

        for i in range(targetList.count()):
            itemWidget = self.getItemWidget(targetList, i)
            if itemWidget.t == course.t:
                return

        self.addNewCourseCopy(targetList, course)

    def removePersonalItem(self, item):
        originList = self.sender()
        courseIdx = originList.indexFromItem(item).row()
        originList.takeItem(courseIdx)

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.progressBar.setValue(0)
        self.label.setText("")
        self.semesterSelectBox.setEnabled(False)
        self.button.setEnabled(False)
        for l in self.entryLists:
            l.clear()
            l.setEnabled(False)
        self.startTime = time.time()

    @QtCore.pyqtSlot(str)
    def updateStatus(self, str):
        self.label.setText(str)
        self.progressBar.setValue(self.progressBar.value() + self.fetchIncrement)

    @QtCore.pyqtSlot(object)
    def fetchingFinished(self, catalogues):
        self.button.setEnabled(True)
        self.progressBar.setValue(0)
        self.label.setText("Importing entries...")

        self.catalogues = catalogues[:]
        for index, c in enumerate(catalogues):
            currentListWidget = self.entryLists[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co.number, co.courseType, co.semester, co.name, co.hours, co.credits, co.link)
                self.label.setText("Importing \"WFK %s\"...(%i/%i)"%(self.catalogueLetters[index], i, len(c.courses)))
                self.progressBar.setValue(int(float(i/len(c.courses))*100))
                QtWidgets.qApp.processEvents()
                
        self.label.setText("Finished (%.2fs)" % (time.time()-self.startTime));
        for l in self.entryLists:
            l.setEnabled(True)
        self.semesterSelectBox.setEnabled(True)
        self.progressBar.setValue(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())