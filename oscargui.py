import sys, os, pickle
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, \
        QWidget, QInputDialog, QLabel, QLineEdit, QMessageBox, QGridLayout
from PyQt6.QtGui import QIcon, QAction, QIntValidator, QPixmap
from PyQt6.QtCore import Qt 
from PIL import Image
# import pytesseract
# import numpy as np
from pprint import pprint as pp
import datetime
# os.chdir('C:\\Users\\dim\\Documents\\GitHub\\OSCAR')
from oscarguts import oscarWorksheet, oscarFileMeta, analysisCache
from oscarguts import oscarBlue, oscarAqua, oscarCream, oscarRed, oscarYellow, bottomUnderline, oscarDGray, oscarImage



class reviewData(QWidget):
    def __init__(self, parent_window, response, filesMeta):  # initialize the words read from the image for human review
        super().__init__()

        if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        iconPath = os.path.join(application_path,"icons","oscarAngry.ico")
        self.setWindowIcon(QIcon(iconPath))
        self.setWindowTitle("Review data")

        layout = QVBoxLayout()

        self.parent_window = parent_window
        response = response  + ['']
        self.fls = filesMeta  # files meta object
        self.fls.updateData()

        # Add a label for context
        self.label = QLabel(f'Please check values for\n{self.fls.name}\nThen send!')
        if self.fls.status == 'ignored':
            self.label2 = QLabel('This file was previously ignored.')
        elif self.fls.status == 'recorded':
            self.label2 = QLabel('This file was already recorded!')
            self.label.setStyleSheet(oscarAqua)
            self.label2.setStyleSheet(oscarAqua)
        elif self.fls.status == 'unstored':
            self.label2 = QLabel("This screen shot is NOT in the spreadsheet!")
            self.label.setStyleSheet(oscarYellow)
            self.label2.setStyleSheet(oscarYellow)
        layout.addWidget(self.label)
        layout.addWidget(self.label2)

        # Create labels and input fields
        # "Timer:", "Kills:", "KillsperMin:", "accuracy:", "crit accuracy:"
        self.labels = ["Hero:", "Timer:", "Kills:", "Kills per min:", "Accuracy:", "Critical Accuracy:","Comment:"]
        self.input_fields = [QLineEdit() for _ in range(len(self.labels))]

        # create some validators for the input fields:
        intValidator = QIntValidator()

        for label, input_field, autoText in zip(self.labels, self.input_fields, response):
            label_widget = QLabel(label)
            input_field.setText(autoText)
            layout.addWidget(label_widget)
            input_field.setText(autoText)
            layout.addWidget(input_field)
            if label in ["Timer:", "Kills:", "KillsperMin:"]:
                input_field.setValidator(intValidator)

        # create action buttons
        act_layout = QHBoxLayout()

        # Create send button
        sendButton = QPushButton("Record")
        sendButton.clicked.connect(self.sendData)
        act_layout.addWidget(sendButton)

        # Create ignore button
        ignoreButton = QPushButton("Ignore")
        ignoreButton.clicked.connect(self.ignoreFile)
        act_layout.addWidget(ignoreButton)

        # Creat show image button
        showButton = QPushButton("Open image")
        showButton.clicked.connect(lambda: self.showImage())  #dummy
        act_layout.addWidget(showButton)

        layout.addLayout(act_layout)

        # create Nav buttons
        nav_layout = QHBoxLayout()

        prevButton = QPushButton("Previous")
        prevButton.clicked.connect(self.show_prev_file)
        nav_layout.addWidget(prevButton)
        
        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.show_next_file)
        nav_layout.addWidget(nextButton)

        # enable/disable navigation buttons
        prevButton.setEnabled(self.fls.index > 0)
        nextButton.setEnabled(self.fls.index < len(self.fls.nameList)-1)

        self.leWorksheet = oscarWorksheet()

        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def show_prev_file(self):  # find previous file in the index and look up it's data.
        # leStats = ["240","32","20","39%","20%"]
        self.fls.index = max(0,self.fls.index-1)  # index the index down
        self.fls.updateData()
        # leStats = oscarImage(self.fls.namePath)ripVAXTA()  # read the new file
        self.parent_window.analyseImage(self.fls.namePath)  # read the new file
        # self.new_window = reviewData(self.parent_window, leStats, self.fls)
        # self.new_window.show()  # show the previous file
        self.close()

    def show_next_file(self):  # find next file in the index and look up it's data.
        # leStats = ["240","32","20","39%","20%"]
        self.fls.index = min(len(self.fls.nameList),self.fls.index+1)  # index the index up
        self.fls.updateData()
        # leStats = oscarImage(self.fls.namePath).ripVAXTA()  # read the new file
        self.parent_window.analyseImage(self.fls.namePath)  # open a new window using the parent's function
        # self.new_window = reviewData(self.parent_window, leStats, self.fls)
        # self.new_window.show()  # show the previous file
        self.close()

    def print_input_values(self):  #  dummy function for button
        for label, input_field in zip(self.labels, self.input_fields):
            value = input_field.text()
            print(f"{label} {value}")

    def sendData(self):  # sends data from the form to the VAXTA sheet
        # get the date time from the file
        leTimeStamp = os.path.getmtime(self.fls.namePath)
        # make the timestamp human readable
        humanTime = datetime.datetime.fromtimestamp(leTimeStamp).strftime(f"%Y-%m-%d %H:%M:%S")
        # add row containing [filename,datetime,thefields values, ..., "recorded" ]
        rowAdd = [
            self.fls.namePath, humanTime
        ] + [
            input_field.text() for input_field in self.input_fields
        ] + ['recorded']
        # Does the file already exist in the spreadsheet column A?
        existingFiles = self.leWorksheet.wks.col_values(1)[1:]
        if self.fls.namePath in existingFiles:  # filename
            rowToReplace = existingFiles.index(self.fls.namePath) + 2
            self.leWorksheet.wks.update(f"A{rowToReplace}",[rowAdd], value_input_option='USER_ENTERED')
        else:
            self.leWorksheet.wks.append_row(rowAdd, value_input_option='USER_ENTERED')
        self.parent_window.fls.updateStatus()
        self.parent_window.display_files()
        self.close()

    def ignoreFile(self):  # sends the file name to the VAXTA sheet so this file path is ignored
        rowAdd = [self.fls.namePath] + [""]*8 + ["ignored"]
        existingFiles = self.leWorksheet.wks.col_values(1)[1:]
        if self.fls.namePath in existingFiles:  # filename
            rowToReplace = existingFiles.index(self.fls.namePath) + 2
            self.leWorksheet.wks.update(f"A{rowToReplace}",[rowAdd], value_input_option='USER_ENTERED')
        else:
            self.leWorksheet.wks.append_row(rowAdd, value_input_option='USER_ENTERED')
            # self.leWorksheet.writeRow(rowAdd)
        self.parent_window.fls.updateStatus()
        self.parent_window.display_files()
        self.close()

    def showImage(self):
        print(self.fls.namePath)
        os.startfile(self.fls.namePath)
        

class FileButtonApp(QMainWindow):
    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
            self.application_path = sys._MEIPASS
        else:
            self.application_path = os.path.dirname(os.path.abspath(__file__))
        iconPath = os.path.join(self.application_path,"icons","oscarAngry.ico")
        self.setWindowIcon(QIcon(iconPath))

        self.setWindowTitle("List of 'Overwatch' images")
        self.setGeometry(100, 100, 800, 200)
        self.initUI()

        # Create a central widget
        centralWidget = QWidget()  # widget prime
        centralLayout = QVBoxLayout()  # Layout that goes to widget prime

        # create main top and bottom layout
        headLayout = QVBoxLayout()  #color key and file buttons
        headLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        footLayout = QVBoxLayout()  # Bottom layout to stick to the bottom
        footLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)
    
        # Create a layout for buttons
        self.buttonLayout = QVBoxLayout()  # file buttons
        self.navigationLayout = QHBoxLayout()  #page nav buttons

        # make the color key labels
        headLabelGray   = QLabel("Gray: ignored")
        headLabelYellow = QLabel("Yellow: unrecorded")
        headLabelYellow.setStyleSheet(oscarYellow)
        headLabelBlue   = QLabel("Blue: recorded")
        headLabelBlue.setStyleSheet(oscarAqua)
        headLableBlankBar = QLabel(' ')  #blank line I'm such a hack
        headLableBlankBar.setStyleSheet(oscarDGray)

        # Create pagination buttons
        self.prevButton = QPushButton("Previous page", self)
        self.nextButton = QPushButton("Next page", self)

        # Create page feed back label
        self.pageFeedback = QLabel("Page _ of _")

        # Connect pagination buttons to functions
        self.prevButton.clicked.connect(self.show_previous_page)
        self.nextButton.clicked.connect(self.show_next_page)


        # Start building the gui
        centralWidget.setLayout(centralLayout)
        centralLayout.addLayout(headLayout)  # Labels
        centralLayout.addLayout(footLayout) # page nav and page feed back

        # Add top labels
        headLayout.addWidget(headLabelGray)
        headLayout.addWidget(headLabelYellow)
        headLayout.addWidget(headLabelBlue) 
        headLayout.addWidget(headLableBlankBar) 

        headLayout.addLayout(self.buttonLayout)  # Buttons row

        # add foot stuff
        footLayout.addLayout(self.navigationLayout)
        footLayout.addWidget(self.pageFeedback)

        # Add pagination buttons
        self.navigationLayout.addWidget(self.prevButton)
        self.navigationLayout.addWidget(self.nextButton)


        # centralLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # centralLayout.addLayout(self.buttonLayout)  # Buttons row
        # headLayout.setLayout(self.buttonLayout)
        self.setCentralWidget(centralWidget)

        # self.pageFeedback.setAlignment(Qt.AlignmentFlag.AlignBottom)


        # Initialize file list and current page
        self.files = []  # List of file paths
        self.current_page = 0

        # object that sends stuff out to the VAXTA Google Spreadsheet
        self.leWorksheet = oscarWorksheet()

        # look for a pickle to get app settings                                                               
        folderPath, pageSize = self.initializeSettings()  #get folder path and page size

        # files object that holds the files data
        self.fls = oscarFileMeta(path=folderPath,pageSize=pageSize)
        # self.fls.dumpData()

        # populate the cache with any unstored files
        self.dtCache = analysisCache()  # setup the cache 
        for idx, leFile in enumerate(self.fls.pathList):  
            if self.fls.statusList[idx] == 'unstored':
                if leFile not in self.dtCache.dC.keys():
                    # add cache if it ain't already and it's gonna be
                    # cache      filenamepath      get the image dat using oscarImage
                    self.dtCache.dC[leFile] = oscarImage(leFile).ripVAXTA()
                    # print(self.dtCache.dC[leFile])
                # else:
                    # print('skipping cacheing')
            # else:
            #     print(f"it wasn't unstored? self.fls.statusList[idx] status")
            #     print(self.fls.statusList[idx])

        self.dtCache.backupCache()



        # Display initial files as buttons
        self.display_files()

    def initUI(self):  # add menu items


        exitPath = os.path.join(self.application_path,'icons','exit.png')
        exitAct = QAction(QIcon(exitPath), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.instance().quit)

        gearPath = os.path.join(self.application_path,'icons','gear.png')
        settingsWin = QAction(QIcon(gearPath), "&Settings", self)
        settingsWin.setStatusTip('directory and page size')
        settingsWin.triggered.connect(lambda: self.settingsPanel(self))

        foldPath = os.path.join(self.application_path,'icons','folder.png')
        # updatePath = QAction(QIcon((":help-content.svg")), '&Update monitored folder', self)
        updatePath = QAction(QIcon(foldPath), '&Update monitored folder', self)
        updatePath.setStatusTip('Update the path of the monitored folder')
        updatePath.triggered.connect(self.updateFolder)

        textPath = os.path.join(self.application_path,'icons','ui-text-field.png')
        editPageSize = QAction(QIcon(textPath), '&Edit page size', self)
        editPageSize.setStatusTip('Update the number of files per page')
        editPageSize.triggered.connect(self.editPage)

        abutPath = os.path.join(self.application_path,'icons','oscarAngrySmall.png')
        showAboutApp = QAction(QIcon(abutPath), '&About OSCAR', self)
        showAboutApp.setStatusTip('What is this app?')
        showAboutApp.triggered.connect(self.aboutOscar)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        fileMenu.addAction(settingsWin)
        fileMenu = menubar.addMenu('&Settings')
        fileMenu.addAction(updatePath)
        fileMenu.addAction(editPageSize)
        fileMenu = menubar.addMenu('&About')
        fileMenu.addAction(showAboutApp)
        # helpMenu = menuBar.addMenu(QIcon(":help-content.svg"), "&Help")

        self.setGeometry(300, 300, 350, 250)
        # self.setWindowTitle('Simple menu')
        self.show()

    def updateFolder (self):  # update monitored folder setting menu
        print("updating path")
        #monitored folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select a directory",self.fls.path) 

        picklePath = os.path.join(self.application_path,"conf.pickle")

        if folder_path != "":
            # put settings into dictionary
            settings = {'folder_path' : folder_path, 'items_per_page' : self.fls.pageSize,}
            # update pickle to conf.pickle
            with open (picklePath,'wb') as p: pickle.dump(settings,p)
            # update main window
            self.fls.path = folder_path
            self.fls.updateStatus()
            self.display_files()
        else:
            print('Blank folder found')
            pageError = QMessageBox(self)
            pageError.setWindowTitle("Looks like it's amateur hour.")
            pageError.setText("Blank folder was ignored!")
            pageError.show()

    def editPage (self):  # update page size settings menu
        print('updating page size')
        # Display an input dialog
        text, ok = QInputDialog.getText(self, "Enter Text", "Please enter a number (4-50):", text=str(self.fls.pageSize))
        picklePath = os.path.join(self.application_path,"conf.pickle")
        if ok and text:
            try:
                if 3 < int(text) < 50:
                    self.fls.pageSize = int(text)
                    settings = {'folder_path' : self.fls.path, 'items_per_page' : self.fls.pageSize,}
                    with open (picklePath,'wb') as p: 
                        pickle.dump(settings,p)
                    self.fls.pageIndex = 0
                    self.fls.updateStatus()
                    self.display_files()
                else:
                    print('failed number test')
            except AttributeError:
                print('attrib error...probably not an int')
                pageError = QMessageBox(self)
                pageError.setWindowTitle("I am not your father")
                pageError.setText("Bad news for you. That page size won't work")
                pageError.show()

    def aboutOscar(self):
        self.aboutWin = QMessageBox()
        self.aboutWin.setWindowTitle("About O.S.C.A.R.")
        self.aboutWin.setText("O.S.C.A.R.")
        self.aboutWin.setInformativeText("O.S.C.A.R. stands for Overwatch Screen Capture Analysis Recorder. It\n"
                                         "scans all files in a specified directory, reads them, then sends that\n"
                                         "data to a Google sheet. You can double check the computer vision by\n"
                                         "taking a look at the file.\n"
                                         "GLHF! ~~EggButler")
        self.aboutWin.setDetailedText("Did somebody say peanut butter?")  #Always plain
        self.aboutWin.setStandardButtons(QMessageBox.StandardButton.Ok)
        leIcon = QIcon(QPixmap(os.path.join(self.application_path,'icons','oscarAngrySmall.png')))
        self.aboutWin.setWindowIcon(leIcon)
        self.aboutWin.exec()

    def initializeSettings(self):  # load config pickle to get folder path and page size
        # Get the directory path; first check settings pickel:
        # get originating directory...so I can get the pickles
        picklePath = os.path.join(self.application_path,"conf.pickle")

        if os.path.exists(picklePath): 
            print('testing pickle')
            # pull settings from dictionary
            with open (picklePath, 'rb') as p:
                settings = pickle.load(p)
            folder_path = settings['folder_path']
            items_per_page = settings['items_per_page']
            # from conf import folder_path
            # print('import sucess', folder_path, items_per_page)
            #  validate pickle data
        else: #no pickle...gotta make one
            folder_path = os.path.join(self.application_path,"sampleImages").replace('\\','/')
            items_per_page = 10   # DEFAULT VALUE
        if folder_path != "" and 3<items_per_page<51:
            print('settings pickle win')
        else:
            print('settings pickle fail') 
            pageError = QMessageBox(self)
            pageError.setWindowTitle('Back...in black.')
            pageError.setText("Sorry, sorry...sorry\nSettings failed. "
                                "Returning to default directory and page size.")
            pageError.show()
            folder_path = "sampleImages"
            # i should put this default value somewhere more intelligent.
            items_per_page = 10   # DEFAULT VALUE
            # put settings into dictionary
            settings = {'folder_path' : folder_path, 'items_per_page' : items_per_page,}
            # Try and make a pickle at conf.pickle
            with open (picklePath,'wb') as p:
                pickle.dump(settings,p)
        return folder_path, items_per_page

    def display_files(self):  # setup and add file buttons and navigation buttons

        # Clear existing buttons
        for i in reversed(range(self.buttonLayout.count())):
            widget = self.buttonLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create buttons for files in the current page list
        for leName, leStatus in self.fls.pagdList[self.fls.pageIndex]:
            button = QPushButton(leName.split("/")[-1], self)
            # give it action
            button.clicked.connect(lambda _, fName=leName: self.analyseImage(fName))
            #style?
            if leStatus == 'ignored':
                button.setStyleSheet(oscarDGray) # cream
                # button.toolTip('Ignored')
            elif leStatus == 'recorded':
                button.setStyleSheet(oscarAqua) # aqua
                # button.toolTip('Recorded')
            elif leStatus == 'unstored':
                button.setStyleSheet(oscarYellow) # lightyellow arylide
                # button.toolTip('Unsaved')
            self.buttonLayout.addWidget(button)

        # enable/disable navigation buttons
        self.prevButton.setEnabled(self.fls.pageIndex > 0)
        self.nextButton.setEnabled(self.fls.pageIndex < self.fls.pageQTY-1)
        self.pageFeedback.setText(f"Page {self.fls.pageIndex+1} of {self.fls.pageQTY}")

    def show_previous_page(self):  # previous page of files and refresh buttons
        self.fls.pageIndex = max(self.fls.pageIndex - 1, 0)
        self.fls.updateData()
        self.display_files()

    def show_next_page(self):  # next page of files
        self.fls.pageIndex = min(self.fls.pageIndex + 1, self.fls.pageQTY - 1)
        self.fls.updateData()
        self.display_files()

    def open_file(self, leMessage):  # dummy function for placeholder button
        # Implement logic to open the selected file
        print(f"Opening file: {leMessage}")

    def settingsPanel(self, parent_window):  # dummy function for placeholder button
        # Implement logic to open the selected file
        print(f"Opening file: leMessage")
        self.setWin = settingsWindow(parent_window)
        self.setWin.show()


    def analyseImage(self, imageFileName):  # take an image path and return it's statistics
        # should do something here with the image:
        self.fls.index = self.fls.pathList.index(imageFileName)
        self.fls.updateData()
        # print('self.dtCache.dC',self.dtCache.dC)
        #check if we have an old data review window and destroy it
        try:
            self.new_window.close()
        except:
            pass
        # check if file is in the dtcache
        # make a list out of the cached file path list 
        nameCacheList = [x for x in self.dtCache.dC.keys()]  # .split('/')[-1]
        if imageFileName in nameCacheList:
            response = self.dtCache.dC[imageFileName]  # get the cached response
            self.new_window = reviewData(self, response, self.fls)  # review cached resp
            self.new_window.show()
        else:
            print("didn't find image in cache")
            # update filesMeta based on the image file name
            response = oscarImage(self.fls.namePath).ripVAXTA()
            self.dtCache.dC[self.fls.namePath] = response  # add/update to the cache
            self.dtCache.backupCache()
            self.new_window = reviewData(self, response, self.fls)
            self.new_window.show()

class settingsWindow(QWidget):
    def __init__(self, parent_window):
        super().__init__()

        if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        iconPath = os.path.join(application_path,"icons","oscarAngry.ico")
        self.setWindowIcon(QIcon(iconPath))
        self.setWindowTitle("Settings window")

        self.pw = parent_window
        # self.fls = filesMeta  # files meta object

        setsGrid = QGridLayout()

        folderLabel = QLabel(f'Monitored directory:\n{self.pw.fls.path}')
        updateFolderButton = QPushButton("Update folder", self)
        updateFolderButton.clicked.connect(self.pw.updateFolder)

        pgSz = self.pw.fls.pageSize
        pageSizeLabel = QLabel(f'Current page size:\n{pgSz}')
        updatePageSizeButton = QPushButton("Update page size", self)
        updatePageSizeButton.clicked.connect(self.pw.editPage)
                                              #Row Col
        setsGrid.addWidget(folderLabel,          0,  1)
        setsGrid.addWidget(updateFolderButton,   0,  0)
        setsGrid.addWidget(pageSizeLabel,        1,  1)
        setsGrid.addWidget(updatePageSizeButton, 1,  0)
        
        self.setLayout(setsGrid)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileButtonApp()
    window.show()
    app.exec()
    # sys.exit(app.exec())

