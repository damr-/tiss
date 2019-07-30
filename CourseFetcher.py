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
from PyQt5 import QtCore

coursesURL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=43093&semester=NEXT"
transferablesURL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?date=20191001&key=57214"
linkprefix = "https://tiss.tuwien.ac.at"
ignoredRows = ["Lehrveranstaltungen des ATHENS-Programmes oder von Gastprofessuren", "Wahlfachkataloge", "LVA-Nummern dazu"]

class Subject:
    def __init__(self, name):
        self.name = name
        self.modules = []
    def isEmpty(self):
        return len(self.modules) == 0

class Module:
    def __init__(self, name):
        self.name = name
        self.catalogues = [] #if the module has no catalogues it has courses, but never both!
        self.courses = []
    def isEmpty(self):
        return len(self.catalogues) == 0 and len(self.courses) == 0

class Catalogue:
    def __init__(self, name):
        self.name = name
        self.courses = []
    
    def isEmpty(self):
        return len(self.courses) == 0

class Course:
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
    return 'Modul ' in element.text
def isCatalogue(element):
    return 'WFK' in element.text
def isCourse(element):
    return 'course' in element['class'][-2].lower() #can also be 'canceledCourse'  #any('course' in c for c in element['class']]):

class WorkerObject(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(object, int)

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
            self.updateSignal.emit("Fetching entries...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        allEntries = soup.select("div.ui-outputpanel")

        headerChilds = soup.select("div.ui-outputpanel span.bold")
        headers = []
        for c in headerChilds:
            if c.parent.name == 'a':
                headers.append(c.parent.parent)
            else:
                headers.append(c.parent)

        coursesChilds = soup.select("div.ui-outputpanel > div.courseKey") #only take courses with an actual existing TISS page
        courses = []
        for c in coursesChilds:
            courses.append(c.parent)

        filteredEntries = []
        for entry in allEntries:
            if entry in headers:
                filteredEntries.append(entry)
                headers.remove(entry)
            elif entry in courses:
                filteredEntries.append(entry)
                courses.remove(entry)
        return filteredEntries
        
    def getVertiefung1Courses(self, url, driver, semester, TIMEOUT):
        self.updateSignal.emit("Connecting to TISS...")
        driver.get(url)
        WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID,'j_id_2b')))

        self.updateSignal.emit("Selecting semester %s..." % semester)
        semesterSelect = Select(driver.find_element_by_id('j_id_2b:semesterSelect'))
        semesterSelect.select_by_visible_text(semester)
        WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element_located((By.ID, 'j_id_2b:j_id_2g')))

        self.updateSignal.emit("Fetching entries...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        allEntries = soup.select("div.ui-outputpanel")

        
        headerChilds = soup.select("div.ui-outputpanel > span.bold")
        headers = []
        for c in headerChilds:
            headers.append(c.parent)
        coursesChilds = soup.select("div.ui-outputpanel > div.courseKey") #only take courses with an actual existing TISS page
        courses = []
        for c in coursesChilds:
            courses.append(c.parent)
        """
        filteredEntries = []
        foundVertiefung1 = False
        for entry in allEntries:
            text = entry.text.strip()
            if entry in headers and "Module Vertiefung 1" in text:
                filteredEntries.append(entry)
                headers.remove(entry)
            elif entry in courses:
                filteredEntries.append(entry)
                courses.remove(entry)
        """

        start = soup.findAll("span", text="Vertiefung 1")[0].parent
        end = soup.findAll("span", text="Vertiefung 2")[0].parent

        filteredEntries = []
        found = False
        for entry in allEntries:
            if entry == start:
                found = True
            elif entry == end:
                break
            if found and (entry in headers or entry in courses):
                filteredEntries.append(entry)
        return filteredEntries

    def sortEntries(self, entries):
        subjects = []
        i=0
        curModule = curCatalogue = None
        skippingVertiefung2 = False
        foundFirstFreieWF = False
        skippingModulProjektarbeit = False

        curSubject = Subject("Vertiefungen")
        subjects.append(curSubject)

        for entry in entries:
            self.updateSignal.emit("Sorting entries (%i/%i)..." % ((i+1), len(entries)))
            
            if any(entry.text.strip() in ignored for ignored in ignoredRows):
                pass
            elif isModule(entry):
                curModule = Module(entry.text.strip())
                curCatalogue = None
                curSubject.modules.append(curModule)
            elif isCatalogue(entry):
                curCatalogue = Catalogue(entry.text.strip())
                curModule.catalogues.append(curCatalogue)
            elif isCourse(entry):
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
                newCourse = Course(number, name, courseType, semester, link, hours, credits)
                if curCatalogue == None:
                    curModule.courses.append(newCourse)
                else:
                    curCatalogue.courses.append(newCourse)         
            else:
                print("Could not categorize " + ' '.join(entry.text.replace('\n',' ').split()))
            i+=1
        return subjects

    @QtCore.pyqtSlot()
    def startWork(self, semester, timeout):
        driver = self.startGecko()

        #courses = self.getEntries(coursesURL, driver, semester, timeout, False)
        #transferablesCourses = self.getEntries(transferablesURL, driver, semester, timeout, True)[1:]  #The first row is another "Transferable Skills"

        """        
        #Find "Transferable Skills" row and add the transferable skill courses
        idx = 0
        for entry in courses:
            idx += 1
            if "Transferable" in entry.text.strip():
                break
        courses[idx:idx] = transferablesCourses
        """

        courses = self.getVertiefung1Courses(coursesURL, driver, semester, timeout)
        vertiefungen = self.sortEntries(courses)

        driver.quit()
        self.updateSignal.emit("Fetching finished")

        count = 0
        for s in vertiefungen:
            count += 1
            for m in s.modules:
                count += 1
                for c in m.catalogues:
                    count += 1
                    for co in c.courses:
                        count += 1
                for co2 in m.courses:
                    count += 1
        self.doneSignal.emit(vertiefungen, count)

class WorkerObject2(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(object, int)

    @QtCore.pyqtSlot()
    def startWork(self, entryList, entries):
        pass