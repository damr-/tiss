from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from PyQt5 import QtCore
from CourseWidget import Course, Catalogue

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
        return webdriver.Firefox(options=options)

    def getVertiefung1Courses(self, url, semester, TIMEOUT):
        self.updateSignal.emit("Connecting to TISS...")

        try:
            self.driver.get(url)
        except WebDriverException:
            return [], "Connection error"

        try:
            WebDriverWait(self.driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID, 'j_id_2e')))
        except TimeoutException:
            return [], "Timed out"

        self.updateSignal.emit(f"Selecting semester {semester}...")
        semesterSelect = Select(self.driver.find_element_by_id('j_id_2e:semesterSelect'))
        semesterSelect.select_by_visible_text(semester)

        try:
            WebDriverWait(self.driver, TIMEOUT).until(EC.invisibility_of_element_located((By.ID, 'j_id_2e:j_id_2j')))
        except TimeoutException:
            return [], "Timed out"

        self.updateSignal.emit("Fetching entries...")
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        allEntries = soup.select("div.ui-outputpanel")

        headerChilds = soup.select("div.ui-outputpanel > span.bold")
        headers = []
        for c in headerChilds:
            headers.append(c.parent)

        # Only take courses with an actual existing TISS page
        coursesChilds = soup.select("div.ui-outputpanel > div.courseKey")
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
        return filteredEntries, ""

    def sortEntries(self, entries, semester, exactSemester):
        catalogues = []
        i = 0
        curCatalogue = None

        for entry in entries:
            self.updateSignal.emit(f"Sorting entries ({i+1}/{len(entries)})...")

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
                curSemester = firstRow[2]
                if not exactSemester or curSemester == semester:
                    name = parts[2]
                    link = linkprefix + entry.findChild("div", {"class": "courseTitle"}, recursive=False).findChild("a")['href']
                    aunts = entry.parent.parent.findChildren("td", recursive=False)
                    hours = float(aunts[2].text.strip())
                    credits = float(aunts[3].text.strip())
                    newCourse = Course(number, courseType, curSemester, name, hours, credits, link)
                    curCatalogue.courses.append(newCourse)
            elif isCanceledCourse(entry):
                pass
            else:
                print("ERROR: Could not categorize " + ' '.join(entry.text.replace('\n', ' ').split()))
            i += 1
        return catalogues

    def startWork(self, semesterSelectBox, exactSemesterBox, timeout):
        semester = semesterSelectBox.currentText()
        exactSemester = exactSemesterBox.isChecked()
        self.driver = self.startGecko()
        courses, msg = self.getVertiefung1Courses(coursesURL, semester, timeout)
        self.driver.quit()
        vertiefungen = self.sortEntries(courses, semester, exactSemester)
        if len(courses) > 0:
            self.updateSignal.emit("Fetching finished")
        else:
            self.updateSignal.emit("Fetching aborted: " + msg)
        self.doneSignal.emit(vertiefungen)
