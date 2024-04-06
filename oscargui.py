import sys, os, pickle
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, \
        QWidget, QInputDialog, QLabel, QLineEdit
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
# from PIL import Image
# import pytesseract
# import numpy as np
from pprint import pprint as pp
import datetime
os.chdir('C:\\Users\\dim\\Dropbox\\projects\\Overwatch Scrape\\v0')
from oscarguts import ripVAXTA, paginateList, oscarWorksheet, oscarBlue, oscarAqua, oscarCream, oscarRed, oscarYellow, bottomUnderline, oscarDGray



class reviewData(QWidget):
    def __init__(self, parent_window, response, filePath, bigFileList, currentIndex):  # initialize the words read from the image for human review
        super().__init__()
        layout = QVBoxLayout()

        self.parent_window = parent_window
        self.filePath = filePath
        self.bigFileList = bigFileList
        self.currentIndex = currentIndex
        # print("self.currentIndex in rd",self.currentIndex)
        # print('len of big file:', len(self.bigFileList))

        # print('bigfilelistspot two',self.bigFileList[self.currentIndex][1]) # = ignored or recorded
        # get the responses from the pytesseract
        # add a blank text spot for the upcoming comment field
        response = response  + ['']

        # # Create five QLineEdit widgets
        # self.text_inputs = []
        # for i in range(5):
        #     input_field = QLineEdit()
        #     self.text_inputs.append(input_field)
        #     layout.addWidget(input_field)

        # Add a label for context
        self.label = QLabel(f'please check values for\n{self.bigFileList[self.currentIndex][0].split("/")[-1]}')
        if self.bigFileList[self.currentIndex][1] == 'ignored':
            self.label2 = QLabel('This file was previously ignored')
        elif self.bigFileList[self.currentIndex][1] == 'recorded':
            self.label2 = QLabel('This file was already recorded!')
            self.label.setStyleSheet(oscarAqua)
            self.label2.setStyleSheet(oscarAqua)
        elif self.bigFileList[self.currentIndex][1] == 'unstored':
            self.label2 = QLabel("This screen shot isn't in the spreadsheet!")
            self.label.setStyleSheet(oscarYellow)
            self.label2.setStyleSheet(oscarYellow)
        layout.addWidget(self.label)
        layout.addWidget(self.label2)

        # Create labels and input fields
        # "Timer:", "Kills:", "KillsperMin:", "accuracy:", "crit accuracy:"
        self.labels = ["Hero", "Timer:", "Kills:", "KillsperMin:", "accuracy:", "critAccuracy:","comment:"]
        self.input_fields = [QLineEdit() for _ in range(len(self.labels))]
        # self.input_fields = [QLineEdit() for _ in range(6)]
        # self.text_inputs = [QLineEdit() for _ in range(5)]

        for label, input_field, autoText in zip(self.labels, self.input_fields, response):
            label_widget = QLabel(label)
            input_field.setText(autoText)
            layout.addWidget(label_widget)
            input_field.setText(autoText)
            layout.addWidget(input_field)

        # create action buttons
        act_layout = QHBoxLayout()

        # Create send button
        sendButton = QPushButton("Send")
        sendButton.clicked.connect(self.sendData)
        act_layout.addWidget(sendButton)

        # Create ignore button
        ignoreButton = QPushButton("ignore")
        ignoreButton.clicked.connect(self.ignoreFile)
        act_layout.addWidget(ignoreButton)

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
        prevButton.setEnabled(self.currentIndex > 0)
        nextButton.setEnabled(self.currentIndex < len(self.bigFileList)-1)

        self.leWorksheet = oscarWorksheet()

        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def show_prev_file(self):  # find previous file in the index and look up it's data.
        # leStats = ["240","32","20","39%","20%"]
        self.currentIndex = max(0,self.currentIndex-1)
        # fileNamePath = self.filePath + '/' + self.bigFileList[self.currentIndex]
        # print(f'new target {self.bigFileList[self.currentIndex][0]}')
        # leFilePath = self.filePath + '/' + self.bigFileList[self.currentIndex][0]
        leFilePath = self.bigFileList[self.currentIndex][0]
        leStats = ripVAXTA(leFilePath)
        # print("self.bigFileList", self.bigFileList)
        # print("len self.bigFileList",len(self.bigFileList))
        # print("self.currentIndex", self.currentIndex)
        # self.new_window = reviewData()
        # print("self.currentIndex in rd",self.currentIndex)
        # print('len of big file:', len(self.bigFileList))
        self.new_window = reviewData(self.parent_window, leStats, self.filePath, self.bigFileList, self.currentIndex)
        self.new_window.show()
        self.close()
        # QCoreApplication.instance().quit

    def show_next_file(self):  # find next file in the index and look up it's data.
        # leStats = ["240","32","20","39%","20%"]
        self.currentIndex = min(len(self.bigFileList),self.currentIndex+1)
        # fileNamePath = self.filePath + '/' + self.bigFileList[self.currentIndex]
        # print(f'new target {self.bigFileList[self.currentIndex][0]}')
        # leFilePath = self.filePath + '/' + self.bigFileList[self.currentIndex][0]
        leFilePath = self.bigFileList[self.currentIndex][0]
        # print('leFilePath',leFilePath)
        leStats = ripVAXTA(leFilePath)
        # print("self.bigFileList", self.bigFileList)
        # print("len self.bigFileList",len(self.bigFileList))
        # print("self.currentIndex", self.currentIndex)
        # self.new_window = reviewData()
        # print("self.currentIndex in rd",self.currentIndex)
        # print('len of big file:', len(self.bigFileList))
        self.new_window = reviewData(self.parent_window, leStats, self.filePath, self.bigFileList, self.currentIndex)
        self.new_window.show()
        self.close()
        # QCoreApplication.instance().quit

    def print_input_values(self):  #  dummy function for button
        for label, input_field in zip(self.labels, self.input_fields):
            value = input_field.text()
            print(f"{label} {value}")

    def sendData(self):
        # get the date time from the file
        # leFullFilePath = os.path.join(self.filePath,self.bigFileList[self.currentIndex][0])
        leTimeStamp = os.path.getmtime(self.bigFileList[self.currentIndex][0])
        # make the timestamp human readable
        humanTime = datetime.datetime.fromtimestamp(leTimeStamp).strftime(f"%Y-%m-%d %H:%M:%S")
        #  add row containing [filename,datetime,thefields values, ..., "recorded" ]
        rowAdd = [
            self.bigFileList[self.currentIndex][0], humanTime
        ] + [
            input_field.text() for input_field in self.input_fields
        ] + ['recorded']
        # print(f"{label} {value}")
        # 'Overwatch 4_3_2024 10_14_00 AM.png'[10:-4]
        # myWorksheet = oscarWorksheet()
        # Does the file already exist in the spreadsheet column A?
        existingFiles = self.leWorksheet.wks.col_values(1)[1:]
        # print('existingFiles',existingFiles)
        if self.bigFileList[self.currentIndex][0] in existingFiles:  # filename
            rowToReplace = existingFiles.index(self.bigFileList[self.currentIndex][0]) + 2
            # print("rowToReplace",rowToReplace)
            # update: which row, what to update with, stuff to make the date work 
            self.leWorksheet.wks.update(f"A{rowToReplace}",[rowAdd], value_input_option='USER_ENTERED')
        else:
            self.leWorksheet.wks.append_row(rowAdd, value_input_option='USER_ENTERED')
        self.parent_window.load_files()
        self.close()

    def ignoreFile(self):
        print('ignore',[self.bigFileList[self.currentIndex][0]])
        rowAdd = [self.bigFileList[self.currentIndex][0]] + [""]*8 + ["ignored"]
        existingFiles = self.leWorksheet.wks.col_values(1)[1:]
        # myWorksheet = oscarWorksheet()
        if self.bigFileList[self.currentIndex][0] in existingFiles:  # filename
            rowToReplace = existingFiles.index(self.bigFileList[self.currentIndex][0]) + 2
            # print("rowToReplace",rowToReplace)
            # update: which row, what to update with, stuff to make the date work 
            self.leWorksheet.wks.update(f"A{rowToReplace}",[rowAdd], value_input_option='USER_ENTERED')
        else:
            self.leWorksheet.wks.append_row(rowAdd, value_input_option='USER_ENTERED')
            # self.leWorksheet.writeRow(rowAdd)
        self.parent_window.load_files()
        self.close()


class FileButtonApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("List of 'Overwatch' images")
        self.setGeometry(100, 100, 800, 200)

        self.initUI()

        # create label
        headLabels = QVBoxLayout()
    
        headLabelGray   = QLabel("gray: ignored")
        headLabelYellow = QLabel("yellow: unrecorded")
        headLabelYellow.setStyleSheet(oscarYellow)
        headLabelBlue   = QLabel("blue: recorded")
        headLabelBlue.setStyleSheet(oscarAqua)
        headLabelBlue.setAlignment(Qt.AlignmentFlag.AlignTop)
        headLableBlankBar = QLabel(' ')
        headLableBlankBar.setStyleSheet(oscarDGray)

        headLabels.addWidget(headLabelGray)
        headLabels.addWidget(headLabelYellow)
        headLabels.addWidget(headLabelBlue) 
        headLabels.addWidget(headLableBlankBar) 

        # Create a layout for buttons
        self.buttonLayout = QVBoxLayout()
        self.navigationLayout = QHBoxLayout()

        # Create pagination buttons
        self.prevButton = QPushButton("Previous Page", self)
        self.nextButton = QPushButton("Next Page", self)

        # Connect pagination buttons to functions
        self.prevButton.clicked.connect(self.show_previous_page)
        self.nextButton.clicked.connect(self.show_next_page)

        # self.navigation_layout.addWidget(self.prevButton)    # Pagination row
        # self.navigation_layout.addWidget(self.nextButton)    # Pagination row

        # Create a central widget
        centralWidget = QWidget()
        centralLayout = QVBoxLayout()
        centralLayout.addLayout(headLabels)  # Labels
        centralLayout.addLayout(self.buttonLayout)  # Buttons row
        centralLayout.addLayout(self.navigationLayout) # nav row
        centralWidget.setLayout(centralLayout)
        centralWidget.setLayout(self.buttonLayout)
        self.setCentralWidget(centralWidget)

        # Initialize file list and current page
        self.files = []  # List of file paths
        self.current_page = 0
        # self.items_per_page = 5  # Adjust as needed
        # DDC add:
        self.initializeSettings()

        self.leWorksheet = oscarWorksheet()

        # Load initial files (you can set this based on user input)
        self.load_files()

    def initUI(self):  # add menu items

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.instance().quit)

        # updatePath = QAction(QIcon((":help-content.svg")), '&Update monitored folder', self)
        updatePath = QAction(QIcon('folder.png'), '&Update monitored folder', self)
        # updatePath.setShortcut('Ctrl+Q')
        updatePath.setStatusTip('Update the path of the monitored folder')
        updatePath.triggered.connect(self.updateFolder)

        editPageSize = QAction(QIcon('ui-text-field.png'), '&Edit page size', self)
        # editPageSize.setShortcut('Ctrl+Q')
        editPageSize.setStatusTip('Update the number of files per page')
        editPageSize.triggered.connect(self.editPage)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        fileMenu = menubar.addMenu('&Settings')
        fileMenu.addAction(updatePath)
        fileMenu.addAction(editPageSize)
        # helpMenu = menuBar.addMenu(QIcon(":help-content.svg"), "&Help")

        self.setGeometry(300, 300, 350, 250)
        # self.setWindowTitle('Simple menu')
        self.show()

    def updateFolder (self):  # update monitored folder
        print("updating path")
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
        # put settings into dictionary
        settings = {'folder_path' : self.folder_path, 'items_per_page' : self.items_per_page,}
        # update pickle to conf.pickle
        with open ('conf.pickle','wb') as p: pickle.dump(settings,p)
        self.load_files()

    def editPage (self):  # update page size
        print('updating page size')
        # Display an input dialog
        text, ok = QInputDialog.getText(self, "Enter Text", "Please enter a number (4-50):")
        if ok and text:
            print(f"User entered: {text}")
            try:
                if 3 < int(text) < 50:
                    print('number good to go')
                    self.items_per_page = int(text)
                    settings = {'folder_path' : self.folder_path, 'items_per_page' : self.items_per_page,}
                    with open ('conf.pickle','wb') as p: pickle.dump(settings,p)
                    self.current_page = 0
                    self.load_files()
                else:
                    print('failed number test')
            except AttributeError:
                print('attrib error...probably not an int')

    def load_files(self):  # load files into a paginated list of lists
        # Simulate loading files from a directory
        # Replace this with your actual logic to populate self.files
        # self.files = [["file1.txt",'status'], "file2.txt", "file3.txt", "file4.txt", "file5.txt"]
        
        # bigFileList = [fN for fN in os.listdir('C:/Users/dim/Dropbox/projects/Overwatch Scrape/VAXTA') if fN[:10] == "Overwatch "]
        # bigFileList = [fN for fN in os.listdir(self.folder_path) if fN[:10] == "Overwatch "]

        #all files in folder regardless of pagination that start with Overwatch and end with png:
        # for later use
        simpleBigFileList = [fN for fN in os.listdir(self.folder_path) if fN[-4:] == ".png" and fN[:10] == "Overwatch "]
        # list for comparison
        fullBigFileList = [self.folder_path+'/'+fN for fN in os.listdir(self.folder_path) if fN[-4:] == ".png" and fN[:10] == "Overwatch "]

        # get the list of ignored and recorded files
        # myWorksheet = oscarWorksheet()
        igList, reList = self.leWorksheet.getStatus()
        # print("igList", igList)
        # print("reList", reList)
        self.bigFileList = []
        # self.bigFileList = [[x,y] for x in simpleBigFileList]
        print("testing the test")

        for file in fullBigFileList:
            if file in igList:
                self.bigFileList.append([file,'ignored'])
            elif file in reList:
                self.bigFileList.append([file,'recorded'])
            else:
                self.bigFileList.append([file,'unstored'])

        self.numberPages = -(len(self.bigFileList) // -self.items_per_page)
        # print("self.numberPages",self.numberPages)
        # print("self.bigFileList",self.bigFileList)
        # if len(self.bigFileList) > self.items_per_page:
        #     print("pagination initiated")
            # return page one:
        self.fileList = paginateList(self.bigFileList, itemsQTY=self.items_per_page)  
        # self.fileList[self.current_page]
        self.files = self.fileList[self.current_page]

        # Display files for the current page
        # print("self.fileList",self.fileList)
        self.display_files()

    def initializeSettings(self):  # load conf pickle or set one up
        # Get the directory path using QFileDialog
        # folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
        if os.path.exists('conf.pickle'): 
            print('testing pickle')
            try:
                # pull settings from dictionary
                # self.getSettingsPickle()
                with open ('conf.pickle', 'rb') as p:
                    settings = pickle.load(p)
                self.folder_path = settings['folder_path']
                self.items_per_page = settings['items_per_page']
                # from conf import folder_path
                print('import sucess')
            except FileNotFoundError:
                print('broken pickle')
                self.folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
                self.items_per_page = 10
                # put settings into dictionary
                settings = {'folder_path' : self.folder_path, 'items_per_page' : self.items_per_page,}
                # update pickle to conf.pickle
                with open ('conf.pickle','wb') as p: pickle.dump(settings,p)
        else:
            print('missing pickle')
            self.folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
            self.items_per_page = 10
            # put settings into dictionary
            settings = {'folder_path' : self.folder_path, 'items_per_page' : self.items_per_page,}
            # update pickle to conf.pickle
            with open ('conf.pickle','wb') as p: pickle.dump(settings,p)

    def display_files(self):  # setup and add file buttons and navigation buttons
        # Add pagination buttons
        self.navigationLayout.addWidget(self.prevButton)
        self.navigationLayout.addWidget(self.nextButton)
        # Clear existing buttons
        for i in reversed(range(self.buttonLayout.count())):
            widget = self.buttonLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # # Calculate start and end indices for the current page
        # start_idx = self.current_page * self.items_per_page
        # end_idx = min((self.current_page + 1) * self.items_per_page, len(self.files))

        #find the button status to add color:
        # igList, reList = self.leWorksheet.getStatus()
        # buttonFileStatus = oscarWorksheet[]
        # [[x,y] for x in ]

        # for file in self.files:
        #     if file in igList:
        #         buttonFileStatus.append[file,'ignored']

        # Create buttons for files in the current page
        for idx in range(len(self.files)):
            file_name = self.files[idx][0]
            file_status = self.files[idx][1]
            button = QPushButton(file_name.split("/")[-1], self)
            button
            # give it action
            button.clicked.connect(lambda _, fName=file_name: self.analyseImage(fName))
            #style?
            if file_status == 'ignored':
                # print(f"{file_name} getting ignored")
                button.setStyleSheet(oscarDGray) # cream
                # button.toolTip('Ignored')
            elif file_status == 'recorded':
                # print(f"{file_name} was recorded")
                button.setStyleSheet(oscarAqua) # aqua
                # button.toolTip('Recorded')
            elif file_status == 'unstored':
                # print(f"{file_name} was unstored")
                button.setStyleSheet(oscarYellow) # lightyellow arylide
                # button.toolTip('Unsaved')
            self.buttonLayout.addWidget(button)

        # enable/disable navigation buttons
        self.prevButton.setEnabled(self.current_page > 0)
        self.nextButton.setEnabled(self.current_page < self.numberPages-1)

    def show_previous_page(self):  # previous page of files and refresh buttons
        # print(self.current_page)
        # print(self.fileList)
        self.current_page = max(self.current_page - 1, 0)
        # print(self.current_page)
        self.files = self.fileList[self.current_page]
        # print("self.files",self.files)
        self.display_files()

    def show_next_page(self):  # next page of files
        # total_pages = (len(self.files) + self.items_per_page - 1) // self.items_per_page
        self.current_page = min(self.current_page + 1, self.numberPages - 1)
        # print(self.files)
        # print(self.fileList)
        # print(self.current_page)
        self.files = self.fileList[self.current_page]
        # print(self.current_page)
        # print(self.files)
        self.display_files()

    def open_file(self, leMessage):  # dummy function for placeholder button
        # Implement logic to open the selected file
        print(f"Opening file: {leMessage}")

    def analyseImage(self, imageFileName):  # take an image path and return it's statistics
        # should do something here with the image:
        fullPath = imageFileName
        # fullPath = self.folder_path + "/" + imageFileName
        print(f"do read this image: {self.folder_path}/{imageFileName}")
        # get "Timer:", "Kills:", "KillsperMin:", "accuracy:", "crit accuracy:"
        # response = {
        #     "Timer" : "240",
        #     "Kills" : "32",
        #     "KillsperMin" : "20",
        #     "accuracy" : "39%",
        #     "critAccuracy" : "20%",
        # }
        # response = ["240","32","20","39%","20%"]
        response = ripVAXTA(fullPath)
        print('try this')
        fileNameList = [x[0] for x in self.bigFileList]
        leIndex = fileNameList.index(imageFileName)
        print('this???? try this`')
        # print(leIndex)
        print("length of big file list",len(self.bigFileList))
        self.new_window = reviewData(self, response, self.folder_path, self.bigFileList, leIndex)
        self.new_window.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileButtonApp()
    window.show()
    app.exec()
    # sys.exit(app.exec())

