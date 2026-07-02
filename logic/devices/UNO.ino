//V5 goal: make the pedal signal 2ms instead of 1ms
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Including Libraries
#include <cdcacm.h> // this library is for using teh Arduino as a USB HOST (NOT device - search this up if unclear), and is for communicating with the TDC
#include <usbhub.h> // handles connection with usb hubs (i.e. dongles for adding more USB ports)
//#include "pgmstrings.h"
#include <SPI.h>
#include <TimerOne.h>

/*
For inforamtion on how to use the TDC, see the following:
https://www.bleuio.com/getting_started/docs/arduino_example/
*/


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Declaring variables
// PINS in the arduino
int Heating_Laser_pin = 7;
int Pedal_pin = 6; // this plugs into TEENSY and is the 'arming' signal (?) - on wire is labelled 'Pseudo pulse' to teensy (to ch2 on teensy) 
int Shutter_pin = 4;
int Monitor_Pin = 8; //! SWE

// TIMES (All times are in units of 100us, the values converted to ms are shown next to them) //! changed by SWE
int HeatingStartTime = 0; // == 0ms
int HeatingStopTime = HeatingStartTime + 3000; //after that, the timer must be restarted) //! SWE: why restarted ?
int StartTDCTime = HeatingStopTime;
int OpenPedalTime = StartTDCTime + 110;  
int ClosePedalTime = OpenPedalTime + 1; 
int OpenShutterTime = 0; //! SWE: no meaning for now
int CloseShutterTime = 0; //! SWE: no meaning for now
//int ReadTDCTime = OpenPedalTime + 2000 + 1000; //! 200 ms TDC time + 50 contingency for communication etc. 
//int ReadTDCTime = StartTDCTime + 2000 + 1000 + 1000; //! 200 ms TDC time + 50 contingency for communication etc. ORIGINAL
int ReadTDCTime = StartTDCTime + 2000 + 1000 + 1000; // PLAYING AROUND
//int HeatingStartTime = 0; // == 0ms
//int HeatingStopTime = 1000; // == 300ms (The heating should last around 300ms, after that, the timer must be restarted)
//int TDCTime = 1000; // == 100ms (The TDC will be open for at most 200ms)
//int OpenPedalTime = 1110; // == 111ms // 
//int ClosePedalTime = 1120; // == 112ms (The first pedal will be open for 1ms to ensure we get a pulse)
//int OpenShutterTime = 1123; // == 112.3ms (The last time possible for the prepulse is aprox. 200us after the pedal closes, so the shutter opens 300us after)
//int CloseShutterTime = 2900; // == 290ms (original 350ms) (The amount of time the shutter stays open is less relevant, so we can keep it open for a large time)
//int ReadTDCTime = 3600; // == original 360ms 

// FLAGS - for knowing the state of the program
volatile bool HeatingStartFlag = false; //! SWE: why not volatile?
volatile bool HeatingStopFlag = false;
volatile bool TDCFlag = false;
volatile bool OpenPedalFlag = false;
volatile bool ClosePedalFlag = false;
volatile bool OpenShutterFlag = false;
volatile bool CloseShutterFlag = false;
volatile bool wait = false; // Flag to prevent from restarting the experiment
volatile int steps = 0; //! SWE new step indicator

// OTHER VARIBLES
uint8_t rcode;
String command; // Command from the pi
volatile int time_c= 0; //! Time counter; SWE: made volatile

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Creating the class for the ACM and starting an Async operation (?) - I believe this is for communication with the TDC? 
class ACMAsyncOper : public CDCAsyncOper {
public:
    uint8_t OnInit(ACM *pacm);
};

uint8_t ACMAsyncOper::OnInit(ACM *pacm) {
  uint8_t rcode;
  // Set DTR = 1 RTS = 1
  rcode = pacm->SetControlLineState(3); // b11 is 3 in decimal
  // Error message
  if (rcode) {
    ErrorMessage<uint8_t>(PSTR("SetControlLineState"), rcode);
    return rcode;
  }

  LINE_CODING lc;
  lc.dwDTERate = 115200; // Baud Rate
  lc.bCharFormat = 1; // Stop Bits
  lc.bParityType = 0; // Parity (None = 0)
  lc.bDataBits = 8; // Bits

  // Error message
  rcode = pacm->SetLineCoding(&lc);
  if (rcode) {
    ErrorMessage<uint8_t>(PSTR("SetLineCoding"), rcode);
  }

  return rcode;
}

USB Usb;
ACMAsyncOper AsyncOper;
ACM Acm(&Usb, &AsyncOper);

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions

void heating() {
  /*
  DESCRIPTION:
    Switches the pin assigned to the heating laser to HIGH and sets the respective flag variable to true
  */
  HeatingStartFlag = true;
  digitalWrite(Heating_Laser_pin, HIGH);
}

void stop_heating() {
  /*
  DESCRIPTION:
    Switches the pin assigned to the heating laser to LOW and sets the respective flag variable to true
  */
  HeatingStopFlag = true;
  digitalWrite(Heating_Laser_pin, LOW);
  //Timer1.restart(); // Restarting the timer  //!turned off by SWE
}



void clear_tdc_buffer(){
  /*
  DESCRIPTION:
    This function is used to clear the tdc buffer
  */


  // uint8_t buf[256];
  uint8_t buf[64];
  uint16_t rcvd = sizeof(buf);
  uint8_t temp;

  // Keep requesting from buffer until the size of return data is zero
  while (rcvd) {
    temp = Acm.RcvData(&rcvd, buf);
    delay(30);
  }
}

void start_tdc() {
  /*
  DESCRIPTION:
    Sends the command to the TDC so that it starts getting timestamps. The TDC will be open for 200ms in TIMESTAMP mode and will expect TTL 
    Signals, The TDC takes about 1.6ms to start after this function is sent. This Funcion does not read the response of the TDC.
  */
  
  TDCFlag = true;
  // const char* command = "*RST;TTL;TIME200;TIMESTAMP;COUNTS? \n"; // I'm assuming this command will tell TDC to go into timestamp mode ORIGINAL
  const char* command = "*RST;TTL;TIME200;TIMESTAMP;COUNTS? \n"; // PLAYING AROUND
  rcode = Acm.SndData(strlen(command), (uint8_t*)command);
  if (rcode) {
      ErrorMessage<uint8_t>(PSTR("SndData"), rcode);
  }
  // Clear the Serial buffer by reading the incoming byte - why does this matter? 
  while (Serial.available()) {
      Serial.read();
  }
  delay(50);

}

void read_tdc(){
  /*DESCRIPTION:
  This Function is used to read the response from the TDC and send it by serial communication to the computer connected to the Arduino UNO.*/
  uint8_t buf[64]; // used to be buf[256], but (for a weird reason) would not allow us to use a 200ms gate with the TDC
  uint16_t rcvd = sizeof(buf); //sizeof(uint16_t) =1 (byte, is the units), so sizeof(buf) is 64 bytes 
  //uint8_t buf2[64];
  //uint16_t rcvd2 = sizeof(buf2);
  rcode = Acm.RcvData(&rcvd, buf); // give the buffer variable to Acm.RcvData
  if (rcode && rcode != hrNAK) {
      ErrorMessage<uint8_t>(PSTR("Ret"), rcode);
  }

  // Print received data to the serial monitor
  if (rcvd) { // if not empty
    Serial.write(buf,rcvd);  // Send all data at once
    Serial.write("END");  // Ensure Python detects the end
  }
  else {
  Serial.write("???");
  Serial.write("END");
  
  }

  // if( rcvd ) { 
  //   for(uint16_t i=0; i < rcvd; i++ ) { //! Looping seems to actually work with TIME200, but the program runs MUCH slower. 
  //     Serial.write((char)buf[i]); //Serial.print() goes MUCH slower . . . maybe write will be faster? 
  //     // it's quite interesting this works WITHOUT an END commmand
  //   }
  // }
  //ABORT command restarts the TDC counting cycle
  // const char* command = "ABORT \n"; // I'm assuming this command will tell TDC to go into timestamp mode
  // rcode = Acm.SndData(strlen(command), (uint8_t*)command);


}

// void read_tdc(){
//   /*
//   DESCRIPTION:
//     This Function is used to read the response from the TDC and send it by serial communication to the computer connected to the Arduino UNO.
//   */


//   // uint8_t buf[256];
//   uint8_t buf[64];
//   uint16_t rcvd = sizeof(buf);
//   uint8_t buf2[64];
//   uint16_t rcvd2 = sizeof(buf2);


//   rcode = Acm.RcvData(&rcvd, buf);
//   if (rcode && rcode != hrNAK) {
//       ErrorMessage<uint8_t>(PSTR("Ret"), rcode);
//   }
//   rcode = Acm.RcvData(&rcvd2, buf2);
//   if (rcode && rcode != hrNAK) {
//       ErrorMessage<uint8_t>(PSTR("Ret"), rcode);
//   }
  
//   // Print received data to the serial monitor
//   if (rcvd && !rcvd2) { // if not empty
//     Serial.write(buf,rcvd);  // Send all data at once
//     Serial.write("END");  // Ensure Python detects the end
//   }
//   else {
//   //Serial.write("???");
//   //Serial.write("END");
//     Serial.write(buf,rcvd);  // Send all data at once
//     Serial.write(buf2,rcvd2);  // Send all data at once
//     //Serial.write("END");  // Ensure Python detects the end
//     Serial.write("END");  // Ensure Python detects the end    
//   }

// }



void open_pedal() { // this signal "arms" the teensy?
  /*
  DESCRIPTION:
    Switches the pin assigned to the PIRL pedal to HIGH and sets the respective flag variable to true
  */
  OpenPedalFlag = true;
  digitalWrite(Pedal_pin, HIGH);
}

void close_pedal() {
  /*
  DESCRIPTION:
    Switches the pin assigned to the PIRL pedal to LOW and sets the respective flag variable to true
  */
  ClosePedalFlag = true;
  digitalWrite(Pedal_pin, LOW);
}

void open_shutter() {
  /*
  DESCRIPTION:
    Switches the pin assigned to the Shutter to HIGH and sets the respective flag variable to true
  */
  OpenShutterFlag = true;
  digitalWrite(Shutter_pin, HIGH);
}

void close_shutter() {
  /*
  DESCRIPTION:
    Switches the pin assigned to the Shutter to LOW and sets the respective flag variable to true
  */
  CloseShutterFlag = true;
  digitalWrite(Shutter_pin, LOW);
}

void main_function() {
  /*
  DESCRIPTION:
    This function is to be attached to the interrupt timer and will run every 100 microseconds. Every time it runs it will increment the time
    counter variable (time_c) so that we can keep track of the time. whenever the counter variable surpasses one of the times specified at 
    the start of the code it will run the respective function, declared above. Here we use ">=" instead of "==" in order to prevent erro crs in
    case the counter variable surpasses the specified time without ever beeing equal to it. We are also using the flag variables to keep track
    of which processes have already happend so that they don`t repeat.
  */

  time_c = time_c + 1; // Increments every 100 microseconds


  //! SWE if (time_c>= HeatingStartTime && !HeatingStartFlag) { // if it's time to start heating and we're not already heating
  if (time_c>= HeatingStartTime && steps==0) { // if it's time to start heating and we're not already heating
    heating();
    clear_tdc_buffer();//interesting why do we clear_tdc_buffer here - as preparation? //! because it is a good place to clear it, we even have to take care we do not clear it before the old data of previous shot is read !!
    steps = steps + 1; 
    //digitalWrite(Monitor_Pin, HIGH);

  }
  //! SWE if (time_c>= HeatingStopTime && !HeatingStopFlag) {
  if (time_c>= HeatingStopTime && steps ==1) {
    //heating();
    //digitalWrite(Monitor_Pin, LOW);
    stop_heating();
    steps = steps + 1; 
  }
  //!if (time_c>= StartTDCTime && !TDCFlag) {
  if (time_c>= StartTDCTime && steps == 2) {
    //digitalWrite(Monitor_Pin, LOW);
    start_tdc();
    steps = steps + 1; 
  }
  //!if (time_c>= OpenPedalTime && !OpenPedalFlag) {
  if (time_c>= OpenPedalTime && steps == 3) {
    //digitalWrite(Monitor_Pin, LOW);
    open_pedal();// is this functino still being used anymore? Yes it is
    steps = steps + 1; 
  }
  //if (time_c>= ClosePedalTime && !ClosePedalFlag) { //! SWE only determines the length of the pulse to teensy
  if (time_c>= ClosePedalTime && steps == 4) { //! SWE only determines the length of the pulse to teensy
    close_pedal();
    //digitalWrite(Monitor_Pin, LOW);
    steps = steps + 1; 
  }
  //if (time_c>= OpenShutterTime && !OpenShutterFlag) {    //! 7 lines turned off by SWE
  //  open_shutter();
  //}
  //if (time_c>= CloseShutterTime && !CloseShutterFlag) {
  //  Timer1.restart(); //! Why does the timer get restarted here!?!?!
  //  close_shutter();
  //}
  //if (time_c >= ReadTDCTime && CloseShutterFlag && wait) { //! SWE
  if (time_c >= ReadTDCTime && wait && TDCFlag) {
    //digitalWrite(Monitor_Pin, HIGH);
    Timer1.stop();
    read_tdc();
    delay(100);//! This might be a source of issues . . . also potentially not.   //SWE : changed to 100 from 1000
    wait = false;
    steps = 0;
    //digitalWrite(Monitor_Pin, LOW);
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Setup Function
void setup(void){
  /*
  DESCRIPTION:
    Initialize a timer object with 100us increments and attaches the main function to the timer. Stablishes Serial Communication with the 
    computer connected to the Arduino UNO, using a baud rate of 115200. Initialize the pins for the Heating laser, Pedal and Shutter as
    outputs. At the end of this setup function the timer is not yet running.
  */
  // Starting timer - confused on how this bit works. 
  Timer1.initialize(100); // 100 us precision
  Timer1.stop(); // Stopping the timer - seems to be stopped here so we can restart for measurements later. 
  Timer1.attachInterrupt(main_function); // Attaching main function - I'm confused on how this works - documentation? 

  // Starting Serial Communication
  Serial.begin(115200);
  #if !defined(__MIPSEL__)
    while (!Serial);
  #endif
  Serial.setTimeout(30); // what does this do?

  // Error message
  if (Usb.Init() == -1) {
    Serial.println("OSCOKIRQ failed to assert"); //what does this error message mean?
  }

  // Initializing Pins
  pinMode(Heating_Laser_pin, OUTPUT);
  pinMode(Pedal_pin, OUTPUT);
  pinMode(Shutter_pin, OUTPUT);
  pinMode(Monitor_Pin, OUTPUT);
  digitalWrite(Monitor_Pin, LOW);
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Loop Function
void loop(void){
  /*
  DESCRIPTION:
    Updates the state of the USB Host port in the shield. Waits for a command from the Attached computer, if the command is equal to "start\n"
    it will reset all of the flag variables, the time counter (time_c) and start the timer with the main function attached. The flag variable
    "wait" is used so that the UNO does not accept the command while the code is still running, and it it set back to false at the end of the
    main function.
  */


  delay(50);
  Usb.Task(); // Updating the USB Host Shield Port
  //Serial.println(Acm.isReady());
 // Serial.println("a");
  if (Acm.isReady() > 0){
    uint8_t rcode;
    if (Serial.available()){
      
      String Command = Serial.readString(); // Command from Pi
      //Serial.print(Command);
      
      if (Command == "start\n" && !wait) { // "start\n" will begin the experiment
        //Serial.println(Command);
        steps = 0; //! SWE
        wait = true; // Signals that the experiment is still ongoing, so that it does not receive any more commands 
        
        time_c = 0; // Resets the time counter
        
        // Reseting the flags
        HeatingStartFlag = false;
        HeatingStopFlag = false;
        TDCFlag = false;
        OpenPedalFlag = false;
        ClosePedalFlag = false;

        OpenShutterTime = 1123;
        OpenShutterFlag = false;
        CloseShutterFlag = false;


        Timer1.restart(); //this is the main thing that HAPPENS - starting the timer 

       } else if (Command == "start2\n" && !wait) { // "start2\n" will begin the experiment without opening or closing the shutter
        //Serial.println(Command);

        steps = 0; //! SWE
        wait = true; // Signals that the experiment is still ongoing, so that it does not receive any more commands 
        
        time_c = 0; // Resets the time counter
        
        // Reseting the flags
        HeatingStartFlag = false;
        HeatingStopFlag = false;
        TDCFlag = false;
        OpenPedalFlag = false;
        ClosePedalFlag = false;

        OpenShutterTime = 1000;
        OpenShutterFlag = false;
        CloseShutterFlag = false;
        

        Timer1.restart(); // Starts the timer

      }
    }
  }
}