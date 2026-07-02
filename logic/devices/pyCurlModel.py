# Logic for communication with the Q-Tune laser via PycURL
# Valid commands are found in section 12.2: List of Laser Commands in the Q-Tune manual

import sys
import pycurl
from urllib.parse import quote
import json
import time
from io import BytesIO

xx = 76
base_url = f"http://192.168.1.{xx}:7557/send?"
username = "QTuser"
password = "QT_76"
userPwd = f"{username}:{password}"


def doCommand(json):
    """
    DESCRIPTION:
        Send a command to the laser. 
        First, the command string is converted into a URL-encoded string. 
        Then, the URL and the URL-encoded command are combined. Finally, the full command is sent.
    PARAMETERS:
        Raw JSON object of the desired (as a string)
    RETURN: 
        None
    """

    # Encodes JSON as a URL
    encodedJson = encodeCurl(json)
    # Combines base URL and encoded JSON. This forms the cURL command that we send to the Q-Tune. 
    url = f"{base_url}{encodedJson}"
    print(f"PYCURL: Sending {url}")
    # Creates pycurl object
    c = pycurl.Curl()
    # Sets the cURL command, setting the Username, Password, and URL 
    c.setopt(c.USERPWD, userPwd)
    c.setopt(c.URL, url)
    # Sends the cURL command and closes.
    c.perform() 
    c.close()    

def encodeCharacterIntoCurl(char):
    """
    DESCRIPTION:
        URL-encode a character (string).
    PARAMETERS:
        A character (string). 
    RETURN: 
        The URL-encoded character as a string. For example, { gets encoded as %7B
    """
    if char == '{':
        return "%7B"
    elif char == '"':
        return "%22"
    elif char == ':':
        return "%3A"
    elif char == ',':
        return "%2C"
    elif char == ' ':
        return "%20"
    elif char == '}':
        return "%7D"
    else:
        return char

def encodeCurl(string):
    """
    DESCRIPTION:
        URL-encode the full JSON command as a string.
    PARAMETERS:
        JSON string 
    RETURN: 
        The full URL-encoded JSON object.
    """
    curl = ""
    for char in string:
        curl = f"{curl}{encodeCharacterIntoCurl(char)}"   
    return curl

def runLaser():
    """
    DESCRIPTION:
        Function to start the laser
    PARAMETERS:
        None
    RETURN: 
        None
    """
    laserRunJson = r'{"action":"control","code":{"device":"laser","values":{"laser-run": 1}}}'
    doCommand(laserRunJson)

def stopLaser():
    """
    DESCRIPTION:
        Function to stop the laser
    PARAMETERS:
        None
    RETURN: 
        None
    """
    # JSON command for stopping the laser
    laserStopJson = r'{"action":"control","code":{"device":"laser","values":{"laser-run": 0}}}'
    # Processes JSON
    doCommand(laserStopJson)

def trigMode(internal: bool, externalMode = 1):
    """
    DESCRIPTION:
        Function to change the triggering mode of the laser.
    PARAMETERS:
        internal: boolean representing whether we want internal or external triggering mode
        externalMode: integer representing whether we want external SP (1) or external TP (2) triggering mode
    RETURN: 
        None
    """
    trigModeInternal = r'{"action":"control","code":{"device":"laser","values":{"trig-mode":0}}}'
    trigModeExternalSingle = r'{"action":"control","code":{"device":"laser","values":{"trig-mode":1}}}'
    trigModeExternalDouble = r'{"action":"control","code":{"device":"laser","values":{"trig-mode":2}}}'
    trigJson = trigModeInternal
    # If the user wants internal triggering, set internal to True
    if internal:
        trigJson = trigModeInternal
    # If the user wants external triggering, set internal to False.
    # If the user wants two-pulse triggering, set externalMode to 2. Otherwise, externalMode is defaulted to 1 (Single-pulse).
    elif not internal:
        if externalMode == 2:
            trigJson = trigModeExternalDouble
        else:
            trigJson = trigModeExternalSingle
    doCommand(trigJson)

def trigModeInternal():
    """
    DESCRIPTION:
        Function to change the triggering mode of the laser to internal
    PARAMETERS:
        None
    RETURN: 
        None
    """
    trigMode(True)

def trigModeExternal():
    """
    DESCRIPTION:
        Function to change the triggering mode of the laser to external single pulse
    PARAMETERS:
        None
    RETURN: 
        None
    """
    trigMode(False)

def trigModeExternalTwoPulse():
    """
    DESCRIPTION:
        Function to change the triggering mode of the laser to external two pulse
    PARAMETERS:
        None
    RETURN: 
        None
    """
    trigMode(False,2)

def changeFrequency(freq):
    """
    DESCRIPTION:
        Function to change the repetition rate of the laser. Will round to the closest possible permitted value
    PARAMETERS:
        freq: float representing the desired new repetition rate
    RETURN: 
        None
    """
    # The Q-Tune will only accept the repetition rate denominator. This value must be an integer hence why we can't be specific with the frequency setting.
    repRateDenominator = 10/freq
    # Calculates the set frequency we get. We round the denominator to the closest integer.
    expectedFrequency = 10/int(repRateDenominator + 0.5)
    # Range of Q-Tune frequency is limited. Makes a check for whether the repetition rate denominator is in range.
    if repRateDenominator < 1 or repRateDenominator > 20:
        print("Q-Tune ERROR: Frequency of {freq} Hz cannot be produced.")
    else:
        # Concatenates the repetition rate denominator provided into our JSON command. F-string will be confused about the curly brackets, making it
        # difficult to simply input the denominator as an F-string variable. So we went with this method.
        repRateJsonPart1 = r'{"action":"control","code":{"device":"laser","values":{"rep-rate-divide": '
        repRateJsonPart2 = r'}}}'
        repRateJson = f'{repRateJsonPart1}{repRateDenominator}{repRateJsonPart2}'
        # Processes JSON
        doCommand(repRateJson)
        print(f"Q-Tune: Frequency adjusted to: {expectedFrequency} Hz")

def startQTune():
    """
    DESCRIPTION:
        Function to start the laser with a little more efficiency by changing the triggering mode to internal and starting the laser
    PARAMETERS:
        None
    RETURN: 
        None
    """
    trigModeInternal()
    runLaser()

def runLaserForSetTime(timeLength, unit = "seconds"):
    """
    DESCRIPTION:
        Function to run the laser for a fixed amount of time, then stop it
    PARAMETERS:
        timeLength: float representing the amount of time laser will be on for
        unit: string representing the correct units of timeLength. Possible values are minutes and seconds. Default is seconds
    RETURN: 
        None
    """
    runLaser()
    print(f"Q-Tune: Laser Start at {time.ctime()}")
    if unit == "Minute" or unit == "Minutes" or unit == "minute" or unit == "minutes" or unit == "min" or unit == "Min":
        timeLength *= 60
    print(f"Q-Tune: Running laser for {timeLength} seconds")
    time.sleep(timeLength)
    stopLaser()
    print(f"Q-Tune: Laser Stop: {time.ctime()}")
 
def startQTuneForSetTime(timeLength, unit = "seconds"):
    """
    DESCRIPTION:
        Function to run the laser for a fixed amount of time, then stop it, with the additional step of changing the triggering mode to internal
    PARAMETERS:
        timeLength: float representing the amount of time laser will be on for
        unit: string representing the correct units of timeLength. Possible values are minutes and seconds. Default is seconds
    RETURN: 
        None
    """
    trigModeInternal()
    runLaserForSetTime(timeLength, unit=unit)

def changeWavelength(wavelength):
    """
    DESCRIPTION:
        Function to change the wavelength of the laser
    PARAMETERS:
        wavelength: float representing desired wavelength. Can be a non-integer.
    RETURN: 
        None
    """
    if 1390 <= wavelength <= 4500:
        if 1682 <= wavelength <= 1701:
            print(f"Q-Tune ERROR: changeWavelength - Wavelength of {wavelength} nm falls within 1682-1701nm discontinuity range.")
        elif 2840 <= wavelength <= 2900:
            print(f"Q-Tune ERROR: changeWavelength - Wavelength of {wavelength} nm falls within 2840-2900nm discontinuity range.")
        else:
            wavelengthJson1 = r'{"action":"control","code":{"device": "laser","values":{"forward-device":"opo","forward-protocol":"wavelength","forward-action":"control","wavelength": '
            wavelengthJson2 = r'}}}'
            wavelengthJsonFull = f'{wavelengthJson1}{wavelength}{wavelengthJson2}'
            doCommand(wavelengthJsonFull)
            print(f"Q-Tune: Wavelength changed to {wavelength} nm.")
    else:
        print(f"Q-Tune ERROR: changeWavelength - Wavelength of {wavelength} nm is out of bounds. Please input a value between 1390nm and 4500nm.")

def changePumpLevel(pump):
    """
    DESCRIPTION:
        Function to change the pump energy level of the laser. Note that decreasing this value decreases Port 1 energy but increases Port 2, and vice-versa.
    PARAMETERS:
        pump: float representing the desired pump energy level. Must be between 0 and 100. Can be a non-integer.
    RETURN: 
        None
    """
    if 0 <= pump <= 100:
        pumpJson1 = r'{"action":"control","code":{"device": "laser","values":{"forward-device":"opo","forward-protocol":"wavelength","forward-action":"control","transmission": '
        pumpJson2 = r'}}}'
        pumpJsonFull = f'{pumpJson1}{pump}{pumpJson2}'
        doCommand(pumpJsonFull)
        print(f"Q-Tune: OPO Pump Energy Levels changed to {pump}%")
    else:
        print("Q-Tune ERROR: changePumpLevel - Pump level is out-of-bounds. Please input a value between 0 and 100%.")

def enableQFG():
    """
    DESCRIPTION:
        Function to enable the external function generator.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    pgJson = r'{"action":"control","code":{"device": "pulse-generator","values":{"device":"pulse-generator","PG-enable": 1}}}'
    doCommand(pgJson)
   

def disablePG():
    """
    DESCRIPTION:
        Function to disable the external function generator.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    pgJson = r'{"action":"control","code":{"device": "pulse-generator","values":{"device":"pulse-generator","PG-enable": 0}}}'
    doCommand(pgJson)

def enableCh1():
    """
    DESCRIPTION:
        Function to enable channel 1 on the external function generator.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    ch1Json = r'{"action":"control","code":{"device":"pulse-generator","values":{"device": "pulse-generator", "ch1-enabled":1}}}'
    doCommand(ch1Json)

def disableCh1():
    """
    DESCRIPTION:
        Function to disable channel 1 on the external function generator.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    ch1Json = r'{"action":"control","code":{"device":"pulse-generator","values":{"device": "pulse-generator", "ch1-enabled":0}}}'
    doCommand(ch1Json)    

def enableBurstMode():
    """
    DESCRIPTION:
        Function to enable burst mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    burstModeJson = r'{"action":"control","code":{"device": "laser","values":{"burst-mode": 1}}}'
    doCommand(burstModeJson)

def disableBurstMode():
    """
    DESCRIPTION:
        Function to disable burst mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    burstModeJson = r'{"action":"control","code":{"device": "laser","values":{"burst-mode": 0}}}'
    doCommand(burstModeJson)

def pgTrigExternal():
    """
    DESCRIPTION:
        Function to put the external function generator into external triggering mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    pgTrigJson = r'{"action":"control","code":{"device": "pulse-generator","values":{"device":"pulse-generator", "PG-burst-trig-mode":1}}}'
    doCommand(pgTrigJson)

def pgTrigInternal():
    """
    DESCRIPTION:
        Function to put the external function generator into internal triggering mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    pgTrigJson = r'{"action":"control","code":{"device": "pulse-generator","values":{"device":"pulse-generator", "PG-burst-trig-mode": 0}}}'
    doCommand(pgTrigJson)

def gallopModeInternal():
    """
    DESCRIPTION:
        Function to set up Gallop Mode with the function generator in internal triggering mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    stopLaser()
    trigModeExternal()
    enableQFG()
    enableCh1()
    pgTrigInternal()
    enableBurstMode()

def gallopModeExternal():
    """
    DESCRIPTION:
        Function to set up Gallop Mode with the function generator in external triggering mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    trigModeExternal()
    enableQFG()
    enableCh1()
    pgTrigExternal()
    enableBurstMode()
    runLaser() # runLaser needs to be run as the laser will not fire unless laser-run = 1

def gallopModeOff():
    """
    DESCRIPTION:
        Function to disable Gallop Mode and configure the laser for firing in Regular Pulse mode.
    PARAMETERS:
        None
    RETURN: 
        None
    """
    stopLaser()
    disableBurstMode()
    disableCh1()
    disablePG()
    trigModeInternal()