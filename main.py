import sys, time, functools, datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextBrowser, QTabWidget, QMessageBox, QLineEdit, \
    QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, QCheckBox, QGroupBox, QShortcut, \
    QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout, QComboBox, QVBoxLayout, QHBoxLayout
from CourseFetcher import WorkerObject
from CourseWidget import Catalogue
from CourseWidget import Course
from CourseWidget import CourseWidget
from FileManager import FileManager

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.timeout = 30
        self.fetchIncrement = 20
        self.height = 600
        self.width = 1200

        self.tissCataloguesRows = 12
        self.tissCataloguesCols = 4
        self.personalCatalogueRowsFirst = 4
        self.personalCatalogueRowsSecond = 8
        self.personalCatalogueCols = 1

        self.tissCatalogues = []
        self.personalCatalogues = []
        self.personalCataloguesTitles = []

        self.initUI()
        self.setupWorkerThread()
        self.loadCatalogues()
        settings = FileManager.loadSettings()
        if len(settings) > 0:
            self.lastFetchDateTime.setText(settings[0])
            self.toggleCourseNumbers.setChecked(FileManager.str2bool(settings[1]))
            self.toggleCourseHours.setChecked(FileManager.str2bool(settings[2]))
            self.exactSemester.setChecked(FileManager.str2bool(settings[3]))

    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout()
        centralWidget.setLayout(gridLayout)

        fetchLayout = QVBoxLayout()
        fetchLayout.setContentsMargins(0, 0, 0, 0)
        fetchLayout.setSpacing(0)

        link = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=43093&semester=NEXT"
        self.currLink = QLabel("", self)
        self.currLink.linkActivated.connect(lambda linkStr: QtGui.QDesktopServices.openUrl(QtCore.QUrl(linkStr)))
        self.currLink.setText('<a href="' + link + '">Curriculum</a>')
        fetchLayout.addWidget(self.currLink)

        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setSpacing(0)
        self.semesterSelectBox = QComboBox(self)
        self.semesterSelectBox.addItem("2019W")
        self.semesterSelectBox.addItem("2020S")
        self.semesterSelectBox.setCurrentIndex(1)
        hlayout.addWidget(self.semesterSelectBox)

        self.fetchButton = QPushButton("Fetch Courses", self)
        self.fetchButton.clicked.connect(self.prepareFetching)
        hlayout.addWidget(self.fetchButton)
        fetchLayout.addLayout(hlayout)

        hlayout2 = QHBoxLayout()
        hlayout2.setContentsMargins(0, 0, 0, 20)
        hlayout2.setSpacing(0)
        self.exactSemester = QCheckBox("Exactly this semester", self)
        hlayout2.setAlignment(QtCore.Qt.AlignRight)
        hlayout2.addWidget(self.exactSemester)
        fetchLayout.addLayout(hlayout2)

        self.statusOutput = QLabel("<Status output>", self)
        fetchLayout.addWidget(self.statusOutput)

        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        fetchLayout.addWidget(self.progressBar)

        lastFetchLayout = QHBoxLayout()
        lastFetchLayout.setContentsMargins(0, 0, 0, 0)
        lastFetchLayout.setSpacing(0)
        self.lastFetchTitle = QLabel("last fetch:", self)
        font = self.lastFetchTitle.font()
        font.setItalic(True)
        font.setPointSize(10)
        self.lastFetchTitle.setFont(font)
        lastFetchLayout.addWidget(self.lastFetchTitle)
        self.lastFetchDateTime = QLabel(self)
        self.lastFetchDateTime.setFont(font)
        lastFetchLayout.addWidget(self.lastFetchDateTime)
        lastFetchLayout.addStretch(0)
        fetchLayout.addLayout(lastFetchLayout)

        fetchGroup = QGroupBox()
        fetchGroup.setLayout(fetchLayout)
        gridLayout.addWidget(fetchGroup, 0, 0)

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
            l.setObjectName(f"WFK {Catalogue.catalogueLetters[index]} list")
            l.setEditTriggers(QAbstractItemView.NoEditTriggers)
            l.setDropIndicatorShown(False)
            l.setDragEnabled(False)
            l.setDefaultDropAction(QtCore.Qt.IgnoreAction)
            l.setSelectionMode(QAbstractItemView.SingleSelection)
            l.itemDoubleClicked.connect(self.listItemDoubleClicked)
            l.keyPressEvent = self.keyPressEventAddPersonalCourse
            self.tabWidget.addTab(l, Catalogue.catalogueLetters[index])

        gridLayout.addWidget(self.tabWidget, 0, 1, self.tissCataloguesRows, self.tissCataloguesCols)

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
            l.setObjectName(f"Personal WFK {Catalogue.catalogueLetters[index]} list")
            l.itemDoubleClicked.connect(self.personalItemDoubleClicked)
            l.keyPressEvent = self.keyPressEventDeleteCourse

            row = 0
            rowSpan = self.personalCatalogueRowsFirst
            col = self.tissCataloguesCols + 1 + self.personalCatalogueCols
            if index > 1:
                row = self.personalCatalogueRowsFirst
                rowSpan = self.personalCatalogueRowsSecond
            if index % 2 == 0:
                col -= self.personalCatalogueCols

            vlayout = QVBoxLayout()
            titleLabel = QLabel("WFK " + Catalogue.catalogueLetters[index], self)
            self.personalCataloguesTitles.append(titleLabel)
            vlayout.addWidget(titleLabel)
            vlayout.addWidget(l)
            gridLayout.addLayout(vlayout, row, col, rowSpan, self.personalCatalogueCols)

        searchLayout = QHBoxLayout()
        searchText = QLineEdit("", self)
        searchText.setPlaceholderText("Search...")
        shortcut = QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(lambda: searchText.setFocus())
        shortcut = QShortcut(QtGui.QKeySequence("Esc"), self)
        shortcut.activated.connect(lambda: self.setFocus())
        searchText.textEdited.connect(self.searchCourses)
        searchLayout.addWidget(searchText)
        searchGroup = QGroupBox()
        searchGroup.setLayout(searchLayout)
        gridLayout.addWidget(searchGroup, 1, 0)

        curriculumLayout = QHBoxLayout()
        curriculumLayout.setContentsMargins(0, 0, 0, 0)
        self.checkCurriculumButton = QPushButton("Check curriculum", self)
        self.checkCurriculumButton.clicked.connect(self.checkCurriculum)
        curriculumLayout.addWidget(self.checkCurriculumButton)

        self.clearCurriculumFeedbackButton = QPushButton("Clear", self)
        self.clearCurriculumFeedbackButton.clicked.connect(self.clearCurriculumFeedback)
        curriculumLayout.addWidget(self.clearCurriculumFeedbackButton)
        curriculumGroup = QGroupBox()
        curriculumGroup.setLayout(curriculumLayout)
        gridLayout.addWidget(curriculumGroup, 2, 0)

        toggleLayout = QVBoxLayout()
        toggleLayout.setContentsMargins(0, 0, 0, 0)
        self.toggleCourseNumbers = QCheckBox("Hide numbers", self)
        self.toggleCourseNumbers.setTristate(False)
        self.toggleCourseNumbers.toggled.connect(lambda hidden: self.setCourseInfoHidden(CourseWidget.HIDE_NUMBER, hidden))
        toggleLayout.addWidget(self.toggleCourseNumbers)
        self.toggleCourseHours = QCheckBox("Hide hours", self)
        self.toggleCourseHours.setTristate(False)
        self.toggleCourseHours.toggled.connect(lambda hidden: self.setCourseInfoHidden(CourseWidget.HIDE_HOURS, hidden))
        toggleLayout.addWidget(self.toggleCourseHours)
        toggleGroup = QGroupBox()
        toggleGroup.setLayout(toggleLayout)
        gridLayout.addWidget(toggleGroup, 3, 0)

        self.resize(self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")

        self.updateTitles()

    def setupWorkerThread(self):
        # Setup the worker object and the worker_thread.
        self.worker = WorkerObject()
        self.worker_thread = QtCore.QThread(self)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Connect any worker signals
        self.worker.doneSignal.connect(self.fetchingFinished)
        self.worker.updateSignal.connect(self.updateStatus)
        self.fetchButton.clicked.connect(functools.partial(self.worker.startWork, self.semesterSelectBox, self.exactSemester, self.timeout))

    def closeEvent(self, event):
        FileManager.storeSettings([self.lastFetchDateTime.text(), self.toggleCourseNumbers.isChecked(), self.toggleCourseHours.isChecked(), self.exactSemester.isChecked()])
        self.storeCourses()
        event.accept()

    def searchCourses(self, text):
        text = text.strip()
        for index in range(len(Catalogue.catalogueLetters)):
            count = 0
            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                if text == "":
                    widget.setHighlit(False)
                    widget.setGreyedOut(False)
                elif text.lower() in widget.course.name.lower():
                    widget.setHighlit(True)
                    count += 1
                else:
                    widget.setGreyedOut(True)
            self.tabWidget.setTabText(index, f"{Catalogue.catalogueLetters[index]} ({count}/{len(self.tissCatalogues[index])})")
        if text == "":
            self.updateTitles()
            self.checkCurriculumButton.setEnabled(True)
            self.clearCurriculumFeedbackButton.setEnabled(True)
        else:
            self.checkCurriculumButton.setEnabled(False)
            self.clearCurriculumFeedbackButton.setEnabled(False)

    def setCourseInfoHidden(self, infoIdx, hidden):
        for index in range(len(Catalogue.catalogueLetters)):
            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                widget.setInfoHidden(infoIdx, hidden)
            for i in range(self.personalCatalogues[index].count()):
                widget = self.getItemWidget(self.personalCatalogues[index], i)
                widget.setInfoHidden(infoIdx, hidden)

    # def addTestCourses(self):
    #     for idx, letter in enumerate(Catalogue.catalogueLetters):
    #         c = Catalogue("Test" + letter)
    #         ca = Course("000.000", "VO", "2019W", "TestName" + str(idx), 3.0, 3.0, "test.com")
    #         c.courses.append(ca)
    #         self.addNewCourse(self.tissCatalogues[idx], ca, False)

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
            self.tabWidget.setTabText(index, f"{Catalogue.catalogueLetters[index]} ({len(self.tissCatalogues[index])}, {credits})")
            credits = 0
            for i in range(self.personalCatalogues[index].count()):
                widget = self.getItemWidget(self.personalCatalogues[index], i)
                credits += widget.course.credits
            self.personalCataloguesTitles[index].setText(f"WFK {Catalogue.catalogueLetters[index]} ({len(self.personalCatalogues[index])}, {credits})")

    def checkCurriculum(self):
        for index in range(len(Catalogue.catalogueLetters)):
            curriculumCatalogue = open(f"WFK/WFK_{Catalogue.catalogueLetters[index]}.txt", 'r')
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

    def clearCurriculumFeedback(self):
        for index in range(len(Catalogue.catalogueLetters)):
            for i in range(self.tissCatalogues[index].count()):
                widget = self.getItemWidget(self.tissCatalogues[index], i)
                widget.removeFeedback()

    def loadCatalogues(self):
        self.setUIEnabled(False)
        (allCatalogues, personalCatalogues) = FileManager.loadCourses()

        for index, c in enumerate(allCatalogues):
            currentListWidget = self.tissCatalogues[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co, False)

        for index, c in enumerate(personalCatalogues):
            currentListWidget = self.personalCatalogues[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co, True)

        self.statusOutput.setText("Courses loaded.")
        self.setUIEnabled(True)
        self.updateTitles()

    def storeCourses(self):
        allCats = self.getCataloguesFromLists(self.tissCatalogues)
        personalCats = self.getCataloguesFromLists(self.personalCatalogues)
        FileManager.storeCourses(allCats, personalCats)

    def getCataloguesFromLists(self, lists):
        cats = []
        curCatalogue = None

        for index, c in enumerate(lists):
            curCatalogue = Catalogue(Catalogue.catalogueLetters[index])
            cats.append(curCatalogue)
            for i in range(lists[index].count()):
                widget = self.getItemWidget(lists[index], i)
                curCatalogue.courses.append(widget.course)
        return cats

    def prepareFetching(self):
        self.statusOutput.setText("")
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
        self.exactSemester.setEnabled(enabled)
        self.progressBar.setValue(0)
        if enabled:
            self.progressBar.setValue(1)

    def updateStatus(self, str):
        self.statusOutput.setText(str)
        self.progressBar.setValue(self.progressBar.value() + self.fetchIncrement)

    def fetchingFinished(self, catalogues):
        if len(catalogues) > 0:
            self.progressBar.setValue(0)
            self.statusOutput.setText("Importing courses...")

            for index, c in enumerate(catalogues):
                currentListWidget = self.tissCatalogues[index]
                for i, co in enumerate(c.courses):
                    self.addNewCourse(currentListWidget, co, False)
                    self.statusOutput.setText(f"Importing \"WFK {Catalogue.catalogueLetters[index]}\"...({i}/{len(c.courses)})")
                    self.progressBar.setValue(int(float(i / len(c.courses)) * 100))
                    QtWidgets.qApp.processEvents()

            self.statusOutput.setText("Finished (%.2fs)" % (time.time() - self.startTime))
            self.lastFetchDateTime.setText(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.setUIEnabled(True)
        self.updateTitles()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
