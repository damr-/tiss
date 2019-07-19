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

semester = "2019W"
url = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?key=43093&semester=NEXT"
transf_skills_url = "https://tiss.tuwien.ac.at/curriculum/public/curriculum.xhtml?date=20191001&key=57214"
ignored_rows = ["Abschlussprüfung Kommissionelle Gesamtprüfung", "Abschlussarbeit Diplomarbeit", "Diplomarbeit und kommissionelle Gesamtprüfung", 
                "Lehrveranstaltungen des ATHENS-Programmes oder von Gastprofessuren", "Wahlfachkataloge", "LVA-Nummern dazu", "Projektarbeiten", 
                "Katalog Projektarbeiten", "LVAs aus dem entsprechenden Angleichkatalog und aus den gebundenen WFK"]
linkprefix = "https://tiss.tuwien.ac.at"
DEBUG_LOG = False
TIMEOUT = 20

class Subject:
    name = ""
    modules = []
    def __init__(self, name):
        self.name = name

class Module:
    name = ""
    catalogues = []
    courses = []        #if the module has no catalogues it has courses, but never both!
    def __init__(self, name):
        self.name = name

class Catalogue:
    name = ""
    courses = []
    def __init__(self, name):
        self.name = name

class Course:
    name = ""
    courseInfos = []
    def __init__(self, name):
        self.name = name

class CourseInfo:
    number = 0
    name = ""
    courseType = ""
    semester = ""
    link = ""
    hours = 0
    credits = 0
    def __init__(self, number, name, courseType, semester, link): #, hours, credits
        self.number = number
        self.name = name
        self.courseType = courseType
        self.semester = semester
        self.link = link
        #self.hours = hours
        #self.credits = credits

def isSubject(element):
    return 'Prüfungsfach' in element.text
def isModule(element):
    return any(element.text.strip() in s for s in ['Freie Wahlfächer', "Transferable Skills"]) or 'Modul ' in element.text
def isCatalogue(element):
    return any(s in element.text for s in ['WFK', 'Katalog Freie Wahlfächer - Technische Physik', 'Modulgruppe '])
def isCourse(element):
    return element['class'][-2] == 'item' #any('item' in c for c in element['class']]):
def isCourseInfo(element):
    return 'course' in element['class'][-2].lower() #can also be 'canceledCourse'  #any('course' in c for c in element['class']]):

def get_entries(url, driver, is_transferables):
    if not is_transferables:
        print("Loading main website...", end='', flush=True)
    else:
        print("Loading transferables website...", end='', flush=True)
    start = time.time()
    driver.get(url)
    WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.ID,'j_id_2b'))) #Wait until main body with courses has been loaded
    print("done (%.2fs)" % (time.time()-start))

    print("Selecting semester...", end='', flush=True)
    start = time.time()
    semesterSelect = Select(driver.find_element_by_id('j_id_2b:semesterSelect'))
    semesterSelect.select_by_visible_text(semester) #Select the correct semester
    WebDriverWait(driver, TIMEOUT).until(EC.invisibility_of_element_located((By.ID, 'j_id_2b:j_id_2g'))) #Wait until spinning gif vanished
    print("done (%.2fs)" % (time.time()-start))

    print("Beautifying HTML...", end='', flush=True)
    start = time.time()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print("done (%.2fs)" % (time.time()-start))

    print("Gathering all entries...", end='', flush=True)
    start = time.time()
    entries = soup.select("div.ui-outputpanel")
    print("done (%.2fs)" % (time.time()-start))
    return entries

options = Options()
options.headless = True
totalStart = time.time()

print("Starting headless gecko...", end='', flush=True)
start = time.time()
driver = webdriver.Firefox(options=options) # use headless firefox to get page with generated content
print("done (%.2fs)" % (time.time()-start))

entries = get_entries(url, driver, False)
transferable_skill_entries = get_entries(transf_skills_url, driver, True)[1:]  #The first row is another "Transferable Skills"

#Find "Transferable Skills" row and add the transferable skill entries
idx = 0
for entry in entries:
    if isModule(entry) and "Transferable Skills" in entry.text:
        idx = entries.index(entry) + 1
        break
entries[idx:idx] = transferable_skill_entries

i=0
start = time.time()
subjects = []
curSubject = curModule = curCatalogue = curCourse = None
if DEBUG_LOG:
    print("Sorting entries...")

for entry in entries:
    if not DEBUG_LOG:
        print("Sorting entries (%i/%i)..." % ((i+1), len(entries)) , end='\r', flush=True)

    if any('nodeTable-level-0' in c for c in entry['class']) or \
        any(entry.text.strip() in ignored for ignored in ignored_rows):
        pass #Skip the main 'Masterstudium Technische Physik' headline row and other specific rows
    elif isSubject(entry):
        if DEBUG_LOG:
            print("SUBJECT: " + entry.text);
        curSubject = Subject(entry.text)
        subjects.append(curSubject)
    elif isModule(entry):
        if DEBUG_LOG:
            print("   MODULE: " + entry.text);
        curModule = Module(entry.text)
        curSubject.modules.append(curModule)
    elif isCatalogue(entry):
        if DEBUG_LOG:
            print("      CATALOGUE: " + entry.text.strip());
        curCatalogue = Catalogue(entry.text.strip())
        curModule.catalogues.append(curCatalogue)
    elif isCourse(entry):
        name = entry.text.strip()[4:] #Skip the course type at the start
        if DEBUG_LOG:
            print("         COURSE: " + name);
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
        #TODO The entry's parent's second and third sibling are Stunden and ECTS. GET THEM!
        #hours = 
        #credits = 
        if DEBUG_LOG:
            print("            COURSEI: " + number + " " + courseType + " " + semester + " " + name + " " + link); #+hours+credits
        curCourse.courseInfos.append(CourseInfo(number, name, courseType, semester, link)) #hours, credits))
    else: #TODO fix the transferables which cannot be categorized yet
        print("Could not categorize " + ' '.join(entry.text.replace('\n',' ').split()))
    i+=1
print("Sorting entries (%i/%i)...done (%.2fs)" % (len(entries), len(entries), (time.time()-start)))
print("Total duration: %.2fs" %(time.time()-totalStart))
driver.quit()