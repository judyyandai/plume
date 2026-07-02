/* Gabriel Caribe and Daniel Pinto H:\test\HEATER\HEATER.ino
Max Planck Institute for the Structure and Dynamics of Matter
Written 2025. 
Email gabe.h.c@hotmail.com or danielpintolzr@gmail.com for questions. 

* Please refer to ELOG entry 146 under SSU_Experiment -> SSU_PLUME2 for a more detailed explination of how this program works *
*/
#define USING_TIMER_TC3         true
#define USING_TIMER_TC4         true      // Not to use with Servo library

#include <SAMDTimerInterrupt.h>
#include <UC1701.h>
#include <Wire.h>
#include <Indio.h>

//////////////////// Initialize the PID Values
float targetTemp = 20.0;
float PIDValue = 0.0; // Value between 0 and 1 that correcponds to what percentage of the heaterPeriod the heater should be on for
float Kp = 1.0; // Proportional coefficiant
float Ki = 0.0; // Integral coefficiant
float Kd = 0.0; // Derivative coefficiant
float currentError = 0.0; // = targetTemp - actualTemp; 0 to start with. 

float heaterOnTime;
float heaterOffTime; 

bool pidOn = false;
bool heaterOn = false;
bool firstTime = true;

float errorIntegral = 0.0; //Integral of the error values
// Times used to determine dt for the integral
unsigned long previousMillis = 0; 
unsigned long timeNow; 
///////////////////

/////////////////// Input and Output Pins
//Input pins
int pt1000Pin1 = 1;
int pt1000Pin2 = 2;

// Output pin
int heaterPin = 8; 
// Tester heater pin, so there's no actual heating happening:
// int heaterPin = 3; 

///////////////////

/////////////////// Create an LCD Object to Display to the Industruino Screen
static UC1701 lcd;
///////////////////

//////////////////// Initialize the Two Timers
SAMDTimer runPIDTimer(TIMER_TC3); // refers to Timer/Counter 3 (TC3), a 16-bit timer on the SAMD21
SAMDTimer heaterTimer(TIMER_TC4); // refers to Timer/Counter 4 (TC4), a 16-bit timer on the SAMD21 -> this timer does not work with Servo Library, use TC5 if you want to use Servo Library

volatile bool runPIDCompareMatch = false; // This is a boolean variable that is true when the runPIDTimer triggers the inturrupt
volatile bool heaterTimerCompareMatch = false; // This is a boolean variable that is true when the heaterTimer triggers the inturrupt
////////////////////

//////////////////// Setting Timer Frequencies, Initializing Counts, and Setting Periods
uint32_t TIMER_INTERVAL_MS[MAX_TIMER]   = { 1000, 100 }; // The first value is the period of the runPIDTimer, the second is the period of the heaterTimer, all in ms
float RUN_PID_FREQ_INTERMEDIATE = (float) TIMER_INTERVAL_MS[TIMER_TC3] / 1000;
float RUN_PID_TIMER_FREQUENCY = 1 / RUN_PID_FREQ_INTERMEDIATE; // Gives the frequency in Hz
float current_temp1; 
float current_temp2; 
int runPIDCount = 0; // Increases every time runPID() is called -> functionality occures only when this reaches heaterPeriod or recalcPeriod
int heaterPeriod = 5; // This must be a positive integar, in seconds
int recalcPeriod = 1; // This must be a positive integar, in seconds


float HEATER_FREQ_INTERMEDIATE = (float) TIMER_INTERVAL_MS[TIMER_TC4] / 1000;
float HEATER_TIMER_FREQUENCY = 1 / HEATER_FREQ_INTERMEDIATE; // Gives the frequency in Hz
int heaterCount = 0; // Increases every time timedDisableHeater() is called -> functionality occures only when this reaches heaterOnTimeCounts
float heaterOnTimeCounts; // This is calculated to HEATER_TIMER_FREQUENCY *  heaterOnTime
////////////////////

void readSerialAndUpdate(){
  /*
  Function entirely for reading in serial commands to change variables. Valid commands are:

  (1) "start" - starts the PID heating system
  (2) "stop" - stops the PID heating system and turns off the heater
  (3) "coeffs" - displays the current values for the Kp, Ki, and Kd coefficients
  (4) "Kp:<value>" - sets Kp coefficient to <value>
  (5) "Ki:<value>" - sets Ki coefficient to <value>
  (6) "Kd:<value>" - sets Kd coefficient to <value>
  (7) "recalcPeriod:<value>" - sets the period (in s) at which the termperature and errorIntegral will be updated and the pid value will be recalculated (without changing the current length of the heating period)
  (8) "pidPeriod:<value>" - sets the pwm period (in s) for the heater (i.e. out of how many seconds the heater can be on for)
  (9) "temp:<value>" - sets the target temperature to <value> degrees celcius
  (1) "temp:? - prints to Serial monitor temperature in degrees celsius from the two probes, e.g. 30.52, 30.68"
  */
  String command;

  if (SerialUSB.available()){
    command = SerialUSB.readStringUntil('\n');

    int indexDelimiter = command.indexOf(":");
    String beforeDelimiter = command.substring(0,indexDelimiter);
    String afterDelimiter = command.substring(indexDelimiter + 1,-1);

    if (command == "start"){
      pidOn = true;
      errorIntegral = 0;
      runPIDCount = 0;
      firstTime = true;
      updateDisplay();
      SerialUSB.println("HEATER Heating System is On");
      setRunPIDTimer();
    }
    else if (command == "stop"){
      runPIDTimer.detachInterrupt();
      pidOn = false;
      turnHeaterOff();
      SerialUSB.println("HEATER Heating System is Off");
    }
    else if (command == "PID"){
      SerialUSB.println(PIDValue*100); 
    }
    else if (command == "coeffs"){
      SerialUSB.print("HEATER Kp: ");
      SerialUSB.println(Kp);
      SerialUSB.print("HEATER Ki: ");
      SerialUSB.println(Ki);
      SerialUSB.print("HEATER Kd: ");
      SerialUSB.println(Kd);
    }
    else if (beforeDelimiter == "Kp"){
      Kp = afterDelimiter.toFloat(); 
      SerialUSB.print("HEATER Changed Kp Coefficient to ");
      SerialUSB.println(Kp);
    }
    else if (beforeDelimiter == "Ki"){
      Ki = afterDelimiter.toFloat();
      SerialUSB.print("HEATER Changed Ki Coefficient to ");
      SerialUSB.println(Ki);
    } 
    else if (beforeDelimiter == "Kd"){
      Kd = afterDelimiter.toFloat();
      SerialUSB.print("HEATER Changed Kd Coefficient to ");
      SerialUSB.println(Kd);
    }
    else if (beforeDelimiter == "recalcPeriod"){
      recalcPeriod = afterDelimiter.toInt();
      SerialUSB.print("HEATER Changed Recalculation Period to ");
      SerialUSB.println(recalcPeriod);
    }
    else if (beforeDelimiter == "heaterPeriod"){
      heaterPeriod = afterDelimiter.toInt();
      SerialUSB.print("HEATER Changed Heater Period to ");
      SerialUSB.println(heaterPeriod);
    }
    else if (beforeDelimiter == "temp"){
      if (afterDelimiter == "?"){        
        SerialUSB.print(current_temp1);
        SerialUSB.print(", ");
        SerialUSB.println(current_temp2);
      }
      else {
        targetTemp = afterDelimiter.toFloat();
        SerialUSB.print("HEATER Changed Target Temperature to ");
        SerialUSB.println(targetTemp);
      }
      
    }
    else {
      SerialUSB.println("INDI " + command + "is not a command!"); 
    } 
  }
}

void setRunPIDTimer(){
  /*
  Setup for the Adafruit ZeroTimer used to trigger the runPIDInterrupt() function
  Note that once the timer has been disabled (i.e. if runPIDTimer.detachInterrupt(); has been called
  in the code) it is much safer to run this function and fully create the Interrupt Timer again 
  rather than running the line: runPIDTimer.enable(true) (as was found during testing)
  */
  runPIDTimer.attachInterruptInterval_MS(TIMER_INTERVAL_MS[TIMER_TC3], runPIDInterrupt);
  // if (runPIDTimer.attachInterruptInterval_MS(TIMER_INTERVAL_MS[TIMER_TC3], runPIDInterrupt))
    // SerialUSB.println("Starting  TIMER_TC3 OK");
  // else
    // SerialUSB.println("Can't set TIMER_TC3. Select another freq. or timer");
}

void setHeaterTimer(){
  /*
  Setup for the Adafruit ZeroTimer used to trigger the timedDisableHeaterInterrupt() function
  Note that once the timer has been disabled (i.e. if heaterTimer.detachInterrupt(); has been called
  in the code) it is much safer to run this function and fully create the Interrupt Timer again 
  rather than running the line: heaterTimer.enable(true) (as was found during testing)
  */ 
  heaterTimer.attachInterruptInterval_MS(TIMER_INTERVAL_MS[TIMER_TC4], timedDisableHeaterInterrupt);
  // if (heaterTimer.attachInterruptInterval_MS(TIMER_INTERVAL_MS[TIMER_TC4], timedDisableHeaterInterrupt));
  // else
    // SerialUSB.println("Can't set TIMER_TC4. Select another freq. or timer");
}

void runPIDInterrupt(){
  runPIDCompareMatch = true; // This variable is used in the main loop to allow the runPID() function to be called
}

void timedDisableHeaterInterrupt(){
  heaterTimerCompareMatch = true; // This variable is used in the main loop to allow the timedDisableHeater() function to be called
}

float readTemp1(){
  /*
  This function reads the voltage at pin pt1000Pin1 as a percentage of 0 to 10 V 
  and returns the temperature in degrees Celsius
  */
  float sensorVal1 = Indio.analogRead(pt1000Pin1); //Read Analog-In CH1 (output depending on selected mode)
  float startTemp = 0.0; // As configured with the dip switches on the WAGO 857-800 in the PID Heater box
  float endTemp = 100.0; // As configured with the dip switches on the WAGO 857-800 in the PID Heater box
  float tempRange = endTemp - startTemp; 
  current_temp1 = (sensorVal1 / 100) * tempRange + startTemp;// This gives the temperature 
  return current_temp1; 
}

float readTemp2(){
  /*
  This function reads the voltage at pin pt1000Pin2 as a percentage of 0 to 10 V 
  and returns the temperature in degrees Celsius
  */
  float sensorVal2 = Indio.analogRead(pt1000Pin2);
  float startTemp = 0.0; // As configured with the dip switches on the WAGO 857-800 in the PID Heater box
  float endTemp = 100.0; // As configured with the dip switches on the WAGO 857-800 in the PID Heater box
  float tempRange = endTemp - startTemp; 
  current_temp2 = (sensorVal2 / 100) * tempRange + startTemp; // This gives the temperature - CHECK THIS. 
  return current_temp2; 
}

void turnHeaterOn(){
  heaterOn = true;
  Indio.digitalWrite(heaterPin, HIGH);
  updateDisplay(); // update LCD display to reflect change
}

void turnHeaterOff(){
  Indio.digitalWrite(heaterPin, LOW); 
  heaterOn = false;
  updateDisplay(); // update LCD display to reflect change
}

void updateDisplay(){
  /*
  This Function updates the LCD display on the Industruino and writes the two temperatures values to the PC vis Serial communication
  following the format 
  t1:<temperature 1 value>
  t2:<temperature 2 value>
  */
  // Print whether the PID system is on (this does not necessarily mean the heater is on, but it does mean that the heater can turn on)
  // Note: if the PID system is off then the heater is off
  lcd.setCursor(0, 0);
  if(pidOn){
    lcd.println("PID SYSTEM ON ");
  }
  else if(!pidOn){
    lcd.println("PID SYSTEM OFF");
  }

  // print percent on
  lcd.setCursor(0, 1);
  lcd.print("Pct time On: ");
  lcd.print(PIDValue*100);
  lcd.print("%  ");

  //print heater on/off
  lcd.setCursor(0, 2); 
  if(heaterOn){
    lcd.println("Heater ON ");
  }
  else if(!heaterOn){
    lcd.println("Heater OFF");
  }

  //print temperature and targetTemp
  lcd.setCursor(0, 3); 
  float temp1 = readTemp1();
  float temp2 = readTemp2();
  float avgT = (temp1 + temp2) / 2;

  lcd.print("Target: ");
  lcd.print(targetTemp);
  lcd.println("deg C");
  lcd.print("Temp 1: ");
  lcd.print(temp1);
  lcd.println("deg C"); 
  lcd.print("Temp 2: ");
  lcd.print(temp2);
  lcd.println("deg C"); 
  lcd.print("Avg Temp: ");
  lcd.print(avgT);
  lcd.print("deg C"); 

  // Write the two temperature values to the PC via Serial communication
  // SerialUSB.write("t1:");
  // SerialUSB.write(String(temp1).c_str());
  // SerialUSB.write("\n");
  // SerialUSB.write("t2:");
  // SerialUSB.write(String(temp2).c_str());
  // SerialUSB.write("\n");
}

float calculatePIDValue(){
  /*
  This function returns a value between 0 and 1 corresponding to what percentage of heating period the heater should stay on for.
  -> To get the heaterOnTime from the value this function returns, multipy the value by the heaterPeriod.

  This function also updates the global errorIntegral variable which stores the accumulated past error values
  */
  unsigned long lastTime;
  float previousError;
  if (firstTime){ // on first run of the function we want dt = 0. 
    lastTime = 0; 
    timeNow = 0; 

    previousError = 0;
    currentError = 0; 

    firstTime = false; 
  } else{
    lastTime = timeNow; //store the previous
    timeNow = millis(); 

    previousError = currentError; 
    float temp1 = readTemp1();
    float temp2 = readTemp2();
    currentError  = targetTemp - ((temp1 + temp2) / 2); 
  }
  unsigned long dt = timeNow - lastTime; 
  errorIntegral = errorIntegral + (currentError + previousError)*dt/2; //trapezoidal numerical integration.
  float output = Kp*currentError + Ki*errorIntegral; 
  if (output*heaterPeriod < 0.5){ //avoid heating pulses of less than 0.5s for electrical reasons. 
    output = 0; 
  } 
  else if ((1-output)*heaterPeriod < 0.5){ // avoid OFF pulses of less than 0.5 second, for the same reason.
    output = 1; 
  }
  // SerialUSB.print("outpus is: ");
  // SerialUSB.println(output);
  return output;
}

void runPID(){
  /*
  Every heaterPeriod, this function gets the PIDValue (between 0 and 1) as calculated in calculatePIDValue(), and then turns
  the heater on for the corresponding amount of time
  */
  // SerialUSB.println("in runPID()"); 
  runPIDCount++;
  if (runPIDCount % heaterPeriod == 0){ //(runPIDCount / RUN_PID_TIMER_FREQUENCY) % heaterPeriod == 0
    PIDValue = calculatePIDValue(); 
    // SerialUSB.print("PIDValue is: ");
    // SerialUSB.println(PIDValue);
    heaterOnTime = PIDValue*heaterPeriod; 
    heaterOffTime = (1-PIDValue)*heaterPeriod; 
    if (heaterOnTime == 0){
      turnHeaterOff();
    } else if (heaterOffTime == 0){
      turnHeaterOn();
    } else{
      // heaterOnTimeCounts is the number of times the timedDisableHeater() function will be called before it disables the heater
      // This allows for the heater to stay on for several seconds, even though the heaterTimer runs at 10Hz
      heaterOnTimeCounts = round(heaterOnTime * HEATER_TIMER_FREQUENCY);
      turnHeaterOn();
      setHeaterTimer();
    }
  } 
  else if (runPIDCount%recalcPeriod == 0){ // this else if statement is used to update the termperature values more frequently than the heaterPeriod
    // Uncomment the next 3 lines if you want the errorIntegral term to be recalculated every recalcPeriod
    // PIDValue = calculatePIDValue();
    // SerialUSB.print("PIDValue is: ");
    // SerialUSB.println(PIDValue);
    updateDisplay();
  }
  runPIDCompareMatch = false;
}

void timedDisableHeater(){
  /*
  This function gets called after the heater is turned on at HEATER_TIMER_FREQUENCY Hz and terns the heater off after 
  heaterOnTime seconds (which got turned into heaterOnTimeCounts)
  */ 
  heaterCount++;
  heaterTimerCompareMatch = false;
  if (heaterCount >= heaterOnTimeCounts){
    heaterTimer.detachInterrupt();
    turnHeaterOff();
    heaterCount = 0;
  }
}

//////////////////// Setup and Main Loop
void setup() {
  SerialUSB.begin(9600); 
  while (!SerialUSB && millis() < 5000);

  // SerialUSB.print(F("\nStarting SAMD21 Timers on ")); SerialUSB.println(BOARD_NAME);
  // SerialUSB.println(SAMD_TIMER_INTERRUPT_VERSION);
  // SerialUSB.print(F("CPU Frequency = ")); SerialUSB.print(F_CPU / 1000000); SerialUSB.println(F(" MHz"));

  lcd.begin();
  Indio.setADCResolution(16);
  Indio.analogReadMode(pt1000Pin1, V10_p);
  Indio.analogReadMode(pt1000Pin2, V10_p);
  
  //set all other pins to INPUT in an attempt to avoid them defaulting to high (which is a known Industruino error). 
  Indio.digitalMode(1, INPUT); 
  Indio.digitalMode(2, INPUT); 
  Indio.digitalMode(3, INPUT); 
  Indio.digitalMode(4, INPUT); 
  Indio.digitalMode(5, INPUT); 
  Indio.digitalMode(6, INPUT); 
  Indio.digitalMode(7, INPUT); 

  Indio.digitalMode(heaterPin, OUTPUT);



  //IMPORTANT LINE!!!!
  Indio.digitalWrite(heaterPin, LOW); // see https://industruino.com/forum/help-1/question/industrino-d21g-all-digital-i-o-written-high-upon-power-up-561. It's known that you need to explicitly write Industruino pins to LOW on start






}

void loop() {
  readSerialAndUpdate();
  if (runPIDCompareMatch){
    runPID();
  }
  if (heaterTimerCompareMatch){
    timedDisableHeater();
  }
  if (!pidOn){
    PIDValue = 0.0;
    updateDisplay();
    delay(500);
  }
}