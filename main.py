import sys, time, functools
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QTextBrowser, \
                            QDesktopWidget, QLabel, QProgressBar, QListWidget, QAbstractScrollArea, \
                            QAbstractItemView, QListView, QListWidgetItem, QSizePolicy, QGridLayout, QComboBox
from CourseFetcher import WorkerObject
from CourseFetcher import Subject
from CourseWidget import CourseWidget
from CategoryWidget import CategoryWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.timeout = 30
        self.fetchIncrement = 20
        
        self.height = 600
        self.width = 800

        self.initUI()
        self.setupWorkerThread()
    
    def initUI(self):
        
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout()
        centralWidget.setLayout(gridLayout)

        self.semesterBox = QComboBox(self)
        self.semesterBox.addItem("2019S")
        self.semesterBox.addItem("2019W")
        self.semesterBox.setCurrentIndex(1)
        gridLayout.addWidget(self.semesterBox, 0, 0)

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

        self.resize(self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Tiss Program")
        self.resizeEvent = self.windowResizeEvent

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
        self.button.clicked.connect(functools.partial(worker.startWork, self.semesterBox.currentText(), self.timeout))

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

    def addNewCourse(self, number, courseType, semester, name, hours, credits, link):
        itemWidget = CourseWidget(number, courseType, semester, name, hours, credits, link)
        self.addNewEntryItem(itemWidget, True)
    
    def addNewEntryItem(self, itemWidget, isCourse):
        item = QListWidgetItem()
        if not isCourse:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable);
        row = self.entryList.count()
        self.entryList.insertItem(row, item)
        self.entryList.setItemWidget(item, itemWidget)
        item.setSizeHint(QtCore.QSize(itemWidget.width(), itemWidget.height()))

    def getItemWidget(self, idx):
        item = self.entryList.item(idx)
        return self.entryList.itemWidget(item)

    @QtCore.pyqtSlot()
    def prepareFetching(self):
        self.progressBar.setValue(0)
        self.label.setText("")
        self.button.setEnabled(False)
        self.entryList.setEnabled(False)
        self.startTime = time.time()

    @QtCore.pyqtSlot(str)
    def updateStatus(self, str):
        self.label.setText(str)
        self.progressBar.setValue(self.progressBar.value() + self.fetchIncrement)

    @QtCore.pyqtSlot(object, int)
    def fetchingFinished(self, subjects, count):
        self.button.setEnabled(True)
        self.label.setText("Importing entries...")
        self.progressBar.setValue(0)
        i = 0
        for s in subjects:
            #self.addNewCategory(s.name, CategoryWidget.SUBJECT)
            i+=1
            for m in s.modules:
                #self.addNewCategory(" " + m.name, CategoryWidget.MODULE)
                i+=1
                for c in m.catalogues:
                    self.addNewCategory(c.name, CategoryWidget.CATALOGUE)
                    i+=1
                    for co in c.courses:
                        self.addNewCourse(co.number, co.courseType, co.semester, co.name, co.hours, co.credits, co.link)
                        i+=1
                        self.label.setText("Importing entries...(%i,%i)"%(i,count))
                        self.progressBar.setValue(int(float(i/count)*100))
                        QtWidgets.qApp.processEvents()
                for co in m.courses:
                    self.addNewCourse(co.number, co.courseType, co.semester, co.name, co.hours, co.credits, co.link)
                    i+=1
                    self.label.setText("Importing entries...(%i,%i)"%(i,count))
                    self.progressBar.setValue(int(float(i/count)*100))
                    QtWidgets.qApp.processEvents()
        self.label.setText("Finished (%.2fs)" % (time.time()-self.startTime));
        self.entryList.setEnabled(True)
        self.progressBar.setValue(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())