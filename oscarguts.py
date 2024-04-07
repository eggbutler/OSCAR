from PIL import Image
import pytesseract
import numpy as np
from pprint import pprint as pp
import datetime
import cv2
import os
import gspread


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
    textList.extend([findTheHeroName(baseImagePath)])
    baseImage = Image.open(baseImagePath)
    # check if the image is windowed:
    # baseImage = cleanWindowedImages(baseImage)
    w, h = baseImage.size

    percentageMatrix = [ # vaxta matrix of snippets in proportions to the page
        [0.047656250,0.114583333,0.125781250,0.142361111], # Timer 
        [0.056640625,0.142361111,0.119140625,0.170138889], # Kills
        [0.033203125,0.168055556,0.142578125,0.195833333], # KillsperMin 
        [0.035156250,0.193750000,0.142578125,0.221527778], # accuracy
        [0.019531250,0.218750000,0.156250000,0.246527778], # crit accuracy
    ]

    for snippet in range(len(percentageMatrix)):
        cropCrap = (
            # smol tuple of how much to crop out the image
            w*percentageMatrix[snippet][0],  # left
            h*percentageMatrix[snippet][1],  # top
            w*percentageMatrix[snippet][2],  # right
            h*percentageMatrix[snippet][3]   # bottom
        )

        # crop out one of the sections 
        # leSnippet = np.array(baseImage.crop(cropCrap))  
        leSnippet = baseImage.crop(cropCrap)

        # Try and clean up the image
        #  matrix of RGBA colors to search for, fuzziness, RGBA colors to change it to
        colorsToChange = [  
            [(240, 240, 240, 255),  30, (255,255,255,255)],  # wall color
            [(200, 200, 200, 255),  30, (255,255,255,255)],  # wall color
            [(160, 160, 160, 255),  30, (255,255,255,255)],  # wall color
            [(120, 120, 120, 255),  30, (255,255,255,255)],  # wall color
            [( 80,  80,  80, 255),  30, (255,255,255,255)],  # wall color
            [( 40,  40,  40, 255),  30, (255,255,255,255)],  # wall color
            [(  5,   5,   5, 255),  30, (255,255,255,255)],  # wall color
            [(236, 153,   0, 255),  70, (  0,  0,  0,255)],  # orangeColor
            [(0,   234, 234, 255),  70, (  0,  0,  0,255)],  # aquaColor 
            [(38,  170, 255, 255),  70, (  0,  0,  0,255)],  # oceanColor
            [(160, 232,  22, 255),  70, (  0,  0,  0,255)],  # limeColor 
            [(0,   230, 150, 255),  70, (  0,  0,  0,255)],  # foamColor 
        ]
        leSnippet = leSnippet.convert("RGBA")
        pixdata = leSnippet.load()

        #trying to take all the gray colors and try to wash them out
        #then find the 5 text colors and bring them out.
        for color in colorsToChange:
            for y in range(leSnippet.size[1]):
                for x in range(leSnippet.size[0]):
                    # totalColorDiff = 0
                    shouldReplace = True
                    for idx in range(3): #include RGB but exclude alpha
                        if abs(pixdata[x, y][idx] - color[0][idx]) > color[1]:
                            shouldReplace = False
                    if shouldReplace:
                        pixdata[x, y] = color[2] #replace with black
        #### for testing image#######
        if saveSnippet:
            timeStampFileName = 'debug\\' + datetime.datetime.now().strftime("%Y%m%d.%H%M%S.%f") + '.png'
            leSnippet.save(timeStampFileName)
        #### for testing image#######
        # convert to an array
        leSnippet = np.array(leSnippet)  

        # analyse it
        leBlurb = pytesseract.image_to_string(leSnippet).replace("\n\n","\n").strip().split("\n")
        # print('leblurbPPP', leBlurb)

        leBlurb[0] = leBlurb[0].replace('  %','%')
        leBlurb[0] = leBlurb[0].replace(' %','%')

        # put each line into the list of stuff (and only the parts after the colon if found)
        if len(leBlurb[0].split(":"))==2:
            textList.extend([leBlurb[0].split(":")[1]])
        else:
            textList.extend(leBlurb)

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
        print("testing mark two")

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
        self.pageQTY = -(len(self.nameList) // -self.pageSize)
        self.pagdList = [[] for _ in range(self.pageQTY)]
        for idx, fileName in enumerate(self.nameList):
            current_page = idx//self.pageSize
            # print(f"fileList[{current_page}].append({fileName})")
            self.pagdList[current_page].append((fileName,self.statusList[idx]))  # ?????

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
