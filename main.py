print("""
  .oooooo.         .oooooo..o         .oooooo.              .o.             ooooooooo.        
 d8P'  `Y8b       d8P'    `Y8        d8P'  `Y8b            .888.            `888   `Y88.      
888      888      Y88bo.            888                   .8"888.            888   .d88'      
888      888       `"Y8888o.        888                  .8' `888.           888ooo88P'       
888      888           `"Y88b       888                 .88ooo8888.          888`88b.         
`88b    d88' .o.  oo     .d8P  .o.  `88b    ooo  .o.   .8'     `888.   .o.   888  `88b.   .o. 
 `Y8bood8P'  Y8P  8""88888P'   Y8P   `Y8bood8P'  Y8P  o88o     o8888o  Y8P  o888o  o888o  Y8P 

            Overwatch Screen Capture Analysis Recorder
""")

import pygsheets.exceptions
import sys, pygsheets, os, pygsheets.worksheet
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from oscargui import FileButtonApp
import pickle


def initializeGoogleSheets():
    if not os.path.exists("sheets.googleapis.com-python.json"):  #spreadsheet cred
        initializeAuth()  #  If we don't have creds go get them
    elif not os.path.exists("vaxta.init"): #spreadsheet was never setup
        initializeVAXTA()



def initializeAuth():
    print("*"*100)
    print("New setup detected!\n\nLet's setup the connection to Google.")
    while not os.path.exists("sheets.googleapis.com-python.json"):
        print("*"*100)
        # print("Copy and paste the URL below into a browser to continue authorization.")
        subprocess.Popen(["start","python","pygAuth.py"], shell = True)
        # try:
        #     gc = pygsheets.authorize(client_secret="scrap_client_secret.json")
        # except Exception as error:
        #     # handle the exception
        #     print("An exception occurred:", error)
    test = input("Hey! It looks we logged in!\nPress Enter and restart the app to use your new credentials.")

def initializeVAXTA():
    askApp = QApplication([])
    window = askVAXTA()
    # print("*"*100)
    # test = input("Hey! It looks we logged in!\nPress Enter to start creating a spreadsheet")
    gc = pygsheets.authorize("sheets.googleapis.com-python.json")
    try:
        # no error means something already exists there
        gc.open("VAXTA")  # oh nooooooo this sheet shouldn't exist...we must investigate
        # ask user what to do about the existing file
        # stat = subprocess.Popen(["start","python","askVAXTA.py"], shell = True)
        # userResponse = askVAXTA()
        window.show()
        askApp.exec()
    except pygsheets.exceptions.SpreadsheetNotFound:
        #sweeet, that means we're clear to create a new clean sheet
        gc.create("VAXTA")
        # gc. setup VAXTA
    with open('vaxta.init','w') as v:
        pickle.dump("vaxta started",v)
        # this marks that vaxta was setup sucessfully
    print("oh no")
    pass


######################################################work on this
def setupVAXTA():
    # add sheets and add other stuff
    print('adding stuff')

def getUserVaxta():  # ask user what to do about the existing VAXTA file
    indecisive = True
    while indecisive:
        resp = input("I found a sheet named VAXTA already.  ")

class askVAXTA(QWidget):
    def __init__(self):
        super().__init__()

        self.response = None

        self.layout = QVBoxLayout(self)

        self.label = QLabel("I am trying to make a sheet named VAXTA but I found\n"
                            "a sheet named VAXTA already!  Please let me know\n"
                            "how you would like to handle that.\n\n")
        self.layout.addWidget(self.label)

        self.button1 = QPushButton("The file is all ready to go.")
        self.button1.addAction(self.useFileAsIs())
        self.layout.addWidget(self.button1)

        self.button2 = QPushButton("Use the existing file and\nadd default sheets to it.")
        self.button2.addAction(self.addSheetsToWorkbook())
        self.layout.addWidget(self.button2)

        self.button3 = QPushButton("Cancel and manually change\nthe sheet to another name")
        self.button3.addAction(self.cancelMe())
        self.layout.addWidget(self.button3)

    def useFileAsIs(self):
        self.response = "asis"

    def addSheetsToWorkbook(self):
        self.response = 'add'

    def cancelMe(self):
        quit()

    def getAnswer(self):
        return self.response


if __name__ == "__main__":
    initializeGoogleSheets()
    app = QApplication(sys.argv)
    window = FileButtonApp()  # the gui
    window.show()
    app.exec()
    # sys.exit(app.exec())

gc = pygsheets.authorize(client_secret="scrap_client_secret.json")

os.getcwd()
gc = pygsheets.authorize("sheets.googleapis.com-python.json")
x = gc.open("VAXTA")
x

import subprocess

import subprocess, os
os.getcwd()
result = subprocess.run(["python", "pygAuth.py"], capture_output=True, text=True, shell=True)
print(result.stdout)


p = subprocess.Popen(["start","cmd", "/k", "echo hello"], shell = True)
p = subprocess.Popen(["start","cmd", "/k", "echo hello"], shell = True)




p = subprocess.Popen(["start","python","pygAuth.py"], shell = True)



p = subprocess.Popen(["python","pygAuth.py"])
p = subprocess.Popen(["python","--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell = True)
p = subprocess.Popen(["python","pygAuth.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell = True)
p = subprocess.Popen(["python","pygAuth.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell = True)
output, errors = p.communicate()

print(output)

os.getcwd()


p.stdout("test")
p.stdin("test")