import sys, time, functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextBrowser, QTabWidget, QMessageBox, \
                            QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, QCheckBox, \
                            QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout, QComboBox, QVBoxLayout
from CourseFetcher import WorkerObject
from CourseWidget import Catalogue
from CourseWidget import Course
from CourseWidget import CourseWidget
from CourseStorer import CourseStorer

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.timeout = 30
        self.fetchIncrement = 20
        self.height = 600
        self.width = 1200

        self.tissCataloguesWidth = 15
        self.tissCataloguesHeight = 8
        self.personalCatalogueWidth = 5
        self.personalCatalogueHeight = 4
        
        self.tissCatalogues = []
        self.personalCatalogues = []
        self.personalCataloguesTitles = []

        self.initUI()
        self.setupWorkerThread()
        self.loadCatalogues()
    
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

        self.fetchButton = QPushButton("Fetch Courses", self)
        self.fetchButton.resize(50, 50)
        gridLayout.addWidget(self.fetchButton, 1, 0)

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

        self.tissCatalogueA, self.tissCatalogueB, self.tissCatalogueC, self.tissCatalogueD = (QListWidget(self) for i in range(4))
        self.tissCatalogues.append(self.tissCatalogueA)
        self.tissCatalogues.append(self.tissCatalogueB)
        self.tissCatalogues.append(self.tissCatalogueC)
        self.tissCatalogues.append(self.tissCatalogueD)
        
        for index, l in enumerate(self.tissCatalogues):
            l.setSizePolicy(sizePolicy)
            l.setMinimumSize(QtCore.QSize(50, 50))
            l.setObjectName("WFK " + Catalogue.catalogueLetters[index] + " list")
            #self.tissCatalogue.setSizeIncrement(QtCore.QSize(1, 1))
            #font =  QtGui.QFont()
            #font.setPointSize(10)
            #self.tissCatalogue.setFont(font)
            #self.tissCatalogue.setStyleSheet("selection-background-color: rgb(159, 181, 255);")
            l.setEditTriggers(QAbstractItemView.NoEditTriggers)
            l.setDropIndicatorShown(False)
            l.setDragEnabled(False)
            l.setDefaultDropAction(QtCore.Qt.IgnoreAction)
            l.setSelectionMode(QAbstractItemView.SingleSelection)
            l.itemDoubleClicked.connect(self.listItemDoubleClicked)
            l.keyPressEvent = self.keyPressEventAddPersonalCourse
            self.tabWidget.addTab(l, Catalogue.catalogueLetters[index])

        gridLayout.addWidget(self.tabWidget, 0, 1, self.tissCataloguesWidth, self.tissCataloguesHeight)

        self.personalCatalogueA, self.personalCatalogueB, self.personalCatalogueC, self.personalCatalogueD = (QListWidget(self) for i in range(4))
        self.personalCatalogues.append(self.personalCatalogueA)
        self.personalCatalogues.append(self.personalCatalogueB)
        self.personalCatalogues.append(self.personalCatalogueC)
        self.personalCatalogues.append(self.personalCatalogueD)
        for index, l in enumerate(self.personalCatalogues):
            l.setSizePolicy(sizePolicy)
            l.setMinimumSize(QtCore.QSize(50, 50))
            l.setEditTriggers(QAbstractItemView.NoEditTriggers)
            l.setDropIndicatorShown(False)
            l.setDragEnabled(False)
            l.setDefaultDropAction(QtCore.Qt.IgnoreAction)
            l.setSelectionMode(QAbstractItemView.SingleSelection)
            l.setObjectName("Personal WFK " + Catalogue.catalogueLetters[index] + " list")
            l.itemDoubleClicked.connect(self.personalItemDoubleClicked)
            l.keyPressEvent = self.keyPressEventDeleteCourse
            
            row = 0
            col = self.tissCataloguesWidth + 1 + self.personalCatalogueWidth
            if index > 1:
                row = self.personalCatalogueHeight + 1
            if index % 2 == 0:
                col -= self.personalCatalogueWidth

            vlayout = QVBoxLayout()
            titleLabel = QLabel("WFK " + Catalogue.catalogueLetters[index], self)
            self.personalCataloguesTitles.append(titleLabel)
            #titleLabel.resize(250, 25)
            vlayout.addWidget(titleLabel)
            vlayout.addWidget(l)
            gridLayout.addLayout(vlayout, row, col, self.personalCatalogueWidth, self.personalCatalogueHeight)

        self.toggleCourseNumbers = QCheckBox("Hide numbers", self)
        self.toggleCourseNumbers.toggled.connect(lambda hidden: self.setCourseInfoHidden(CourseWidget.HIDE_NUMBER, hidden))
        gridLayout.addWidget(self.toggleCourseNumbers, 4, 0)
        self.toggleCourseHours = QCheckBox("Hide hours", self)
        self.toggleCourseHours.toggled.connect(lambda hidden: self.setCourseInfoHidden(CourseWidget.HIDE_HOURS, hidden))
        gridLayout.addWidget(self.toggleCourseHours, 5, 0)

        self.checkCurriculumButton = QPushButton("Check curriculum", self)
        self.checkCurriculumButton.clicked.connect(self.checkCurriculum)
        gridLayout.addWidget(self.checkCurriculumButton, 6, 0)

        self.clearCurriculumFeedbackButton = QPushButton("Clear color", self)
        self.clearCurriculumFeedbackButton.clicked.connect(self.clearCurriculumFeedback)
        gridLayout.addWidget(self.clearCurriculumFeedbackButton, 7, 0)

        self.resize(self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")
        
        #self.addTestCourses()
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
        self.fetchButton.clicked.connect(self.prepareFetching)
        self.fetchButton.clicked.connect(functools.partial(worker.startWork, self.semesterSelectBox.currentText(), self.timeout))

        #def connectSignals(self):
            #self.gui.button_cancel.clicked.connect(self.forceWorkerReset)
            #self.signalStatus.connect(self.updateStatus)
            #self.aboutToQuit.connect(self.forceWorkerQuit)

        """def forceWorkerQuit(self):
            if worker_thread.isRunning():
                worker_thread.terminate()
                worker_thread.wait()"""

    def closeEvent(self, event):
        resBtn = QMessageBox.question( self, "Save?",
                                        "Do you want to save the courses?\n",
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                        QMessageBox.Yes)
        if resBtn == QMessageBox.Yes:
            self.storeCourses()
        elif resBtn == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def setCourseInfoHidden(self, infoIdx, hidden):
        for index in range(len(Catalogue.catalogueLetters)):
            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                widget.setInfoHidden(infoIdx, hidden)
            for i in range(self.personalCatalogues[index].count()):
                widget = self.getItemWidget(self.personalCatalogues[index], i)
                widget.setInfoHidden(infoIdx, hidden)

    def clearCurriculumFeedback(self):
        for index in range(len(Catalogue.catalogueLetters)):
            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                widget.setNeutral()

    def addTestCourses(self):
        for idx, letter in enumerate(Catalogue.catalogueLetters):
            c = Catalogue("Test"+letter)
            ca = Course("000.000", "VO", "2019W", "TestName"+str(idx), 3.0, 3.0, "test.com")
            c.courses.append(ca)
            self.addNewCourse(self.tissCatalogues[idx], ca, False)
        
    def addNewCourse(self, targetList, course, isPersonal):
        itemWidget = CourseWidget(course, isPersonal)
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
        originList = self.tissCatalogues[tabIdx]
        if len(originList.selectedItems()) == 0:
            return
        
        item = originList.selectedItems()[0]
        targetList = self.personalCatalogues[tabIdx]
        self.tryAddPersonalCourse(targetList, originList, item)

    def listItemDoubleClicked(self, item):
        originList = self.sender()
        catalogueIdx = self.tissCatalogues.index(originList)
        targetList = self.personalCatalogues[catalogueIdx]
        self.tryAddPersonalCourse(targetList, originList, item)

    def tryAddPersonalCourse(self, targetList, originList, originItem):
        course = originList.itemWidget(originItem).course
        for i in range(targetList.count()):
            itemWidget = self.getItemWidget(targetList, i)
            if itemWidget.course.sameAs(course):
                return
        self.addNewCourse(targetList, course, True)
        self.updateTitles()

    def keyPressEventDeleteCourse(self, e):
        super().keyPressEvent(e)
        if e.key() != QtCore.Qt.Key_Backspace:
            return

        for i, l in enumerate(self.personalCatalogues):
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
        for index in range(len(Catalogue.catalogueLetters)):
            credits = 0
            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                credits += widget.course.credits
            self.tabWidget.setTabText(index, Catalogue.catalogueLetters[index] + " (" + str(credits) + ")")
            credits = 0
            for i in range(self.personalCatalogues[index].count()):
                widget = self.getItemWidget(self.personalCatalogues[index], i)
                credits += widget.course.credits
            self.personalCataloguesTitles[index].setText("WFK " + Catalogue.catalogueLetters[index] + " (" + str(credits) + ")")

    def checkCurriculum(self):
        for index in range(len(Catalogue.catalogueLetters)):
            curriculumCatalogue = open("WFK/WFK_" + Catalogue.catalogueLetters[index] + ".txt", 'r')
            curriculumCourses = []
            for line in curriculumCatalogue:
                parts = line.strip().split('|')
                courseName = parts[0]
                courseType = parts[1]
                courseCredits = float(parts[2])
                curriculumCourses.append(Course("", courseType, "", courseName, 0.0, courseCredits, ""))

            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                course = widget.course
                val = course.existsInCurriculum(curriculumCourses)
                if val > -1:
                    widget.setNegativeFeedback(val)

    def loadCatalogues(self):
        self.setUIEnabled(False)
        (allCatalogues, personalCatalogues) = CourseStorer.loadCourses()

        for index, c in enumerate(allCatalogues):
            currentListWidget = self.tissCatalogues[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co, False)

        for index, c in enumerate(personalCatalogues):
            currentListWidget = self.personalCatalogues[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co, True)

        self.label.setText("Courses loaded.")
        self.setUIEnabled(True)
        self.updateTitles()

    def storeCourses(self):
        allCats = self.cataloguesFromLists(self.tissCatalogues)
        personalCats = self.cataloguesFromLists(self.personalCatalogues)
        CourseStorer.storeCourses(allCats, personalCats)

    def cataloguesFromLists(self, lists):
        cats = []
        curCatalogue = None

        for index,c in enumerate(lists):
            curCatalogue = Catalogue(Catalogue.catalogueLetters[index])
            cats.append(curCatalogue)
            for i in range(lists[index].count()):
                widget = self.getItemWidget(lists[index], i)
                curCatalogue.courses.append(widget.course)
        return cats

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.label.setText("")
        for l in self.tissCatalogues:
            l.clear()
        self.setUIEnabled(False)
        self.startTime = time.time()

    def setUIEnabled(self, enabled):
        self.semesterSelectBox.setEnabled(enabled)
        self.fetchButton.setEnabled(enabled)
        for l in self.tissCatalogues:
            l.setEnabled(enabled)
            self.updateTitles()
        self.checkCurriculumButton.setEnabled(enabled)
        self.clearCurriculumFeedbackButton.setEnabled(enabled)
        val = 0
        if enabled:
            val = 1
        self.progressBar.setValue(val)

    @QtCore.pyqtSlot(str)
    def updateStatus(self, str):
        self.label.setText(str)
        self.progressBar.setValue(self.progressBar.value() + self.fetchIncrement)

    @QtCore.pyqtSlot(object)
    def fetchingFinished(self, catalogues):
        self.progressBar.setValue(0)
        self.label.setText("Importing courses...")

        for index, c in enumerate(catalogues):
            currentListWidget = self.tissCatalogues[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co, False)
                self.label.setText("Importing \"WFK %s\"...(%i/%i)"%(Catalogue.catalogueLetters[index], i, len(c.courses)))
                self.progressBar.setValue(int(float(i/len(c.courses))*100))
                QtWidgets.qApp.processEvents()
                
        self.label.setText("Finished (%.2fs)" % (time.time()-self.startTime));
        self.setUIEnabled(True)
        self.updateTitles()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())