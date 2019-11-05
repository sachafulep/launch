import sys
import subprocess
import collections
from pathlib import Path
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QListWidget, QLineEdit, QVBoxLayout, QWidget, QLabel
from PySide2.QtCore import SIGNAL, QObject


def run():
    app = QtWidgets.QApplication([])
    mainWidget = MainWidget()
    mainWidget.show()
    mainWidget.lineEdit.setFocus()
    sys.exit(app.exec_())


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.installEventFilter(self)

        self.listWidget = QListWidget(self)
        self.applications = {}

        self.getApplications(Path("/home/sacha/.local/share/applications"))
        self.getApplications(Path("/usr/share/applications"))

        self.applications = collections.OrderedDict(sorted(self.applications.items()))

        for application in self.applications.values():
            if (application.name != ""):
                self.listWidget.addItem(application.name)

        self.lineEdit = QLineEdit(self)

        layout = QVBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.listWidget)
        self.setLayout(layout)

        self.lineEdit.textChanged.connect(self.onTextChanged)
        self.listWidget.setCurrentRow(0)

    def getApplications(self, path):
        for file in path.iterdir():
            if (str(file).endswith(".desktop")):
                file = open(file, "r")
                application = Application("", "")

                for line in file.readlines():
                    if line.startswith("Name="):
                        name = line.split("=")[1][:-1]
                        application.name = name

                    if line.startswith("Exec"):
                        command = line.split("=")[1][:-1]
                        application.command = command

                    self.applications[application.name] = application

    def onTextChanged(self, text):
        if text == "":
            self.listWidget.clear()
            
            for application in self.applications.values():
                self.listWidget.addItem(application.name)
        else:
            filteredDict = {}

            for application in self.applications.values():
                if text.lower() in application.name.lower():
                    filteredDict[application.name] = application

            self.listWidget.clear()
            
            for application in filteredDict.values():
                self.listWidget.addItem(application.name)

        self.listWidget.setCurrentRow(0)


    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Return:
                subprocess.Popen(
                    [self.applications[self.listWidget.currentItem().text()].command], 
                    shell=True
                )
                sys.exit()
                return True

            if key == QtCore.Qt.Key_Escape:
                sys.exit()
                return True

            if key == QtCore.Qt.Key_Down:
                if self.listWidget.currentRow() < self.listWidget.count() - 1:
                    self.listWidget.setCurrentRow(self.listWidget.currentRow() + 1)
                    return True

            if key == QtCore.Qt.Key_Up:
                if self.listWidget.currentRow() != 0:
                    self.listWidget.setCurrentRow(self.listWidget.currentRow() - 1)
                    return True
        
        return False


class Application():
    def __init__(self, name, command):
        super().__init__()
        self.name = name
        self.command = command


if __name__ == "__main__":
    run()
