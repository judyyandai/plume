from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from plumeObject import Plume 
from PIL import ImageTk, Image
# import plumeFunction as pf
import pickle as pickle
import os
import csv
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import random
from scipy.optimize import curve_fit 
from IPython.display import clear_output
import pandas as pd
import sys
import plumeAnalysis
import ctypes

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)




#Experimental Plume Pickle (file)
fileExtension = ".epp" 
# temporary directories used for tesing the GUI
tempDirectory = r"P:\F250_len\F250_41mm_Pre_runSeries\data"
tempSampleDirectory = r"Z:\Users\coop\Matthew_2025\PlumeSamples"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
tempQuickDirectory = r"P:\F250_len\F250_41mm_Pre_runSeries\data\below6000ns" #For making creating plumes quicker. Won't work for loading as there aren't any plume pickle files there.
tempImgDirectory = r"P:\F250_len\F250_41mm_Pre_runSeries\images\Fast_Loading"
tempName = "allPlumes(120825)"
tempName2 = "testing"
tempImageName = "1743521811_000001800_000002072.png"

# Robyn temp directories for testing
tempRAdata = r"Z:\Users\coop\Robyn_2025\PlumeAnalysis\TestFolder\Data"
tempRAimages = r"Z:\Users\coop\Robyn_2025\PlumeAnalysis\TestFolder\Images"

# INPUT: String, String
# PURPOSE: Load a list of Plumes through pickle. The method takes in the directory of the file and the file's name as two separate parameters
# OUTPUT: List of Plumes
def loadPlumes(directory, fileName):
    file = open(os.path.join(directory, fileName), "rb")
    return pickle.load(file)

# INPUT: List of Plumes, String, String
# PURPOSE: Create a file with directory and save a list of Plumes into that file through pickle
# OUTPUT: None
# Note: Try looking to streamline the file naming process
def savePlumes(plumes, directory, fileName):
    # global fileExtension
    # name = fileName + fileExtension
    file = open(os.path.join(directory, fileName), "wb")
    pickle.dump(plumes, file)

# INPUT: None
# PURPOSE: goes through the directory and creates plumes from the csv files in that directory 
# OUTPUT: List of Plumes
def createPlumeList(directory, imageDirectory):
    plumes = []
    files = os.listdir(directory)
    total = len(files)
    for i in range(len(files)):
        file = files[i]
        progress = float(i/total)*100
        print(f"createPlumeList Progress: {progress:.4g}%")
        rows = []
        #print(files)
        if file.endswith(".csv"):
            plumeName = file.strip(".csv")
            plume = Plume(plumeName, directory, imageDirectory)
            plumes.append(plume)
    return plumes

# INPUT: List of Plumes
# PURPOSE: Retrieves the longest list of contours in this list of plumes. Is used to tell if the plumes have been analyzed before or not.
# OUTPUT: Integer 
def returnMaxContourLength(plumes):
    lenList = []
    for plume in plumes:
        contours = plume.contours
        lenList.append(len(contours))
    print(np.max(lenList))
    return np.max(lenList)

# INPUT: String
# PURPOSE: Return a Plume's parameter given its tag
# OUTPUT: Float or Boolean
def returnParameter(plume, tag: str):
    if tag == "Lifetime":
        return plume.lifeTime
    elif tag == "Voltage":
        return plume.voltage
    elif tag == "Jet Length":
        return plume.jetHeight
    elif tag == "Fracture Radius":
        return plume.fractureRadius
    elif tag == "Plume Height":
        return plume.height
    elif tag == "Plume Width":
        return plume.width
    elif tag == "Lift Off":
        return plume.isLiftOff
    elif tag == "Fracture":
        return plume.isFracture
    elif tag == "Perfect":
        return plume.isPerfect
    elif tag == "Laser":
        return plume.laser
    else:
        print("returnParameter ERROR: Not valid parameter.")

# INPUT: Integer, integer, list, string 
# PURPOSE: Finds plumes whose given parameter is within the lower and upper bounds and returns them
# OUTPUT: List of Plumes
def returnPlumesWithinBoundary(lower, upper, plumes, tag: str):
    global isExclusion
    sortedPlumes = []
    for plume in plumes:
        try:
            parameter = returnParameter(plume, tag)
            if not isExclusion:
                if lower < parameter <= upper:
                    sortedPlumes.append(plume)
            else:
                if not (lower < parameter <= upper):
                    sortedPlumes.append(plume)
        # if parameter == "Lifetime":
        #     if lower < plume.getLifeTime() <= upper:
        #         sortedPlumes.append(plume)
        # elif parameter == "Voltage":
        #     if lower < plume.getVoltage() <= upper:
        #         sortedPlumes.append(plume)
        # elif parameter == "Jet Length":
        #     if lower < plume.getJetHeight() <= upper:
        #         sortedPlumes.append(plume)
        # elif parameter == "Fracture Radius":
        #     if lower < plume.getFractureRadius() <= upper:
        #         sortedPlumes.append(plume)
        # elif parameter == "Plume Height":
        #     if lower < plume.height <= upper:
        #         sortedPlumes.append(plume)
        # elif parameter == "Plume Width":
        #     if lower < plume.width <= upper:
        #         sortedPlumes.append(plume)
        except:
            print('Parameter is not readable. Please enter "Lifetime", "Voltage", "Jet Length", "Fracture Radius", "Plume Height", "Plume Width" and the lower and upper bounds for those parameters')
    return sortedPlumes

# INPUT: Float, Float, String, Float, Float, String, List of Plumes
# PURPOSE: Finds Plumes that have two qualitative parameters within their respective boundaries
# OUTPUT: List of Plumes
def returnPlumesWithinTwoBoundaries(lower1, upper1, tag1: str, lower2, upper2, tag2: str, plumes):
    global isExclusion
    sortedPlumes = []
    for plume in plumes:
        try:
            parameter1 = returnParameter(plume,tag1)
            parameter2 = returnParameter(plume, tag2)
            if not isExclusion:
                if lower1 < parameter1 <= upper1 and lower2 < parameter2 <= upper2:
                    sortedPlumes.append(plume)
            else:
                #if not (lower1 < parameter1 <= upper1) and not (lower2 < parameter2 <= upper2):
                if not (lower1 < parameter1 <= upper1) or not (lower2 < parameter2 <= upper2):
                    sortedPlumes.append(plume)
        except:
            print('Either parameter is not readable. Please enter "Lifetime", "Voltage", "Jet Length", "Fracture Radius", "Plume Height", "Plume Width" and the lower and upper bounds for those parameters') 
    return sortedPlumes

# INPUT: List of Plumes, String
# PURPOSE: Finds plumes that have the given parameter return them
# OUTPUT: List of plumes
def returnPlumesWithParameter(plumes, tag: str):
    global isExclusion
    sortedPlumes = []
    for plume in plumes:
        try:
            parameter = returnParameter(plume, tag)
            if not isExclusion:
                if parameter:
                    sortedPlumes.append(plume)
            else:
                if not parameter:
                    sortedPlumes.append(plume)
        except:
            print('Parameter is not readable. Please enter "Fracture", "Lift Off", or "Perfect"')
    return sortedPlumes

# INPUT: List of Plumes, String, Integer (cond.), Integer (cond.), Boolean (cond.)
# PURPOSE: An automatic plume finder within a plume list. Ask for a plume with a given parameter or within a given constraint on said parameter.
# OUTPUT: List of Plumes

# NOTE: Updating the plume's parameters such as Lift Offs or Jet length is given through isEvaluated. If the plume has already been evaluated prior to running it through 
# binPlumes method, set isEvaluated to True when using it. If the plume hasn't, set isEvaluated to False (Note that this will drastically increase processing time).
# The default values on lower, upper, and isEvaluated will be run if they aren't defined in the method call.
# To change them simply add the values in sequence of the method call or manually assign it 
# (e.g. binPlumes(plumes, "Jet Length", lower = 2000, upper = 3000) or binPlumes(plumes, "Perfect", isEvaluated = False)).
quantitativeParams = ["Lifetime","Voltage","Jet Length", "Fracture Radius", "Plume Height", "Plume Width"]
qualitativeParams = ["Perfect","Lift Off", "Fracture", "Laser"]
def binPlumes(plumes, parameter: str, lower = 0, upper = 0):
    binnedPlumes = []
    if parameter in quantitativeParams:
        binnedPlumes = returnPlumesWithinBoundary(lower, upper, plumes, parameter)
    elif parameter in qualitativeParams:
        binnedPlumes = returnPlumesWithParameter(plumes, parameter)
    else:
        print('Not readable. Please input "Lifetime", "Voltage", or "Jet Length" and the lower and upper ' \
        'bounds for those parameters, or "Perfect" or "Lift Off" or "Fracture" and whether you want to evaluate them first (defaulted to "no") ')
    return binnedPlumes

def binPlumesMultipleParam(plumes, parameter1, parameter2, lower1 = 0, upper1 = 0, lower2 = 0, upper2 = 0):
    binnedPlumes = []
    # Case1: Quantitative and Quantitative
    if parameter1 in quantitativeParams and parameter2 in quantitativeParams:
        binnedPlumes = returnPlumesWithinTwoBoundaries(lower1, upper1, parameter1, lower2, upper2, parameter2, plumes)
    # Case2: Quantitative and Qualitative
    elif parameter1 in quantitativeParams and parameter2 in qualitativeParams:
        binnedPlumes = returnPlumesWithinBoundary(lower1, upper1, plumes, parameter1)
        binnedPlumes = returnPlumesWithParameter(binnedPlumes, parameter2)
    # Case3: Qualitative and Quantitative
    elif parameter1 in qualitativeParams and parameter2 in quantitativeParams:
        binnedPlumes = returnPlumesWithinBoundary(lower2, upper2, plumes,parameter2)
        binnedPlumes = returnPlumesWithParameter(binnedPlumes, parameter1)
    # Case4: Qualitative and Qualitative
    elif parameter1 in qualitativeParams and parameter2 in qualitativeParams:
        binnedPlumes = returnPlumesWithParameter(plumes, parameter1)
        binnedPlumes = returnPlumesWithParameter(binnedPlumes, parameter2)
    else:
        print('Not readable. Please input "Lifetime", "Voltage", or "Jet Length" and the lower and upper ' \
        'bounds for those parameters, or "Perfect" or "Lift Off" or "Fracture" and whether you want to evaluate them first (defaulted to "no") ')
    return binnedPlumes

# INPUT: List of Plumes, String, Integer, Integer
# PURPOSE: Creates a list of numbers that runs concurrent to the list of plumes within
# OUTPUT: List of Integers, List of Plumes
def binPlumesIntoIntervals(plumes, parameter, amountInterval, interval):
    listOfListOfPlumes = []
    categoryOfPlumes = []
    
    binnedPlumes = binPlumes(plumes, parameter, 0, interval*(amountInterval+1))

    # Separate plumes into groups within a particular interval
    for i in range(amountInterval):     
        #listOfListOfPlumes.append(binPlumes(plumes, "Lifetime", interval*i, interval*(i+1)))
        listOfListOfPlumes.append(binPlumes(plumes, parameter, interval*i, interval*(i+1)))
        
    # Simplify the plumes by identifying them with the interval they are separated into
    for i in range(len(listOfListOfPlumes)):
        for plume in listOfListOfPlumes[i]:
            lowerBound = interval*i
            upperBound = interval*(i+1)
            categoryOfPlumes.append(f"{lowerBound:.4g} - {upperBound:.4g}")
            #categoryOfPlumes.append(interval*(i+1))

    if len(categoryOfPlumes) != len(binnedPlumes):
        print("Error: Intervals are insufficient to capture the range of parameter values within these plumes. Try increasing amountInterval or interval")

    return categoryOfPlumes, binnedPlumes

# INPUT: Plume, String
# PURPOSE: Returns the given parameter of the plume
# OUTPUT: Integer or Boolean (Depends on the value of parameter)
def returnMeanParam(plume, parameter):
    if parameter == "Lifetime":
        return plume.getLifeTime()
    elif parameter == "Voltage":
        return plume.getVoltage()
    elif parameter == "Jet Length":
        return plume.getJetHeight()
    elif parameter == "Perfect":
        return plume.getIsPerfect()
    elif parameter == "Lift Off":
        return plume.getIsLiftOff()
    elif parameter == "Fracture":
        return plume.getIsFracture()
    elif parameter == "Fracture Radius":
        return plume.getFractureRadius()
    elif parameter == "Plume Height":
        return plume.height
    elif parameter == "Plume Width":
        return plume.width
    elif parameter == "Laser":
        return plume.laser
    else:
        print("meanParam: Invalid. Please enter Lifetime, Voltage, Jet Length, Perfect, Lift Off, Fracture")


# INPUT: String
# PURPOSE: Reads the category and returns a default value determined by the code's author
# OUTPUT: Float
def returnDefaultIncrement(category):
    if category == "Lifetime":
        return 1000 #us
    elif category == "Voltage":
        return 0.1
    elif category == "Jet Length":
        return 100
    elif category == "Fracture Radius":
        return 20
    elif category == "Plume Height":
        return 275 #um
    elif category == "Plume Width":
        return 70 #um
    else:
        print("Category: Invalid. Please enter Lifetime, Voltage, Jet Length, or Fracture Radius")

# INPUT: List of Plumes, String, String
# PURPOSE: Look through a list of plumes and receive information about one of its parameters (meanParam) when related to discrete intervals of another parameter (category) 
# OUTPUT: DataFrame
def takeAverageResult(plumes, category, meanParam, increment): 
    global isExclusion
    categoryOfPlumes = []
    binnedPlumes = []
    #isExclusion = False
    #binExcludeVar1.set(0)
    try:
        increment = float(increment)
    except:
        increment = returnDefaultIncrement(category)
    try:
        #Amount intervals is an arbitrarily large number
        categoryOfPlumes, binnedPlumes = binPlumesIntoIntervals(plumes, category, 1000, increment)
        plumeCategorizedParams = []
        plumeMeanParams = []
        for i in range(len(binnedPlumes)):
            plume = binnedPlumes[i]
            plumeCategorizedParams.append(categoryOfPlumes[i])
            plumeMeanParams.append(returnMeanParam(plume, meanParam))
        category = f"{category} ({returnUnits(category)})"
        if returnIsMeasurable(meanParam):
            meanParam = f"{meanParam} ({returnUnits(meanParam)})"
        df = pd.DataFrame({category: plumeCategorizedParams, meanParam: plumeMeanParams})
        print(df)
        return df.groupby([category], sort=False).describe()
    except:
        messagebox.showerror(title="Increment too small", message="Increment you chose is too small for this parameter. This will fill up the screen.")
    

# INPUT: Integer
# PURPOSE: Returns "" or " not" as text to indicate that a list of plumes with maxContourLength has been analyzed before
# OUTPUT: String ("" or " not")
def returnAnalysisText(maxContourLength):
    analysisText = " not"
    if maxContourLength > 0:
        analysisText = ""  
    return analysisText

# INPUT: List of Plumes, String
# PURPOSE: Code that prints text displaying whether plumes have been analyzed or not
# OUTPUT: None
def buttonClickTemplate(plumes, plumeLabelText, plumesName = "untitled", isPlumesOfInterest = True, extraWord = ""):
    global plumesOfInterest
    global plumeLabel
    global plumesOfInterestName
    plumesOnTemplate = plumes
    if isPlumesOfInterest:
        plumesOfInterest = plumes
        plumesOfInterestName = plumesName
        plumesOnTemplate = plumesOfInterest
    #Check if these plumes have been analyzed before
    try:
        maxContourLength = returnMaxContourLength(plumesOnTemplate)
        analysisText = returnAnalysisText(maxContourLength)      
        plumesLength = len(plumesOnTemplate)
        plumeLabelTextTemplate = f"{plumesLength}{extraWord} Plumes {plumeLabelText}\nThese Plumes have{analysisText} been analyzed before."
        plumeLabel['text'] = plumeLabelTextTemplate
    except:
        if len(plumesOnTemplate) == 0:
            zeroText = "No Plumes were detected.\nThere's nothing else to do, please go back."
            plumeLabel['text'] = zeroText
        else:
            print("ERROR - buttonClickTemplate: Unknown error. Not from zero-size plumes. Please remove the try-catch in the method and investigate.")
    # plumeLabel = Label(window, text = plumeLabelTextTemplate)
    # plumeLabel.place(x = screenWidth*0.9 - screenWidth*0.45, y = screenHeight*0.9 - screenHeight*0.45)

# INPUT: List of Plumes, String, String, String
# PURPOSE: Saves inputted plumes and creates text saying that they have been saved. Makes checks to see if saving would work or not
# OUTPUT: None
def savePlumesForReal(plumes, directory, name, text):
    try: 
        savePlumes(plumes, directory, name)
        buttonClickTemplate(plumes, text, name, isPlumesOfInterest=False)
    except:
        messagebox.showerror(title="Directory or name invalid", message = "Either directory is an invalid directory or name has invalid characters. Please try again.")

# INPUT: String
# PURPOSE: Checks to see if the file ends with fileExtension
# OUTPUT: Boolean
def checkFileExtension(name):
    global fileExtension
    try:
        hasFileExtension = name.endswith(fileExtension)
        if hasFileExtension:
            return hasFileExtension
        else:
            messagebox.showerror(title="Invalid file", message=f"Invalid file. Please input a {fileExtension} file")
            return hasFileExtension
    except:
        messagebox.showerror(title="Invalid file", message=f"Invalid file. Please input a {fileExtension} file")
        return hasFileExtension

# INPUT: String
# PURPOSE: Takes in a parameter and returns the corresponding unit used in our experiment. "" otherwise.
# OUTPUT: String
def returnUnits(parameter):
    if parameter == "Lifetime":
        return "ns"
    elif parameter == "Voltage":
        return "V"
    elif parameter == "Fracture Radius" or parameter == "Jet Length" or parameter == "Plume Height" or parameter == "Plume Width":
        return "um" 
    else: 
        return ""
    
# INPUT: String
# PURPOSE: Returns whether a parameter is measurable 
# OUTPUT: Boolean
def returnIsMeasurable(parameter):
    return parameter in quantitativeParams
    #return parameter == "Jet Length" or parameter == "Lifetime" or parameter == "Voltage" or parameter == "Fracture Radius" or parameter 

# GUI + FRONT-END METHODS

# Create window + title
window = Tk()
window.title("Plume Analysis GUI")

# Window parameters - Sizes of widgets will be related to these two values for the sake of generalization
screenWidth = window.winfo_screenwidth()
screenHeight = window.winfo_screenheight()

# Set Windows size
window.geometry(f'{int(screenWidth*(0.9))}x{int(screenHeight*0.9)}')

# Scale up the text size
textScalar = screenWidth*0.0015
window.tk.call('tk', 'scaling', textScalar)

# GLOBAL PARAMETERS - VALUES TO BE SHARED ACROSS BUTTONS AND ACROSS PAGES

#The plumes variable that will be operated on in the GUI
plumesOfInterest = [] # -- > The current set of plumes that will undergo evaluations like analysis, saving, or binning. 
# A temporary plumesOfInterest for binning will be made in case the user wants to save a freshly binned set of plumes
plumesOfInterestName = "untitled" #This will be the name associated with the plumeOfInterest

#Back button value - Tracks what page we are on
#pageValue = [0,0,0] # Aside from pageArchive these parameters are useless - delete them when you're 100% sure you don't need them
# pageValueIndex = 0
# isAnalysisSubPage = False
pageArchive = [] #An array used for tracking which pages to print out when the back button is pressed

# Plume Label Panel
plumeLabelArchive = [] # An array used for tracking the main text on the GUI (called the plumeLabel)
binText = "" # A String used for the Bin Plumes button - which stores the parameter of interest of the user when binning and remembers it across pages
binText2 = ""
isBinningTwo = False
isExclusion = False

binnedPlumesOfInterest = [] # An array used for the Bin Plumes button - stores the list of Plumes that falls under
numberBins = 0
# the parameter bin/category that the user wants


# MAKE CHECKS FOR VALID FILES WITH AND WITHOUT THE FILE EXTENSION

# Function for when "load plumes" button is clicked. Will read the two entries below it and finds a corresponding pickle file containing Plumedata
def load_plume_clicked():
    directory = loadDirectoryEntry.get()
    name = loadNameEntry.get()
    if directory == "Enter Directory of Data" or name == "Enter Name of File":    
        messagebox.showinfo(title = "Loading", message = f"Loading Plumes... Please enter directory and filename")
    elif checkFileExtension(name):
        messagebox.showinfo(title = "Loading", message = f"Loading {name} from {directory}...")
        try:
            plumesOfInterest = loadPlumes(directory, name)
            plumeLabelText = f"\nloaded from file: {name}"
            buttonClickTemplate(plumesOfInterest, plumeLabelText, name)
        except:
            messagebox.showerror(title = "Error: Invalid directory", message = f"Either\n{directory}\nis not a valid directory or\n{name} \nis not an existing fileName. Please try again.")

# Function for when "create plumes" button is clicked. Will read the two directories below it and creates Plume Objects from the data directory. 
# Both directories will be tied to the plume object
def create_plume_clicked():
    directory = createDirectoryEntry.get()
    imgDirectory = createImgDirectoryEntry.get()
    if directory == "Enter Directory of Data" or imgDirectory == "Enter Directory of Images":
        messagebox.showinfo(title = "Creating", message = "Creating Plumes... Please enter the directory of your plume data")
    else: 
        userInput = messagebox.askquestion(title = "Creating", message = f"Creating Plumes from \n{directory}\n{imgDirectory}\nContinue?")
        if userInput == "yes":
            try:    
                plumesOfInterest = createPlumeList(directory, imgDirectory)
                plumeLabelText = f"created"
                buttonClickTemplate(plumesOfInterest, plumeLabelText)
            except:
                messagebox.showerror(title = "Error: Invalid directory", message = f"Either\n{directory}\n{imgDirectory}\nare not valid directories. Please try again.")
        #messagebox.showinfo(title = "Results", message = f"{len(plumes)}{plumes[-1].isFracture}")
        
# Function for when "save plumes" button is clicked. Will read the two entries below and creates a pickle file out of plumesOfInterest.
# PlumesOfInterest is expected to have plume data already.
def save_plume_clicked():
    save_plume_functionality(plumesOfInterest)

# INPUT: List of Plumes
# PURPOSE: Saves a list of Plumes into an epp file into a given directory under a given name
# OUTPUT: None
def save_plume_functionality(plumes, context = "Start Page"):
    global plumesOfInterest
    global binnedPlumesOfInterest
    directory = saveDirectoryEntry.get()
    name = saveNameEntry.get()
    if not name.endswith(fileExtension):
        name = name + fileExtension
    savingText = f"saved into\n{directory}\nas\n{name}"
    plumesSize = len(plumes)
    if plumesSize  == 0 and context == "Start Page":
        messagebox.showinfo(title= "No plumes loaded",message = "No Plumes to be saved. Please create or load Plumes before saving.")
    elif plumesSize == 0 and context == "Binning":
        messagebox.showinfo(title = "No plumes detected", message = "No plumes detected from binning. Nothing will be saved.")
    elif name == "Name the file" or directory == "Enter Directory of Data":
        messagebox.showerror(title = "No Name. No Directory",message = "Please name the file and directory.")
    else:
        userInput = messagebox.askquestion(title="Save the File?", message=f"Save {plumesSize} plumes into\n{directory}\nas a file named {name}?")
        if userInput == "yes":
            try:
                loadPlumes(directory, name)
                userInput = messagebox.askquestion(title = "FileName Already Exists?", message=f"It seems that {name} is already an existing file in {directory}.\nAre you sure you want to overwrite the file?")
                if userInput == "yes":
                    savePlumesForReal(plumes, directory, name, savingText)
                elif userInput == "no":
                    print("METHOD save_plume_clicked: Saving discontinued.")
            except:
                savePlumesForReal(plumes, directory, name, savingText)
        else:
            print("METHOD save_plume_clicked: Saving discontinued.")

# INPUT: none
# PURPOSE: Saves the currently binned list of Plumes 
# OUTPUT: None
def save_binned_plume_clicked():
    global binnedPlumesOfInterest
    save_plume_functionality(binnedPlumesOfInterest, context="Binning")

# INPUT: none
# PURPOSE: Displaces all widgets currently displayed. A helper function used for switching pages on the GUI
# OUTPUT: None
def hideWindow():
    for i in window.winfo_children():
        i.place_forget()

# INPUT: None
# PURPOSe: Switches to the Analysis Page of the GUI after reading the current plumesOfInterest
# OUTPUT: None
def analyze_plume_clicked():
    global plumesOfInterest
    global plumesOfInterestName
    global pageValue
    global plumeLabelArchive
    global pageArchive
    global pageValueIndex 
    if len(plumesOfInterest) == 0:
        messagebox.showinfo(message = "No Plumes to be analyzed. Please create or load Plumes before analysis.")
    else:
        userInput = messagebox.askquestion(title = "Analyzing", message = f"Analyzing {len(plumesOfInterest)} Plumes from the \n{plumesOfInterestName} file. Continue?")
        if userInput == "yes":
            #Will run an entirely different Python Window
            hideWindow() 
            #pageValue = [1,0,0]
            analysisText = f"from file:\n{plumesOfInterestName}\nare now under analysis"
            plumeLabelArchive.append(plumeLabel['text'])
            pageArchive.append(pageStart)
            buttonClickTemplate(plumesOfInterest, analysisText, plumesOfInterestName)
            placeSpecifiedWidgets(pageStartAnalysis)

# INPUT: None
# PURPOSE: Uncheck all boxes
# OUTPUT: None
def uncheckAllBoxes():
    global checkBoxList
    for checkBox in checkBoxList:
        checkBox.set(0)

# INPUT: None
# PURPOSE: Switches to the Analysis Page of GUI but now evaluating the recently binned Plumes
# OUTPUT None
def analyze_binned_plume_clicked():
    global plumesOfInterest
    global plumesOfInterestName
    global pageValue
    global plumeLabelArchive
    global pageArchive
    global pageValueIndex 
    global binnedPlumesOfInterest
    global binText
    if len(binnedPlumesOfInterest) == 0:
        messagebox.showinfo(message = "No Plumes detected. Nothing will be analyzed.")
    else:
        userInput = messagebox.askquestion(title = "Analyzing", message = f"Analyzing {len(binnedPlumesOfInterest)} binned plumes. Continue?")
        if userInput == "yes":
            setDefault()
            uncheckAllBoxes()
            setExclusive()
            #Will run an entirely different Python Window
            hideWindow() 
            #pageValue = [1,0,0]
            firstPage = pageArchive[0]
            firstLabel = f"{len(binnedPlumesOfInterest)} plumes from file:\n{plumesOfInterestName}\nare currently being evaluated."
            pageArchive = [firstPage]
            plumeLabelArchive = [firstLabel]
            analysisText = f"binned from file:\n{plumesOfInterestName}\nare now under analysis"
            #plumeLabelArchive.append(plumeLabel['text'])
            #pageArchive.append(pageStart)
            if returnIsMeasurable(binText):
                buttonClickTemplate(binnedPlumesOfInterest, analysisText, plumesOfInterestName)
            else:
                buttonClickTemplate(binnedPlumesOfInterest, analysisText, plumesOfInterestName, extraWord=f" {binText}")
            placeSpecifiedWidgets(pageStartAnalysis)


# INPUT: None
# PURPOSE: Goes to the page loaded prior to the current one. Hides all widget currently and replaces them with the most recent set of widgets.
# A previous page must have been in place before. In other words, global variable pageArchive and plumeLabelArchive must not be empty.
# OUTPUT: None
def back_button_clicked():
    global pageValue
    global pageValueIndex
    global pageArchive
    hideWindow()    
    setDefault()
    previousPage = pageArchive[-1]
    placeSpecifiedWidgets(previousPage)
    plumeLabel['text'] = plumeLabelArchive[-1]
    del plumeLabelArchive[-1]
    del pageArchive[-1]
    print(f"PLUME LABEL ARCHIVE: {plumeLabelArchive}")
    #print(pageValueIndex)

# INPUT: None
# PURPOSE: Empties out entry widgets and unchecks boxes if necessary
# OUTPUT: None
def setDefault():
    global binText
    global binText2
    global isBinningTwo
    global pageArchive
    text = binText
    if isBinningTwo and not returnIsMeasurable(binText):
        text = binText2
    elif isBinningTwo and returnIsMeasurable(binText) and returnIsMeasurable(binText2):
        upperEntry.delete(0, END)
        lowerEntry.delete(0, END)
        addPlaceHolder(upperEntry, f"Upper {binText}")  
        addPlaceHolder(lowerEntry, f"Lower {binText}")
        upperEntry2.delete(0, END)
        lowerEntry2.delete(0, END)
        addPlaceHolder(upperEntry2, f"Upper {binText2}")  
        addPlaceHolder(lowerEntry2, f"Lower {binText2}")
    upperEntry.delete(0, END)
    lowerEntry.delete(0, END)
    addPlaceHolder(upperEntry, f"Upper {text}")  
    addPlaceHolder(lowerEntry, f"Lower {text}")
    saveDirectoryEntry.delete(0, END)
    saveNameEntry.delete(0, END)
    addPlaceHolder(saveDirectoryEntry, saveDirectoryDefault)
    addPlaceHolder(saveNameEntry, saveNameDefault)    
    loadDirectoryEntry.delete(0, END)
    loadNameEntry.delete(0, END)
    loadDirectoryEntry.insert(0,"")
    loadNameEntry.insert(0, "")
    addPlaceHolder(loadDirectoryEntry, loadDirectoryDefault)
    addPlaceHolder(loadNameEntry, loadNameDefault)
    createDirectoryEntry.delete(0, END)
    createImgDirectoryEntry.delete(0, END)
    addPlaceHolder(createDirectoryEntry, createDirectoryDefault)
    addPlaceHolder(createImgDirectoryEntry, createImgDirectoryDefault)
    incrementEntry.delete(0, END)
    addPlaceHolder(incrementEntry, incrementEntryText)
    findPlumeEntry.delete(0, END)
    addPlaceHolder(findPlumeEntry, findPlumeEntryText)
    try:
        pageArchive.index(pageBin2)
    except:
        binTwoVar1.set(0)
    try:
        pageArchive.index(pageBin)
    except:
        try:
            pageArchive.index(pageBin2)
        except:
            binExcludeVar1.set(0)
    setExclusive()

def setExclusive():
    global binExcludeVar1
    global isExclusion
    if binExcludeVar1.get():
        isExclusion = True
        print("setExclusive: exclusive")
    else:
        isExclusion = False
        print("setExclusive: not exclusive")
    

# INPUT: None
# PURPOSE: Implementation not finished yet. 
# OUTPUT: None
def start_analysis_clicked():
    global plumesOfInterestName
    global plumesOfInterest
    userInput = messagebox.askquestion(title="Start Analysis.", message=f"Analyzing {len(plumesOfInterest)} Plumes from {plumesOfInterestName}. Continue?")
    if userInput == "yes":
        # Check if plumes have been analyzed before by checking if they have their contours
        buttonClickTemplate(plumesOfInterest, "will now be analyzed.")
        contourLength = returnMaxContourLength(plumesOfInterest)
        initDirectory = plumesOfInterest[0].directory
        file = filedialog.asksaveasfilename(initialdir=initDirectory, title = "Export Analyzed EPP file to where?", filetypes=(("EPP files", "*.epp*"), ("All files", "*.*")))
        if 0 < contourLength:
            # Rough implementation: If Plumes have been analyzed before, then don't skip the contours
            plumeAnalysis.createAnalysis(plumesOfInterest, evaluateLiftOff=True, evaluatePerfect=True, evaluateFracture=True)
        else:
            plumeAnalysis.createAnalysis(plumesOfInterest, skipContours=False, evaluateLiftOff=True, evaluatePerfect=True, evaluateFracture=True)
        if file:
            nameIndex = file.rfind(r"/")
            savePlumes(plumesOfInterest, file[:nameIndex], file[(nameIndex+1):] + ".epp")
            messagebox.showinfo(title="Exported data successfully", message=f"Plume data is exported to {file[:nameIndex]}\nwith EPP file {file[(nameIndex+1):]}.epp")
        buttonClickTemplate(plumesOfInterest, "have finished going through analysis.")

def placePlumeImage(plume, root):
    global plumeLabelX
    global plumeLabelY
    tempImg = os.path.join(plume.imageDirectory, f"{plume.name}.png")
    plumeImage = Image.open(tempImg)
    imageSize = screenWidth*0.40
    plumeImage.thumbnail((imageSize,imageSize))
    # plumeImage = plumeImage
    plumeImage = ImageTk.PhotoImage(plumeImage)
    # Create label
    plumeImageLabel = Label(root, image=plumeImage)
    plumeImageLabel.image = plumeImage
    xScalar = 3/4
    yScalar = 1/4
    plumeImageLabel.place(x = plumeLabelX*xScalar, y = plumeLabelY*yScalar)
    
    #plumeLabel["text"] = ""

def returnOptionalStat(condition, optionalStat, optionalStatName):
    units = returnUnits(optionalStatName)
    if condition:
        optionalText = f"\n{optionalStatName}: {optionalStat:.5g} {units}"
    else:
        optionalText = ""
    return optionalText

def placePlumeStats(plume, root):
    global screenWidth
    global screenHeight
    name = plume.name
    lifeTime = plume.lifeTime
    voltage = plume.voltage
    fracture = plume.isFracture
    fractureRadius = plume.fractureRadius
    liftOff = plume.isLiftOff
    jetLength = plume.jetHeight
    perfect = plume.isPerfect
    height = plume.height
    width = plume.width
    laser = plume.laser
    fractureRadiusText = returnOptionalStat(fracture, fractureRadius, "Fracture Radius")
    jetLengthText = returnOptionalStat(liftOff, jetLength, "Jet Length")
    statisticsText = f"Name: {name}\nLifetime: {lifeTime:.5g} ns\nVoltage: {voltage:.5g} V\nFracture: {fracture}{fractureRadiusText}\nLiftOff: {liftOff}{jetLengthText}\nPerfect Plume: {perfect}\nPlume Height: {height:.5g} um\nPlume Width: {width:.5g} um\nLaser: {laser}\nScale bar reads 200 um."
    xScalar = 1/15
    yScalar = 1/3
    placeX = xScalar*screenWidth
    placeY = yScalar*screenHeight
    statistics = Label(root, text=statisticsText)
    statistics.place(x = placeX, y = placeY)
    
def returnPlumeToFind():
    try:
        index = int(findPlumeEntry.get())
        plume = plumesOfInterest[index]
        return plume
    except:
        nameToFind = findPlumeEntry.get()
        for plume in plumesOfInterest:
            plumeName = plume.name
            if plumeName == nameToFind:
                return plume
        messagebox.showerror(title="Couldn't find", message="Couldn't find Plume. Either index entered is not an index, index is out of bounds, \nor name is invalid.\nExclude the file type if the name doesn't work.")
        return "ERROR"

def find_plume_enter_clicked():
    global plumesOfInterestName
    global plumesOfInterest
    global plumeLabel
    if findPlumeEntry.get() == findPlumeEntryText:
        messagebox.showerror(title="Enter Number or Name", message="Please enter an index or filename of the Plume you want to find.")
    else:
        plumeOfInterest = returnPlumeToFind()
        if plumeOfInterest == "ERROR":
            print("find plumes: invalid entry")
        else:
            plumeStatsWindow = Toplevel()
            plumeStatsWindow.geometry(f'{int(screenWidth*(0.9))}x{int(screenHeight*0.9)}')
            plumeStatsWindow.title("Plume Stats")
            placePlumeImage(plumeOfInterest, plumeStatsWindow)
            placePlumeStats(plumeOfInterest, plumeStatsWindow)
            plumeStatsWindow.mainloop()


# INPUT: None
# PURPOSE: Implementation not finished yet. 
# OUTPUT: None
def find_plumes_clicked():
    global plumesOfInterestName
    global plumesOfInterest
    global plumeLabel
    createNewPage(pageStartAnalysis, pageFindPlume, "are up for selection.\nPlease enter the index or the name of the\nPlume that you would like to find.")
    #messagebox.showinfo(message=f"Finding median plume of {len(plumesOfInterest)} plumes")
    tempImageName = "1743521811_000001800_000002072.png"
    # tempImg = r"P:\F250_len\F250_41mm_Pre_runSeries\images\Fast_Loading\1743521811_000001800_000002072.png"
    # #tempImg = r"C:\Users\mpsdgst7\Downloads\bella.jpg"
    # # tempImg = r"C:\Users\mpsdgst7\Downloads\20230907_114141.jpg"
    # plumeOfInterest = plumesOfInterest[int(len(plumesOfInterest)/2)]    # tempImg = os.path.join(plumeOfInterest.imageDirectory, f"{plumeOfInterest.name}.png")
    # # plumeImage = Image.open(tempImg)
    # # imageSize = screenWidth*0.40
    # # plumeImage.thumbnail((imageSize,imageSize))
    # # plumeImage = plumeImage
    # #plumeImage = ImageTk.PhotoImage(plumeImage)
    # plumeStatsWindow = Toplevel()
    # plumeStatsWindow.geometry(f'{int(screenWidth*(0.9))}x{int(screenHeight*0.9)}')
    # plumeStatsWindow.title("Plume Stats")
    # #placePlumeImage(plumeImage, plumeStatsWindow)
    # # Create label
    # # plumeImageLabel = Label(plumeStatsWindow, image=plumeImage)
    # # xScalar = 3/4
    # # yScalar = 1/4
    # # plumeImageLabel.place(x = plumeLabelX*xScalar, y = plumeLabelY*yScalar)
    # # plumeImageLabel.image = plumeImage
    # placePlumeImage(plumeOfInterest, plumeStatsWindow)
    # placePlumeStats(plumeOfInterest, plumeStatsWindow)
    # plumeStatsWindow.mainloop()
    # #plumeLabel.image = plumeImage
    
   # plumeImageLabel.pack(expand=1, fill=BOTH)

# INPUT: None
# PURPOSE: Implementation not finished yet. 
# OUTPUT: None
def correlate_data_clicked():
    global plumesOfInterest
    newText = "are currently for evaluation.\nPlease select two parameters to correlate with each other."
    createNewPage(pageStartAnalysis, pageCorrelateData, newText)
    #messagebox.showinfo(message=f"Please choose the independent variable")

# INPUT: None
# PURPOSE: Loads the Page pageBin. 
# OUTPUT: None
def bin_plumes_clicked():
    global isAnalysisSubPage
    global plumesOfInterest
    global plumesOfInterestName
    global pageValue
    global pageValueIndex
    #pageValue = [1,1,0]
    binningText = "are now being binned.\nPlease select which parameters to sort the Plumes by."
    plumeLabelArchive.append(plumeLabel['text'])
    pageArchive.append(pageStartAnalysis)
    buttonClickTemplate(plumesOfInterest, binningText, plumesOfInterestName)
    hideWindow()
    placeSpecifiedWidgets(pageBin)

# INPUT: Page (List of Widgets), Page, String
# PURPOSE: Updates the page to newPage and stores the currently replaced page
# OUTPUT: None
def createNewPage(previousPage, newPage, newText, isPlumesOfInterest = True, otherPlumes = [], keyword = ""):
    global plumesOfInterest
    global plumesOfInterestName
    global plumeLabelArchive
    global pageArchive
    plumeLabelArchive.append(plumeLabel['text'])
    pageArchive.append(previousPage)
    if isPlumesOfInterest:
        buttonClickTemplate(plumesOfInterest, newText, plumesOfInterestName, isPlumesOfInterest)
    else:
        buttonClickTemplate(otherPlumes, newText, isPlumesOfInterest=False, extraWord = keyword)
    hideWindow()
    try:
        placeSpecifiedWidgets(newPage)
    except:
        print(f"createNewPage: inputted page is not an existing page or something went wrong with the widgets. Please create one in widgetsList or input an existing one.")

# PAGE 1,1 methods
# INPUT: list of Plumes, String
# PURPOSE: Returns a list of a plume's parameter
# OUTPUT: List of Floats
def getParamList(plumes, parameter):
    parameterList = []
    if parameter == "Lifetime":
        for plume in plumes:
            parameterList.append(plume.lifeTime)
    elif parameter == "Voltage":
        for plume in plumes:
            parameterList.append(plume.voltage)
    elif parameter == "Jet Length":
        for plume in plumes:
            if not plume.jetHeight == 0:
               parameterList.append(plume.jetHeight)
    elif parameter == "Fracture Radius":
        for plume in plumes:
            if not plume.fractureRadius == 0:
                parameterList.append(plume.fractureRadius)
    elif parameter == "Plume Height":
        for plume in plumes:
            if not plume.height == 0:
                parameterList.append(plume.height)
    elif parameter == "Plume Width":
        for plume in plumes:
            if not plume.width == 0:
                parameterList.append(plume.width)
    else:
        print("ERROR getParamList: parameter is unrecognized")
    return parameterList

# INPUT: List of Plumes, String
# PURPOSE: Returns the median of the parameter list
# OUTPUT: Float
def getParameterMedian(plumes, parameter):
    parameterList = getParamList(plumes, parameter)
    #print(f"LENGTH {len(parameterList)}")
    if len(parameterList) == 0:    
        parameterMedian = 0
    else:
        parameterMedian = np.median(parameterList)
    return parameterMedian

# def returnIncludeOrExclude(parameter):
#     userInput = messagebox.askquestion(title=f"Include or Exclude {parameter}", message=f"Would you like exclude all {parameter} Plumes instead?\n(Click No to include all {parameter} plumes and click Yes to exclude them instead.)")
#     if userInput == "no":
#         return parameter
#     elif userInput == "yes":
#         return f"X-{parameter}"

def returnAltPage(variable, page1, page2):
    if variable.get() == 0:
        return page1
    elif variable.get() == 1:
        return page2

# INPUT: None
# PURPOSE: Turns the global variable binText into the selected parameter. Checks to see if the selected parameter on binList 
# is a measurable parameter and loads pageBinMeasurables if so. If not, it will find all Plumes that have the 
# selected parameter (marked as True) and loads a list of them as a temporary plumesOfInterest. 
# OUTPUT: None
def select_bin_parameter_clicked():
    global plumeLabel
    global binText
    global binText2
    global plumesOfInterestName
    global plumesOfInterest
    global binnedPlumesOfInterest
    global lowerText
    global upperText
    global isBinningTwo
    global isExclusion
    binText = binList.get(ANCHOR)
    binText2 = -1
    isBinningTwo = (binTwoVar1.get())
    isExclusion = (binExcludeVar1.get())
    lowerText = f"Lower {binText}"
    upperText = f"Upper {binText}"
    upperEntry.delete(0, END)
    lowerEntry.delete(0, END)
    addPlaceHolder(lowerEntry, lowerText)
    addPlaceHolder(upperEntry, upperText)
    page = returnAltPage(binTwoVar1, pageBin, pageBin2)
    # Check if the user wants to bin by two parameters
    if isBinningTwo:
        binText2 = binList2.get(ANCHOR) # Looks at list dedicated for second-option parameter
        if binText == binText2:
            # Case 0: Both are the same parameter
            # This is too redundant so we're going to tell the user to not pick that
            messagebox.showerror(title="Both options are the same", message="Please select two different options. The two parameters are the same.")
        elif returnIsMeasurable(binText) and returnIsMeasurable(binText2): 
            # Case 1: Both are quantitative
            # Produce a page with two entry boxes. The user will add the range of their two parameters here.
            # You might need to make a different widget for the select button
            print("Both are quantitative")
            lowerText = f"Lower {binText}"
            upperText = f"Upper {binText}"
            upperEntry.delete(0, END)
            lowerEntry.delete(0, END)
            addPlaceHolder(lowerEntry, lowerText)
            addPlaceHolder(upperEntry, upperText)
            lowerText2 = f"Lower {binText2}"
            upperText2 = f"Upper {binText2}"
            upperEntry2.delete(0, END)
            lowerEntry2.delete(0, END)
            addPlaceHolder(lowerEntry2, lowerText2)
            addPlaceHolder(upperEntry2, upperText2)
            binQuantitative(binText, plumesOfInterest, page, binMultipleQuantities=True, binText2 = binText2)
        elif returnIsMeasurable(binText) and not returnIsMeasurable(binText2):
            # Case 2: First is quantitative, second is qualitative
            # Produce prompt whether to include or exclude qualitative parameter
            # and then produce page asking the user for the range of their quantitative parameter
            print("First is quantitative, second is qualitative")
            #binText2 = returnIncludeOrExclude(binText2)
            lowerText = f"Lower {binText}"
            upperText = f"Upper {binText}"
            upperEntry.delete(0, END)
            lowerEntry.delete(0, END)
            addPlaceHolder(lowerEntry, lowerText)
            addPlaceHolder(upperEntry, upperText)
            binQuantitative(binText, plumesOfInterest, page)
        elif not returnIsMeasurable(binText) and returnIsMeasurable(binText2):
            # Case 3: First is qualitative, second is quantitative
            # Like Case 2, except there might be different versions
            # of the same widget (E.g. different select button or entry)
            print("Case 3: First is qualitative, second is quantitative")
            # IMPLEMENT binQuantitative into this
            #binText = returnIncludeOrExclude(binText)
            lowerText = f"Lower {binText2}"
            upperText = f"Upper {binText2}"
            upperEntry.delete(0, END)
            lowerEntry.delete(0, END)
            addPlaceHolder(lowerEntry, lowerText)
            addPlaceHolder(upperEntry, upperText)
            binQuantitative(binText2, plumesOfInterest, page)
        else:
            # Case 4: Both
            # Produce prompt whether to include or exclude parameter for both.
            # No need to create a separate page.
            # rewrite this considering the binParamsMultiple function instead
            print("Case 4")
            # binText = returnIncludeOrExclude(binText)
            # binText2 = returnIncludeOrExclude(binText2)
            # binnedPlumes, binText = binQualitative(binText, plumesOfInterest)
            # binnedPlumes, binText2 = binQualitative(binText2, binnedPlumes)
            binnedPlumes = binPlumesMultipleParam(plumesOfInterest, binText, binText2)
            if isExclusion:
                binText = f"Non-{binText} and Non-{binText2}"
            else:
                binText = f"{binText} and {binText2}"
            binnedPlumesOfInterest = binnedPlumes
            #print(len(binnedPlumes))
            binningResultsText = f"detected from \n {plumesOfInterestName}.\nThere are {len(plumesOfInterest)} Plumes in total."
            createNewPage(page, pageBinSave, binningResultsText, isPlumesOfInterest=False, otherPlumes=binnedPlumes, keyword = f" {binText}")
    else:
        if returnIsMeasurable(binText):
            # units = returnUnits(binText)
            # parameterMedian = getParameterMedian(plumesOfInterest, binText)
            # #print(parameterMedian)
            # binMeasurableText = f"will be sorted according to {binText}.\nPlease input the lower and upper bounds of the {binText}\nyou want the Plumes to be.\nThe Units are in {units}. \nThe median {binText} of the \n{plumesOfInterestName}\ndataset is: \n{parameterMedian:.4g} {units}"
            # createNewPage(page,pageBinMeasurables,binMeasurableText)
            binQuantitative(binText, plumesOfInterest, page)
        elif not returnIsMeasurable(binText):
            binnedPlumes, binText = binQualitative(binText, plumesOfInterest)
            binnedPlumesOfInterest = binnedPlumes
            #print(len(binnedPlumes))
            binningResultsText = f"detected from \n {plumesOfInterestName}.\nThere are {len(plumesOfInterest)} Plumes in total."
            createNewPage(page, pageBinSave, binningResultsText, isPlumesOfInterest=False, otherPlumes=binnedPlumes, keyword = f" {binText}")
    # else:
    #     binText = returnIncludeOrExclude(binText)
    #     binnedPlumes = binPlumes(plumesOfInterest, binText, 0, 0)
    #     binnedPlumesOfInterest = binnedPlumes
    #     #print(len(binnedPlumes))
    #     binningResultsText = f"detected from \n {plumesOfInterestName}.\nThere are {len(plumesOfInterest)} Plumes in total."
    #     createNewPage(page, pageBinSave, binningResultsText, isPlumesOfInterest=False, otherPlumes=binnedPlumes, keyword = f" {binText}")

def binQualitative(binText, plumes):
    global isExclusion
    #binText = returnIncludeOrExclude(binText)
    binnedPlumes = binPlumes(plumes, binText, 0, 0)
    if isExclusion:
        binText = f"Non-{binText}"
    else:
        binText = f"{binText}"
    return binnedPlumes, binText

# PRObLEM the lowerEntry and upperEntry read the first binText and not the second one even if the first is not measurables
def binQuantitative(binText, plumes, page, binMultipleQuantities = False, binText2 = ""):
    global isExclusion
    if isExclusion:
        labelText = "exclude"
    else:
        labelText = "be"
    units = returnUnits(binText)
    median = getParameterMedian(plumes, binText)
    if binMultipleQuantities and returnIsMeasurable(binText2):        
        units2 = returnUnits(binText2)
        median2 = getParameterMedian(plumes, binText2)
        binMeasurableText = f"will be sorted according to {binText}\nand {binText2}. Please input the lower and upper bounds of the \n{binText} and {binText2} you want the Plumes to {labelText}.\nThe units are in {units} and {units2} respectively.\nThe median {binText} and the median {binText2} of the \n{plumesOfInterestName}\ndataset is: \n{median:.4g} {units}\nand\n{median2:.4g} {units2}"
        createNewPage(page, pageBin2Measurables, binMeasurableText)
    else:    
        binMeasurableText = f"will be sorted according to {binText}.\nPlease input the lower and upper bounds of the {binText}\nyou want the Plumes to {labelText}.\nThe units are in {units}. \nThe median {binText} of the \n{plumesOfInterestName}\ndataset is: \n{median:.4g} {units}"
        createNewPage(page,pageBinMeasurables,binMeasurableText)





# MAKE CHECKS FOR WHEN LOWER AND UPPER VALUES ARENT FLOATS OR INTEGERS
# INPUT: None
# PURPOSE: Reads the lower and upper 
# OUTPUT: None
def enter_clicked():
    global binText
    global binText2
    global isBinningTwo
    global isExclusion
    global plumesOfInterestName
    global plumesOfInterest
    global binnedPlumesOfInterest
    #try:
    upper = float(upperEntry.get())
    lower = float(lowerEntry.get())
    units = returnUnits(binText)
    prevPage = pageBinMeasurables
    qualityKey= ""
    if isExclusion:
        binningResultsText = f"found outside {lower} and {upper} {units} in \n {plumesOfInterestName}. \nThere are {len(plumesOfInterest)} Plumes in total."
    else:
        binningResultsText = f"found within {lower} and {upper} {units} in \n {plumesOfInterestName}. \nThere are {len(plumesOfInterest)} Plumes in total."
    if isBinningTwo:
        if not returnIsMeasurable(binText):
            units = returnUnits(binText2)
            if isExclusion:
                qualityKey = f" Non-{binText}"
                binningResultsText = f"found outside {lower} and {upper} {units} in \n {plumesOfInterestName}. \nThere are {len(plumesOfInterest)} Plumes in total."
            else:
                qualityKey - f" {binText}"
            binnedPlumes = binPlumesMultipleParam(plumesOfInterest, binText, binText2, lower2 = lower, upper2 = upper)
        elif not returnIsMeasurable(binText2):
            if isExclusion:
                qualityKey = f" Non-{binText2}"
            else:
                qualityKey = f" {binText2}"
            binnedPlumes = binPlumesMultipleParam(plumesOfInterest, binText, binText2, lower1 = lower, upper1 = upper)
        else:
            upper2 = float(upperEntry2.get())
            lower2 = float(lowerEntry2.get())
            units2 = returnUnits(binText2)
            binnedPlumes = binPlumesMultipleParam(plumesOfInterest, binText, binText2, lower1 = lower, upper1 = upper, lower2 = lower2, upper2 = upper2)
            prevPage = pageBin2Measurables
            if isExclusion:
                binningResultsText = f"found with {binText} outside {lower} and {upper} {units} and \n{binText2} outside {lower2} and {upper2} {units2} in\n{plumesOfInterestName}. \nThere are {len(plumesOfInterest)} Plumes in total."
            else:
                binningResultsText = f"found with {binText} within {lower} and {upper} {units} and \n{binText2} within {lower2} and {upper2} {units2} in\n{plumesOfInterestName}. \nThere are {len(plumesOfInterest)} Plumes in total."
    else:
        binnedPlumes = binPlumes(plumesOfInterest, binText, lower, upper)     
    binnedPlumesOfInterest = binnedPlumes
    createNewPage(prevPage, pageBinSave, binningResultsText, isPlumesOfInterest=False, otherPlumes=binnedPlumes, keyword = qualityKey)    
        #print(len(binnedPlumes))
    # except:
    #     messagebox.showerror(title = "Invalid Values", message = "Entered values are not valid. Please input a number or value.")

# INPUT: List of String, Tk
# PURPOSE: Creates a list of Label widgets out of the values in the given row and places it into the root
# OUTPUT: List of Widgets
def convertRowOfValuesToWidget(row, root):
    widgetRow = []
    for item in row:
        widget = Label(root, text = item)
        widgetRow.append(widget)
    return widgetRow

# Parameters for the the window that pops up after correlate data is run.
# Most of these values except for newWindowStarts and newWindowEnds aren't really of use. They're mostly here as debugging tools. 
# Remove them if you would like.
newWindowXGap = int(screenWidth/16)
newWindowYGap = int(screenHeight/16)
newWindowXStart = int(screenWidth/30)
newWindowYStart = int(screenHeight/30)
newWindowXEnd = int(4*screenWidth/5)
newWindowYEnd = int(7*screenHeight/8)

def export_data_clicked():
    global plumesOfInterest
    x = independentParameterList.get(ANCHOR)
    y = dependentParameterList.get(ANCHOR)
    xUnits = f"({returnUnits(x)})"
    yUnits = ""
    dataX,dataY = getData(plumesOfInterest, x,y)
    if returnIsMeasurable(y):
        yUnits = f"({returnUnits(y)})"
    initDirectory = plumesOfInterest[0].directory
    file = filedialog.asksaveasfilename(initialdir=initDirectory, title = "Export CSV file of data to where?", filetypes=(("CSV files", "*.csv*"), ("All files", "*.*")))
    if file:
        with open(file+".csv", 'w', newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"{x} {xUnits}",f"{y} {yUnits}"])
            for i in range(len(plumesOfInterest)):
                xCell = dataX[i]
                yCell = dataY[i]
                writer.writerow([xCell, yCell])
        nameIndex = file.rfind(r"/")
        messagebox.showinfo(title="Exported data successfully", message=f"Raw data is exported to {file[:nameIndex]}\nas {file[(nameIndex+1):]}")

def plot_data_clicked():
    global plumesOfInterest
    matplotlib.use("TkAgg") #switch to a backend that allows matplotlib figures to be shown
    x = independentParameterList.get(ANCHOR)
    y = dependentParameterList.get(ANCHOR)
    xUnits = f"({returnUnits(x)})"
    yUnits = ""
    dataX,dataY = getData(plumesOfInterest, x,y)
    if returnIsMeasurable(y):
        yUnits = f"({returnUnits(y)})"
        plt.scatter(dataX,dataY, s=7)
        plt.title(f"{y} {yUnits} vs {x} {xUnits}")
        plt.xlabel(f"{x} {xUnits}")
        plt.ylabel(f"{y} {yUnits}")
        plt.show()
    else:
        binnedPlumes = binPlumes(plumesOfInterest, y)
        binnedDataX = getData(binnedPlumes, x,y)[0]
        plt.hist(dataX, ec = "white", label = f"All Plumes", bins=numberBins)
        plt.hist(binnedDataX, ec = "white", label=f"{y} Plumes", bins=numberBins)
        plt.xlabel(f"{x} {xUnits}")
        plt.ylabel("Amount of Plumes")
        plt.title(f"{x} {xUnits} histogram ")
        plt.legend()
        plt.show()
    matplotlib.use("agg") #switch back to a backend that doesn't allow matplotlib figures to be shown for memory allocation purposes
        



# INPUT: List of Widgets, Tk, interger, integer
# PURPOSE: Lays out a list of widgets in a row onto the root Tk window
# OUTPUT: None
def createRow(row, root, placeY = newWindowYStart, xGap = newWindowXGap):
    widgetRow = convertRowOfValuesToWidget(row, root)
    for i in range(len(widgetRow)):
        widget = widgetRow[i]
        widget.place(x = (newWindowXStart + xGap*i), y = placeY)

# INPUT: 2D Array of Widgets, Tk, String
# PURPOSE: Lays out list of widget rows as a table into the root Tk window
# OUTPUT: None
def createTable(rows, root, dependentLabel):
    global numberBins 
    numRows = len(rows)
    numCols = len(rows[0])
    xGapModified = (newWindowXEnd-newWindowXStart)/numCols#/numCols
    yGapModified = (newWindowYEnd-newWindowYStart)/numRows#/numRows
    dependentLabelStartX = newWindowXStart + xGapModified
    dependentLabelStartY = newWindowYStart/4
    dependentLabel.place(x = dependentLabelStartX,y = dependentLabelStartY)
    for i in range(numRows):
        row = rows[i]
        createRow(row, root, placeY = newWindowYStart + i*yGapModified, xGap = xGapModified)
    exportDataButton = Button(root, text = "Export Raw Data", command = export_data_clicked)
    exportDataButton.place(x = newWindowXEnd, y = newWindowYStart)
    #if measurable or not measurable:
    numberBins = numRows - 1
    plotButton = Button(root, text="Plot Data", command=plot_data_clicked)
    plotButton.place(x = newWindowXEnd, y = newWindowYStart + screenHeight/15)

# INPUT: String(?), String, String, Integer, Boolean 
# PURPOSE: Evaluates if the Stat given gives info about majority param or frequency of param and remodifies stat for the table.
# Stat and column must come from a pandas data table. Stat must also be concerned with a dependent parameter that is qualitative (E.g. Perfect, fracture, lift=off)
# OUTPUT: String
def checkForBooleanStat(stat, column, dependentText, count, tempTopStat):
    isBoolean = False
    if not returnIsMeasurable(dependentText):
        isBoolean = True
    if column == "top" and isBoolean:
        print("top accessed")
        if stat == "1":
            stat = f"{dependentText}"
        elif stat == "0":
            stat = f"Not {dependentText}"
    elif column == "freq" and isBoolean:
        print("freq accessed")
        stat = float(stat)
        count = float(count)
        if tempTopStat: 
            percent = 100*(stat/count)
        else:
            percent = 100*(1-(stat/count))
        stat = f"{percent:.3g}%"
    else:
        print("nothing accessed")
    return stat

# INPUT: Data Table, String, String
# PURPOSE: Recreate a data table onto a Tk window
# OUTPUT: None
def tableResult(result,x,y):
    #print(result) - Use for debugging 
    independent = result.axes[0].name
    independentValues  = result.axes[0]
    statsColumns = result.axes[1]
    dependentText = result.axes[1][0][0]
    columns = []
    stats = []
    for i in range(len(independentValues)):
        columns = [independent]
        tempStats = [independentValues[i]]
        count = result.values[i][0]
        for j in range(len(statsColumns)):
            stat = f"{result.values[i][j]:.5g}"
            column = statsColumns[j][1]
            tempTopStat = result.values[i][2] #Checks the column with the "top" statistic. Only works for qualitative parameters. Is disregarded in checkForBooleanStat otherwise.
            stat = checkForBooleanStat(stat, column, dependentText, count, tempTopStat)
            columns.append(column)
            tempStats.append(stat)
        stats.append(tempStats)  
    stats.insert(0, columns)
    tableWindow = Tk()
    tableWindow.title(f"Summary of {y} data with {x}")
    dependentLabel = Label(tableWindow, text=dependentText)
    tableWindow.geometry(f'{int(screenWidth*(0.9))}x{int(screenHeight*0.9)}')
    createTable(stats, tableWindow, dependentLabel)#, returnIsMeasurable(y))
    tableWindow.mainloop()

def assignParameter(plumes, param):
    values = []
    if param == "Lifetime":
        for plume in plumes:
            values.append(plume.lifeTime)
    elif param == "Voltage":
        for plume in plumes:
            values.append(plume.voltage)
    elif param == "Fracture":
        for plume in plumes:
            values.append(plume.isFracture)
    elif param == "Fracture Radius":
        for plume in plumes:
            values.append(plume.fractureRadius)
    elif param == "Lift Off":
        for plume in plumes:
            values.append(plume.isLiftOff)
    elif param == "Jet Length":
        for plume in plumes:
            values.append(plume.jetHeight)
    elif param == "Perfect":
        for plume in plumes:
            values.append(plume.isPerfect)
    elif param == "Plume Height":
        for plume in plumes:
            values.append(plume.height)
    elif param == "Plume Width":
        for plume in plumes:
            values.append(plume.width)
    elif param == "Laser":
        for plume in plumes:
            values.append(plume.laser)
    else:
        print("I Have nothing for you")
    return values


def getData(plumes, xParam, yParam):    
    xValues = assignParameter(plumes, xParam)
    yValues = assignParameter(plumes, yParam)
    return xValues,yValues

        

# INPUT: None
# PURPOSE: When the correlate button is clicked, create a dataset between the independent and dependent variables the user selected
# OUTPUT: None
def correlate_selected_clicked():
    global plumesOfInterest
    global plumeLabel
    x = independentParameterList.get(ANCHOR)
    y = dependentParameterList.get(ANCHOR)
    increment = incrementEntry.get()
    if not x and not y:
        messagebox.showerror(title = "Null Parameters", message = "No parameters selected. Please select from the list boxes your variables.")
    elif x == y:
        messagebox.showerror(title = "ERROR: Same Parameter", message="Cannot correlate the same parameters together. Please select something else.")
    elif not x:
        messagebox.showerror(title = "Null Independent", message="Please select an independent variable")
    elif not y:
        messagebox.showerror(title = "Null Dependent", message="Please select a dependent variable")        
    else: 
        plumeLabel['text'] = f"Table correlating \n{x}\nand\n{y}\ncreated!"
        try:
            # data = getData(plumesOfInterest, x, y)
            # print(f"X-Values: {data[0]}\nY-Values: {data[1]}")
            result = takeAverageResult(plumesOfInterest, x,y, increment)
            tableResult(result,x,y)
        except:
            print("ERROR: Out of bounds result")
        
# INPUT: Entry Widget, String
# PURPOSE: Inserts text into the entry widget as a placeholder for the user, which disappears and reappears 
# when the user clicks on and off the widget
# OUTPUT: None
# Reference: https://www.tutorialkart.com/python/tkinter/how-to-set-placeholder-for-entry-widget-in-tkinter-python/
def addPlaceHolder(entry, placeholder_text):
    # INPUT: event - MouseEvent
    # PURPOSE: When the mouse is clicked on the entry box, remove the placeholder text and let any inputted text be black
    # OUTPUT: None
    def on_entry_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, END)
            entry.configure(fg="black")

    # INPUT: event - MouseEvent
    # PURPOSE: When the mouse clicks off the entry box (after having clicked on it before), 
    # insert placeholder text if the entry box is empty
    def on_entry_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder_text)
            entry.configure(fg="gray")

    entry.insert(0, placeholder_text)
    entry.config(fg="grey")
    entry.bind("<FocusIn>", on_entry_focus_in)
    entry.bind("<FocusOut>", on_entry_focus_out)

# INPUT: float, String
# PURPOSE: Creates an entry box widget with a set width and functionality for placeholder text
# OUTPUT: Entry Widget
def createEntry(width, placeHolderText):
    entry = Entry(window, width = int(width))
    addPlaceHolder(entry, placeHolderText)
    return entry

def switchBinPage():
    #print(binTwoVar1)
    hideWindow()
    if binTwoVar1.get() == 1:
        placeSpecifiedWidgets(pageBin2)
    elif binTwoVar1.get() == 0:
        placeSpecifiedWidgets(pageBin)

# Entry box values
entryWidth = int(screenWidth*0.025)
entryHeight = int(screenHeight*0.001)

# Title 
titleLabel = Label(window, text="Plume Image Analysis - Start", font =("TkDefaultFont", int(screenWidth*0.0055)))
analysisTitleLabel = Label(window, text=f"Plume Image Analysis", font =("TkDefaultFont", int(screenWidth*0.0055)))
binTitleLabel = Label(window, text=f"Bin Plumes", font =("TkDefaultFont", int(screenWidth*0.0055)))

# OUTPUT
plumeLabel = Label(window, text = "Hello!\nPlease create or load a set of Plumes before analysis", compound='top')

# Buttons - MAKE BETTER NAMES

# PAGE 0
buttonWidth = int(screenWidth*0.022)
buttonHeight = int(screenHeight*0.0000001)
loadPlumeButton = Button(window, text = "Load a previous set of Plume Analysis Objects", command=load_plume_clicked, width=buttonWidth, height = buttonHeight)
createPlumeButton = Button(window, text = "Create a new set of Plume Analysis Objects", command = create_plume_clicked, width=buttonWidth)
savePlumeButton = Button(window, text = "Save current set of Plume Analysis Objects", command = save_plume_clicked, width = buttonWidth)
analyzePlumeButton = Button(window, text = "Analyze current set of Plume Analysis Objects", command = analyze_plume_clicked, width = buttonWidth)

# BACK BUTTON - ANALYSIS PAGES
backButton = Button(window,text = "Back", command = back_button_clicked, width = int(buttonWidth/2))

# PAGE 1
buttonWidth1 = int(buttonWidth/2)
binTwoVar1 = IntVar() 
binExcludeVar1 = IntVar()
checkBoxList = [binTwoVar1, binExcludeVar1]
startAnalysisButton = Button(window, text = "Start Analysis", command = start_analysis_clicked, width=buttonWidth1)
findPlumesButton = Button(window, text = "Find Plume", command= find_plumes_clicked, width=buttonWidth1)
correlateDataButton = Button(window, text = "Correlate the data", command= correlate_data_clicked, width=buttonWidth1)
binPlumesButton = Button(window, text = "Bin Plumes", command = bin_plumes_clicked, width=buttonWidth1)
binTwoCheck = Checkbutton(window, text = "Bin by two parameters",
                          variable=binTwoVar1, onvalue=1, offvalue=0, command=switchBinPage)
binExcludeCheck = Checkbutton(window, text = "Exclude Bin", 
                              variable=binExcludeVar1, onvalue=1, offvalue=0, command=setExclusive)
listScalar = 0.35

# Page 1,1
longWidth = int(screenWidth*0.0050)
binParameterOptions = ["Lifetime", "Voltage", "Fracture", "Fracture Radius", "Lift Off", "Jet Length", "Perfect", "Plume Height", "Plume Width", "Laser"]
binList = Listbox(window, selectmode="single",width=int(buttonWidth*listScalar),height=buttonHeight, font = ("TkDefaultFont", int(longWidth*(7/8))))
for item in binParameterOptions:
    binList.insert(END, item)
binList2 = Listbox(window, selectmode="single",width=int(buttonWidth*listScalar),height=buttonHeight, font = ("TkDefaultFont", int(longWidth*(7/8))))
for item in binParameterOptions:
    binList2.insert(END, item)
selectBinParamButton = Button(window, text = "Select", command = select_bin_parameter_clicked, width = buttonWidth1)

# Page 1,1,1
lowerText2 = ""
upperText2 = ""
if returnIsMeasurable(binText):
    print("Im measurable!")
    lowerText = f"Lower {binText}"
    upperText = f"Upper {binText}"
    if isBinningTwo and returnIsMeasurable(binText2):
        lowerText2 = f"Lower {binText2}"
        upperText2 = f" Upper {binText2}"
elif not returnIsMeasurable(binText):
    lowerText = f"Lower {binText2}"
    upperText = f"Upper {binText2}"

lowerEntry = createEntry(int(buttonWidth1), lowerText)
upperEntry = createEntry(int(buttonWidth1), upperText)
lowerEntry2 = createEntry(int(buttonWidth1), lowerText2)
upperEntry2 = createEntry(int(buttonWidth1), upperText2)
enterButton = Button(window, text = "Enter", command = enter_clicked, width = buttonWidth1)

# Page 1,1,2
saveBinnedPlumeButton = Button(window, text = "Save binned set of Plume Analysis Objects", command = save_binned_plume_clicked, width = buttonWidth)
analyzeBinnedPlumeButton = Button(window, text = "Analyze binned set of Plume Analysis Objects", command = analyze_binned_plume_clicked, width = buttonWidth)

# Page 1,2
independentText = Label(window, text = "Choose the independent variable", font =("TkDefaultFont", longWidth))
independentParameterOptions = ["Lifetime", "Voltage", "Fracture Radius", "Jet Length", "Plume Height", "Plume Width"]
dependentText = Label(window, text = "Choose the dependent variable", font =("TkDefaultFont", longWidth))
dependentParameterOptions = ["Lifetime", "Voltage", "Fracture", "Fracture Radius", "Lift Off", "Jet Length", "Perfect", "Plume Height", "Plume Width", "Laser"]
independentParameterList = Listbox(window, selectmode="single",width=int(buttonWidth*listScalar),height=buttonHeight, font=("TkDefaultFont", int(longWidth*(7/8))))
dependentParameterList = Listbox(window, selectmode="single",width=int(buttonWidth*listScalar),height=buttonHeight,  font=("TkDefaultFont", int(longWidth*(7/8))))
for item in independentParameterOptions:
    independentParameterList.insert(END, item)
for item in dependentParameterOptions:
    dependentParameterList.insert(END, item)
space = Label(window, text = "", width=0)
correlateSelectedButton = Button(window, text = "Correlate Selected", command = correlate_selected_clicked, width = buttonWidth1)
incrementEntryText = "(Optional) - Enter Increment for independent variable"
incrementEntry = createEntry(entryWidth, incrementEntryText)

# Page 1,3
findPlumeEntryText = "Enter Index or name of Plume"
findPlumeEntry = createEntry(entryWidth*(3/4), findPlumeEntryText)
findPlumeEnterButton = Button(window, text = "Enter", command = find_plume_enter_clicked, width = buttonWidth1)


# Entry Box - Directory

loadDirectoryDefault = "Enter Directory of Data"
loadDirectoryEntry = createEntry(entryWidth, loadDirectoryDefault)
loadNameDefault = "Enter Name of File"
loadNameEntry = createEntry(entryWidth, loadNameDefault)
createDirectoryDefault = "Enter Directory of Data"
createDirectoryEntry = createEntry(entryWidth, createDirectoryDefault)
createImgDirectoryDefault = "Enter Directory of Images"
createImgDirectoryEntry = createEntry(entryWidth, createImgDirectoryDefault)

# Entry Box  - Save
saveDirectoryDefault = "Enter Directory of Data"
saveDirectoryEntry = createEntry(entryWidth, saveDirectoryDefault)
saveNameDefault = "Name the file"
saveNameEntry = createEntry(entryWidth, saveNameDefault)



#Grid
screenCoordinateY = 6
screenCoordinateX = 2
entryIndent = screenWidth*0.01
startCoordinateX = screenWidth*0.01
startCoordinateY = screenHeight*0.01
yScalar = screenHeight*0.07
row = [0,1,2,3,4,5]
widgetsRow0 = [titleLabel,
               loadPlumeButton, 
               loadDirectoryEntry, 
               loadNameEntry,
               createPlumeButton, 
               createDirectoryEntry,
               createImgDirectoryEntry,
               savePlumeButton, 
               saveDirectoryEntry,
               saveNameEntry,
               analyzePlumeButton]

widgetsIndent0 = [entryIndent,
                0,
                entryIndent,
                entryIndent,
                0,
                entryIndent,
                entryIndent,
                0,
                entryIndent,
                entryIndent,
                0]

widgetsRow1 = [analysisTitleLabel,
               backButton,
               startAnalysisButton,
               findPlumesButton,
               correlateDataButton,
               binPlumesButton
               ]

widgetsIndent1 = [0,
                  0,
                  0,
                  0,
                  0,
                  0
                  ]

widgetsRow1_1 = [binTitleLabel,
                 backButton,
                 selectBinParamButton,
                 binTwoCheck,
                 binExcludeCheck,
                 binList]

widgetsIndent1_1 = [0,
                    0,
                    0,
                    entryIndent,
                    entryIndent,
                    0,
                    ]

widgetsRow1_1b = [binTitleLabel,
                 backButton,
                 selectBinParamButton,
                 binTwoCheck,
                 binExcludeCheck,
                 binList,
                 space,
                 space,
                 space,
                 binList2]

widgetsIndent1_1b = [0,
                    0,
                    0,
                    entryIndent,
                    entryIndent,
                    0,
                    -entryIndent,
                    -entryIndent,
                    -entryIndent,
                    0
                    ]

widgetsRow1_1_1 = [backButton,
                   lowerEntry,
                   upperEntry,
                   enterButton
                   ]

widgetsIndent1_1_1 = [0,
                      0,
                      0,
                      0
                      ]

widgetsRow1_1_1b = [backButton,
                    lowerEntry,
                    upperEntry,
                    space,
                    lowerEntry2,
                    upperEntry2,
                    enterButton]

widgetsIndent1_1_1b = [0,
                       0,
                       0,
                       0,
                       0,
                       0,
                       0
                       ]

widgetsRow1_1_2 = [backButton,
                   saveBinnedPlumeButton,
                   saveDirectoryEntry,
                   saveNameEntry,
                   analyzeBinnedPlumeButton]

widgetsIndent1_1_2 = [0,
                      0,
                      entryIndent,
                      entryIndent,
                      0]

widgetsRow1_2 = [backButton,
                 correlateSelectedButton,
                 independentText,
                 independentParameterList,
                 space,
                 incrementEntry,
                 #space,
                 dependentText,
                 dependentParameterList]

widgetsIndent1_2  = [0,
                     0,
                     0,
                     0,
                     -entryIndent,
                     entryIndent,
                     #0,
                     0,
                     0]

widgetsRow1_3 = [backButton,
                 findPlumeEntry,
                 findPlumeEnterButton]

widgetsIndent1_3 = [0,
                    0,
                    0]

# INPUT: List of Widgets, List of Integers
# PURPOSE: Will lay out all of the widgets row by row into the GUI
# OUTPUT: None
def placeWidgets(widgetsRow, widgetsIndent):
    for i in range(len(widgetsRow)):
        widget = widgetsRow[i]
        indent = widgetsIndent[i]
        #widget.place(x = 0, y = 50*i)

        #widget.place(x = 25 + indent, y = (65*i + 50))
        widget.place(x = startCoordinateX + indent, y = yScalar*i + startCoordinateY)

# INPUT: None
# PURPOSE: Places the plumeLabel widget 
# OUTPUT: None
plumeLabelX = screenWidth*0.9 - screenWidth*0.45
plumeLabelY = screenHeight*0.9 - screenHeight*0.55
def outputWidget():
    plumeLabel.place(x = plumeLabelX, y = plumeLabelY)

pageStart = [widgetsRow0, widgetsIndent0]
pageStartAnalysis = [widgetsRow1, widgetsIndent1]
pageBin = [widgetsRow1_1, widgetsIndent1_1]
pageBin2 = [widgetsRow1_1b, widgetsIndent1_1b]
pageBinMeasurables = [widgetsRow1_1_1, widgetsIndent1_1_1]
pageBin2Measurables = [widgetsRow1_1_1b, widgetsIndent1_1_1b]
pageBinSave = [widgetsRow1_1_2, widgetsIndent1_1_2]
pageCorrelateData = [widgetsRow1_2, widgetsIndent1_2]
pageFindPlume = [widgetsRow1_3, widgetsIndent1_3]
widgetsList = [pageStart, pageStartAnalysis, pageBin, pageBin2, pageBinMeasurables, pageBin2Measurables, pageBinSave, pageCorrelateData, pageFindPlume]


# INPUT: Page (list of Widget)
# PURPOSE: Finds the pageOfInterest in widgetsList and places all of its widgets
# OUTPUT: None
def placeSpecifiedWidgets(pageOfInterest):
    try:
        widgetsIndex = widgetsList.index(pageOfInterest)
    except:
        print("placeSpecifiedWidgets: pageOfInterest could not be found")
    specifiedPage = widgetsList[widgetsIndex]
    widgetsRow = specifiedPage[0]
    widgetsIndent = specifiedPage[1]
    outputWidget()
    placeWidgets(widgetsRow, widgetsIndent)
    print(f"NAME OF FILE: {plumesOfInterestName}")

#Place Start Screen Widgets
outputWidget()
placeWidgets(widgetsRow0, widgetsIndent0)

#Creates icon in window
#window.iconbitmap(bitmap=r'\\cfelm-ssuubNASa\massspec\Users\coop\Matthew_2025\Code\PlumeAnalysis\PlumeAnalysisGUI (Week 24+)\Week 46\eppFileImage.ico')
fileName = os.path.basename(__file__)
currentDir = __file__[:np.abs(len(__file__)-len(fileName))] 
#print(fileName)
#print(
icon = Image.open(os.path.join(currentDir, r'eppFileImage.ico'))
icon = ImageTk.PhotoImage(icon)
#window.iconbitmap(bitmap=os.path.join(currentDir, r'eppFileImage.ico'))
window.iconphoto(True, icon)
window.mainloop()
