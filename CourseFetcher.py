from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from PyQt5 import QtCore
from CourseWidget import Course
from CourseWidget import Catalogue

coursesURL = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=43093&semester=NEXT"
linkprefix = "https://tiss.tuwien.ac.at"
ignoredRows = ["Lehrveranstaltungen des ATHENS-Programmes oder von Gastprofessuren", "Wahlfachkataloge", "LVA-Nummern dazu", "Gebundener WFK D) Angewandte Physik (Fortsetzung)"]

def isCatalogue(element):
    return 'WFK' in element.text
def isCourse(element):
    return 'course' == element['class'][-2] #any('course' in c for c in element['class']]):
def isCanceledCourse(element):
    return 'canceledCourse' == element['class'][-2]

class WorkerObject(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.driver = None

    def startGecko(self):
        self.updateSignal.emit("Starting headless browser...")
        options = Options()
        options.headless = True
        return webdriver.Firefox(options=options)  # use headless firefox to get page with generated content

    def getEntries(self, url, driver, semester, TIMEOUT, isTransferables):
        if not isTransferables:
            self.updateSignal.emit("Connecting to TISS...")
        driver.get(url)
        WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID,'j_id_2b')))  #Wait until main body with courses has been loaded

        if not isTransferables:
            self.updateSignal.emit("Selecting semester %s..." % semester)
        semesterSelect = Select(driver.find_element_by_id('j_id_2b:semesterSelect'))
        semesterSelect.select_by_visible_text(semester) #Select the correct semester
        WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element_located((By.ID, 'j_id_2b:j_id_2g')))  #Wait until spinning gif vanished

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
        
    def getVertiefung1Courses(self, url, semester, TIMEOUT):
        self.updateSignal.emit("Connecting to TISS...")
        self.driver.get(url)

        WebDriverWait(self.driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID,'j_id_2b')))
        #TODO HANDLE TIMEOUT EXCEPTION

        self.updateSignal.emit("Selecting semester %s..." % semester)
        semesterSelect = Select(self.driver.find_element_by_id('j_id_2b:semesterSelect'))
        semesterSelect.select_by_visible_text(semester)
        WebDriverWait(self.driver, TIMEOUT).until(EC.invisibility_of_element_located((By.ID, 'j_id_2b:j_id_2g')))
        #TODO HANDLE TIMEOUT EXCEPTION

        self.updateSignal.emit("Fetching entries...")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        allEntries = soup.select("div.ui-outputpanel")
        
        headerChilds = soup.select("div.ui-outputpanel > span.bold")
        headers = []
        for c in headerChilds:
            headers.append(c.parent)
        coursesChilds = soup.select("div.ui-outputpanel > div.courseKey") #only take courses with an actual existing TISS page
        courses = []
        for c in coursesChilds:
            courses.append(c.parent)

        start = soup.findAll("span", text="Vertiefung 1")[0].parent
        end = soup.findAll("span", text="Vertiefung 2")[0].parent

        filteredEntries = []
        found = False
        for entry in allEntries:
            if entry == start:
                found = True
                continue
            elif entry == end:
                break
            if found and (entry in headers or entry in courses):
                filteredEntries.append(entry)
        return filteredEntries

    def sortEntries(self, entries):
        catalogues = []
        i=0
        curCatalogue = None

        for entry in entries:
            self.updateSignal.emit("Sorting entries (%i/%i)..." % ((i+1), len(entries)))
            
            if any(entry.text.strip() == ignored for ignored in ignoredRows):
                pass
            elif isCatalogue(entry):
                curCatalogue = Catalogue(entry.text.strip())
                catalogues.append(curCatalogue)
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
                newCourse = Course(number, courseType, semester, name, hours, credits, link)
                curCatalogue.courses.append(newCourse)
            elif isCanceledCourse(entry):
                pass
            else:
                print("ERROR: Could not categorize " + ' '.join(entry.text.replace('\n',' ').split()))
            i+=1
        return catalogues

    def startWork(self, semester, timeout):
        self.driver = self.startGecko()
        courses = self.getVertiefung1Courses(coursesURL, semester, timeout)
        vertiefungen = self.sortEntries(courses)
        self.driver.quit()
        self.updateSignal.emit("Fetching finished")
        self.doneSignal.emit(vertiefungen)

    #TODO Test this
    def abort(self):
        self.driver.quit()
