import sys, time, functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextBrowser, QTabWidget, \
                            QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, \
                            QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout, QComboBox
from CourseFetcher import WorkerObject
from CourseFetcher import Catalogue
from CourseWidget import CourseWidget
from CategoryWidget import CategoryWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.timeout = 30
        self.fetchIncrement = 20
        self.height = 600
        self.width = 800
        self.entryLists = []
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
        self.tabWidget.setMinimumSize(QtCore.QSize(50, 50))

        self.entryListA, self.entryListB, self.entryListC, self.entryListD = (QListWidget(self) for i in range(4))
        self.entryLists.append(self.entryListA)
        self.entryLists.append(self.entryListB)
        self.entryLists.append(self.entryListC)
        self.entryLists.append(self.entryListD)

        for index, l in enumerate(self.entryLists):
            l.setSizePolicy(sizePolicy)
            l.setMinimumSize(QtCore.QSize(50, 50))
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

            self.tabWidget.addTab(l, self.catalogueLetters[index])
        
        gridLayout.addWidget(self.tabWidget, 0, 1, 10, 5)

        self.resize(self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")

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

    def addNewCourse(self, catalogueList, number, courseType, semester, name, hours, credits, link):
        itemWidget = CourseWidget(number, courseType, semester, name, hours, credits, link)
        item = QListWidgetItem()
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable);
        row = catalogueList.count()
        catalogueList.insertItem(row, item)
        catalogueList.setItemWidget(item, itemWidget)
        item.setSizeHint(QtCore.QSize(itemWidget.width(), itemWidget.height()))

    def getItemWidget(self, catalogueList, idx):
        item = catalogueList.item(idx)
        return catalogueList.itemWidget(item)

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.progressBar.setValue(0)
        self.label.setText("")
        self.semesterSelectBox.setEnabled(False)
        self.button.setEnabled(False)
        for l in self.entryLists:
            l.setEnabled(False)
            
        #TODO: REMOVE ALL ITEMS FROM entryListABCD
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
        
        for index, c in enumerate(catalogues):
            currentListWidget = self.entryLists[index]
            for i, co in enumerate(c.courses):
                self.addNewCourse(currentListWidget, co.number, co.courseType, co.semester, co.name, co.hours, co.credits, co.link)
                self.label.setText("Importing \"WFK %s\"...(%i,%i)"%(self.catalogueLetters[index], i, len(c.courses)))
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