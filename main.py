import sys, time, functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextBrowser, QTabWidget, \
                            QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, QCheckBox, \
                            QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout, QComboBox, QVBoxLayout
from CourseFetcher import WorkerObject
from CourseWidget import Catalogue
from CourseWidget import Course
from CourseWidget import CourseWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.entryListsWidth = 15
        self.entryListsHeight = 8
        self.personalWidth = 5
        self.personalHeight = 4
        self.timeout = 30
        self.fetchIncrement = 20
        self.height = 600
        self.width = 1200
        self.catalogues = []
        self.entryLists = []
        self.personalLists = []
        self.personalListsTitles = []
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
            l.itemDoubleClicked.connect(self.listItemDoubleClicked)
            l.keyPressEvent = self.keyPressEventAddPersonalCourse
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
            l.setObjectName("Personal WFK " + self.catalogueLetters[index] + " list")
            l.itemDoubleClicked.connect(self.personalItemDoubleClicked)
            l.keyPressEvent = self.keyPressEventDeleteCourse
            
            row = 0
            col = self.entryListsWidth + 1 + self.personalWidth
            if index > 1:
                row = self.personalHeight + 1
            if index % 2 == 0:
                col -= self.personalWidth

            vlayout = QVBoxLayout()
            titleLabel = QLabel("WFK " + self.catalogueLetters[index], self)
            self.personalListsTitles.append(titleLabel)
            #titleLabel.resize(250, 25)
            vlayout.addWidget(titleLabel)
            vlayout.addWidget(l)
            gridLayout.addLayout(vlayout, row, col, self.personalWidth, self.personalHeight)

        self.toggleCourseNumbers = QCheckBox("Hide numbers", self)
        self.toggleCourseNumbers.toggled.connect(lambda hidden: self.setCourseInfoHidden(CourseWidget.HIDE_NUMBER, hidden))
        gridLayout.addWidget(self.toggleCourseNumbers, 4, 0)
        self.toggleCourseHours = QCheckBox("Hide hours", self)
        self.toggleCourseHours.toggled.connect(lambda hidden: self.setCourseInfoHidden(CourseWidget.HIDE_HOURS, hidden))
        gridLayout.addWidget(self.toggleCourseHours, 5, 0)

        self.checkCurriculumButton = QPushButton("Check curriculum", self)
        self.checkCurriculumButton.clicked.connect(self.checkCurriculum)
        gridLayout.addWidget(self.checkCurriculumButton, 6, 0)

        self.clearCheckButton = QPushButton("Clear color", self)
        self.clearCheckButton.clicked.connect(self.clearCurriculumFeedback)
        gridLayout.addWidget(self.clearCheckButton, 7, 0)

        self.resize(self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")
        
        self.addTestCourses()
        self.updateTitles()

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

    def setCourseInfoHidden(self, infoIdx, hidden):
        for index, catalogue in enumerate(self.catalogues):
            for i in range(self.entryLists[index].count()):
                widget = self.getItemWidget(self.entryLists[index], i)
                widget.setInfoHidden(infoIdx, hidden)
            for i in range(self.personalLists[index].count()):
                widget = self.getItemWidget(self.personalLists[index], i)
                widget.setInfoHidden(infoIdx, hidden)

    def clearCurriculumFeedback(self):
        for index, catalogue in enumerate(self.catalogues):
            for i in range(self.entryLists[index].count()):
                widget = self.getItemWidget(self.entryLists[index], i)
                widget.setNeutral()

    def addTestCourses(self):
        for idx, letter in enumerate(self.catalogueLetters):
            c = Catalogue("Test"+letter)
            ca = Course("000.000", "VO", "2019W", "TestName"+str(idx), 3.0, 3.0, "test.com")
            c.courses.append(ca)
            self.catalogues.append(c)
            self.addNewCourse(self.entryLists[idx], ca)
        
    def addNewCourse(self, targetList, course):
        itemWidget = CourseWidget(course)
        item = QListWidgetItem()
        row = targetList.count()
        targetList.insertItem(row, item)
        targetList.setItemWidget(item, itemWidget)
        item.setSizeHint(QtCore.QSize(itemWidget.width(), itemWidget.height()))

    def getItemWidget(self, targetList, idx):
        item = targetList.item(idx)
        return targetList.itemWidget(item)

    def keyPressEventAddPersonalCourse(self, e):
        super().keyPressEvent(e)
        if e.key() != QtCore.Qt.Key_Return:
            return

        tabIdx = self.tabWidget.currentIndex()
        originList = self.entryLists[tabIdx]
        if len(originList.selectedItems()) == 0:
            return
        
        item = originList.selectedItems()[0]
        targetList = self.personalLists[tabIdx]
        self.tryAddPersonalCourse(targetList, originList, item)

    def listItemDoubleClicked(self, item):
        originList = self.sender()
        catalogueIdx = self.entryLists.index(originList)
        targetList = self.personalLists[catalogueIdx]
        self.tryAddPersonalCourse(targetList, originList, item)

    def tryAddPersonalCourse(self, targetList, originList, originItem):
        course = originList.itemWidget(originItem).course
        for i in range(targetList.count()):
            itemWidget = self.getItemWidget(targetList, i)
            if itemWidget.course.sameAs(course):
                return
        self.addNewCourse(targetList, course)
        self.updateTitles()

    def keyPressEventDeleteCourse(self, e):
        super().keyPressEvent(e)
        if e.key() != QtCore.Qt.Key_Backspace:
            return

        for i, l in enumerate(self.personalLists):
            if l.hasFocus() and len(l.selectedItems()) == 1:
                item = l.selectedItems()[0]
                self.removeItemFromPersonal(l, item)
                return

    def personalItemDoubleClicked(self, item):
        originList = self.sender()
        self.removeItemFromPersonal(originList, item)        

    def removeItemFromPersonal(self, personalList, item):
        courseIdx = personalList.indexFromItem(item).row()
        personalList.takeItem(courseIdx)
        self.updateTitles()

    def updateTitles(self):
        for index, catalogue in enumerate(self.catalogues):
            credits = 0
            for i in range(self.entryLists[index].count()):
                widget = self.getItemWidget(self.entryLists[index], i)
                credits += widget.course.credits
            self.tabWidget.setTabText(index, self.catalogueLetters[index] + " (" + str(credits) + ")")
            credits = 0
            for i in range(self.personalLists[index].count()):
                widget = self.getItemWidget(self.personalLists[index], i)
                credits += widget.course.credits
            self.personalListsTitles[index].setText("WFK " + self.catalogueLetters[index] + " (" + str(credits) + ")")

    def checkCurriculum(self):
        folder = "WFK/"

        for index, catalogue in enumerate(self.catalogues):
            curriculumCatalogue = open(folder + "WFK_" + self.catalogueLetters[index] + ".txt", 'r')
            curriculumCourses = []
            for line in curriculumCatalogue:
                parts = line.strip().split(' ')
                courseType = parts[-3]
                courseCredits = parts[-1]
                courseName = (' '.join(parts[:-4])).strip()
                curriculumCourses.append(Course("", courseType, "", courseName, 0.0, courseCredits, ""))

            for i in range(self.entryLists[index].count()):
                widget = self.getItemWidget(self.entryLists[index], i)
                course = widget.course
                if not course.existsInCurriculum(curriculumCourses):
                    print("'" + course.name + "' not found in WFK " + self.catalogueLetters[index])
                    widget.setFeedback(False)
                else:
                    widget.setFeedback(True)

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.progressBar.setValue(0)
        self.label.setText("")
        self.semesterSelectBox.setEnabled(False)
        self.button.setEnabled(False)
        for l in self.entryLists:
            l.clear()
            l.setEnabled(False)
            self.updateTitles()
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
                self.addNewCourse(currentListWidget, co)
                self.label.setText("Importing \"WFK %s\"...(%i/%i)"%(self.catalogueLetters[index], i, len(c.courses)))
                self.progressBar.setValue(int(float(i/len(c.courses))*100))
                QtWidgets.qApp.processEvents()
                
        self.label.setText("Finished (%.2fs)" % (time.time()-self.startTime));
        for l in self.entryLists:
            l.setEnabled(True)
        self.semesterSelectBox.setEnabled(True)
        self.progressBar.setValue(1)
        self.updateTitles()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())