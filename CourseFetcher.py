import time
from collections import deque
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from PyQt5 import QtCore, QtGui, QtWidgets

coursesURL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=43093&semester=NEXT"
transferablesURL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?date=20191001&key=57214"
ignoredRows = ["Abschlussprüfung Kommissionelle Gesamtprüfung", "Abschlussarbeit Diplomarbeit", "Diplomarbeit und kommissionelle Gesamtprüfung", 
                "Lehrveranstaltungen des ATHENS-Programmes oder von Gastprofessuren", "Wahlfachkataloge", "LVA-Nummern dazu", "Projektarbeiten", 
                "Katalog Projektarbeiten", "LVAs aus dem entsprechenden Angleichkatalog und aus den gebundenen WFK",
                "Externe Lehrveranstaltungen am IFF Wien"]
catalogueNames = ['WFK', 'Katalog Freie Wahlfächer - Technische Physik', 'Modulgruppe ', 'Technik für Menschen', 'Gender Awareness', 'Sprachkompetenz',
                'Sozialkompetenz', 'Medienkompetenz', 'Rechts- und wirtschaftswissenschaftliche Kompetenz', 'Sonstiges']
moduleNames = ['Freie Wahlfächer', "Transferable Skills"]
linkprefix = "https://tiss.tuwien.ac.at"

class Subject:
    def __init__(self, name):
        self.name = name
        self.modules = []

class Module:
    def __init__(self, name):
        self.name = name
        self.catalogues = []
        self.courses = []        #if the module has no catalogues it has courses, but never both!

class Catalogue:
    def __init__(self, name):
        self.name = name
        self.courses = []

class Course:
    def __init__(self, name):
        self.name = name
        self.courseInfos = []

class CourseInfo:
    def __init__(self, number, name, courseType, semester, link, hours, credits):
        self.number = number
        self.name = name
        self.courseType = courseType
        self.semester = semester
        self.link = link
        self.hours = hours
        self.credits = credits

def isSubject(element):
    return 'Prüfungsfach' in element.text
def isModule(element):
    return any(element.text.strip() in s for s in moduleNames) or 'Modul ' in element.text
def isCatalogue(element):
    return any(s in element.text for s in catalogueNames)
def isCourse(element):
    return element['class'][-2] == 'item' #any('item' in c for c in element['class']]):
def isCourseInfo(element):
    return 'course' in element['class'][-2].lower() #can also be 'canceledCourse'  #any('course' in c for c in element['class']]):

class WorkerObject(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

    def startGecko(self):
        self.updateSignal.emit("Starting headless browser...")
        options = Options()
        options.headless = True
        return webdriver.Firefox(options=options) # use headless firefox to get page with generated content

    def getEntries(self, url, driver, semester, TIMEOUT, isTransferables):
        if not isTransferables:
            self.updateSignal.emit("Connecting to TISS...")
        driver.get(url)
        WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID,'j_id_2b'))) #Wait until main body with courses has been loaded

        if not isTransferables:
            self.updateSignal.emit("Selecting semester %s..." % semester)
        semesterSelect = Select(driver.find_element_by_id('j_id_2b:semesterSelect'))
        semesterSelect.select_by_visible_text(semester) #Select the correct semester
        WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element_located((By.ID, 'j_id_2b:j_id_2g'))) #Wait until spinning gif vanished

        if not isTransferables:
            self.updateSignal.emit("Fetching courses...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup.select("div.ui-outputpanel")

    def sortCourses(self, courses):
        subjects = []
        i=0
        curSubject = curModule = curCatalogue = curCourse = None
        for entry in courses:
            self.updateSignal.emit("Sorting courses (%i/%i)..." % ((i+1), len(courses)))

            if any('nodeTable-level-0' in c for c in entry['class']) or \
                any(entry.text.strip() in ignored for ignored in ignoredRows):
                pass #Skip the main "Masterstudium Technische Physik" headline row and other specific rows
            elif isSubject(entry):
                curSubject = Subject(entry.text)
                subjects.append(curSubject)
            elif isModule(entry):
                curModule = Module(entry.text)
                curCatalogue = None
                curSubject.modules.append(curModule)
            elif isCatalogue(entry):
                curCatalogue = Catalogue(entry.text.strip())
                curModule.catalogues.append(curCatalogue)
            elif isCourse(entry):
                name = entry.text.strip() #[4:] to skip the course type at the start
                curCourse = Course(name)
                if curCatalogue == None:
                    curModule.courses.append(curCourse)
                else:
                    curCatalogue.courses.append(curCourse)
            elif isCourseInfo(entry):
                parts = entry.text.strip().splitlines()
                firstRow = parts[0].split(' ')
                number = firstRow[0]
                courseType = firstRow[1]
                semester = firstRow[2]
                name = parts[2]
                link = linkprefix + entry.findChild("div", {"class": "courseTitle"}, recursive=False).findChild("a")['href']
                aunts = entry.parent.parent.findChildren("td", recursive=False)
                hours = float(aunts[2].text.strip())
                credits = float(aunts[3].text.strip())        
                curCourse.courseInfos.append(CourseInfo(number, name, courseType, semester, link, hours, credits))
            else:
                print("Could not categorize " + ' '.join(entry.text.replace('\n',' ').split()))
            i+=1
        return subjects

    @QtCore.pyqtSlot()
    def startWork(self, semester, timeout):
        totalStart = time.time()
        driver = self.startGecko()

        courses = self.getEntries(coursesURL, driver, semester, timeout, False)
        transferablesCourses = self.getEntries(transferablesURL, driver, semester, timeout, True)[1:]  #The first row is another "Transferable Skills"
        
        #Find "Transferable Skills" row and add the transferable skill courses
        idx = 0
        for entry in courses:
            idx += 1
            if isModule(entry) and "Transferable Skills" in entry.text:
                break
        courses[idx:idx] = transferablesCourses
        
        subjects = self.sortCourses(courses)
        driver.quit()
        self.updateSignal.emit("Fetching finished (%.2fs)" %(time.time()-totalStart))
        self.doneSignal.emit(subjects)