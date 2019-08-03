import os.path
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QHBoxLayout, QFrame, QLayout
from CourseWidget import Catalogue
from CourseWidget import Course
    
class CourseStorer():

    FOLDER = "data/"
    ALL_COURSES_FILENAME = "ALL_COURSES.TXT"
    PERSONAL_COURSES_FILENAME = "PERSONAL_COURSES.TXT"
        
    def storeCourses(allCoursesCatalogues, personalCoursesCatalogues):
        CourseStorer._storeCatalogues(allCoursesCatalogues, CourseStorer.ALL_COURSES_FILENAME)
        CourseStorer._storeCatalogues(personalCoursesCatalogues, CourseStorer.PERSONAL_COURSES_FILENAME)

    def _storeCatalogues(catalogues, fileName):
        if not os.path.isdir(CourseStorer.FOLDER):
            os.makedirs(CourseStorer.FOLDER)
        fileName = CourseStorer.FOLDER + fileName

        if os.path.isfile(fileName):
            f = open(fileName, 'r+')
            f.truncate(0)
            f.close()
        f = open(fileName, 'w')

        for index, cat in enumerate(catalogues):
            f.write(Catalogue.catalogueLetters[index] + "\n")
            for c in cat.courses:
                f.write(c.number + "|" + c.courseType + "|" + c.semester + "|" + c.name + "|" + str(c.hours) + "|" + str(c.credits) + "|" + c.link + "\n")
        f.close()

    def loadCourses():
        allCatalogues = CourseStorer._loadCatalogues(CourseStorer.ALL_COURSES_FILENAME)
        personalCatalogues = CourseStorer._loadCatalogues(CourseStorer.PERSONAL_COURSES_FILENAME)
        return (allCatalogues, personalCatalogues)

    def _loadCatalogues(fileName):
        if not os.path.isdir(CourseStorer.FOLDER):
            os.makedirs(CourseStorer.FOLDER)
        fileName = CourseStorer.FOLDER + fileName
        if not os.path.isfile(fileName):
            return []

        f = open(fileName, 'r')
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
