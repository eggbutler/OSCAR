import sys, os, pickle
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, \
        QWidget, QInputDialog, QLabel, QLineEdit, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
# from PIL import Image
# import pytesseract
# import numpy as np
from pprint import pprint as pp
import datetime
# os.chdir('C:\\Users\\dim\\Documents\\GitHub\\OSCAR')
from oscarguts import ripVAXTA, oscarWorksheet, oscarFileMeta, analysisCache
from oscarguts import oscarBlue, oscarAqua, oscarCream, oscarRed, oscarYellow, bottomUnderline, oscarDGray



class reviewData(QWidget):
    def __init__(self, parent_window, response, filesMeta):  # initialize the words read from the image for human review
        super().__init__()
        layout = QVBoxLayout()

        self.parent_window = parent_window
        response = response  + ['']
        self.fls = filesMeta  # files meta object
        self.fls.updateData()

        # Add a label for context
        self.label = QLabel(f'please check values for\n{self.fls.name}')
        if self.fls.status == 'ignored':
            self.label2 = QLabel('This file was previously ignored')
        elif self.fls.status == 'recorded':
            self.label2 = QLabel('This file was already recorded!')
            self.label.setStyleSheet(oscarAqua)
            self.label2.setStyleSheet(oscarAqua)
        elif self.fls.status == 'unstored':
            self.label2 = QLabel("This screen shot isn't in the spreadsheet!")
            self.label.setStyleSheet(oscarYellow)
            self.label2.setStyleSheet(oscarYellow)
        layout.addWidget(self.label)
        layout.addWidget(self.label2)

        # Create labels and input fields
        # "Timer:", "Kills:", "KillsperMin:", "accuracy:", "crit accuracy:"
        self.labels = ["Hero", "Timer:", "Kills:", "KillsperMin:", "accuracy:", "critAccuracy:","comment:"]
        self.input_fields = [QLineEdit() for _ in range(len(self.labels))]

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
        prevButton.setEnabled(self.fls.index > 0)
        nextButton.setEnabled(self.fls.index < len(self.fls.nameList)-1)

        self.leWorksheet = oscarWorksheet()

        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def show_prev_file(self):  # find previous file in the index and look up it's data.
        # leStats = ["240","32","20","39%","20%"]
        self.fls.index = max(0,self.fls.index-1)  # index the index down
        self.fls.updateData()
        # leStats = ripVAXTA(self.fls.namePath)  # read the new file
        self.parent_window.analyseImage(self.fls.namePath)  # read the new file
        # self.new_window = reviewData(self.parent_window, leStats, self.fls)
        # self.new_window.show()  # show the previous file
        self.close()

    def show_next_file(self):  # find next file in the index and look up it's data.
        # leStats = ["240","32","20","39%","20%"]
        self.fls.index = min(len(self.fls.nameList),self.fls.index+1)  # index the index up
        self.fls.updateData()
        # leStats = ripVAXTA(self.fls.namePath)  # read the new file
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


class FileButtonApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('icons/oscarAngry.ico'))

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
                    self.dtCache.dC[leFile] = ripVAXTA(leFile)  
                    # print(self.dtCache.dC[leFile])
                # else:
                    # print('skipping cacheing')
            # else:
            #     print(f"it wasn't unstored? self.fls.statusList[idx] status")
            #     print(self.fls.statusList[idx])

        self.dtCache.backupCache()


        # Add pagination buttons
        self.navigationLayout.addWidget(self.prevButton)
        self.navigationLayout.addWidget(self.nextButton)

        self.pageFeedback = QLabel("Page _ of _")
        centralLayout.addWidget(self.pageFeedback)

        # Display initial files as buttons
        self.display_files()

    def initUI(self):  # add menu items

        exitAct = QAction(QIcon('icons/exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.instance().quit)

        # updatePath = QAction(QIcon((":help-content.svg")), '&Update monitored folder', self)
        updatePath = QAction(QIcon('icons/folder.png'), '&Update monitored folder', self)
        updatePath.setStatusTip('Update the path of the monitored folder')
        updatePath.triggered.connect(self.updateFolder)

        editPageSize = QAction(QIcon('icons/ui-text-field.png'), '&Edit page size', self)
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

    def updateFolder (self):  # update monitored folder setting menu
        print("updating path")
        folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
        # put settings into dictionary
        settings = {'folder_path' : folder_path, 'items_per_page' : self.fls.pageSize,}
        # update pickle to conf.pickle
        with open ('conf.pickle','wb') as p: pickle.dump(settings,p)
        self.fls.path = folder_path
        self.display_files

    def editPage (self):  # update page size settings menu
        print('updating page size')
        # Display an input dialog
        text, ok = QInputDialog.getText(self, "Enter Text", "Please enter a number (4-50):")
        if ok and text:
            try:
                if 3 < int(text) < 50:
                    self.fls.pageSize = int(text)
                    settings = {'folder_path' : self.fls.path, 'items_per_page' : self.fls.pageSize,}
                    with open ('conf.pickle','wb') as p: 
                        pickle.dump(settings,p)
                    self.fls.pageIndex = 0
                    self.fls.updateStatus()
                    self.display_files()
                else:
                    print('failed number test')
            except AttributeError:
                print('attrib error...probably not an int')
                pageError = QMessageBox(self)
                pageError.setWindowTitle('Oops?!')
                pageError.setText("Bad news for you. That page size won't work")

    def initializeSettings(self):  # load config pickle to get folder path and page size
        # Get the directory path using QFileDialog
        # folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
        if os.path.exists('conf.pickle'): 
            print('testing pickle')
            try:
                # pull settings from dictionary
                with open ('conf.pickle', 'rb') as p:
                    settings = pickle.load(p)
                folder_path = settings['folder_path']
                items_per_page = settings['items_per_page']
                # from conf import folder_path
                print('import sucess')
            except FileNotFoundError:
                print('broken pickle')
                folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
                items_per_page = 10
                # put settings into dictionary
                settings = {'folder_path' : folder_path, 'items_per_page' : items_per_page,}
                # update pickle to conf.pickle
                with open ('conf.pickle','wb') as p: pickle.dump(settings,p)
        else:
            print('missing pickle')
            folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
            items_per_page = 10
            # put settings into dictionary
            settings = {'folder_path' : folder_path, 'items_per_page' : items_per_page,}
            # update pickle to conf.pickle
            with open ('conf.pickle','wb') as p: pickle.dump(settings,p)
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

    def analyseImage(self, imageFileName):  # take an image path and return it's statistics
        # should do something here with the image:
        self.fls.index = self.fls.pathList.index(imageFileName)
        self.fls.updateData()
        # print('self.dtCache.dC',self.dtCache.dC)
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
            response = ripVAXTA(self.fls.namePath)
            self.dtCache.dC[self.fls.namePath] = response  # add/update to the cache
            self.dtCache.backupCache()
            self.new_window = reviewData(self, response, self.fls)
            self.new_window.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileButtonApp()
    window.show()
    app.exec()
    # sys.exit(app.exec())

