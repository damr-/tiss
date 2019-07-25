from EntryWidget import EntryWidget
from PyQt5.QtWidgets import QLabel

class CategoryWidget(EntryWidget):
    def __init__(self, categoryName):
        self.categoryName = categoryName
        super().__init__()

    def initUI(self):
        super().initUI()
        self.label = QLabel(self)
        self.label.setText(self.categoryName)
        self.label.resize(1000, 30)
        self.horizontalLayout.addWidget(self.label)