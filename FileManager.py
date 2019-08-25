import os.path
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QFrame, QLayout
from CourseWidget import Catalogue
from CourseWidget import Course
    
class FileManager():
    FOLDER = "data/"
    ALL_COURSES_FILENAME = "ALL_COURSES.TXT"
    PERSONAL_COURSES_FILENAME = "PERSONAL_COURSES.TXT"
    SETTINGS_FILENAME = "SETTINGS.TXT"
        
    def storeCourses(allCoursesCatalogues, personalCoursesCatalogues):
        FileManager._storeCatalogues(allCoursesCatalogues, FileManager.ALL_COURSES_FILENAME)
        FileManager._storeCatalogues(personalCoursesCatalogues, FileManager.PERSONAL_COURSES_FILENAME)

    def _storeCatalogues(catalogues, fileName):
        f = FileManager.openFile(fileName, True)
        for index, cat in enumerate(catalogues):
            f.write(Catalogue.catalogueLetters[index] + "\n")
            for c in cat.courses:
                f.write(c.number + "|" + c.courseType + "|" + c.semester + "|" + c.name + "|" + str(c.hours) + "|" + str(c.credits) + "|" + c.link + "\n")
        f.close()

    def loadCourses():
        allCatalogues = FileManager._loadCatalogues(FileManager.ALL_COURSES_FILENAME)
        personalCatalogues = FileManager._loadCatalogues(FileManager.PERSONAL_COURSES_FILENAME)
        return (allCatalogues, personalCatalogues)

    def _loadCatalogues(fileName):
        f = FileManager.openFile(fileName, False)
        if f == None:
            return []

        catalogues = []
        curCatalogue = None
        for line in f:
            text = line.strip()

            if any(text == letter for letter in Catalogue.catalogueLetters):
                curCatalogue = Catalogue(text)
                catalogues.append(curCatalogue)
                continue

            parts = text.split('|')

            number = parts[0]
            courseType = parts[1]
            semester = parts[2]
            name = parts[3]
            hours = float(parts[4])
            credits = float(parts[5])
            link = parts[6]

            c = Course(number, courseType, semester, name, hours, credits, link)
            curCatalogue.courses.append(c)
        f.close()
        return catalogues

    def storeSettings(settings):
        f = FileManager.openFile(FileManager.SETTINGS_FILENAME, True)
        text = ""
        for s in settings:
            text += str(s) + "|"
        f.write(text[:-1])

    def loadSettings():
        f = FileManager.openFile(FileManager.SETTINGS_FILENAME, False)
        if f == None:
            return []
        data = f.readline().split('|')
        return data

    def str2bool(text):
        return text == "True"

    def openFile(fileName, write):
        if not os.path.isdir(FileManager.FOLDER):
            os.makedirs(FileManager.FOLDER)
        fileName = FileManager.FOLDER + fileName

        if write:
            if os.path.isfile(fileName):
                f = open(fileName, 'r+')
                f.truncate(0)
                f.close()
            return open(fileName, 'w')
        if os.path.isfile(fileName):
            return open(fileName, 'r')
        return None
