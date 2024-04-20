from PIL import Image
import pytesseract
import numpy as np
from pprint import pprint as pp
import datetime
import cv2
import os, sys
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

class oscarImage():
    """take a file path and read it...options for saving snippets"""
    def __init__(self, filePath) -> None:
        self.leP = filePath
        # if os.path.exists(filePath):
        #     print("heyoooooooo lets goooo")
        # else:
        #     print('nope no filePath')
        if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
            self.application_path = sys._MEIPASS
        else:
            self.application_path = os.path.dirname(os.path.abspath(__file__))
        self.debugPath = os.path.join(self.application_path,'debug')

    def ripVAXTA(self):  # take path and return scoreboard and hero
        textList = []
        textList.append(self.findHeroName())
        textList.extend(self.ripScoreboard())
        return textList
    
    def ripScoreboard(self,saveRGB=False,saveColorExtracts=False):  # Take a path and return what info is in the top left VAXTA corner
        """take a VAXTA Screenshot and output a list of lines from there"""
        # empty list for output:
        textList = []
        # look for hero name:
        # textList.append(findTheHeroName(baseImagePath))
        baseImage = Image.open(self.leP)
        # check if the image is windowed:
        # baseImage = cleanWindowedImages(baseImage)
        w, h = baseImage.size

        # vaxta snippet of scoreboard in proportions to the page
        # percentageMatrix = [0.02600,0.14000,0.15500,0.29600] # scoreboard
        # smol tuple of how much to crop out the image calculated range by 
        # getting the loosest measurement from a list of the most extreme window sizes
        #                                Left        Top      Right    Bottom
        cLeft, cTop, cRight, cBottom = ( 0.02209375, 0.11200, 0.15500, 0.29600 )

        cropCrap = ( 
            w*cLeft,   # left
            h*cTop,    # top
            w*cRight,  # right
            h*cBottom  # bottom
        )
        # crop out one of the sections 
        scoreBoard = baseImage.crop(cropCrap)
        if saveRGB:
            if len(self.leP.split("/"))>=2:
                fName = self.leP.split('/')[-1].split('.')[-2]
            else:
                fName = self.leP.split('.')[-2]
            scoreBoardPath = os.path.join(self.debugPath,datetime.datetime.now().strftime("%d.%H%M%S.%f") + f'-Scoreboard-{fName}.png')
            scoreBoard.save(scoreBoardPath)
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
            if saveColorExtracts:
                leFileName = datetime.datetime.now().strftime("%d.%H%M%S.%f") + f'-{nickName}.png'
                leFilePath = os.path.join(self.debugPath,leFileName)
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
            # print(leBlurb)
            if len(leBlurb.split(":"))==2:
                textList.append(leBlurb.split(":")[1])
            else:
                textList.append(leBlurb)

        return textList

    def findHeroName(self, templatesType = "A", saveSnippet = False, saveColor=False):  # scan a bottom right strip and return a hero String
        # return hero name
        """take an image path an return a hero's name"""
        testImage = Image.open(self.leP)
        w,h = testImage.size
        # propCrop = [0.7871093750,0.8208333333,0.9335937500,0.9305555556]  # proportional crop dims guns
        # propCrop = [0.62500000,0.79861111,0.82031250,0.97222222]  # proportional crop dims abilities
        # propCrop = [0.66406250,0.79861111,0.89843750,0.97222222]  # proportional crop dims abilities
        propCrop = [0.66406250,0.79861111,0.91796875,0.97222222]  # proportional crop dims abilities
        # image to test
        cvImage = cv2.imread(self.leP)
        #crop likely area:         #left               top                righ               bott
        left, top, right, bottom = (int(w*propCrop[0]),int(h*propCrop[1]),int(w*propCrop[2]),int(h*propCrop[3]))
        cropImg = cvImage[ top : bottom , left : right ]
        if saveColor:
            colorPath = os.path.join(self.debugPath,datetime.datetime.now().strftime("%d.%H%M%S.%f") +"colorCrop-test.png")
            cv2.imwrite(colorPath, cropImg)
        # Extract white color
        hsvImage = cv2.cvtColor(cropImg,cv2.COLOR_BGR2HSV) # cropped test image to hsv
        testImages = {  #  amber, white, and red extracted colors from the cropped test image
            "a":cv2.inRange(hsvImage,(5  , 200, 200),(15,  230, 230)),  # amber colors extracted
            "w":cv2.inRange(hsvImage,(0  ,   0, 205),(180,  50, 255)),  # white colors extracted
            "r":cv2.inRange(hsvImage,(155, 160, 180),(180, 255, 255))}  # red colors extracted
        if saveSnippet:
            for each in testImages:
                colorPath = os.path.join(self.debugPath,datetime.datetime.now().strftime("%d.%H%M%S.%f") +" "+ each + "-test.png")
                cv2.imwrite(colorPath, testImages[each])

        # if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
        #     application_path = sys._MEIPASS
        # else:
        #     application_path = os.path.dirname(os.path.abspath(__file__))
        templateDirectory = os.path.join(self.application_path,"templates")
        fullDirectoryList = os.listdir(templateDirectory)
        templates = [[x[:-4], cv2.imread(os.path.join(templateDirectory,x), cv2.IMREAD_GRAYSCALE)] for x in fullDirectoryList if x[-7:-6] == templatesType]
        for template in templates:
            if w == 2560:
                # print("no scale necessary")
                templateScaled = template[1]
            else:
                # print("so scaley rn")
                scaleDown = w/2560.000000000000
                templateScaled = cv2.resize(
                    template[1],
                    (0,0), 
                    fx= scaleDown, 
                    fy= scaleDown, 
                    interpolation= cv2.INTER_AREA)
            result = cv2.matchTemplate(testImages[template[0][-2:-1]],templateScaled, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            # print("max_val",max_val)
            if max_val > 0.8:
                # template[0] is the associated name from the file name of the template
                print(f"Found {template[0][:-3]} at position {max_loc}")
                return template[0][:-3]
        print("no hero found")
        return ""


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
        if getattr(sys, 'frozen', False): # If  run as a PyInstaller bootloader
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        self.picklePath = os.path.join(application_path,"dataCache.pickle")

        # get a pickle
        if os.path.exists(self.picklePath):
            print('found the cache')
            with open (self.picklePath, 'rb') as p:
                self.dC = pickle.load(p)
        else:
            print('no data cache found; starting a new one')
            self.dC = {}
            # return self.datacache

    def backupCache(self):
        with open (self.picklePath,'wb') as p: 
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
  
    # from oscarguts import oscarImage
    # left = "C:/Users/dim/Documents/GitHub/OSCAR/Overwatch 4_9_2024 6_21_21 PM WreckingBall.png"
    # right = "C:/Users/dim/Documents/GitHub/OSCAR/Overwatch 4_9_2024 6_19_50 PM Sigma.png"

    # leftTest = oscarImage(left).findHeroName(saveColor=True)
    # rightTest = oscarImage(right).findHeroName(saveColor=True)
    # leftTest = oscarImage(left).findHeroName(saveSnippet=True)
    # rightTest = oscarImage(right).findHeroName(saveSnippet=True)
    # scoretest = oscarImage(left).ripScoreboard(saveRGB=True, saveColorExtracts=True)
    
    # ripTest = oscarImage(left).ripVAXTA()
