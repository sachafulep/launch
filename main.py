import sys
import subprocess
import collections
import fcntl
import sys
from pathlib import Path
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QListWidget, QLineEdit, QVBoxLayout, QWidget, QLabel
from PySide2.QtCore import SIGNAL, QObject
from PySide2.QtGui import QPalette


def run():
    pid_file = '/home/sacha/Documents/projects/launch/program.pid'
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # another instance is running
        sys.exit(0)

    app = QtWidgets.QApplication([])
    mainWidget = MainWidget()
    mainWidget.show()
    mainWidget.lineEdit.setFocus()
    sys.exit(app.exec_())


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.installEventFilter(self)
        self.applications = self.getApplications()
        self.setLayout(self.createLayout())

    def createLayout(self):
        self.listWidget = QListWidget(self)
        self.lineEdit = QLineEdit(self)

        for application in self.applications.values():
            if (application.name != ""):
                self.listWidget.addItem(application.name)

        layout = QVBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.listWidget)

        self.lineEdit.textChanged.connect(self.onTextChanged)
        self.listWidget.setCurrentRow(0)

        self.changeStyling()

        return layout

    def changeStyling(self):
        palette = QPalette()
        palette.setColor(QPalette.Background, QtCore.Qt.white)
        self.setPalette(palette)

        self.listWidget.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)

        self.setStyleSheet("""
            QLineEdit {
                border: 0px;
                font-size: 15px;
                padding: 10px 10px 10px 0px;
            }

            QListWidget {
                border: 0px;
            }

            QListWidget::item {
                padding: 15px 10px 10px 10px;
                border-radius: 5px;
            }

            QListWidget::item:selected {
                background-color: #abb6d1;
                color: #000000;
            }
        """)

    def getApplications(self):
        dictionary = {}

        self.parseDesktopFiles(
            Path("/home/sacha/.local/share/applications"), dictionary)
        self.parseDesktopFiles(Path("/usr/share/applications"), dictionary)

        return collections.OrderedDict(sorted(dictionary.items()))

    def parseDesktopFiles(self, path, dictionary):
        for file in path.iterdir():
            if (str(file).endswith(".desktop")):
                file = open(file, "r")
                application = Application("", "")
                isDesktopEntry = False

                for line in file.readlines():
                    if line.startswith("[") and "[Desktop Entry]" in line:
                        isDesktopEntry = True
                    elif line.startswith("[") and "[Desktop Entry]" not in line:
                        isDesktopEntry = False

                    if isDesktopEntry:
                        if line.startswith("Name="):
                            name = line.split("=")[1][:-1]
                            application.name = name

                        if line.startswith("Exec"):
                            command = line.split("=")[1][:-1]
                            application.command = command

                        dictionary[application.name] = application

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
                input = self.lineEdit.text()
                if input.startswith("-c"):
                    subprocess.Popen(
                            [input[3:]],
                            shell=True
                        )
                else:
                    application = self.applications[self.listWidget.currentItem().text()]

                    if "%" in application.command:
                        substring = "%" + application.command.split("%")[1]

                        subprocess.Popen(
                            [application.command.replace(substring, "")],
                            shell=True
                        )
                    else:
                        subprocess.Popen(
                            [application.command],
                            shell=True
                        )

                sys.exit()
                return True

            if key == QtCore.Qt.Key_Escape:
                sys.exit()
                return True

            if key == QtCore.Qt.Key_Down:
                if self.listWidget.currentRow() < self.listWidget.count() - 1:
                    self.listWidget.setCurrentRow(
                        self.listWidget.currentRow() + 1)
                    return True

            if key == QtCore.Qt.Key_Up:
                if self.listWidget.currentRow() != 0:
                    self.listWidget.setCurrentRow(
                        self.listWidget.currentRow() - 1)
                    return True

        return False


class Application():
    def __init__(self, name, command):
        super().__init__()
        self.name = name
        self.command = command


if __name__ == "__main__":
    run()
