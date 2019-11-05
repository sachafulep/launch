import sys
import subprocess
from pathlib import Path
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QListWidget, QLineEdit, QVBoxLayout, QWidget, QLabel


def run():
    app = QtWidgets.QApplication([])
    mainWidget = MainWidget()
    mainWidget.show()
    sys.exit(app.exec_())


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.installEventFilter(self)

        listWidget = QListWidget(self)
        self.applications = {}

        self.getApplications(Path("/home/sacha/.local/share/applications"))
        self.getApplications(Path("/usr/share/applications"))

        for application in self.applications.values():
            if (application.name != ""):
                listWidget.addItem(application.name)

        lineEdit = QLineEdit(self)

        layout = QVBoxLayout()
        layout.addWidget(lineEdit)
        layout.addWidget(listWidget)
        self.setLayout(layout)

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

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_Escape:
                QtCore.QCoreApplication.quit()
                subprocess.Popen(["xfce4-terminal"])
                return True
        
        return False


class Application():
    def __init__(self, name, command):
        super().__init__()
        self.name = name
        self.command = command


if __name__ == "__main__":
    run()
