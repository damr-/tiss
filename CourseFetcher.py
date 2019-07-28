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
    def isEmpty(self):
        return len(self.modules) == 0

class Module:
    def __init__(self, name):
        self.name = name
        self.catalogues = []
        self.courses = []        #if the module has no catalogues it has courses, but never both!
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
    return any(element.text.strip() == s for s in moduleNames) or 'Modul ' in element.text
def isCatalogue(element):
    return any(s in element.text for s in catalogueNames)
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
        headerChilds = soup.select("div.ui-outputpanel > span.bold")
        headers = []
        for c in headerChilds:
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
        
    def sortEntries(self, entries):
        subjects = []
        i=0
        curSubject = curModule = curCatalogue = None
        foundFirstFreieWF = False
        skippingVertiefung2 = False

        for entry in entries:
            self.updateSignal.emit("Sorting entries (%i/%i)..." % ((i+1), len(entries)))

            if any('nodeTable-level-0' in c for c in entry['class']) or \
                any(entry.text.strip() in ignored for ignored in ignoredRows):
                pass #Skip the main "Masterstudium Technische Physik" headline row and other specific rows
            elif isSubject(entry):
                text = entry.text
                if skippingVertiefung2: #The next subject is "Allgemeine Pflichtfächer"
                    text = entry.text + "(Vertiefung 2 ONLY)"   #add text to clarify that it's only for "Vertiefung 2"
                    skippingVertiefung2 = False                 #stop skipping
                curSubject = Subject(text)
                subjects.append(curSubject)                
            elif isModule(entry):
                if entry.text.strip() == "Freie Wahlfächer": #For some reason, there are two "Freie Wahlfächer" in the list.
                    if not foundFirstFreieWF:
                        foundFirstFreieWF = True
                    else:   #skip second "Freie Wahlfächer"
                        i+=1
                        continue
                elif entry.text.strip() == "Modul Vertiefung 2":
                    skippingVertiefung2 = True
                    i += 1
                    continue
                
                curModule = Module(entry.text)
                curCatalogue = None
                curSubject.modules.append(curModule)
            elif skippingVertiefung2:
                i += 1
                continue
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

        courses = self.getEntries(coursesURL, driver, semester, timeout, False)
        transferablesCourses = self.getEntries(transferablesURL, driver, semester, timeout, True)[1:]  #The first row is another "Transferable Skills"
        
        #Find "Transferable Skills" row and add the transferable skill courses
        idx = 0
        for entry in courses:
            idx += 1
            if isModule(entry) and "Transferable Skills" in entry.text:
                break
        courses[idx:idx] = transferablesCourses
        
        subjects = self.sortEntries(courses)
        driver.quit()
        self.updateSignal.emit("Fetching finished")
        count = 0
        for s in subjects:
            count += 1
            for m in s.modules:
                count += 1
                for c in m.catalogues:
                    count += 1
                    for co in c.courses:
                        count += 1
                for co2 in m.courses:
                    count += 1
        self.doneSignal.emit(subjects, count)

class WorkerObject2(QtCore.QObject):
    updateSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(object, int)

    @QtCore.pyqtSlot()
    def startWork(self, entryList, entries):
        pass