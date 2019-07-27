import sys, time, functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QCheckBox, QTextBrowser, \
                            QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, \
                            QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout
from CourseFetcher import WorkerObject
from CourseFetcher import Subject
from CourseWidget import CourseWidget
from CategoryWidget import CategoryWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupWorkerThread()
    
    def initUI(self):
        self.semester = "2019W"
        self.timeout = 30
        self.fetchIncrement = 20
        self.hiddenItems = {}
        
        height = 600
        width = 800
        
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout()
        centralWidget.setLayout(gridLayout)

        self.button = QPushButton("do", self)
        self.button.resize(50, 50)
        gridLayout.addWidget(self.button, 0, 0)

        self.label = QLabel("<Status output>", self)
        self.label.resize(250, 25)
        gridLayout.addWidget(self.label, 1, 0)

        self.progressBar = QProgressBar(self)
        self.progressBar.resize(250, 50)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        gridLayout.addWidget(self.progressBar, 2, 0)

        self.toggle = QCheckBox("toggle", self)
        self.toggle.toggled.connect(self.toggleCourses)
        gridLayout.addWidget(self.toggle, 3, 0)

        self.entryList = QListWidget(self)
        self.entryList.setObjectName("Entrylist")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.entryList.sizePolicy().hasHeightForWidth())
        self.entryList.setSizePolicy(sizePolicy)
        self.entryList.setMinimumSize(QtCore.QSize(50, 50))
        self.entryList.setSizeIncrement(QtCore.QSize(1, 1))
        font =  QtGui.QFont()
        font.setPointSize(10)
        self.entryList.setFont(font)
        self.entryList.setStyleSheet("selection-background-color: rgb(159, 181, 255);")
        self.entryList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.entryList.setDropIndicatorShown(False)
        self.entryList.setDragEnabled(False)
        self.entryList.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.entryList.setSelectionMode(QAbstractItemView.SingleSelection)
        gridLayout.addWidget(self.entryList, 0, 1, 10, 5)

        self.resize(width,height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")

        self.resizeEvent = self.windowResizeEvent

        """
        self.addNewCourseInfo("100.000", "VO", "2019W", "TEST", 2, 3, "http://www.google.com")
        self.addNewCategory("Subject", CategoryWidget.SUBJECT)
        self.addNewCategory("Module", CategoryWidget.MODULE)
        self.addNewCategory("Catalogue", CategoryWidget.CATALOGUE)
        self.addNewCategory("Course", CategoryWidget.COURSE)
        """

    def windowResizeEvent(self, e):
        for i in range(self.entryList.count()):
            item = self.entryList.item(i);
            itemWidget = self.entryList.itemWidget(item)
            if type(itemWidget) is CategoryWidget:
                itemWidget.updateMinimumSize()


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
        self.button.clicked.connect(functools.partial(worker.startWork, self.semester, self.timeout))

        #def connectSignals(self):
            #self.gui.button_cancel.clicked.connect(self.forceWorkerReset)
            #self.signalStatus.connect(self.updateStatus)
            #self.aboutToQuit.connect(self.forceWorkerQuit)

        """def forceWorkerQuit(self):
            if worker_thread.isRunning():
                worker_thread.terminate()
                worker_thread.wait()"""

    def addNewCategory(self, text, categoryType):
        itemWidget = CategoryWidget(text, categoryType)
        self.addNewEntryItem(itemWidget, False)

    def addNewCourseInfo(self, number, courseType, semester, name, hours, credits, link):
        itemWidget = CourseWidget(number, courseType, semester, name, hours, credits, link)
        self.addNewEntryItem(itemWidget, True)
    
    def addNewEntryItem(self, itemWidget, isCourseInfo):
        item = QListWidgetItem()
        if not isCourseInfo:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable);
        row = self.entryList.count()
        self.entryList.insertItem(row, item)
        self.entryList.setItemWidget(item, itemWidget)
        item.setSizeHint(QtCore.QSize(itemWidget.width(), itemWidget.height()))
    
    def getEntry(self, index):
        i=0
        for s in self.subjects:
            if i == index:
                return s
            i+=1
            for m in s.modules:
                if i == index:
                    return m
                i+=1
                for c in m.catalogues:
                    if i == index:
                        return c
                    i+=1
                    for co in c.courses:
                        if i == index:
                            return co
                        i+=1
                        for ci in co.courseInfos:
                            if i == index:
                                return ci
                            i+=1
                for co2 in m.courses:
                    if i == index:
                        return co2
                    i+=1
                    for ci2 in co2.courseInfos:
                        if i == index:
                            return ci2
                        i+=1

    def getItemWidget(self, idx):
        item = self.entryList.item(idx)
        return self.entryList.itemWidget(item)

    @QtCore.pyqtSlot(bool)
    def toggleCourses(self, toggle):
        if toggle:
            idx = 1
            rowsToHide = []
            itemWidgets = []
            #lastLen = -1
            #TODO: do this search once when the list was fetched from TISS 
            #later, when courses are missing because they are already in one's personal WFK list, manually add them to hiddenItems
            # when they are moved to the personal WFK list
            #while True:
            for s in self.subjects:
                if s.isEmpty():
                    rowsToHide.append(idx)
                idx += 1
                for m in s.modules:
                    if m.isEmpty():
                        rowsToHide.append(idx)
                    idx += 1
                    for c in m.catalogues:
                        if c.isEmpty():
                            rowsToHide.append(idx)
                        idx += 1
                        for co in c.courses:
                            if co.isEmpty():
                                rowsToHide.append(idx)
                            else:
                                for aab in co.courseInfos:
                                    print(aab.name)
                            idx += 1
                    for co2 in m.courses:
                        if co2.isEmpty():
                            rowsToHide.append(idx)
                        else:
                            for aab in co2.courseInfos:
                                print(aab.name)
                        idx += 1

            for row in rowsToHide:
                listWidgetitem = self.entryList.takeItem(row)
                self.hiddenItems[row] = listWidgetitem
        else:
            for row in self.hiddenItems:
                listWidgetitem = self.hiddenItems[row]
                self.entryList.insertItem(row, listWidgetitem)

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.progressBar.setValue(0)
        self.label.setText("")
        self.button.setEnabled(False)
        self.entryList.setEnabled(False)
        self.toggle.setEnabled(False)
        self.startTime = time.time()

    @QtCore.pyqtSlot(str)
    def updateStatus(self, str):
        self.label.setText(str)
        self.progressBar.setValue(self.progressBar.value() + self.fetchIncrement)

    @QtCore.pyqtSlot(object, int)
    def fetchingFinished(self, subjects, count):
        self.subjects = subjects
        self.button.setEnabled(True)
        self.label.setText("Importing entries...")
        self.progressBar.setValue(0)
        i = 0
        for s in subjects:
            self.addNewCategory(s.name, CategoryWidget.SUBJECT)
            i+=1
            for m in s.modules:
                self.addNewCategory(" " + m.name, CategoryWidget.MODULE)
                i+=1
                for c in m.catalogues:
                    self.addNewCategory("  " + c.name, CategoryWidget.CATALOGUE)
                    i+=1
                    for co in c.courses:
                        self.addNewCategory("   " + co.name, CategoryWidget.COURSE)
                        i+=1
                        for ci in co.courseInfos:
                            self.addNewCourseInfo(ci.number, ci.courseType, ci.semester, ci.name, ci.hours, ci.credits, ci.link)
                            i+=1
                            self.label.setText("Importing entries...(%i,%i)"%(i,count))
                            self.progressBar.setValue(int(float(i/count)*100))
                            QtWidgets.qApp.processEvents()
                for co2 in m.courses:
                    self.addNewCategory("   " + co2.name, CategoryWidget.COURSE)
                    i+=1
                    for ci2 in co2.courseInfos:
                        self.addNewCourseInfo(ci2.number, ci2.courseType, ci2.semester, ci2.name, ci2.hours, ci2.credits, ci2.link)
                        i+=1
                        self.label.setText("Importing entries...(%i,%i)"%(i,count))
                        self.progressBar.setValue(int(float(i/count)*100))
                        QtWidgets.qApp.processEvents()
        self.label.setText("Finished (%.2fs)" % (time.time()-self.startTime));
        self.entryList.setEnabled(True)
        self.progressBar.setValue(1)
        self.toggle.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())