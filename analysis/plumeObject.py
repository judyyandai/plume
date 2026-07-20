import os
import csv

class Plume:

    # Maybe get rid of the directory parameter?
    

    def __init__(self, name: str, directory: str, imageDirectory: str, contours = [], isFracture = False, fractureRadius = 0, isLiftOff = False, jetHeight = 0, isPerfect = False, height=0, width=0):
        lifeTime, voltage, laser = self.getCsvParams(name, directory)
        self.name = name
        self.directory = directory
        self.imageDirectory = imageDirectory
        self.lifeTime = lifeTime
        self.voltage = voltage
        self.contours = contours
        self.isFracture = isFracture
        self.fractureRadius = fractureRadius
        self.isLiftOff = isLiftOff
        self.jetHeight = jetHeight
        self.isPerfect = isPerfect
        self.height = height
        self.width = width
        self.laser = laser

    # INPUT: String, String (directory)
    # PURPOSE: Opens a CSV file using a filepath appended between name and directory and returns lifeTime and voltage from the file
    # OUTPUT: Float, Float
    def getCsvParams(self, name, directory):
        rows = []
        name = f"{name}.csv"
        csvFile = open(os.path.join(directory, name), "r")
        read = csv.reader(csvFile)
        for row in read: 
            rows.append(row)
        dataRow = rows[1]
        
        lifeTime = float(dataRow[1])
        # print(lifeTime)
        voltage = float(dataRow[2])
        # print(voltage)

        # Default to "PIRL" if the column is missing or empty (for handling older csv files)
        laser = dataRow[10].strip() if len(dataRow) > 10 and dataRow[10].strip() else "PIRL"
        # print(laser)

        return lifeTime, voltage, laser
    

    # Getters - Not really necessary but don't exclude since some methods use these.
    def getName(self):
        return self.name
    
    def getDirectory(self):
        return self.directory
    
    def getImageDirectory(self):
        return self.imageDirectory

    def getLifeTime(self):
        return self.lifeTime
    
    def getVoltage(self):
        return self.voltage
    
    def getContours(self):
        return self.contours
    
    def getIsFracture(self):
        return self.isFracture
    
    def getFractureRadius(self):
        return self.fractureRadius
    
    def getIsLiftOff(self):
        return self.isLiftOff
    
    def getJetHeight(self):
        return self.jetHeight
    
    def getIsPerfect(self):
        return self.isPerfect
    
    def getLaser(self):
        return self.laser
    
    # Setters - also not necessary but also don't exclude
    def setName(self, name: str):
        self.name = name

    def setDirectory(self, directory: str):
        self.directory = directory

    def setImageDirectory(self, imageDirectory: str):
        self.imageDirectory = imageDirectory

    def setLifeTime(self, lifeTime:int):
        self.lifeTime = lifeTime
    
    def setVoltage(self, voltage: float):
        self.voltage = voltage

    def setContours(self, contours: list):
        self.contours = contours

    def setIsFracture(self, isFracture: bool):
        self.isFracture = isFracture

    def setFractureRadius(self, fractureRadius: float):
        self.fractureRadius = fractureRadius
        
    
    def setIsLiftOff(self, isListOff: bool):
        self.isLiftOff = isListOff
    
    def setJetLength(self, jetLength: float):
        self.jetHeight = jetLength

    def setIsPerfect(self, isPerfect: bool):
        self.isPerfect = isPerfect

 #Stuff to maybe put: The contour list, directory, image (which shares the name with its corresponding csv), image directory 

# class Plume_analysis:
#     def _init_(self, directory: str, plumes = []):
#         self.directory = directory
#         self.plumes = plumes

#     # Getters
#     def getDirectory(self):
#         return self.directory

#     def getPlumes(self):
#         return self.plumes

#     # Setters
#     def setDirectory(self, directory):
#         self.directory = directory

#     def setPlumes(self, plumes):
#         self.plumes = plumes

#     # INPUT: Integer, integer, list, string 
#     # PURPOSE: Finds plumes whose given parameter is within the lower and upper bounds and returns them
#     # OUTPUT: List of Plumes
#     def returnPlumesWithinInterval(lower, upper, plumes, parameter: str):
#         sortedPlumes = []
#         for plume in plumes:
#             if parameter == "Lifetime":
#                 if lower <= plume.getLifeTime() <= upper:
#                     sortedPlumes.append(plume)
#             elif parameter == "Voltage":
#                 if lower <= plume.getVoltage() <= upper:
#                     sortedPlumes.append(plume)
#         return sortedPlumes

#     # INPUT: None
#     # PURPOSE: goes through the directory and creates plumes from the csv files in that directory 
#     # OUTPUT: List of Plumes
#     def createPlumeList(directory):
#         plumes = []
#         files = os.listdir(directory)

#         for file in files:
#             if file.endswith(".csv"):
#                 plumeName = file

#                 csvFile = open(os.path.join(files, file), "r")
#                 reader = csv.reader(csvFile)
#                 dataRow = reader[1]
#                 temp = [float(x) for x in dataRow[1][0:8]]
#                 lifeTime = temp[1]
#                 voltage = temp[2]

#                 plume = Plume(plumeName, directory, lifeTime, voltage)
#                 plumes.append(plume)

#         return plumes
    
# directory = r"Z:\Users\coop\Matthew_2025\Report\ReportPhotos\KennyData\PerfectPlume"

# plumeAnal = Plume_analysis(directory)
#plumes = plumeAnal.createPlumeList(directory)

# my_plume = Plume("name", "directory", 20, 2)
# print(my_plume.getLifeTime())


    # def save_plumes







