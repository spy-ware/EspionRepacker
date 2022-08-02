# BSPzipGUI.py -- Made by spy-ware.

from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from PyQt5.uic import loadUi
from PyQt5 import QtGui
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
import shutil
import os


class Worker(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, pathBSP, pathMAP, pathDIR):
        super(QObject, self).__init__()

        self.pathBSP = pathBSP
        self.pathMAP = pathMAP
        self.pathDIR = pathDIR

    def run(self):

        self.progress.emit("")

        if self.pathBSP == ('', '') or self.pathDIR == ('', '') or self.pathMAP == "":

            self.finished.emit(
                "Please navigate to required file and directories")
        else:
            try:

                mapdir = self.pathMAP.split("/")
                bspmap = mapdir[-1]
                mapdir.pop()
                maps = ''.join(f"{str(x)}/" for x in mapdir)

                self.progress.emit(f"Checking {maps}")
                if os.path.exists(f"{self.pathDIR}/{bspmap}"):

                    self.progress.emit(f"Deleting {self.pathDIR}/{bspmap}")
                    os.remove(f"{self.pathDIR}/{bspmap}")

                self.progress.emit(f"Copying {self.pathMAP} to {self.pathDIR}")
                shutil.copy(self.pathMAP, self.pathDIR)

                self.progress.emit(f"Changing directory to {self.pathBSP}")
                os.chdir(self.pathBSP)

                self.progress.emit(f"Repacking {bspmap}")
                os.system(
                    f"bspzip -repack \"../tf/maps/{bspmap}\"")

                self.progress.emit(f"Checking for dir {self.pathDIR}/out")
                if not os.path.exists(f"{self.pathDIR}/out/"):

                    self.progress.emit(f"Creating dir {self.pathDIR}/out")
                    os.mkdir(f"{self.pathDIR}/out")

                self.progress.emit(
                    f"Checking {self.pathDIR}/out/ for {bspmap}")
                if os.path.exists(f"{self.pathDIR}/out/{bspmap}"):

                    self.progress.emit(f"Deleting {self.pathDIR}/out/{bspmap}")
                    os.remove(f"{self.pathDIR}/out/{bspmap}")

                self.progress.emit(f"Copying {bspmap} to {self.pathDIR}/out/")
                shutil.copy(self.pathMAP, f"{self.pathDIR}/out/")

                self.progress.emit(f"Deleting {self.pathMAP}")
                os.remove(self.pathMAP)

                self.progress.emit(
                    f"Copying {self.pathDIR}/{bspmap} to {maps}")
                shutil.copy(f"{self.pathDIR}/{bspmap}", maps)

                self.progress.emit(f"Deleting {self.pathDIR}/{bspmap}")
                os.remove(f"{self.pathDIR}/{bspmap}")

                self.finished.emit(f"Finished repacking {bspmap}")

            except Exception as e:

                self.finished.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, pathBSP="", pathMAP="", pathDIR=""):
        super(MainWindow, self).__init__()
        self.pathBSP = pathBSP
        self.pathMAP = pathMAP
        self.pathDIR = pathDIR
        dirname = os.path.dirname(__file__)
        loadUi(os.path.join(dirname, "bspzipgui.ui"), self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(dirname, "BSPzipGUI.ico")))

        self.labelCREDIT.setText("BSPzipGUI 1.00 - Made by spy-ware")
        self.labelERR.setText("")
        self.ButtonMAP.clicked.connect(lambda: self.browsefile(
            "Select map", self.labelMAP))
        self.ButtonBSP.clicked.connect(lambda: self.browsefolder(
            "Select TF2 bin folder", self.labelBSP, "b"))
        self.ButtonDIR.clicked.connect(lambda: self.browsefolder(
            "Select output directory", self.labelDIR, "d"))
        self.ButtonREPACK.clicked.connect(self.repack)

    def browsefile(self, title, label):
        file_name = QFileDialog.getOpenFileName(
            self, title, "/", "BSP files (*.bsp)")
        if file_name != ('', ''):
            label.setText(str(file_name[0].replace("\\", "/")))
            self.pathMAP = file_name[0]
        else:
            label.setText(file_name)

    def browsefolder(self, title, label, var):
        folder_path = QFileDialog.getExistingDirectory(self, title, "/")
        if folder_path != "":
            folder_path = folder_path.replace("\\", "/")
            label.setText(folder_path)
            match var:
                case "b":
                    self.pathBSP = folder_path
                case "d":
                    self.pathDIR = folder_path
        else:
            label.setText(folder_path)

    def progresslabel(self, message):
        self.labelERR.setText(message)
        print(message)

    def repack(self):
        self.thread = QThread()
        self.worker = Worker(self.pathBSP, self.pathMAP, self.pathDIR)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.progresslabel)
        self.worker.finished.connect(self.progresslabel)
        self.thread.start()
        self.ButtonREPACK.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.ButtonREPACK.setEnabled(True)
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(600, 430)
    window.show()
    sys.exit(app.exec_())