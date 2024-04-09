from PIL import Image
import pytesseract
import numpy as np
from pprint import pprint as pp
import datetime
import cv2
import os
import gspread
import pickle


oscarBlue    = "background-color: #001524; color:#FFF;"  # darkblue  Too dark
oscarAqua    = "background-color: #15616D; color:#FFF;"  # aqua (done recorded)
oscarCream   = "background-color: #FFECD1;"  # cream
oscarRed     = "background-color: #D1462F;"  # chili red
oscarYellow  = "background-color: #E3C567;"  # lightyellow arylide (unstored)
oscarDGray   = "background-color: #F0F0F0;"  # default grey

bottomUnderline = "border-width:5px; border-color:black;"

def paginateList(listofdata, itemsQTY=5):  # take a list and cut it up into lists of lists
    # qty of pages:
    numberPages = -(len(listofdata) // -itemsQTY)
    fileList = [[] for _ in range(numberPages)]
    for idx, fileName in enumerate(listofdata):
        current_page = idx//itemsQTY
        fileList[current_page].append(fileName)
    return fileList

def ripVAXTA(baseImagePath, saveSnippet = False):  # Take a path and return what info is in the top left VAXTA corner
    """take a VAXTA Screenshot and output a list of lines from there"""
    # empty list for output:
    textList = []
    # look for hero name:
    textList.append(findTheHeroName(baseImagePath))
    baseImage = Image.open(baseImagePath)
    # check if the image is windowed:
    # baseImage = cleanWindowedImages(baseImage)
    w, h = baseImage.size

    # vaxta snippet of scoreboard in proportions to the page
    # percentageMatrix = [0.02600,0.14000,0.15500,0.29600] # scoreboard
    # smol tuple of how much to crop out the image calculated range by 
    # getting the loosest measurement from a list of the most extreme window sizes
    #                                Left     Top      Right    Bottom
    cLeft, cTop, cRight, cBottom = ( 0.02600, 0.11200, 0.15500, 0.29600 )

    cropCrap = ( 
        w*cLeft,   # left
        h*cTop,    # top
        w*cRight,  # right
        h*cBottom  # bottom
    )
    # crop out one of the sections 
    scoreBoard = baseImage.crop(cropCrap)
    if saveSnippet:
        if len(baseImagePath.split("/"))>=2:
            fName = baseImagePath.split('/')[-1].split('.')[-2]
        else:
            fName = baseImagePath.split('.')[-2]
        leFilePath = 'debug\\' + datetime.datetime.now().strftime("%d.%H%M%S.%f") + f'-Scoreboard-{fName}.png'
        scoreBoard.save(leFilePath)
    # HSV arrays of the bottom and top ranges to look for.  Hue is really doing the 
    # heavy lifting here
    colorRanges = [
        [np.array([15,130,130]),np.array([22,255,255]), "timer"],        # orange (Timer)
        [np.array([85,130,130]),np.array([95,255,255]), "kills"],        # aqua (Kills)
        [np.array([98,130,130]),np.array([107,255,255]),"kpm"],          # blue (Kills per min)
        [np.array([35,130,130]),np.array([45,255,255]), "accuracy"],     # lime (Green Accuracy)
        [np.array([75,130,130]),np.array([85,255,255]), "critAccuracy"], # green (Crit Accuracy)
    ]

    # Make a new image pulling each color (top/bottom) pair
    for bot, top, nickName in colorRanges:  
        MIN = bot
        MAX = top
        # convert the scoreboard PIL to a CV2 then to an NP and do stuff
        nArray = np.array(scoreBoard)
        # nArray = cv2.imread(scoreBoard)
        hsv_img = cv2.cvtColor(nArray ,cv2.COLOR_RGB2HSV)
        # Use OpenCV to read the hue pulled
        frame_threshed = cv2.inRange(hsv_img, MIN, MAX)

        #### for testing image#######
        if saveSnippet:
            if os.path.exists('debug'):  #  if there is a debug folder save the snippet there
                # print('test two')
                leFilePath = 'debug\\' + datetime.datetime.now().strftime("%d.%H%M%S.%f") + f'{nickName}.png'
            else:  #  save the snippets to root
                # print('test one ')
                leFilePath = datetime.datetime.now().strftime("%d.%H%M%S.%f") + f'{nickName}.png'
            # timeStampFileName = leFilePath
            #make a png out of the color extract
            cv2.imwrite(leFilePath,frame_threshed)
            # lePNG = cv2.imencode('.png', frame_threshed)
            # lePNG.save(leFilePath)
        #### for testing image#######

        # convert to an array
        nArray = np.array(frame_threshed)

        # analyse it
        leBlurb = pytesseract.image_to_string(nArray, config=r"--psm 7").replace("\n\n","\n").strip()
        # leBlurb = pytesseract.image_to_string(leSnippet)  # .replace("\n\n","\n").strip().split("\n")
        # print('leblurbPPP', leBlurb)
        # custom_oem_psm_config = r'--oem 3 --psm 6'
        # pytesseract.image_to_string(image, config=custom_oem_psm_config

        leBlurb = leBlurb.replace('  %','%')
        leBlurb = leBlurb.replace(' %','%')

        # put each line into the list of stuff (and only the parts after the colon if found)
        print(leBlurb)
        if len(leBlurb.split(":"))==2:
            textList.append(leBlurb.split(":")[1])
        else:
            textList.append(leBlurb)

    return textList

def cleanWindowedImages(leImage):
    # """remove the title bar from windowed screen shots"""
    # leImage = Image.open("Overwatch 6_15_2023 1_27_11 PM.png")
    w, h = leImage.size
    cropTop = (
        # smol tuple to get the title bar
        1,      # left: 1 pixel black line
        0,      # top: all the tops
        w,      # right: full width
        32  # bottom: at least I have a 30PX 
    )
    # crop out one of the sections 
    titleBar = leImage.crop(cropTop)
    # titleBar.save('test.png')
    # analyse it
    leBlurb = pytesseract.image_to_string(np.array(titleBar)).lower()
    # print('leblurbxx',leBlurb)
    if ("over" in leBlurb) or ("watch" in leBlurb):
        # clip off the top
        print('clipping title bar')
        # print('old image dims:', leImage.size)
        lrCrop = (w - (h-33)*16/9)/2
        noTitleCrop = (
            # smol tuple to crop off the title bar
            lrCrop,   # left: 1 pixel black line
            32,       # top: remove the top
            w-lrCrop, # right: full width
            h-1       # bottom: full bottom 
        )
        leImage = leImage.crop(noTitleCrop)
        print('new image dims:', leImage.size)
        return leImage
    else:
        print('not clipping title bar')
        return leImage

# Iterate through templates and find matches in a screen shot
def findTheHeroName(leFilePath,templatesType="Ab"):  # Templates = Ul or Ab
    """take an image path an return a hero's name"""
    # slice out the bottom left corner: left, top, right, bottom 
    baseImage = Image.open(leFilePath)
    w,h = baseImage.size
    propCrop = (0.62500000, 0.79861111, 0.82031250, 0.97222222)
    realCrop = (propCrop[0]*w, propCrop[1]*h, propCrop[2]*w, propCrop[3]*h)
    croppedImage = baseImage.crop(realCrop)
 
    # image to test
    image = cv2.cvtColor(np.array(croppedImage), cv2.COLOR_RGB2BGR)
    # image = cv2.imread(leFilePath)
    # listOfTemplates (thumbnails to look for)
    templates = [ 
        [x[:-7], cv2.imread(os.path.abspath(os.path.join("templates",x)))] \
        for x in os.listdir("templates") if x[-7:-5] == templatesType  # 'Ul' or 'Ab'
    ]
    for template in templates:
        result = cv2.matchTemplate(image, template[1], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # You can set a threshold to consider a match
        if max_val > 0.8:
            # template[0] is the associated name from the file name of the template
            print(f"Found {template[0]} at position {max_loc}")
            # print(template[1])
            return template[0]

# findTheHeroName("C:/Users/dim/Dropbox/projects/Overwatch Scrape/VAXTA/Overwatch 6_24_2023 9_52_04 AM.png")

class oscarWorksheet():
    """interact with the worksheet"""
    def __init__(self) -> None:
        self.gc = gspread.service_account()
        self.wks = self.gc.open('VAXTA').worksheet('DATA(leave)')

    def getStatus(self):  # return a list of done and ignored files from the sheet
        fnl = self.wks.col_values(1)[1:]  # filename
        stl = self.wks.col_values(10)[1:] # status 
        #Make an ignore and recorded list:
        ignoreList = []
        recordList = []
        for fN, sT in zip(fnl,stl):
            if sT == 'ignored':
                ignoreList.append(fN)
            else:
                recordList.append(fN)
        return(ignoreList,recordList)
    
    def writeTest(self):  # write todays date and time to the sheet
        stringNow = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M')
        addRow = [f'fake{stringNow}.png',stringNow] + [None]*7 + ['ignored']
        self.wks.append_row(addRow)


class oscarFileMeta():
    """object including all the various file formats I need for running the app"""
    def __init__(
            self,
            path="C:/Users/dim/Videos/Captures",
            pageSize=10,
            index=0,
            pageIndex=0,
    ) -> None:
        self.path = path
        # self.bigFileList = bigFileList
        self.index = index
        self.pageSize = pageSize
        self.pageIndex = pageIndex
        self.leWorksheet = oscarWorksheet()
        self.updateStatus()

    def updateStatus(self):
        # get the list of ignored and recorded files from the spread sheet and line them up with the directory
        # get a fresh list of files in a directory starting with overwatch and ends with .png
        self.nameList = [fN for fN in os.listdir(self.path) if fN[-4:] == ".png" and fN[:10] == "Overwatch "]

        self.pathList = []
        self.statusList = []

        igList, reList = self.leWorksheet.getStatus()

        for file in self.nameList:
            if self.path+'/'+file in igList:
                self.pathList.append(self.path+'/'+file)
                self.statusList.append('ignored')
            elif self.path+'/'+file in reList:
                self.pathList.append(self.path+'/'+file)
                self.statusList.append('recorded')
            else:
                self.pathList.append(self.path+'/'+file)
                self.statusList.append('unstored')

        # make a list of files that are paginated
        # qty of pages:
        self.pageQTY = -(len(self.pathList) // -self.pageSize)
        self.pagdList = [[] for _ in range(self.pageQTY)]
        for idx, filePath in enumerate(self.pathList):
            current_page = idx//self.pageSize
            # print(f"fileList[{current_page}].append({fileName})")
            self.pagdList[current_page].append((filePath,self.statusList[idx]))  # ?????

        self.updateData()

    def updateData(self):
        self.name = self.nameList[self.index]
        self.namePath = self.pathList[self.index]
        self.status = self.statusList[self.index]

    # def updateFileIndex(self,leFileIndex):
    #     self.fileIndex = leFileIndex
    #     self.updateData()

    # def updatePageIndex(self,lePageIndex):
    #     self.pageIndex = lePageIndex
    #     self.updateStatus()

    def dumpData(self):
        print('self.name:')
        pp(self.name)
        print('self.path')
        pp(self.path)
        print('self.namePath')
        pp(self.namePath)
        print('self.index')
        pp(self.index)
        print('self.pageQTY')
        pp(self.pageQTY)
        print('self.pageIndex')
        pp(self.pageIndex)
        print('self.pathList')
        pp(self.pathList)
        print('self.statusList')
        pp(self.statusList)
        print('self.nameList')
        pp(self.nameList)
        print('self.pagdList')
        pp(self.pagdList)
        # print('')
        # pp()


class analysisCache:
    """obect to hold the cache data coming out of Tesseract"""
    """{"filename and path':[val1, ... val6]}"""
    def __init__(self) -> None:
        # get a pickle
        if os.path.exists('dataCache.pickle'):
            print('found the cache')
            with open ('dataCache.pickle', 'rb') as p:
                self.dC = pickle.load(p)
        else:
            print('no data cache found; starting a new one')
            self.dC = {}
            # return self.datacache

    def backupCache(self):
        with open ('dataCache.pickle','wb') as p: 
            pickle.dump(self.dC,p)



if __name__ == '__main__':
    test = oscarFileMeta()
    test.dumpData()

    # self.name:
    # 'Overwatch 3_29_2024 2_30_03 PM.png'
    # self.path
    # 'C:/Users/dim/Videos/Captures'
    # self.namePath
    # 'C:/Users/dim/Videos/Captures/Overwatch 3_29_2024 2_30_03 PM.png'
    # self.index
    # 0
    # self.pageQTY
    # 5
    # self.pageIndex
    # 0
    # self.pathList
    # ['C:/Users/dim/Videos/Captures/Overwatch 3_29_2024 2_30_03 PM.png',
    # 'C:/Users/dim/Videos/Captures/Overwatch 3_29_2024 2_44_16 PM.png',
    # 'C:/Users/dim/Videos/Captures/Overwatch 8_8_2023 10_12_22 AM.png']
    # self.statusList
    # ['recorded',
    # 'ignored',
    # 'recorded']
    # self.nameList
    # ['Overwatch 3_29_2024 2_30_03 PM.png',
    # 'Overwatch 3_29_2024 2_44_16 PM.png',
    # 'Overwatch 8_8_2023 10_12_22 AM.png']
    # self.pagdList
    # [[('Overwatch 3_29_2024 2_30_03 PM.png', 'recorded'),
    # ('Overwatch 3_30_2024 4_09_46 PM.png', 'ignored')],
    # [('Overwatch 3_30_2024 4_09_50 PM.png', 'recorded'),
    # ('Overwatch 4_2_2024 4_51_28 PM Ana.png', 'ignored')],
    # [('Overwatch 4_2_2024 4_51_40 PM Baptiste.png', 'ignored'),
    # ('Overwatch 8_8_2023 10_12_22 AM.png', 'recorded')]]

    # test.index +=1
    # test.updateData
