import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextBrowser, QPushButton, QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, QAbstractItemView, QListView, QListWidgetItem, QSizePolicy
from PyQt5 import QtCore, QtGui
import functools
from CourseFetcher import WorkerObject
from CourseFetcher import Subject
from CourseWidget import CourseWidget
from EntryWidget import EntryWidget

class App(QWidget):
    #signalStatus = QtCore.pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupWorkerThread()
        #self.connectSignals()
    
    def initUI(self):
        self.semester = "2019W"
        self.timeout = 30
        self.progress = 0
        self.increment = 20

        height = 600
        width = 800
        
        self.button = QPushButton("do", self)
        self.button.move(0, 0)
        self.button.resize(50, 50)

        self.label = QLabel("<Status output>", self)
        self.label.move(60, 5)
        self.label.resize(250, 25)

        self.progressBar = QProgressBar(self)
        self.progressBar.move(60, 15)
        self.progressBar.resize(250, 50)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

        #self.textEdit = QTextBrowser(self)
        #self.textEdit.move(70, 70)
        #self.textEdit.resize(width * 0.8, height * 0.8)
        #self.textEdit.setReadOnly(False)
        #self.textEdit.setOpenExternalLinks(True)

        self.entryList = QListWidget(self) #(gridLayout instead of self or sth)
        self.entryList.move(70, 70)
        self.entryList.resize(width * 0.8, height * 0.8)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.entryList.sizePolicy().hasHeightForWidth())
        self.entryList.setSizePolicy(sizePolicy)
        self.entryList.setMinimumSize(QtCore.QSize(50, 50))
        self.entryList.setMaximumSize(QtCore.QSize(9000, 9000))
        self.entryList.setSizeIncrement(QtCore.QSize(0, 0))
        font =  QtGui.QFont()
        font.setPointSize(10)
        self.entryList.setFont(font)
        self.entryList.setStyleSheet("selection-background-color: rgb(159, 181, 255);")
        self.entryList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.entryList.setAutoScrollMargin(1)
        self.entryList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.entryList.setProperty("showDropIndicator", False)
        self.entryList.setDragEnabled(False)
        self.entryList.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.entryList.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.entryList.setSelectionMode(QAbstractItemView.SingleSelection) #.ExtendedSelection
        self.entryList.setResizeMode(QListView.Adjust)
        self.entryList.setUniformItemSizes(False)
        self.entryList.setObjectName("courseList")


        self.resize(width,height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")
        self.show()

        #self.addNewCourse("100.000", "VO", "2019W", "TEST", 2, 3, "http://www.google.com")
        #self.addNewEntry("TEST2")

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
    
    def addNewEntry(self, text):
        itemWidget = EntryWidget(text)
        self.addNewEntryItem(itemWidget)

    def addNewCourse(self, number, courseType, semester, name, hours, credits, link):
        itemWidget = CourseWidget(number, courseType, semester, name, hours, credits, link)
        self.addNewEntryItem(itemWidget)
        
    def addNewEntryItem(self, itemWidget):
        item = QListWidgetItem()
        row = self.entryList.currentRow() + 1
        if len(self.entryList.selectedItems()) == 0:
            row = self.entryList.count()
        self.entryList.insertItem(row, item)
        self.entryList.setItemWidget(item, itemWidget)
        item.setSizeHint(QtCore.QSize(0, itemWidget.height()))

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.progressBar.setValue(0)
        self.label.setText("")
        self.button.setEnabled(False)

    @QtCore.pyqtSlot(str)
    def updateStatus(self, str):
        self.label.setText(str)
        self.progress += self.increment
        self.progressBar.setValue(self.progress)

    @QtCore.pyqtSlot(object)
    def fetchingFinished(self, subjects):
        #text = "" 
        #TODO try to replace this by another worker!?
        self.button.setEnabled(True)
        for s in subjects:
            self.addNewEntry(s.name)
            for m in s.modules:
                self.addNewEntry("  " + m.name)
                for c in m.catalogues:
                    self.addNewEntry("    " + c.name)
                    for co in c.courses:
                        self.addNewEntry("      " + co.name)
                        for ci in co.courseInfos:
                            self.addNewCourse(ci.number, ci.courseType, ci.semester, ci.name, ci.hours, ci.credits, ci.link)
                for co2 in m.courses:
                    self.addNewEntry("      " + co2.name)
                    for ci2 in co2.courseInfos:
                        self.addNewCourse(ci2.number, ci2.courseType, ci2.semester, ci2.name, ci2.hours, ci2.credits, ci2.link)
        #self.textEdit.setText(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())