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
import datetime, json, gspread
# from scrap_client_secret import clientSecret
# from askVAXTA import askVAXTA
from sys import exit


def initializeGoogleSheets():
    if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    vaxPath = os.path.join(application_path, 'vaxta.status')
    try:
        with open(vaxPath,'r') as v:
            vResponse = v.read()
    except FileNotFoundError:
    # except Exception as err:
        vResponse = "blank"
        # print(err)
    secretPath = "sheets.googleapis.com-python.json"
    if not os.path.exists(secretPath):  #spreadsheet cred
        initializeAuth()  #  If we don't have creds go get them
    elif vResponse != 'vaxta done':
        initializeVAXTA()

def initializeAuth():
    print("*"*100)
    print("New setup detected!\n\nLet's setup the connection to Google.")
    count = 0
    if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    # secretPath = os.path.join(application_path, "sheets.googleapis.com-python.json")
    secretPath = "sheets.googleapis.com-python.json"
    thisDir = os.getcwd()
    print(f'{thisDir=}')
    while not os.path.exists(secretPath):
    # if not os.path.exists("sheets.googleapis.com-python.json"):
        print("*"*50)
        print('next line')
        # print(clientSecretJson)
        appCredPath = os.path.join(application_path,"scrap_client_secret.json")
        try:
            gc = pygsheets.authorize(client_secret=appCredPath)
            # gc = pygsheets.authorize(client_secret="sample_client_secret.json")
        except Exception as error:
            # handle the exception
            print("An exception occurred:", error)
        #  safety counter b/c i'm a hack
        count +=1
        if count == 10:
            print('error will robinson')
            with open(secretPath, "w") as f:
                f.write("oops.  emergency cancel.")
            exit(1)
        #  safety counter b/c i'm a hack
    test = input("Hey! We logged in!\nPress Enter and restart the app to use your new credentials.")
    exit(0)

class VAXTASpreadSheet():
    def __init__(self) -> None:
        # if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
        #     application_path = sys._MEIPASS
        # else:
        #     application_path = os.path.dirname(os.path.abspath(__file__))
        # self.tokenPath  = os.path.join(application_path , "sheets.googleapis.com-python.json")
        self.tokenPath  = "sheets.googleapis.com-python.json"
        self.gc = pygsheets.authorize(self.tokenPath)

    def checkVAXTA(self):  # does the sheet exist?
        try:
            self.gc.open("VAXTA")
            return True
        except pygsheets.exceptions.SpreadsheetNotFound:
            return False
        
    def checkDataSheet(self):  # Does the data worksheet exist?
        spreadSh = self.gc.open('VAXTA')
        try:
            spreadSh.worksheet_by_title('DATA(leave)')
            # spreadSh.worksheet(property="title",value="DATA(leave)")
            return True
        except pygsheets.exceptions.WorksheetNotFound:
            return False
        
    def existingSpreadsheetFeedback(self):  # get user feed back on what to do with the existing "vaxta" file
        askApp = QApplication([])
        askWindow = askVAXTA()
        askWindow.show()
        askApp.exec()
        return askWindow.response

    def makeNewSpreadSheet(self):
        self.gc.create("VAXTA")

    def makeNewDataSheet(self):
        spreadSh = self.gc.open("VAXTA")
        dataSheet = spreadSh.add_worksheet("DATA(leave)",rows=2,cols=10,index=0)
        # create the header row with the headList
        headList = ["FILENAME", "DATETIME", "HERO", "TIMER", "KILLS", 
                    "KPM", "ACCURACY", "CRIT ACCURACY", 
                    "COMMENT", "STATUS"]
        for idx, label in enumerate(headList):
            pygsheets.Cell((1,idx+1)).link(dataSheet).set_value(label)
        #freeze top row
        dataSheet.frozen_rows = 1
        # return dataSheet

    def archiveExistingDataWorksheet(self):  # copy the existing data sheet to another spot
        existingSpreadsheet = self.gc.open("VAXTA")
        rightMeow = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
        newTitle = f"DATA(leave)-{rightMeow}"
        # jsonProp = {"properties": {"title": "DATA(leave)"}}
        workSh = existingSpreadsheet.worksheet_by_title('DATA(leave)')
        # copy data sheet to the last index in the spreadsheet
        existingSpreadsheet.add_worksheet(newTitle,src_tuple=(existingSpreadsheet.id, workSh.id),src_worksheet=workSh,index=-1)
        existingSpreadsheet.del_worksheet(workSh)
        # workSh = pygsheets.Worksheet(existingSpreadsheet,jsonProp)
        # workSh.title = f"DATA(leave)-{rightMeow}"

    def getStatus(self):  # return a list of done and ignored files from the sheet
        spreadSheet = self.gc.open("VAXTA")
        dataSheet = spreadSheet.worksheet_by_title("DATA(leave)")
        status = dataSheet.get_values_batch([f"A2:A{dataSheet.rows}",f"J2:J{dataSheet.rows}"])
        ignoreList = []
        recordList = []
        for row in range(len(status[0])):
            print(status[1][row][0])
            print (status[0][row][0])
            print("#"*10)
            if status[1][row][0] == "ignored":
                ignoreList.append(status[0][row][0])
            else:
                recordList.append(status[0][row][0])
                
    def writeTest(self):  # write todays date and time to the sheet
        spreadSheet = self.gc.open("VAXTA")
        dataSheet = spreadSheet.worksheet("DATA(leave)")
        stringNow = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M')
        addRow = [f'fake{stringNow}.png',stringNow] + [None]*7 + ['ignored']
        dataSheet.append_row(addRow)

def initializeVAXTA():
    vaxSpr = VAXTASpreadSheet()  # VAXTA Spreadsheet
    if vaxSpr.checkVAXTA():  # spreadsheet named vaxta already exists
        print("existing vaxta found")
        userResponse = vaxSpr.existingSpreadsheetFeedback()
        print("userResponse")
        print(userResponse)
        if userResponse == "add":
            #archive existing and create new worksheet
            if vaxSpr.checkDataSheet(): #data sheet exists:
                vaxSpr.archiveExistingDataWorksheet()
                # vaxSpr.makeNewSpreadSheet()
                vaxSpr.makeNewDataSheet()
            else: # data work sheet doesn't exist
                vaxSpr.makeNewDataSheet()
        elif userResponse == "asis":
            #  trust but verify
            if not vaxSpr.checkDataSheet():  # data sheet missing, so we'll add it
                print("this shouldn't print")
                vaxSpr.makeNewDataSheet()
    else:  # spreadsheet does not exist
        vaxSpr.makeNewSpreadSheet()
        vaxSpr.makeNewDataSheet()
    if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    vaxPath = os.path.join(application_path, 'vaxta.status')
    if vaxSpr.checkVAXTA() and vaxSpr.checkDataSheet():
        # worksheet and data sheet are there!!!
        with open(vaxPath,'w') as s:
            s.write("vaxta done")
        print('vaxta done!')
    else:
        print('general vaxta failure')

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
        self.button1.clicked.connect(lambda: self.useFileAsIs())
        self.layout.addWidget(self.button1)

        self.button2 = QPushButton("Use the existing file and\nadd new default sheets to it.")
        self.button2.clicked.connect(lambda: self.addSheetsToWorkbook())
        self.layout.addWidget(self.button2)

        self.button3 = QPushButton("Cancel and manually change\nthe sheet to another name")
        self.button3.clicked.connect(lambda: self.cancelMe())
        self.layout.addWidget(self.button3)
        if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        self.vaxPath = os.path.join(application_path, 'vaxta.status')
        
    def useFileAsIs(self):
        with open(self.vaxPath,'w') as v:
            v.write("vaxta asis")
        self.response = "asis"
        self.close()

    def addSheetsToWorkbook(self):
        with open(self.vaxPath,'w') as v:
            v.write("vaxta add sheets")
        self.response = 'add'
        self.close()

    def cancelMe(self):
        exit(0)

    def getAnswer(self):
        return self.response

if __name__ == "__main__":
    initializeGoogleSheets()
    app = QApplication(sys.argv)
    window = FileButtonApp()  # the gui
    window.show()
    app.exec()
    # sys.exit(app.exec())

