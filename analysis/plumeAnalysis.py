# Generated from: Image_sorter_160326.ipynb
# Converted at: 2026-04-28T14:59:53.874Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import csv
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import time
import random
from scipy.optimize import curve_fit 
from IPython.display import clear_output
from plumeObject import Plume 
import pickle as pickle
import pandas as pd
import statistics

# #### Universal Params

matplotlib.use("agg") # Switches Matplotlib's backend to agg instead of tkinter. Helps with creating and saving figures while saving on memory.
pixelToMicrometre = 200/169.5 #200 um per 169.5 pixels
perfectPlumeDifferenceXValue = 50
perfectPlumeDifferenceYValue = 10
jetHeightThresholdDenominator = 12
requiredHeightMicro = 200
requiredHeight = requiredHeightMicro/pixelToMicrometre #Micrometre to pixel
contourDifferenceThreshold = 90
floor_denominator = 8
# Inspection zone
inspection_x = 457
inspection_w = 80

# #### Image Analysis Methods


# METHODS FOR IMAGE ANALYSIS

def getOverallAndInHighest(contours, inspectParam_x = inspection_x, inspectParam_w = inspection_w):
    in_highest= 3000
    overall_highest = 3000
    high_point = 0,0
    

    for i, contour in enumerate(contours):
        for point in contour:
            x = point[0][0]
            y = point[0][1]
            if(inspectParam_x < x < inspectParam_x + inspectParam_w):
                if(in_highest > y):
                    in_highest = y
            if(inspectParam_x - inspectParam_w < x < inspectParam_x + 2 * inspectParam_w):
                if(overall_highest > y):
                    overall_highest = y
    return (overall_highest,in_highest)


#INPUT: Integer (base_height_y) and Integer (in_highest). Both must be >= 0
#PURPOSE: Get the absolute difference between the base of the plume and the top of the plume and return the height
#OUTPUT: Integer (height) >= 0 
def getPlumeHeight(base_height_y, in_highest):
    height = np.abs(base_height_y - in_highest)
    return height



def getPlumeWidth50(contours,base_height_y,in_highest):
    plumeWidth50_left = 3000
    plumeWidth50_right = 0
    height = getPlumeHeight(base_height_y, in_highest)

    for i, contour in enumerate(contours):
        for point in contour:
            x = point[0][0]
            y = point[0][1]
                
            if(height > 60):
                if((height)/2 + in_highest + 20 > y > (height)/2 + in_highest):
                    if(plumeWidth50_left > x):
                        plumeWidth50_left = x
                    if(plumeWidth50_right < x):
                        plumeWidth50_right = x
        
    return (plumeWidth50_left,plumeWidth50_right)

def getIntersectDistances(ipl):      
    interscting_distance_list = []
    
    if len(ipl) > 0:
        sorted_ipl = sorted(ipl, key=lambda x: x[0])

        previous_x = sorted_ipl[0][0]
        for intersectingPoint in sorted_ipl:
            x = intersectingPoint[0]
            if(x != previous_x):
                interscting_distance_list.append(x - previous_x)
                previous_x = x
                
    return interscting_distance_list


def getIntersectCount(intersectDistances, pixelSeperation):     
    intersect_count =0  
    
    if intersectDistances is not None:
        intersect_count = 1
        
        for i in intersectDistances:
            if i > pixelSeperation:
                intersect_count += 1

    return intersect_count


def findBaseHeight(grayBubbleImage, inspection_x, seperation, threshold):     
    # Extract a 1D vertical strip of pixel values located "seperation" pixels to the left of the inspection area,
    # where the plume should not interfere.
    # Scan from the top down until a pixel with intensity below "threshold" is found — treat that position as the base of the plume.
    list_y = grayBubbleImage[:,inspection_x - seperation]
    for i in range(len(list_y)):
        if list_y[i] < threshold:
            base_height = i
            return base_height
        

        
def filterContours(contours, minArea, maxArea):     
    # Filter out contour based on their area
    filtered_contours = []
    # min_area = 150  # Get rid of specks of noise on the image
    # max_area = 50000 # Prevent detecting large unwanted structures
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if minArea < area < maxArea:
            filtered_contours.append(cnt)
    return filtered_contours


# INPUT: Integer, Integer, Integer, Contour, Integer, Integer, 2D array of integers (gives position of point)
# PURPOSE: Find whether point is located within a certain height of the plume (E.g. around 85% up the plume) and appends it to an Intersecting Points List (ipl)
# OUTPUT: none
def checkIntersectionInContour(percentage, base_height_y, in_highest, contour, x , y, ipl):
    height = getPlumeHeight(base_height_y, in_highest)
    fraction = (100 - percentage)/100
    if(in_highest + int(height*fraction) - 10 < y < in_highest + int(height*fraction)):
            cv2.circle(contour, (x, y), 3, (0, 0, 0), -1)
            ipl.append((x,y))

# INPUT: List of Contours (Which gives a list of positions)
# PURPOSE: Concatenate each contour into one big list
# OUTPUT: List of positions (list of 2D array of integers)
def joinContours(contours):
    joinedList = []
    for i in range(len(contours)):
        for j in range(len(contours[i])):
            x = int(contours[i][j][0][0])
            y = int(contours[i][j][0][1])
            joinedList.append([x,y])

    return joinedList


# INPUT: List of Contours (Which gives a list of positions)
# PURPOSE: Take each point of the contours and combine them into a list sorted by descending height
# OUTPUT: A list of points (list of 2D array of integers)
def sortPoints(contours):
    joinedList = []
    sortedList = []

    joinedList = joinContours(contours)

    sortedList = sorted(joinedList, key=lambda x:x[1])
    return sortedList


# INPUT: List of points (2D array of integers), integer, integer
# PURPOSE: Get a List of Points and filter out points that are below 90% height of the plume
# OUTPUT: List of Points
def get90PercentPlume(points, base_height_y, in_highest):
    ninetyPlume = []
    for i in range(len(points)):
        percentage = 90
        y = points[i][1]
        x = points[i][0]
        height = getPlumeHeight(base_height_y, in_highest) #Taken from Kenny Lai's code for checkIntersectionInContour. Feel free to modularize this bit.
        fraction = (100 - percentage)/100
        if( y < in_highest + int(height*fraction)):
            ninetyPlume.append([x,y])
        else:
            return ninetyPlume
    
    return ninetyPlume

# INPUT: List of points, integer, integer. points must be sorted through sortPoints(points)
# PURPOSE: Get the height of the jet. Iterate through the points until you meet the threshold.
# OUTPUT: integer (JetHeight)
def getJetHeight(points, base_height_y, in_highest):
    jetHeight = 0
    for i in range(len(points)):
        x = points[0][0]
        y = points[0][1]
        xBelow = points[i][0]
        yBelow = points[i][1]
        difference = float(np.abs(x - xBelow))
        height = getPlumeHeight(base_height_y, in_highest)
        threshold = height/jetHeightThresholdDenominator
        if(difference >= threshold):
            jetHeight = float(np.abs(y - yBelow))
            break

    return jetHeight

# INPUT: List of points 
# PURPOSE: Check if there is a tip formed at the top of the plume. Done by iterating down the plume and checking if horizontal neighbouring
# points are nearby (Making a tip) or far away (Not making a tip)
# OUTPUT: Boolean determining whether there is a jet or not 
def checkForJet(points, base_height_y, in_highest):
    sortedPoints = sortPoints(points)
    jetHeight = getJetHeight(sortedPoints, base_height_y, in_highest)
    sortedPoints = get90PercentPlume(sortedPoints, base_height_y, in_highest)
    heightOf90Percent = np.abs(sortedPoints[0][1] - sortedPoints[-1][1])
    diff = jetHeight - heightOf90Percent
    if(diff >= 0):
        return True
    else:
        return False

# INPUT: List of contours (List of 2d integer array), Boolean
# PURPOSE: Get points of the plume that are above 90% height of the plume and check if an elongation jet has formed at the top.
# OUTPUT: Boolean
def findLiftOffs(contours, valid, base_height_y, in_highest):
    #liftOffText = "Lift-Off present"
    isLiftOff = True
    if(valid):
        isJet = checkForJet(contours, base_height_y, in_highest)
        if not isJet:
            isLiftOff = False
    else:
        isLiftOff = False
    return isLiftOff

# INPUT: List of Contours (Must be 4d-array)
# PURPOSE: Locate the highest point (lowest y-value of the contour) of the plume and return it
# OUTPUT: List of integers (x-coordinate, y-coordinate)
def findTopPoint(contours):
    hsort = sortPoints(contours)
    xsorted = hsort[0][0]
    ysorted = hsort[0][1]
    return [xsorted, ysorted]

# INPUT: List of Contours, Boolean, Integer, Integer
# PURPOSE: Evaluate whether the Plume has fractures or have popped
# OUTPUT: Boolean
def checkFractures(contours, valid, base_height_y, in_highest):
    hasFractures = True
    if findLiftOffs(contours, valid, base_height_y, in_highest): #and findHoleFractures()
        hasFractures = True
    elif not contours:
        print("Contours list is empty")
    else:
        hasFractures = False
    return hasFractures

# INPUT: List of points 
# PURPOSE: Takes a contour and measures its length by iterating through each point and summing the distances between them
# OUTPUT: Integer
def calculateContourLength(contour):
    distance = 0
    for i in range(len(contour)-1):
            x = contour[i][0]
            y = contour[i][1]
            nextX = contour[i+1][0]
            nextY = contour[i+1][1]
            delta_x = x-nextX
            delta_y = y-nextY
            distance += np.sqrt(delta_x**2  + delta_y**2)
    return distance

# INPUT: List of points, List of points
# PURPOSE: Checks the difference between points of two contours and returns the smallest distance between them
# OUTPUT: Integer
def calculateDifferenceBetweenContours(contour1, contour2):
    #Iterate through contour1, and compare the difference between each point in contour2
    min_distance = np.inf
    for point1 in contour1:
        x1 = point1[0]
        y1 = point1[1]
        for point2 in contour2:
            x2 = point2[0]
            y2 = point2[1]
            delta_x = np.abs(x1-x2)
            delta_y = np.abs(y1-y2)
            distance = np.sqrt(delta_x**2 + delta_y**2)
            if distance < min_distance:
                min_distance = distance
    return min_distance

# INPUT: List of contours
# PURPOSE: Looks through contours and returns the longest contour
# OUTPUT: Contour (or a list of points)
def findLongestContour(contours):
    longestContour = []
    longestLength = 0
    for contour in contours: 
        distance = calculateContourLength(contour)
        if(distance >= longestLength):
            longestContour = contour
            longestLength = distance        
    return longestContour
        
# INPUT: Image, Contour
# PURPOSE: Places pale pink dots along the given contour. Is made if you want to track or single out a contour on an image.
# OUTPUT: None (void)
def mapContours(image, contour):
    # firstContour = contour[0]
    # lastContour = contour[-1]
    # cv2.circle(image, firstContour[0], 20, (200,200,200), -1)
    # cv2.circle(image, lastContour[0], 10, (200,200,0), -1)
    for i in range(len(contour)):
        currentContour = contour[i]
        for point in currentContour:
            cv2.circle(image, point,10, (255,0,0), -1)
    #return firstContour[0][1] <= lastContour[0][1]

# INPUT: List of Contours, Integer, Integer
# PURPOSE: Modifies contours so that points at the bottom are ignored.
# OUTPUT: List of Contours
def removeFloors(contours, base_height_y, in_highest):
    new_contours = []
    height = getPlumeHeight(base_height_y, in_highest)
    for contour in contours:
        #print(contour)
        new_contour = [] 
        for i in range(len(contour)):
            contour_y = contour[i][0][1]
            contour_x = contour[i][0][0]
            # print(contour_x, contour_y)
            # print(base_height_y)
            if contour_y < (base_height_y - (height/floor_denominator)):#5)):
                new_contour.append([contour_x, contour_y])
        if len(new_contour) != 0:
            new_contours.append(new_contour)
    #print(new_contours)
    return new_contours

# INPUT: Contour, Integer
# PURPOSE: Locates lowest or highest point in the contour and returns it. Param = 1 for bottom point, param = 2 for top point. 
# OUTPUT: Point (x-value, y-value)
def findTopOrBottomPoint(contour, param = 1):
    x = 0
    y = 0
    for point in contour:
        tempX = point[0]
        tempY = point[1]
        if param == 1:
            if(tempY >= y):
                x = tempX
                y = tempY
        elif param == 2:
            if(tempY <= y):
                x = tempX
                y = tempY
    return x, y

# INPUT: Contour, Point
# PURPOSE: Evaluates whether the contour goes around the outline of the Plume without breaking. Is evaluated as True if the lowest y-value is passed again at a 
# farther x-coordinate
# OUTPUT: Boolean
def isContourContinuous(contour, bottomPoint):
    bottomX,bottomY = bottomPoint
    #print(bottomX, bottomY)
    isContinuous = False
    for point in contour:
        x = point[0]
        y = point[1]
        differenceX = np.abs(x - bottomX)
        differenceY = np.abs(y - bottomY)
        if differenceY <= perfectPlumeDifferenceYValue and differenceX >= perfectPlumeDifferenceXValue:
            isContinuous = True
            return isContinuous
    return isContinuous

# INPUT: List of Contours, Contour
# PURPOSE: Modifies list of contours to exclude a contour (normally the longest contour).
# OUTPUT: List of Contours
def removeContour(contours, removeContour):
    for contour in contours:
        areTheSame = np.array_equal(contour, removeContour)
        if areTheSame:
            contours.remove(contour)
    return contours

# INPUT: List of Contours, Contour, Point
# PURPOSE: Goes through each contour in the list, append it to the longest contour, and then see if 
# that makes this new contour continuous
# OUTPUT: Contour (not actually a list) 
def reevaluateContour(contours, longestContour, bottomPoint):
    newList = longestContour
    for contour in contours:
        distance = calculateDifferenceBetweenContours(contour, longestContour)
        if distance <= contourDifferenceThreshold:
            # print(contour)
            # print(longestContour)
            newList = longestContour + contour
            if isContourContinuous(newList, bottomPoint):
                return newList
    return newList

# INPUT: Contour
# PURPOSE: Creates the bottom point
# OUTPUT: Point
def createBottom(contour):
    bottomPoint = []
    bottomX, bottomY = findTopOrBottomPoint(contour)
    bottomPoint.append(bottomX)
    bottomPoint.append(bottomY)
    return bottomPoint

# INPUT: Image, List of Contours, Boolean, Integer, Integer (idth i need the Image parameter?)
# PURPOSE: Evaluates if the plume on the image is a perfect plume
# OUTPUT: Boolean
def checkPerfectPlume(image, contours, valid, base_height_y, in_highest):
    # Check for fractures (don't have fracture functionality so far, just lift-off fractures right now)
    # Remove contours on the floor
    # Check for the longest contour
    # Check if the contour is continuous
    # If so, then the plume is a perfect plume
    bottomPoint = []
    mapList = []
    plumeHeight = getPlumeHeight(base_height_y, in_highest)
    hasFractures = checkFractures(contours, valid, base_height_y, in_highest)
    if not valid or hasFractures or plumeHeight <= requiredHeight:
        return False
    contours = removeFloors(contours, base_height_y, in_highest)
    #mapContours(image, contours)
    longestContour = findLongestContour(contours)
    contours = removeContour(contours, longestContour)
    bottomPoint = createBottom(longestContour)
    mapList.append(longestContour)
    #mapContours(image, mapList)
    isContinuous = isContourContinuous(longestContour, bottomPoint)
    #return isContinuous
    if not isContinuous:
        newContour = reevaluateContour(contours, longestContour, bottomPoint)
        list = []
        list.append(newContour)
        #mapContours(image, list)
        isContinuous = isContourContinuous(newContour, bottomPoint)
    return isContinuous

# INPUT: Plume
# PURPOSE: Obtains the Image of the Plume, grayscales it, resize it, and return it as a variable
# OUTPUT: Image
def getBubbleImageGrayScale(plume: Plume, isMeghanad = False):
    plumeName = plume.getName()
    imageDirectory = plume.getImageDirectory()
    if isMeghanad:
        plumeDirectory = os.path.join(imageDirectory, plumeName + ".bmp")
    else:
        plumeDirectory = os.path.join(imageDirectory, plumeName + ".png")
    bubble_image_gray =  cv2.imread(plumeDirectory, cv2.IMREAD_GRAYSCALE)
    #bubble_image_gray = cv2.resize(bubble_image_gray, (bubble_image_gray.shape[1] // 2, bubble_image_gray.shape[0] // 2), interpolation=cv2.INTER_AREA)
    try:
        bubble_image_gray = cv2.resize(bubble_image_gray, (bubble_image_gray.shape[1] // 2, bubble_image_gray.shape[0] // 2), interpolation=cv2.INTER_AREA)
    except:
        print("image not detected")
    return bubble_image_gray

# INPUT: Plume
# PURPOSE: Check if the Plume is valid (I.e. did not pop prematurely)
# OUTPUT: Boolean
def checkValidity(plume):
    contours = plume.getContours() 
    overall_highest, in_highest = getOverallAndInHighest(contours)
    bubble_image_gray = getBubbleImageGrayScale(plume)
    base_height_y = findBaseHeight(bubble_image_gray, inspection_x, 200, 30)
    valid = in_highest == overall_highest and getPlumeHeight(base_height_y, in_highest) > 40 and in_highest != 3000
    return valid


# INPUT: Plume
# PURPOSE: Checks the validity of a plume with custom derived parameters (E.g. contours, overall_highest, etc.)
def checkValidityLite(plume, contours, overall_highest, in_highest, bubble_image_gray, base_height_y):
    valid = in_highest == overall_highest and getPlumeHeight(base_height_y, in_highest) > 40 and in_highest != 3000
    return valid



# #### Plume Object Methods


# METHODS FOR PLUME SORTING AND CREATION - 21/7/25

# INPUT: Directory (as a String), Directory (as a String)
# PURPOSE: goes through the directory and creates plumes from the csv files in that directory 
# OUTPUT: List of Plumes
def createPlumeList(directory, imageDirectory):
    plumes = []
    files = os.listdir(directory)

    for file in files:
        # rows = []
        #print(files)
        if file.endswith(".csv"): #Only look at csv files. Ignore anything else.
            plumeName = file.strip(".csv")
            #print(plumeName)

            # csvFile = open(os.path.join(directory, file), "r")
            # read = csv.reader(csvFile)
            # for row in read: 
            #     rows.append(row)
            # dataRow = rows[1]
            #print(dataRow)
            # lifeTime = float(dataRow[1])
            # voltage = float(dataRow[2])

            plume = Plume(plumeName, directory, imageDirectory)#, lifeTime, voltage)
            plumes.append(plume)

    return plumes

# INPUT: List of Plumes, String
# PURPOSE: Finds a plume within a list of plume given its file name
# OUTPUT: Plume 
def findPlume(plumes, name):
    for plume in plumes:
        if name == plume.getName():
            return plume
    print("No plume detected. Please enter a valid file name for the plume.")    

# INPUT: Integer, Image, Plume
# PURPOSE: Applies a Gaussian blur to the image of acceptable plumes and filters out contours
# OUTPUT: None
def applyBlurAndFind(total_brightness, bubble_image_gray, plume):
    if total_brightness > 0:
        # Apply Gaussian blur to reduce noise of the image
        # Setting the size of the kernal
        kernalX = 5
        kernalY = 5
        # Set to zero to tell OpenCV to automatically calculatethe standard deviation for the X direction based on the kernal size
        sigmaX = 0
        bubble_blurred = cv2.GaussianBlur(bubble_image_gray, (kernalX, kernalY), sigmaX)
        # Applying Adaptive threshold
        bubble_thresh = cv2.adaptiveThreshold(
            bubble_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        # Detect contours
        # cv2.RETR_EXTERNAL mode return only the outermost contours
        # cv2.CHAIN_APPROX_NONE store all boundary points of the contour
        contours = cv2.findContours(bubble_thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)[0]
        # Filter out contour based on their area
        filtered_contours = filterContours(contours,minArea = 250, maxArea = 500000)
        plume.setContours(filtered_contours)

# INPUT: Plume
# PURPOSE: Create a list of contours of a given plume object and set the plume
# OUTPUT: None
def createContours(plume: Plume): #Functionality is adapted from Kenny_Final_image_sorter by Kenny Lai
    bubble_image_gray = getBubbleImageGrayScale(plume)
    total_brightness = bubble_image_gray.sum()
    # NOTE: TRY REPLACING THIS WITH THE METHOD ABOVE
    if total_brightness > 0:
        # Apply Gaussian blur to reduce noise of the image
        # Setting the size of the kernal
        kernalX = 5
        kernalY = 5
        # Set to zero to tell OpenCV to automatically calculatethe standard deviation for the X direction based on the kernal size
        sigmaX = 0
        bubble_blurred = cv2.GaussianBlur(bubble_image_gray, (kernalX, kernalY), sigmaX)
        # Applying Adaptive threshold
        bubble_thresh = cv2.adaptiveThreshold(
            bubble_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        # Detect contours
        # cv2.RETR_EXTERNAL mode return only the outermost contours
        # cv2.CHAIN_APPROX_NONE store all boundary points of the contour
        contours = cv2.findContours(bubble_thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)[0]
        # Filter out contour based on their area
        filtered_contours = filterContours(contours,minArea = 250, maxArea = 500000)
        plume.setContours(filtered_contours)

# INPUT: List of plumes
# PURPOSE: Iteratres through each plume in a list of plumes and creates their contours
# OUTPUT: None
def createContoursForAllPlumes(plumes):
    total = len(plumes)
    print("createContours: Looking for contours...")
    for i in range(len(plumes)):
        progress = float(i/total)*100
        plume = plumes[i]
        createContours(plume)
        print(f"createContours Progress: {progress:.4g}%")


# INPUT: Plume
# PURPOSE: Check if the Plume has a lift-off and update the plume's isLiftOff and jetLength parameters if so.
# OUTPUT: None
def evaluatePlumeLiftOffParameter(plume: Plume):
    # Setup variables
    bubble_image_gray = getBubbleImageGrayScale(plume)
    base_height_y = findBaseHeight(bubble_image_gray, inspection_x, 200, 30)
    contours = plume.getContours()
    sortedPoints = sortPoints(contours)
    in_highest = getOverallAndInHighest(contours)[1]
    valid = checkValidity(plume)
    # Evaluation
    liftOffTrue = findLiftOffs(contours, valid, base_height_y, in_highest)
    if liftOffTrue:
        plume.setIsLiftOff(True)
        jetLength = getJetHeight(sortedPoints, base_height_y, in_highest)*pixelToMicrometre
        plume.setJetLength(jetLength)
    else:
        plume.setIsLiftOff(False)
        plume.setJetLength(0)

# INPUT: Plume
# PURPOSE: Check if the Plume has a lift-off and update the plume's isLiftOff and jetLength parameters if so.
# OUTPUT: None
def evaluatePlumeLiftOffParameterLite(plume: Plume, base_height_y, contours, in_highest, valid):
    # Setup variables
    sortedPoints = sortPoints(contours)
    # Evaluation
    liftOffTrue = findLiftOffs(contours, valid, base_height_y, in_highest)
    if liftOffTrue:
        plume.setIsLiftOff(True)
        jetLength = getJetHeight(sortedPoints, base_height_y, in_highest)*pixelToMicrometre
        plume.setJetLength(jetLength)
    else:
        plume.setIsLiftOff(False)
        plume.setJetLength(0)

# INPUT: Plume
# PURPOSE: Check if the Plume is a "Perfect Plume" and update the plume's isPerfect parameter accordingly
# OUTPUT: None
def evaluatePlumePerfectParameter(plume: Plume):
    # Setup variables
    bubble_image_gray = getBubbleImageGrayScale(plume)
    base_height_y = findBaseHeight(bubble_image_gray, inspection_x, 200, 30)
    bubble_image_contour = cv2.cvtColor(bubble_image_gray, cv2.COLOR_GRAY2BGR)
    contours = plume.getContours()
    in_highest = getOverallAndInHighest(contours)[1]
    valid = checkValidity(plume)
    # Evaluation
    isPerfect = checkPerfectPlume(bubble_image_contour, contours, valid, base_height_y, in_highest)
    if isPerfect:
        plume.setIsPerfect(True)
    else:
        plume.setIsPerfect(False)

# INPUT: Plume
# PURPOSE: Check if the Plume is a "Perfect Plume" and update the plume's isPerfect parameter accordingly
# OUTPUT: None
def evaluatePlumePerfectParameterLite(plume: Plume, base_height_y, bubble_image_contour, contours, in_highest, valid):
    # Evaluation
    isPerfect = checkPerfectPlume(bubble_image_contour, contours, valid, base_height_y, in_highest)
    if isPerfect:
        plume.setIsPerfect(True)
    else:
        plume.setIsPerfect(False)

# INPUT: Integer, Integer, String
# PURPOSE: Prints output of plume evaluation process
# OUTPUT: None
def printProgress(index, total, parameter):
    progress = float(index/total)*100
    print(f"{parameter} Progress: {progress:.4g}%")

# INPUT: List of Plumes, String
# PURPOSE: Given a parameter, evaluate whether the plume has that parameter
# OUTPUT: None
def evaluateAllPlumesForParameter(plumes, parameter, skipContours = False, image = None): 
    total = len(plumes)
    if not skipContours:
        createContoursForAllPlumes(plumes)
    print(f"evaluateAllPlumesForParameter: Checking for {parameter}...")
    if parameter == "Lift Off":
        for i in range(len(plumes)):
            plume = plumes[i]
            evaluatePlumeLiftOffParameter(plume)
            printProgress(i, total, parameter)
    elif parameter == "Perfect":
        for i in range(len(plumes)):
            plume = plumes[i]
            evaluatePlumePerfectParameter(plume)
            printProgress(i, total, parameter)
    elif parameter == "Fracture":
        for i in range(len(plumes)):
            plume = plumes[i]
            evaluatePlumeFractureParameter(plume)
            printProgress(i, total, parameter)
    else:
        print('Parameter is not readable. Please input "Perfect" or "Lift Off" or "Fracture."')

# INPUT: Integer, integer, list, string 
# PURPOSE: Finds plumes whose given parameter is within the lower and upper bounds and returns them
# OUTPUT: List of Plumes
def returnPlumesWithinBoundary(lower, upper, plumes, parameter: str):
    sortedPlumes = []
    for plume in plumes:
        if parameter == "Lifetime":
            if lower < plume.getLifeTime() <= upper:
                sortedPlumes.append(plume)
        elif parameter == "Voltage":
            if lower < plume.getVoltage() <= upper:
                sortedPlumes.append(plume)
        elif parameter == "Jet Length":
            if lower < plume.getJetHeight() <= upper:
                sortedPlumes.append(plume)
        elif parameter == "Fracture Radius":
            if lower < plume.getFractureRadius() <= upper:
                sortedPlumes.append(plume)
        else:
            print('Parameter is not readable. Please enter "Lifetime", "Voltage", "Jet Length", "Fracture Radius" and the lower and upper bounds for those parameters')
            break
    return sortedPlumes

# INPUT: List of Plumes, String
# PURPOSE: Finds plumes that have the given parameter return them
# OUTPUT: List of plumes
def returnPlumesWithParameter(plumes, parameter):
    sortedPlumes = []
    for plume in plumes:
        if parameter == "Lift Off":
            if plume.getIsLiftOff():
                sortedPlumes.append(plume)
        elif parameter == "Perfect":
            if plume.getIsPerfect():
                sortedPlumes.append(plume)
        elif parameter == "Fracture":
            if plume.getIsFracture():
                sortedPlumes.append(plume)
    return sortedPlumes

# INPUT: List of Plumes, String, Integer (cond.), Integer (cond.), Boolean (cond.)
# PURPOSE: An automatic plume finder within a plume list. Ask for a plume with a given parameter or within a given constraint on said parameter.
# OUTPUT: List of Plumes

# NOTE: Updating the plume's parameters such as Lift Offs or Jet length is given through isEvaluated. If the plume has already been evaluated prior to running it through 
# binPlumes method, set isEvaluated to True when using it. If the plume hasn't, set isEvaluated to False (Note that this will drastically increase processing time).
# The default values on lower, upper, and isEvaluated will be run if they aren't defined in the method call.
# To change them simply add the values in sequence of the method call or manually assign it 
# (e.g. binPlumes(plumes, "Jet Length", lower = 2000, upper = 3000) or binPlumes(plumes, "Perfect", isEvaluated = False)).

def binPlumes(plumes, parameter: str, lower = 0, upper = 0, isEvaluated = True):
    binnedPlumes = []
    if parameter == "Lifetime" or parameter == "Voltage" or parameter == "Jet Length" or parameter == "Fracture Radius":
        if parameter == "Jet Length" and not isEvaluated:
            evaluateAllPlumesForParameter(plumes, "Lift Off")
        elif parameter == "Fracture Radius" and not isEvaluated:
            evaluateAllPlumesForParameter(plumes, "Fracture")
        binnedPlumes = returnPlumesWithinBoundary(lower, upper, plumes, parameter)
    elif parameter == "Perfect" or parameter == "Lift Off" or parameter == "Fracture":
        if not isEvaluated:
            evaluateAllPlumesForParameter(plumes, parameter)
        binnedPlumes = returnPlumesWithParameter(plumes, parameter)
    else:
        print('Not readable. Please input "Lifetime", "Voltage", or "Jet Length" and the lower and upper ' \
        'bounds for those parameters, or "Perfect" or "Lift Off" or "Fracture" and whether you want to evaluate them first (defaulted to "no") ')
    return binnedPlumes

# INPUT: List of Plumes, String, Integer
# PURPOSE: Takes user input to find plumes within a range of its parameter. 
# OUTPUT: List of Plumes
def binPlumesWithMeasurableValues(plumes, txt: str, paramNum: int):
    lower = int(input("Input the lowest " + txt))
    upper = int(input("Input the highest " + txt))
    if paramNum == 4 or paramNum == 7:
        isEvaluated = askForProcessing()
        binnedPlumes = binPlumes(plumes, txt, lower, upper, isEvaluated)
    binnedPlumes = binPlumes(plumes, txt, lower, upper)
    return binnedPlumes
    
# INPUT: None
# PURPOSE: Ask user for input on whether they want to process plumes
# OUTPUT: Boolean
def askForProcessing():
    shouldBeEvaluated = True
    choices = [1,2] 
    shouldProcess = int(input("Do you want to process your plumes (This may take a long time)? Input 1 for Yes. Input 2 for No."))
    while shouldProcess not in choices:
        print("ERROR: Number is neither 1 or 2. Please try again.")
        shouldProcess = int(input("Do you want to process your plumes (This may take a long time)? Input 1 for Yes. Input 2 for No."))
    if shouldProcess == 1:
        shouldBeEvaluated = False
    elif shouldProcess == 2:
        shouldBeEvaluated = True
    return shouldBeEvaluated

# INPUT: List of Plume
# PURPOSE: Ask user for input for plume that meet the range given also via user input
# OUTPUT: List of Plume
def binPlumesWithUserInput(plumes):
    binnedPlumes = []
    choices = [1,2,3,4,5]
    txt = ''
    shouldBeEvaluated = True
    parameter = int(input("Press 1 to bin with Lifetime \nPress 2 to bin with Pulse Voltage \nPress 3 to bin by Lift-Off fractures \nPress 4 to bin by Jet Length \n" \
        "Press 5 to bin by Perfect Plumes \nPress 6 to bin with Hole fractures \nPress 7 to bin by Hole Fracture Radius"))
    while parameter not in choices:
        print("Number is out of bounds. Please try again.")
        parameter = int(input("Press 1 to bin with Lifetime \nPress 2 to bin with Pulse Voltage \nPress 3 to bin by Lift-Off fractures \nPress 4 to bin by Jet Length \n" \
        "Press 5 to bin by Perfect Plumes \nPress 6 to bin with Hole fractures \nPress 7 to bin by Hole Fracture Radius"))
    if parameter == 1:
        txt = "Lifetime"
    elif parameter == 2:
        txt = "Voltage"
    elif parameter == 3:
        txt = "Lift Off"
    elif parameter == 4:
        txt = "Jet Length"
    elif parameter == 5:
        txt = "Perfect"
    elif parameter == 6:
        txt = "Fracture"
    elif parameter == 7:
        txt = "Fracture Radius"
    if parameter == 1 or parameter == 2 or parameter == 4 or parameter == 7:
        binnedPlumes = binPlumesWithMeasurableValues(plumes, txt, parameter)
    elif parameter == 3 or parameter == 5 or parameter == 6:
        shouldBeEvaluated = askForProcessing()
        binnedPlumes = binPlumes(plumes, txt, isEvaluated = shouldBeEvaluated)
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
            categoryOfPlumes.append(interval*(i+1))

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
    else:
        print("meanParam: Invalid. Please enter Lifetime, Voltage, Jet Length, Perfect, Lift Off, Fracture")


# INPUT: List of Plumes, String, String
# PURPOSE: Look through a list of plumes and receive information about one of its parameters (meanParam) when related to discrete intervals of another parameter (category) 
# OUTPUT: DataFrame
def takeAverageResult(plumes, category, meanParam): 
    categoryOfPlumes = []
    binnedPlumes = []

    if category == "Lifetime":
        categoryOfPlumes, binnedPlumes = binPlumesIntoIntervals(plumes, "Lifetime", 10, 1000)
        print(len(categoryOfPlumes), len(binnedPlumes))
    elif category == "Voltage":
        categoryOfPlumes, binnedPlumes = binPlumesIntoIntervals(plumes, "Voltage", 10, 0.2)
        print(len(categoryOfPlumes), len(binnedPlumes))
    elif category == "Jet Length":
        categoryOfPlumes, binnedPlumes = binPlumesIntoIntervals(plumes, "Jet Length", 15, 100)
        print(len(categoryOfPlumes), len(binnedPlumes))
    elif category == "Fracture Radius":
        categoryOfPlumes, binnedPlumes = binPlumesIntoIntervals(plumes, "Fracture Radius", 100, 30)
    else:
        print("Category: Invalid. Please enter Lifetime, Voltage, Jet Length, or Fracture Radius")


    plumeNames = []
    plumeCategorizedParams = []
    plumeMeanParams = []
    for i in range(len(binnedPlumes)):
        plume = binnedPlumes[i]
        plumeNames.append(plume.getName())
        plumeCategorizedParams.append(categoryOfPlumes[i])
        plumeMeanParams.append(returnMeanParam(plume, meanParam))

    df = pd.DataFrame({category: plumeCategorizedParams, meanParam: plumeMeanParams}, index = plumeNames)
    return df.groupby([category]).describe()

# INPUT: List of Plumes, String, String
# PURPOSE: Create a file with directory and save a list of Plumes into that file through pickle
# OUTPUT: None
# Note: Try looking to streamline the file naming process
def savePlumes(plumes, directory, fileName):
    file = open(os.path.join(directory, fileName), "wb")
    pickle.dump(plumes, file)

# INPUT: String, String
# PURPOSE: Load a list of Plumes through pickle. The method takes in the directory of the file and the file's name as two separate parameters
# OUTPUT: List of Plumes
def loadPlumes(directory, fileName):
    file = open(os.path.join(directory, fileName), "rb")
    return pickle.load(file)

# INPUT: String, String
# PURPOSE: Copies a saved plumeList file onto a new object. Useful when adding a new parameter to the PlumeObject file, which won't update plumes loaded from a plume file.
# IMPORTANT: MAKE SURE THAT WHEN YOU ADD A PLUME PARAMETER TO SET A DEFAULT VALUE TO SAID PARAMETER IN THE INSTANTIATION AS THE LOADED PLUMEFILE WON'T KNOW HOW TO GET THIS NEW PARAMETER
# OUTPUT: List of Plumes
def copyPlumes(directory, fileName):
    oldPlumes = loadPlumes(directory, fileName)
    newPlumes = []
    for oldPlume in oldPlumes:
        name = oldPlume.getName()
        directory = oldPlume.getDirectory()
        imageDirectory = oldPlume.getImageDirectory()
        lifeTime = oldPlume.getLifeTime()
        voltage = oldPlume.getVoltage()
        contours = oldPlume.getContours()
        isFracture = oldPlume.getIsFracture()
        fractureRadius = oldPlume.getFractureRadius()
        isLiftOff = oldPlume.getIsLiftOff()
        jetHeight = oldPlume.getJetHeight()
        isPerfect = oldPlume.getIsPerfect()
        height = oldPlume.height
        width = oldPlume.width
        newPlume = Plume(name, directory, imageDirectory, contours, isFracture, fractureRadius, isLiftOff, jetHeight, isPerfect, height, width) #IMPORTANT: THIS LINE
        newPlumes.append(newPlume)
    return newPlumes


# #### createAnalysis Methods


# INPUT: Plume
# PURPOSE: Gets the corresponding csv file and returns the MISSING parameters that weren't part of the plume object instantiation
# OUTPUT: List of Floats
def getCsvElements(plume):
    rows = []
    name = plume.getName()
    directory = plume.getDirectory()
    file = os.path.join(directory, (name + ".csv"))
    csvFile = open(file, "r")
    read = csv.reader(csvFile)
    for row in read: 
        rows.append(row)
    dataRow = rows[1]
    setDelay = float(dataRow[0]) #ns
    q1c = float(dataRow[3]) 
    lensFocalLength = float(dataRow[4]) #mm
    lensHeight = float(dataRow[5]) #mm
    pressure = float(dataRow[6]) #mbar
    pulse_voltage = float(dataRow[7]) #V
    return setDelay, q1c, lensFocalLength, lensHeight, pressure, pulse_voltage

# INPUT: Plume
# PURPOSE: Returns all of the parameters of the plume
# OUTPUT: String, String, String, Float, Boolean, Float, Boolean, Boolean, Float 
def getParams(plume):
    name = plume.getName()
    directory = plume.getDirectory()
    imageDirectory = plume.getImageDirectory()
    lifetime = plume.getLifeTime()
    voltage = plume.getVoltage()
    isLiftOff = plume.getIsLiftOff()
    jetLength = plume.getJetHeight()
    isPerfect = plume.getIsPerfect()
    isFracture = plume.getIsFracture()
    fractureRadius = plume.getFractureRadius()
    return name, directory, imageDirectory, lifetime, voltage, isLiftOff, jetLength, isPerfect, isFracture, fractureRadius

# INPUT: Plume, Boolean
# PURPOSE: Gets parameters of the plume that are obtained within the image and are not saved as a parameter
# OUTPUT: Image, List of Contours, Integer, Integer, Integer, Integer, Integer
def deriveParams(plume, isMeghanad = False):
    bubble_image_gray = getBubbleImageGrayScale(plume, isMeghanad)
    bubble_image_contour = cv2.cvtColor(bubble_image_gray, cv2.COLOR_GRAY2BGR)
    contours = plume.getContours()
    base_height_y =  findBaseHeight(bubble_image_gray, inspection_x, 200, 30)
    overall_highest,in_highest = getOverallAndInHighest(contours)
    plumeWidth50_left,plumeWidth50_right = getPlumeWidth50(contours,base_height_y,in_highest)
    return bubble_image_contour, contours, base_height_y, overall_highest, in_highest, plumeWidth50_left, plumeWidth50_right

# INPUT: Image, Integer, Integer, Integer, Integer, Integer, Integer, Integer
# PURPOSE: Draws Lines onto the Plume image; Areas of inspection, outer areas of inspection, plume width, plume height
# OUTPUT: None
def drawInspectionArea(bubble_image_contour, inspection_x, inspection_w, plumeWidth50_left, plumeWidth50_right, overall_highest, in_highest, base_height_y):
    cv2.rectangle(bubble_image_contour, (inspection_x, 0), (inspection_x + inspection_w, 2448), (0,0,0), 2)
    cv2.rectangle(bubble_image_contour, (inspection_x-inspection_w, 0), (inspection_x + 2*inspection_w, 2448), (34,125,0), 2)
    cv2.line(bubble_image_contour, (inspection_x + inspection_w+100, base_height_y), (inspection_x + inspection_w+100, overall_highest), (23,53,23), 2)
    cv2.line(bubble_image_contour, (inspection_x + inspection_w+100, base_height_y), (inspection_x + inspection_w+100, in_highest), (255,0,0), 2)
    cv2.line(bubble_image_contour, (plumeWidth50_left, base_height_y), (plumeWidth50_right, base_height_y), (255,53,255), 2)

# INPUT: String, Image, String, String
# PURPOSE: Adds the Plume image into a specified "folderTag" (If the folderTag is "fracture" or "lift off" then the Plume 
# added would have fractures or lift-offs respectively. If the folderTag is "analysis" then the Plume is added by default).   
# OUTPUT: None
def savePlumeImageIntoDirectory(folderTag, 
                               bubble_image_contour, imageDirectory, plumeName):
        plt.figure(figsize=(8, 8))
        plt.imshow(bubble_image_contour)
        plt.title(plumeName)
        plt.axis("off")             
        os.makedirs(os.path.join(imageDirectory,folderTag), exist_ok=True)
        plt.savefig(os.path.join(imageDirectory,folderTag, plumeName))
        #clear_output(wait=False)
        #plt.show(block=False) 
        #plt.pause(0.5)
        plt.close('all')


# INPUT: (Sighs) String, String, String, Integer, Integer, Integer, Integer, Integer, Integer, Float, Float, Float, 
# Float, String, Float, Float, Boolean, Boolean, Integer, List of Integer, List of Integer, List of Integer
# PURPOSE: Writes down the Plume's parameters into a csv file and saves it into a specified folderTag
# OUTPUT: None
def savePlumeIntoDirectory(folderTag, fileName, directory, setDelay,lifetime,voltage,q1c,lensFocalLength,lensHeight,pressure,pulse_voltage, jetLength, fractureRadius,text, height, width,isHeightValid, isWidthValid, intersect_count,
                               idl_90, idl_85, idl_80):
    fileName = fileName.split(".")[0]
    os.makedirs(os.path.join(directory,folderTag), exist_ok=True)
    with open(os.path.join(directory,folderTag,fileName+".csv"), mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Set Delay(ns)" ,"True Delay(ns)",	 "Voltage(V)",	 "q1c",	 "lens focal length(mm)",	 "lens height(mm)",	 "pressure(mbar)",	 "Pulse Voltage (V)", "Jet Length (um)", "Fracture Radius (um)"])
        writer.writerow([setDelay,lifetime,voltage,q1c,lensFocalLength,lensHeight,pressure,pulse_voltage, jetLength, fractureRadius])
        writer.writerow(["State", "Height", "Width","Height Valid", "Width Valid","Intersect Count"])  # This adds a new row
        writer.writerow([text, height, width,isHeightValid, isWidthValid, intersect_count])  # This adds a new row
        writer.writerow(["Intersect Distance List (90% Height)"])  # This adds a new row
        writer.writerow(idl_90) 
        writer.writerow(["Intersect Distance List (85% Height)"])  # This adds a new row
        writer.writerow(idl_85) 
        writer.writerow(["Intersect Distance List (80% Height)"])  # This adds a new row
        writer.writerow(idl_80) 




# INPUT: List of Plumes, Boolean, Boolean, Boolean, Boolean
# PURPOSE: Goes through each plume in a list, and prints out an analyed image and saves it and its corresponding csv file
# OUTPUT: None
# Add functionality for evaluating parameters and updating them (e.g. jet length)
def createAnalysis(plumes, skipContours = True, evaluateLiftOff = False, evaluatePerfect = False, evaluateFracture = False, evaluateParameter = False):
    total_count = len(plumes)
    current_index = 0
    #jetHeights = []
    if not skipContours:
        createContoursForAllPlumes(plumes)
    if evaluateLiftOff:
        evaluateAllPlumesForParameter(plumes, "Lift Off", skipContours=True)
    if evaluatePerfect:
        evaluateAllPlumesForParameter(plumes, "Perfect", skipContours=True)
    if evaluateFracture:
        evaluateAllPlumesForParameter(plumes, "Fracture", skipContours=True) 
    if evaluateParameter:
        evaluateAllPlumesForParameter(plumes, "Your Parameter", skipContours=True)
    print("Starting Post-Processing...")
    for plume in plumes:
        print("current index = " + str(current_index))
        print("progress: " + str(((current_index + 1)/total_count)*100) + "%")
        #make its own method
        #Plume object params
        name, directory, imageDirectory, lifetime, voltage, isLiftOff, jetLength, isPerfect, isFracture, fractureRadius = getParams(plume)
        # Derived Params
        bubble_image_contour, contours, base_height_y, overall_highest, in_highest, plumeWidth50_left, plumeWidth50_right = deriveParams(plume)
        # Validity
        valid = checkValidity(plume)
        #Csv params
        setDelay, q1c, lensFocalLength, lensHeight, pressure, pulse_voltage = getCsvElements(plume)

        interscting_points_list_85 = []
        interscting_points_list_80 = []
        interscting_points_list_90 = []

        #make its own method
        for contour in contours:
            cv2.drawContours(bubble_image_contour, [contour], -1, (random.randint(0,255), random.randint(0,255), random.randint(0,255)), 2)
            for point in contour:
                #make its own method
                x = point[0][0]
                y = point[0][1]

                checkIntersectionInContour(85, base_height_y, in_highest, bubble_image_contour, x, y, interscting_points_list_85)
                checkIntersectionInContour(80, base_height_y, in_highest, bubble_image_contour, x, y, interscting_points_list_80)
                checkIntersectionInContour(90, base_height_y, in_highest, bubble_image_contour, x, y, interscting_points_list_90)

        # list consist of the horizontal distances between sucessive intersecting points
        idl_85 = getIntersectDistances(interscting_points_list_85)
        idl_80 = getIntersectDistances(interscting_points_list_80)
        idl_90 = getIntersectDistances(interscting_points_list_90)

        intersect_count = getIntersectCount(idl_85,7)

        #make its own method
        drawInspectionArea(bubble_image_contour, inspection_x, inspection_w, plumeWidth50_left, plumeWidth50_right, overall_highest, in_highest, base_height_y)
        
        height = getPlumeHeight(base_height_y, in_highest) * pixelToMicrometre
        width_pixel = abs(plumeWidth50_left - plumeWidth50_right)
        width = width_pixel * pixelToMicrometre    

        plume.height = height
        plume.width = width
        
        text = "Acceptable plume"
        fontColor  = (0,255,0)

        # Determining whether the width and height extracted are valid
        isWidthValid = (inspection_w/2 < width_pixel < inspection_w * 5)
        isHeightValid = (base_height_y - in_highest >= 0)

        #make its own method
        if not valid:
            fontColor  = (255,0,0)
            if(abs(base_height_y - overall_highest) > 100):
                text = "Premature pop"
            else:
                text = "No plume"
        
        # Draw a big pink circle at the tip of the plume.
        topPoint = findTopPoint(contours)
        cv2.circle(bubble_image_contour, topPoint, 10, (252,15,192) ,-1)

        #make its own method
        # Write some Text
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,1000)
        fontScale              = 1.2
        thickness              = 1
        lineType               = 2
        text_height            = 900            

        cv2.putText(bubble_image_contour,"State: "  + text , 
            (10,text_height), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        

        cv2.putText(bubble_image_contour,"Actual Lifetime = " + str(lifetime) +"ns", 
            (10,text_height +40), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        cv2.putText(bubble_image_contour,"Plume height = " + str(round(height,2))+"um", 
            (10,text_height +80), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        cv2.putText(bubble_image_contour,"Plume width = " + str(round(width,2))+"um  "+ " isValid = "+ str(isWidthValid), 
            (10,text_height +120), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        cv2.putText(bubble_image_contour,"Pulse voltage = " + str(round(pulse_voltage,2))+"V   " " isValid = "+  str(isHeightValid), 
            (10,text_height +160), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        cv2.putText(bubble_image_contour,"intersect points = " + str(intersect_count),
            (10,text_height +200), 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        #If the plume is found to have liftOffs, then display a text saying that a liftoff is present
        #make its own method
        if isLiftOff:
            
            #jetHeights.append(jetLength)
            
            cv2.putText(bubble_image_contour,"LiftOff Fracture present" + ";  Jet Height = " + str("%.2f"%jetLength)+"um", 
            (10,text_height +240), 
            font, 
            fontScale,
            (200,200,200),
            thickness,
            lineType)

            # Get jetHeight and take the micrometer conversion. Then put text for it.

            
            #liftOffDelayTimes.append(trueDelay) 


            # cv2.putText(bubble_image_contour, "Jet Height = " + str("%.2f"%jetHeight)+"um",
            # (10,text_height +280), 
            # font, 
            # fontScale,
            # (200,200,200),
            # thickness,
            # lineType)

            savePlumeIntoDirectory("lift_off_data", name, directory,
                                    setDelay,lifetime,voltage,q1c,lensFocalLength,lensHeight,pressure, pulse_voltage, jetLength, fractureRadius,
                                    text, height, width,isHeightValid, isWidthValid, intersect_count,
                                    idl_90, idl_85, idl_80)
            savePlumeImageIntoDirectory("lift_off_images",
                                        bubble_image_contour, imageDirectory, name)

        #If the plume is perfect, then display text saying that the plume is perfect
        #make its own method
        if isPerfect:
            cv2.putText(bubble_image_contour,"Perfect Plume",
            (10,text_height +240), 
            font, 
            fontScale,
            (200,200,200),
            thickness,
            lineType)
            savePlumeImageIntoDirectory("perfect_plume_images",
                                        bubble_image_contour, imageDirectory, name)
            savePlumeIntoDirectory("perfect_plume_data", name, directory,
                                   setDelay,lifetime,voltage,q1c,lensFocalLength,lensHeight,pressure,pulse_voltage, jetLength, fractureRadius,
                                    text, height, width,isHeightValid, isWidthValid, intersect_count,
                                    idl_90, idl_85, idl_80)           
            
        if isFracture:
            cv2.putText(bubble_image_contour,"Fracture detected" + ";  Fracture radius = " + str("%.2f"%fractureRadius)+"um",
            (10,text_height +280), 
            font, 
            fontScale,
            (200,200,200),
            thickness,
            lineType)
            savePlumeImageIntoDirectory("fracture_images",
                                        bubble_image_contour, imageDirectory, name)
            savePlumeIntoDirectory("fracture_data", name, directory,
                                   setDelay,lifetime,voltage,q1c,lensFocalLength,lensHeight,pressure,pulse_voltage, jetLength, fractureRadius,
                                    text, height, width,isHeightValid, isWidthValid, intersect_count,
                                    idl_90, idl_85, idl_80)           

        savePlumeImageIntoDirectory("analysis_images", 
                               bubble_image_contour, imageDirectory, name)

        # Make this a method - savePlumeIntoDirectory(isLiftOff, isPerfect, isFracture) - change so that it could save all of the original elements

        savePlumeIntoDirectory("analysis_data", name, directory,
                               setDelay,lifetime,voltage,q1c,lensFocalLength,lensHeight,pressure,pulse_voltage, jetLength, fractureRadius,
                               text, height, width,isHeightValid, isWidthValid, intersect_count,
                               idl_90, idl_85, idl_80)
        

        # write folder for listoff
        # write folder for perfect plumes


        current_index += 1
    





# #### Fracture Methods


# INPUT: List of Contours, integer
# PURPOSE: Returns contours whose top point (highest y-value) and bottom point (lowest y-value) are at a higher location than the threshold
# OUTPUT: List of contours (in which contours are a list of points, in which points are a list of integers)
def contoursAboveThreshold(contours, threshold):
    contoursAboveThreshold = []
    for contour in contours:
        topY = findTopOrBottomPoint(contour, 2)[1]
        botY = findTopOrBottomPoint(contour)[1]
        if topY <= threshold and botY <= threshold:
            contoursAboveThreshold.append(contour)
    return contoursAboveThreshold

# INPUT: Contour (List of points), Point (List of Integers)
# PURPOSE: Check the distances between a given point and each individual point of a contour. Then, return the average of those distances.
# OUTPUT: Integer
def averageDistanceToCenter(contour, center):
    xCenter = center[0]
    yCenter = center[1]
    distances = []
    for point in contour:
        x = point[0]
        y = point[1]
        x_distance = np.abs(x - xCenter)
        y_distance = np.abs(y - yCenter)
        distance = np.sqrt(x_distance**2 + y_distance**2)
        distances.append(distance)
    return statistics.fmean(distances)

# INPUT: Contour
# PURPOSE: Find the largest distance between two points in a contour (diameter) and then return the halved value (radius)
# OUTPUT: Integer
def getLargestRadius(contour):
    maxDistance = 0
    for i in range(len(contour)):
        x = contour[i][0]
        y = contour[i][1]
        for j in range(len(contour)):
            nextX = contour[j][0]
            nextY = contour[j][1]
            delta_x = np.abs(x-nextX)
            delta_y = np.abs(y-nextY)
            distance = np.sqrt(delta_x**2 + delta_y**2)
            if distance >= maxDistance:
                maxDistance = distance
    return maxDistance/2


# INPUT: Plume, integer, integer, Image
# PURPOSE: Evaluate whether a fracture is located in the plume and measure its radius. Has base_height_y and in_highest predefined.
# OUTPUT: None
def evaluatePlumeFractureParameterLite(plume, base_height_y, in_highest, image = None):
    contours = plume.getContours()
    contours = removeFloors(contours, base_height_y, in_highest)
    # longestContour = findLongestContour(contours)    
    fracture_threshold = int(base_height_y - getPlumeHeight(base_height_y, in_highest)/2)
    # find the contour whose top point and bottom point are above the threshold. this should neglect the outline contour as its bottom point should be at the ground, as well as lift-off veins 
    # as their top and bottom point should be below the threshold
    fractureContours = contoursAboveThreshold(contours, fracture_threshold)
    circleContours = []
    if len(fractureContours) > 0:
        for contour in fractureContours:
            # draws a smallest circle it could fit around a contour
            (x_axis,y_axis),radius = cv2.minEnclosingCircle(np.array(contour))

            #mec refers to minEnclosingCircle
            mecCenter = (int(x_axis),int(y_axis))
            mecRadius = int(radius)

            #cv2.circle(image,mecCenter, 2, (255,0,0),10)
            #cv2.circle(image,mecCenter,mecRadius,(0,255,0),2)
            #Find the radius of the contour. Iterate through the points in each contour and get the difference it could have with the minEnclosingCircle's (mec) center, 
            # average these values to get an average distance and compare that to the minEnclosingCircle's radius. If it is close to the radius, then confirm it as a fracture hole.
            contourRadius = averageDistanceToCenter(contour, mecCenter)
            # print(contourRadius)
            # print("circle:", mecRadius)
            if np.abs(contourRadius - mecRadius) <= mecRadius/3:
                circleContours.append(contour)
                plume.setIsFracture(True)
                fractureRadius = getLargestRadius(contour)*pixelToMicrometre
                #fractureRadius = mecRadius*pixelToMicrometre
                if fractureRadius > plume.getFractureRadius():
                    plume.setFractureRadius(fractureRadius)
            # 090326 note: I don't know why I had this here. This would actually neglect a lot of fracture plumes wouldn't it? Since the algorithm could detect a fracture, set its isFracture value 
            # to True and its fractureRadius value to the calculated radius, and then move on to the next contour, evaluate it as false, and then undo the fracture settings? This would mean that only
            # Fracture plumes with a fracture hole at its last index in its contours list would be confirmed. 
            # else:
            #     plume.setIsFracture(False)
            #     plume.setFractureRadius(0)

    try:
        #print(len(circleContours))
        for contour in circleContours:
            mapContours(image, [contour])
    except:
        print("No image")


# INPUT: Plume, image
# PURPOSE: Find base_height_y and in_highest, evaluate whether a fracture is present in the plume and measure its radius.
# OUTPUT: None
def evaluatePlumeFractureParameter(plume, image = None):
    base_height_y= deriveParams(plume)[2]
    in_highest = deriveParams(plume)[4]
    evaluatePlumeFractureParameterLite(plume, base_height_y, in_highest, image)

# #### Distribution Computer


# INPUT: List of Plumes, String
# PURPOSE: Creates a histogram of plumes who have a certain parameter
# OUTPUT: None
def distribute(plumes, parameter: str):
    if parameter == "Lift Off" or parameter == "Perfect" or parameter == "Fracture":
        distributedPlumes = binPlumes(plumes, parameter)
        distributedTimes = []
        allTimes = []
        for plume in distributedPlumes:
            lifetime = plume.lifeTime
            distributedTimes.append(lifetime)
        for plume in plumes:
            lifetime = plume.lifeTime
            allTimes.append(lifetime)
        fig = plt.figure(figsize=(10,10))
        ax1 = fig.add_subplot(2,1,1)
        ax2 = fig.add_subplot(2,1,2, sharey = ax1)
        ax1.hist(distributedTimes, ec = 'white', bins = 20, label= parameter)
        ax2.hist(allTimes, color='orange' ,ec = 'white', bins = 20, label='total plumes')
        fig.supxlabel("Actual lifeTimes")
        fig.supylabel("Quantity of Plumes")
        fig.suptitle("Quantity of Plume vs. Actual Lifetime")
        fig.legend()
    else:
        print("Invalid Parameter. Please enter either 'Lift Off', 'Perfect', or 'Fracture'")

# #### Plotter and Fitter


# INPUT: Plume, String
# PURPOSE: Returns the requested parameter of the plume and its corresponding unit of measurement 
# OUTPUT: Integer/Float, String
def returnInputtedParam(plume, parameter: str):
    if parameter == "Voltage":
        return plume.voltage, "V"
    elif parameter == "Jet Length":
        return plume.jetHeight, "um"
    elif parameter == "Fracture Radius":
        return plume.fractureRadius, "um"
    else:
        print('returnInputtedParam: Invalid. Please input "Voltage", "Jet Length", or "Fracture Radius."')

# INPUT: Float, Float, Float (Or integer idk)
# PURPOSE: Linear function for fitting
# OUTPUT: Integer/Float
def function(x, m, b):
        return m*x + b

# INPUT: List of Integers, List of Integer, Integer, Integer
# PURPOSE: Fits the data points with a linear function and returns the fitted y-values, parameters, and standard deviation
# OUTPUT: List of Integers, Integer, Integer, Integer
def fitTimesToFunction(xData, yData, mGuess = 0, bGuess = 0):
    fitY = []
    [m,b], covariance = curve_fit(function, xData, yData, [mGuess,bGuess])
    for i in range(len(yData)):
        x = xData[i]
        fitY.append(function(x, m, b) )
    standard_deviation = np.sqrt(np.diag(covariance))
    return fitY, m, b, standard_deviation

# INPUT: List of Plumes
# PURPOSE: Returns highest time
# OUTPUT: Integer
def getMaxTime(plumes):
    max = 0
    for plume in plumes:
        lifetime = plume.lifeTime
        if lifetime >= max:
            max = lifetime
    return max

# INPUT: List of Plumes, String, Integer, Integer, Integer, Integer, Integer, Integer
# PURPOSE: Searches for plumes within the given time constraints and y-value constraints and fits the y-value data within said constraint
# OUTPUT: None
def fitPlumes(plumes, parameter: str, 
              lowerTime = 0, upperTime = None, 
              lowerDependent = 0, upperDependent = np.inf,
              mGuess = 0, bGuess = 0):
    if not upperTime:
        upperTime = getMaxTime(plumes)
    plumesOfInterest = binPlumes(plumes, "Lifetime", lowerTime, upperTime)
    plumesOfInterest = binPlumes(plumesOfInterest, "Perfect")
    plumesOfInterest = binPlumes(plumesOfInterest, parameter, lowerDependent, upperDependent) 
    print(len(plumesOfInterest))
    lifetimes = []
    dependentVariables = []
    for plume in plumesOfInterest:
        lifetime = plume.lifeTime/1000
        dependentVariable, unit = returnInputtedParam(plume, parameter)
        lifetimes.append(lifetime)
        dependentVariables.append(dependentVariable)
    
    
    fitY, speed, intercept, sigma = fitTimesToFunction(lifetimes, dependentVariables, mGuess, bGuess)
    plt.scatter(lifetimes, dependentVariables, 1)
    plt.xlim(lowerTime/1000, upperTime/1000)
    plt.plot(lifetimes, fitY, 1)
    print("Intercept: ",intercept)
    plt.title(parameter + " vs. Plume lifetime (" + str("%.2f"%speed) + "+/-" + str("%.2f"%sigma[0]) + "m/s)")
    plt.xlabel("Plume lifetime (us)")
    plt.ylabel(parameter + " (" + unit + ")")

# directory = r"P:\F250_len\F250_41mm_Pre_runSeries\data"
# # fractureSample = createPlumeList(r"Z:\Users\coop\Matthew_2025\PlumeSamples\Fracture\data", r"Z:\Users\coop\Matthew_2025\PlumeSamples\Fracture\images")
# # print(len(fractureSample))
# plumes = loadPlumes(directory, "testing.epp")

# createAnalysis(plumes)

