////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Including Libraries
#include <Indio.h>
#include <Wire.h>
#include <Arduino.h>
#include <U8g2lib.h>
#include <I2C_eeprom.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Creating LCD Display object
U8G2_UC1701_MINI12864_F_2ND_4W_HW_SPI u8g2(U8G2_R2, /* cs=*/ 19, /* dc=*/ 22); 

// Creating an object to access the eeprom memory
#define EEPROM_SIZE 255
I2C_eeprom eeprom50(0x50, EEPROM_SIZE);

// Settings in each channel
volatile int CH1_type = 1; // CH1           Setting 1 displays the raw voltage received by the channel 
volatile int CH2_type = 1; // CH2           See Manual for the Gauges Supported by settings 2 and 3
volatile int CH3_type = 1; // CH3           
volatile int CH4_type = 1; // CH4  
int CH5_type = 0; // CH5

volatile int gauge_type = 1; // Variable to store the Gauge Selected by the USER
volatile int CH_selected = 1; // Variable to store the Channel selected by the USER

volatile int pos = 18; // Position of the cursor in the menu, Starts at 20 and increases by 13
volatile int last_pos; // Last possible position in the menu, used to stop the cursor from going further

volatile bool enter_flag = false; // Flag to detect if enter was pressed

String menu = "0"; // Menu page               Menu 0 = Channel Selection
//                                            Menu 1 = Settings Selection

String head;
String arg;
int value;
String command;
char zero = '0';
char set_code = 'S';
char read_code = 'R';
float pressure;
String units;
String success = "ok";
String expon = "e";

volatile int prev_end; // Position at which the previous string printed on the display ends

// Analog PINS for the voltage readings
int read_pin1 = 1; // CH1
int read_pin2 = 2; // CH2
int read_pin3 = 3; // CH3
int read_pin4 = 4; // CH4

// Voltage reading
float U_1; // CH1
float U_2; // CH2
float U_3; // CH3
float U_4; // CH4

// Value to be printed
float P_1; //CH1
float P_2; //CH2
float P_3; //CH3
float P_4; //CH4

String P_5_string; //CH5

// Values of the exponents in the scientific notation
int CH1_exp; //CH1
int CH2_exp; //CH2
int CH3_exp; //CH3
int CH4_exp; //CH4

// Pump pressure reading
const int TxEnablePin = 9;
byte byte_received = 1;
int d5;
int d4;
int d3;
int d2;
int d1;
int d0;


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
float set2_formula(float U){
  /*
  Given a Voltage reading U, returns the respective pressure according
  to the settings 2 conversion formula (See Manual for the Gauges tat use this setting)
  */
  return pow(10,(1.667 * U - 11.33));
}

float set3_formula(float U){
  /*
  Given a Voltage reading U, returns the respective pressure according
  to the settings 3 conversion formula (See Manual for the Gauges tat use this setting)
  */
  return pow(10,((U-6.143) / 1.286));
}

float voltage_to_pressure(int type, float voltage){
  /*
  Converts the voltage to pressure according to the formula
  of the specified Gauge Type
  */
  if (type == 1) {
    return voltage;
  }
  if (type == 2) {
    return set2_formula(voltage);
  }
  if (type == 3) {
    return set3_formula(voltage);
  }
}

int correct_exponents(float pressure, int type){
  /*
  Finds the correct value needed to be on the exponent of the scientific notation, so that the number shown
  is never smaller than 1.
  */
  int counter = 0;

  if (type == 2){
    if(pressure > 1000){
      return 0;
    }
    if(pressure < pow(10, -9)){
      return 0;
    }
  }

  if (type == 3){
    if(pressure > 1000){
      return 0;
    }
    if(pressure < 5 * pow(10, -4)){
      return 0;
    }
  }

  while (pressure < 1){
    pressure *= 10;
    counter ++;
  }
  return -counter;
}

float correct_value(float pressure, int type){
  /*
  Corrects the value of the pressure so that it is larger than one, must be used along with
  correct_exponents so that the actual value is not wrong
  */

  int counter = 0;
  if (type == 2){
    if(pressure > 1000){
      return 1000;
    }
    if(pressure < pow(10, -9)){
      return 0;
    }
  }

  if (type == 3){
    if(pressure > 1000){
      return 1000;
    }
    if(pressure < 5 * pow(10, -4)){
      return 0;
    }
  }

  while (pressure < 1){
    pressure *= 10;
    counter ++;
  }
  return pressure;
}


const char* num_to_type(int type_num){
  /*
  Given a number returns the respective gauge type:
    1 = Pfeiffer 251/261 ("PF  ")
    2 = KJLC CCPG ("CCPG")
    3 = KJLC PIR ("PIR ")
    4 = Raw Voltage ("VOLT")
  */
  if (type_num == 0){
    return "----";
  }
  if (type_num == 1){
    return "SET1";
  }
  if (type_num == 2){
    return "SET2";
  }
  if (type_num == 3){
    return "SET3";
  }
}

void print_info(const char* Channel, int height, int Setting, int exponent, float value){
  /*
  Given the information about the channel, prints the values in the lcd screen
  in the correct position
  */
  prev_end = 10; // Keep track of the last position
  prev_end += u8g2.drawStr(7, height, Channel); // Print the Channel
  prev_end += u8g2.drawStr(prev_end, height, " ");
  u8g2.drawVLine(prev_end-2, 14, u8g2.getDisplayHeight()-14); // Vertical line to separate
  
  prev_end += u8g2.drawStr(prev_end, height, num_to_type(Setting)); // Print the setting
  prev_end += u8g2.drawStr(prev_end, height, " ");
  u8g2.drawVLine(prev_end, 14, u8g2.getDisplayHeight()-14); // Vertical line to separate
  
  prev_end += u8g2.drawStr(prev_end + 2, height, String(value, 2).c_str()); // Print the Pressure/Voltage Value
  prev_end += u8g2.drawStr(prev_end, height, " ");
  
  if (exponent != 99){ // Chacking for error code (99)
    if (exponent != 0){ // If the exponent is zero we don't need to print the scientific notation
      prev_end += u8g2.drawStr(prev_end, height, "e");
      prev_end += u8g2.drawStr(prev_end, height, String(exponent).c_str());
    }
    if (Setting == 1){// Volts
      prev_end += u8g2.drawStr(prev_end, height, "V   ");
    }else{ // mbar
      prev_end += u8g2.drawStr(prev_end, height, "mbar");
    }
  } else { // if the error code is received, print an X instead of the units
    prev_end += u8g2.drawStr(prev_end, height, "X       ");
  }
}

void print_info5(const char* Channel, int height, int Setting, String print_value){
  /*
  Given the information about the channel, prints the values in the lcd screen
  in the correct position
  */
  prev_end = 10; // Keep track of the last position
  prev_end += u8g2.drawStr(7, height, Channel); // Print the Channel
  prev_end += u8g2.drawStr(prev_end, height, " ");

  prev_end += u8g2.drawStr(prev_end, height, num_to_type(Setting)); // Print the setting
  prev_end += u8g2.drawStr(prev_end, height, " ");
  
  prev_end += u8g2.drawStr(prev_end + 2, height, print_value.c_str()); // Print the Pressure/Voltage Value
  prev_end += u8g2.drawStr(prev_end, height, " ");
  
}

void down() {
  /*
  Function to be triggered when the down key is pressed
  increases position by 1 if its not in the last position
  */
  if (pos < last_pos-10){
    pos += 10;
  }
  u8g2.clearDisplay();
}

void up() {
  /*
  Function to be triggered when the up key is pressed
  decreases position by 1 if its not in the first position
  */
  if (pos > 21){
    pos -= 10;
  }
  u8g2.clearDisplay();
}

void enter() {
  /*
  Function to be triggered when the enter key is pressed
  changes the enter_flag to true
  */
  enter_flag = true;
  u8g2.clearDisplay();
}

int serial_interpreter(String argument, int channel_type, float pressure, int exponent){
  
  String arg_read = "READ\n";
  arg_read.toUpperCase();
  for (int i = 0; i < argument.length(); i++){
    if (argument.substring(i, i+1) == " "){ 
      arg = argument.substring(0, i);
      value = argument.substring(i+1).toInt();
    }
  }
  if (arg == "SET"){
    if (value == 1 || value == 2 || value == 3){
      SerialUSB.println(success);
      return value;
    }
    else{
      SerialUSB.println("Invalid Setting");
      return channel_type;
    }
  }
  else if (arg == arg_read){
    SerialUSB.print(pressure);
    SerialUSB.print(expon);
    SerialUSB.println(exponent);
    return channel_type;
  }
  else {
    SerialUSB.print("Invalid Argument");
    return channel_type;
  }
}

void setup() {
  SerialUSB.begin(9600);
  Serial.begin(9600);

  pinMode(TxEnablePin, OUTPUT);

  Wire.begin();
  eeprom50.begin();

  // Setting up the lcd Screen parameters
  u8g2.begin();
  u8g2.clearDisplay(); // Clearing anything left on the display

  u8g2.setDrawColor(1);
    
  pinMode(26, OUTPUT); //           Turning on the background light
  digitalWrite(26, HIGH); //        of the display using pin 26

  // Showing the Setup Screen
  setup_screen();

  Indio.setADCResolution(16);

  // Membrane buttons
  //pinMode(23, INPUT); // DOWN
  Indio.digitalMode(1, OUTPUT); // Clear CH1 to LOW
  Indio.digitalWrite(1, LOW); //
  Indio.digitalMode(1, INPUT); // Set CH1 as an input
  Indio.digitalMode(2, OUTPUT); // Clear CH1 to LOW
  Indio.digitalWrite(2, LOW); //
  Indio.digitalMode(2, INPUT); // Set CH1 as an input
  Indio.digitalMode(3, OUTPUT); // Clear CH1 to LOW
  Indio.digitalWrite(3, LOW); //
  Indio.digitalMode(3, INPUT); // Set CH1 as an input

  
  // Getting the Gauge types from the eeprom memory
  get_memory();
  CH1_type = eeprom50.readByte(1); // CH1
  CH2_type = eeprom50.readByte(2); // CH2
  CH3_type = eeprom50.readByte(3); // CH3
  CH4_type = eeprom50.readByte(4); // CH4

  //setting up the analog read pins 
  Indio.analogReadMode(read_pin1, V10); // CH1
  Indio.analogReadMode(read_pin2, V10); // CH2
  Indio.analogReadMode(read_pin3, V10); // CH3
  Indio.analogReadMode(read_pin4, V10); // CH4
  
  delay(2000);
  u8g2.clearDisplay(); // Clearing the setup screen
}


void loop() {
  u8g2.clearBuffer(); // Clearing the information in the Buffer


  // read voltages 
  U_1 = Indio.analogRead(read_pin1); // CH1
  U_2 = Indio.analogRead(read_pin2); // CH2
  U_3 = Indio.analogRead(read_pin3); // CH3
  U_4 = Indio.analogRead(read_pin4); // CH4

  // Translate to pressure 
  P_1 = voltage_to_pressure(CH1_type, U_1); // CH1
  P_2 = voltage_to_pressure(CH2_type, U_2); // CH2
  P_3 = voltage_to_pressure(CH3_type, U_3); // CH3
  P_4 = voltage_to_pressure(CH4_type, U_4); // CH4
  P_5_string = pump_pressure(); // CH5


  // Getting the exponents
  CH1_exp = correct_exponents(P_1, CH1_type); // CH1
  CH2_exp = correct_exponents(P_2, CH2_type); // CH2
  CH3_exp = correct_exponents(P_3, CH3_type); // CH3
  CH4_exp = correct_exponents(P_4, CH4_type); // CH4

  // Correcting the values for scientific notation
  P_1 = correct_value(P_1, CH1_type); // CH1
  P_2 = correct_value(P_2, CH2_type); // CH2
  P_3 = correct_value(P_3, CH3_type); // CH3
  P_4 = correct_value(P_4, CH4_type); // CH4

  //Serial Communication
  if (SerialUSB.available() > 0) { //check for connection
    command = SerialUSB.readString();

    //Divide command by header and argument
    for (int i = 0; i < command.length(); i++){
      if (command.substring(i, i+1) == ":"){ 
        head = command.substring(0, i);
        arg = command.substring(i+1);
      }
    }
    
    head.toUpperCase();
    arg.toUpperCase();

    if (head == "CH1"){
      CH1_type = serial_interpreter(arg, CH1_type, P_1, CH1_exp);
      eeprom50.writeByte(1, CH1_type);
    }else if (head == "CH2"){
      CH2_type = serial_interpreter(arg, CH2_type, P_2, CH2_exp);
      eeprom50.writeByte(2, CH2_type);
    }else if (head == "CH3"){
      CH3_type = serial_interpreter(arg, CH3_type, P_3, CH3_exp);
      eeprom50.writeByte(3, CH3_type);
    }else if (head == "CH4"){
      CH4_type = serial_interpreter(arg, CH4_type, P_4, CH4_exp);
      eeprom50.writeByte(4, CH4_type);
    }else{
      SerialUSB.print("Invalid Header");
    }
   }


  // Reading membrane buttons
  if (Indio.digitalRead(1)){ 
    down();
  }
  if (Indio.digitalRead(2)){
    enter();
  }
  if (Indio.digitalRead(3)){
    up();
  }

  if (menu == "0"){ // Menu 0
    menu_0();
  }
  if (menu == "1"){
    menu_1();
  }
  u8g2.sendBuffer();
}


void menu_0(){
  // Printing Header
  u8g2.clearBuffer();	
  u8g2.setFont(u8g2_font_sonicmania_te);
  u8g2.drawButtonUTF8(5, 12, U8G2_BTN_INV, u8g2.getDisplayWidth()-5*2,  5,  0, "Channel Selection" );
  u8g2.drawHLine(0, 0, u8g2.getDisplayWidth());
  u8g2.drawHLine(0, 1, u8g2.getDisplayWidth());
  u8g2.setDrawColor(0);
  u8g2.drawHLine(0, 14, u8g2.getDisplayWidth());
  u8g2.setDrawColor(1);
  last_pos = 52;
  
  // Print cursor
  u8g2.drawDisc(2, pos, 2, U8G2_DRAW_ALL);

  // Printing Options
  u8g2.setFont(u8g2_font_profont10_mf);

 


  print_info("CH1", 22, CH1_type, CH1_exp, P_1); // CH1
  print_info("CH2", 32, CH2_type, CH2_exp, P_2); // CH2
  print_info("CH3", 42, CH3_type, CH3_exp, P_3); // CH3
  print_info("CH4", 52, CH4_type, CH4_exp, P_4); // CH4
  print_info5("485", 62, CH5_type, P_5_string); // CH5
  

  if (enter_flag == true){
    enter_flag = false;
    menu = "1";
    CH_selected = (pos-18) / 10 + 1;
    pos = 18;
  }
}

void menu_1(){
  // Printing Header
  u8g2.clearBuffer();	
  u8g2.setFont(u8g2_font_sonicmania_te);
  u8g2.drawButtonUTF8(5, 12, U8G2_BTN_INV, u8g2.getDisplayWidth()-5*2,  5,  0, "Channel");
  u8g2.setDrawColor(0);
  u8g2.drawStr(60, 12, String(CH_selected).c_str());
  u8g2.setDrawColor(1);
  u8g2.drawHLine(0, 0, u8g2.getDisplayWidth());
  u8g2.drawHLine(0, 1, u8g2.getDisplayWidth());
  u8g2.setDrawColor(0);
  u8g2.drawHLine(0, 14, u8g2.getDisplayWidth());
  u8g2.setDrawColor(1);
  last_pos = 42;
  
  // Print cursor
  u8g2.drawDisc(2, pos, 2, U8G2_DRAW_ALL);

  // Printing Options
  u8g2.setFont(u8g2_font_profont10_mf);

  u8g2.drawStr(7, 22, num_to_type(1));
  u8g2.drawStr(7, 32, num_to_type(2));
  u8g2.drawStr(7, 42, num_to_type(3));

  if (enter_flag == true){
    u8g2.clearDisplay();
    enter_flag = false;
    menu = "0";
    int gauge_type = (pos-18) / 10 + 1;;
    if (CH_selected == 1){
      CH1_type = gauge_type;
      eeprom50.writeByte(1, gauge_type);
    }
    if (CH_selected == 2){
      CH2_type = gauge_type;
      eeprom50.writeByte(2, gauge_type);
    }
    if (CH_selected == 3){
      CH3_type = gauge_type;
      eeprom50.writeByte(3, gauge_type);
    }
    if (CH_selected == 4){
      CH4_type = gauge_type;
      eeprom50.writeByte(4, gauge_type);
    }
    pos = 18;
  }
}

void get_memory(){
  if (eeprom50.readByte(1) != 1 && eeprom50.readByte(1) != 2 && eeprom50.readByte(1) != 3){
    eeprom50.writeByte(1, 1);
    eeprom50.writeByte(2, 1);
    eeprom50.writeByte(3, 1);
    eeprom50.writeByte(4, 1);
  }else if (eeprom50.readByte(2) != 1 && eeprom50.readByte(2) != 2 && eeprom50.readByte(2) != 3){
    eeprom50.writeByte(1, 1);
    eeprom50.writeByte(2, 1);
    eeprom50.writeByte(3, 1);
    eeprom50.writeByte(4, 1);
  }else if (eeprom50.readByte(3) != 1 && eeprom50.readByte(3) != 2 && eeprom50.readByte(3) != 3){
    eeprom50.writeByte(1, 1);
    eeprom50.writeByte(2, 1);
    eeprom50.writeByte(3, 1);
    eeprom50.writeByte(4, 1);
  }else if (eeprom50.readByte(4) != 1 && eeprom50.readByte(4) != 2 && eeprom50.readByte(4) != 3){
    eeprom50.writeByte(1, 1);
    eeprom50.writeByte(2, 1);
    eeprom50.writeByte(3, 1);
    eeprom50.writeByte(4, 1);
  }
}

String pump_pressure(){
  digitalWrite(TxEnablePin, HIGH);

  //unit address
  Serial.write(48);
  Serial.write(48);
  Serial.write(49);

  //for queary 0,0 for control or response 1,0 
  Serial.write(48);
  Serial.write(48);

  //parameter number
  Serial.write(55);
  Serial.write(52);
  Serial.write(48); 

  //data length 
  Serial.write(48);
  Serial.write(50);

  //data
  Serial.write(61);
  Serial.write(63);

  //checksum ( sum of ascII before this mod 256)
  Serial.write(49);
  Serial.write(48);
  Serial.write(54);

  //character return
  Serial.write(13);

  delay(5);
  digitalWrite(TxEnablePin, LOW);

  if (Serial.available()<1){
    String s = "X       ";
    return s;
  }

  byte_received = 0;
  int counter = 1;
  while(byte_received!=13 && byte_received != 255){
    byte_received = Serial.read();
    if (counter == 11)
      d5 = byte_received;
    if (counter == 12)
      d4 = byte_received;
    if (counter == 13)
      d3 = byte_received;
    if (counter == 14)
      d2 = byte_received;
    if (counter == 15)
      d1 = byte_received;
    if (counter == 16)
      d0 = byte_received;
    counter++;
  }

  int e = (String(d1-48) + String(d0-48)).toInt();
  String s = String(d5-48) + "." + String(d4-48) + String(d3-48) + "e" + String(e-20) + " mbar";
  return s;
}

void setup_screen(){
  /*
  Function that manualy sets the pixels in the screen to show the setup screen
  */
  u8g2.setFont( u8g2_font_ncenB10_tr);
  int d = 85; // Delay

  u8g2.clear();
  delay(d);
  // Line 1 
  u8g2.drawPixel(0, 59);
  u8g2.drawPixel(0, 60);
  u8g2.drawPixel(0, 61);
  // Line 2
  u8g2.drawPixel(0, 40);
  u8g2.drawPixel(0, 41);
  // Line 3
  u8g2.drawPixel(0, 31);
  u8g2.drawPixel(1, 31);
  u8g2.drawPixel(2, 31);
  u8g2.drawPixel(2, 32);
  // Line 4
  u8g2.drawPixel(0, 42);
  u8g2.drawPixel(1, 42);
  u8g2.drawPixel(2, 42);
  u8g2.drawPixel(3, 42);
  u8g2.drawPixel(3, 41);
  u8g2.drawPixel(4, 41);
  
  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(1, 60);
  u8g2.drawPixel(1, 61);
  u8g2.drawPixel(1, 62);
  // Line 2
  u8g2.drawPixel(1, 41);
  u8g2.drawPixel(1, 42);
  u8g2.drawPixel(2, 42);
  u8g2.drawPixel(2, 43);
  // Line 3
  u8g2.drawPixel(3, 32);
  u8g2.drawPixel(4, 32);
  u8g2.drawPixel(5, 32);
  // Line 4
  u8g2.drawPixel(5, 41);
  u8g2.drawPixel(6, 41);
  u8g2.drawPixel(7, 41);
  u8g2.drawPixel(7, 40);
  u8g2.drawPixel(8, 40);
  
  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(2, 60);
  u8g2.drawPixel(2, 61);
  u8g2.drawPixel(2, 62);
  // Line 2
  u8g2.drawPixel(3, 42);
  u8g2.drawPixel(3, 43);
  u8g2.drawPixel(4, 43);
  u8g2.drawPixel(4, 44);
  // Line 3
  u8g2.drawPixel(6, 32);
  u8g2.drawPixel(7, 32);
  u8g2.drawPixel(7, 33);
  u8g2.drawPixel(8, 33);
  // Line 4
  u8g2.drawPixel(9, 40);
  u8g2.drawPixel(10, 40);
  u8g2.drawPixel(11, 40);
  u8g2.drawPixel(11, 39);
  u8g2.drawPixel(12, 39);
  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(3, 61);
  u8g2.drawPixel(3, 62);
  u8g2.drawPixel(3, 63);
  // Line 2
  u8g2.drawPixel(5, 43);
  u8g2.drawPixel(5, 44);
  u8g2.drawPixel(6, 44);
  u8g2.drawPixel(6, 45);
  // Line 3
  u8g2.drawPixel(9, 33);
  u8g2.drawPixel(10, 33);
  u8g2.drawPixel(11, 33);
  u8g2.drawPixel(11, 34);
  u8g2.drawPixel(12, 34);
  // Line 4
  u8g2.drawPixel(13, 39);
  u8g2.drawPixel(14, 39);
  u8g2.drawPixel(15, 39);
  u8g2.drawPixel(16, 39);
  
  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(4, 62);
  u8g2.drawPixel(4, 63);
  // Line 2
  u8g2.drawPixel(7, 45);
  u8g2.drawPixel(7, 46);
  u8g2.drawPixel(8, 45);
  u8g2.drawPixel(8, 46);
  // Line 3
  u8g2.drawPixel(13, 34);
  u8g2.drawPixel(14, 34);
  u8g2.drawPixel(15, 34);
  u8g2.drawPixel(15, 35);
  // Line 4
  u8g2.drawPixel(16, 38);
  u8g2.drawPixel(17, 38);
  u8g2.drawPixel(18, 38);
  u8g2.drawPixel(19, 38);
  u8g2.drawPixel(20, 38);
  
  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(5, 62);
  u8g2.drawPixel(5, 63);
  // Line 2
  u8g2.drawPixel(9, 46);
  u8g2.drawPixel(9, 47);
  u8g2.drawPixel(10, 47);
  u8g2.drawPixel(10, 48);
  u8g2.drawPixel(10, 47);
  u8g2.drawPixel(10, 48);
  // Line 3
  u8g2.drawPixel(16, 35);
  u8g2.drawPixel(17, 35);
  u8g2.drawPixel(18, 35);
  u8g2.drawPixel(19, 35);
  u8g2.drawPixel(19, 36);
  // Line 4
  u8g2.drawPixel(21, 38);
  u8g2.drawPixel(21, 37);
  u8g2.drawPixel(22, 37);
  u8g2.drawPixel(23, 37);
  u8g2.drawPixel(24, 37);
  
  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(6, 63);
  // Line 2
  u8g2.drawPixel(11, 47);
  u8g2.drawPixel(11, 48);
  u8g2.drawPixel(12, 48);
  u8g2.drawPixel(12, 49);
  // Line 3
  u8g2.drawPixel(20, 36);
  u8g2.drawPixel(21, 36);
  u8g2.drawPixel(22, 36);
  u8g2.drawPixel(23, 36);
  u8g2.drawPixel(23, 37);
  // Line 4
  u8g2.drawPixel(25, 37);
  u8g2.drawPixel(26, 37);
  u8g2.drawPixel(26, 36);
  u8g2.drawPixel(27, 36);
  u8g2.drawPixel(28, 36);
  u8g2.drawPixel(29, 36);

  u8g2.sendBuffer();
  delay(d);
  // Line 1
  u8g2.drawPixel(7, 63);
  // Line 2
  u8g2.drawPixel(13, 49);
  u8g2.drawPixel(13, 50);
  u8g2.drawPixel(14, 49);
  u8g2.drawPixel(14, 50);
  u8g2.drawPixel(15, 49);
  u8g2.drawPixel(15, 50);
  // Line 3
  u8g2.drawPixel(24, 37);
  u8g2.drawPixel(25, 37);
  u8g2.drawPixel(26, 37);
  u8g2.drawPixel(27, 37);
  u8g2.drawPixel(27, 38);
  // Line 4
  u8g2.drawPixel(30, 36);
  u8g2.drawPixel(31, 36);
  u8g2.drawPixel(32, 36);
  u8g2.drawPixel(32, 35);
  u8g2.drawPixel(33, 35);
  u8g2.drawPixel(34, 35);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(16, 50);
  u8g2.drawPixel(16, 51);
  u8g2.drawPixel(17, 50);
  u8g2.drawPixel(17, 51);
  u8g2.drawPixel(18, 51);
  u8g2.drawPixel(18, 52);
  // Line 3
  u8g2.drawPixel(28, 38);
  u8g2.drawPixel(29, 38);
  u8g2.drawPixel(30, 38);
  u8g2.drawPixel(31, 38);
  u8g2.drawPixel(31, 39);
  u8g2.drawPixel(32, 39);
  // Line 4
  u8g2.drawPixel(35, 35);
  u8g2.drawPixel(36, 35);
  u8g2.drawPixel(37, 35);
  u8g2.drawPixel(38, 35);
  u8g2.drawPixel(38, 34);
  u8g2.drawPixel(39, 34);
  u8g2.drawPixel(40, 34);
  u8g2.drawPixel(41, 34);
  u8g2.drawPixel(42, 34);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(19, 51);
  u8g2.drawPixel(19, 52);
  u8g2.drawPixel(20, 52);
  u8g2.drawPixel(20, 53);
  u8g2.drawPixel(21, 52);
  u8g2.drawPixel(21, 53);
  u8g2.drawPixel(22, 53);
  u8g2.drawPixel(22, 54);
  // Line 3
  u8g2.drawPixel(33, 39);
  u8g2.drawPixel(34, 39);
  u8g2.drawPixel(35, 39);
  u8g2.drawPixel(35, 40);
  u8g2.drawPixel(36, 40);
  u8g2.drawPixel(37, 40);
  // Line 4
  u8g2.drawPixel(43, 34);
  u8g2.drawPixel(44, 34);
  u8g2.drawPixel(45, 34);
  u8g2.drawPixel(46, 34);
  u8g2.drawPixel(46, 35);
  u8g2.drawPixel(47, 35);
  u8g2.drawPixel(48, 35);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(23, 53);
  u8g2.drawPixel(23, 54);
  u8g2.drawPixel(24, 54);
  u8g2.drawPixel(24, 55);
  u8g2.drawPixel(25, 54);
  u8g2.drawPixel(25, 55);
  u8g2.drawPixel(26, 55);
  u8g2.drawPixel(26, 56);
  // Line 3
  u8g2.drawPixel(38, 40);
  u8g2.drawPixel(39, 40);
  u8g2.drawPixel(39, 41);
  u8g2.drawPixel(40, 41);
  // Line 4
  u8g2.drawPixel(49, 35);
  u8g2.drawPixel(50, 35);
  u8g2.drawPixel(51, 35);
  u8g2.drawPixel(52, 35);
  u8g2.drawPixel(52, 36);
  u8g2.drawPixel(53, 36);
  u8g2.drawPixel(54, 36);
  u8g2.drawPixel(55, 36);
  u8g2.drawPixel(56, 36);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(27, 55);
  u8g2.drawPixel(27, 56);
  u8g2.drawPixel(28, 55);
  u8g2.drawPixel(28, 56);
  u8g2.drawPixel(29, 56);
  u8g2.drawPixel(29, 57);
  // Line 3
  u8g2.drawPixel(41, 41);
  u8g2.drawPixel(42, 41);
  u8g2.drawPixel(42, 42);
  u8g2.drawPixel(43, 42);
  u8g2.drawPixel(44, 42);
  // Line 4
  u8g2.drawPixel(57, 36);
  u8g2.drawPixel(58, 36);
  u8g2.drawPixel(58, 37);
  u8g2.drawPixel(59, 37);
  u8g2.drawPixel(60, 37);
  u8g2.drawPixel(61, 37);
  u8g2.drawPixel(62, 37);
  u8g2.drawPixel(63, 37);
  u8g2.drawPixel(63, 38);
  u8g2.drawPixel(64, 38);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(30, 56);
  u8g2.drawPixel(30, 57);
  u8g2.drawPixel(31, 57);
  u8g2.drawPixel(31, 58);
  u8g2.drawPixel(32, 57);
  u8g2.drawPixel(32, 58);
  u8g2.drawPixel(33, 57);
  u8g2.drawPixel(33, 58);
  // Line 3
  u8g2.drawPixel(45, 42);
  u8g2.drawPixel(45, 43);
  u8g2.drawPixel(46, 43);
  u8g2.drawPixel(47, 43);
  u8g2.drawPixel(48, 43);
  u8g2.drawPixel(48, 44);
  u8g2.drawPixel(49, 44);
  // Line 4
  u8g2.drawPixel(65, 38);
  u8g2.drawPixel(66, 38);
  u8g2.drawPixel(67, 38);
  u8g2.drawPixel(68, 38);
  u8g2.drawPixel(68, 39);
  u8g2.drawPixel(69, 39);
  u8g2.drawPixel(70, 39);
  u8g2.drawPixel(71, 39);
  u8g2.drawPixel(72, 39);
  u8g2.drawPixel(73, 39);
  u8g2.drawPixel(73, 40);
  u8g2.drawPixel(74, 40);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(34, 57);
  u8g2.drawPixel(34, 58);
  u8g2.drawPixel(35, 58);
  u8g2.drawPixel(35, 59);
  // Line 3
  u8g2.drawPixel(50, 44);
  u8g2.drawPixel(51, 44);
  u8g2.drawPixel(51, 45);
  u8g2.drawPixel(52, 45);
  u8g2.drawPixel(53, 45);
  u8g2.drawPixel(54, 45);
  u8g2.drawPixel(54, 46);
  // Line 4
  u8g2.drawPixel(75, 40);
  u8g2.drawPixel(76, 40);
  u8g2.drawPixel(77, 40);
  u8g2.drawPixel(77, 41);
  u8g2.drawPixel(78, 41);
  u8g2.drawPixel(79, 41);
  u8g2.drawPixel(80, 41);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(34, 57);
  u8g2.drawPixel(34, 58);
  u8g2.drawPixel(35, 58);
  u8g2.drawPixel(35, 59);
  // Line 3
  u8g2.drawPixel(55, 46);
  u8g2.drawPixel(56, 46);
  u8g2.drawPixel(57, 46);
  u8g2.drawPixel(57, 47);
  u8g2.drawPixel(58, 47);
  u8g2.drawPixel(59, 47);
  u8g2.drawPixel(60, 47);
  u8g2.drawPixel(60, 48);
  // Line 4
  u8g2.drawPixel(81, 41);
  u8g2.drawPixel(81, 42);
  u8g2.drawPixel(82, 42);
  u8g2.drawPixel(83, 42);
  u8g2.drawPixel(84, 42);
  u8g2.drawPixel(84, 43);
  u8g2.drawPixel(85, 43);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(36, 58);
  u8g2.drawPixel(36, 59);
  u8g2.drawPixel(37, 58);
  u8g2.drawPixel(37, 59);
  // Line 3
  u8g2.drawPixel(61, 48);
  u8g2.drawPixel(62, 48);
  u8g2.drawPixel(63, 48);
  u8g2.drawPixel(63, 49);
  u8g2.drawPixel(64, 49);
  u8g2.drawPixel(65, 49);
  u8g2.drawPixel(66, 49);
  u8g2.drawPixel(66, 50);
  // Line 4
  u8g2.drawPixel(86, 43);
  u8g2.drawPixel(87, 43);
  u8g2.drawPixel(87, 44);
  u8g2.drawPixel(88, 44);
  u8g2.drawPixel(89, 44);
  u8g2.sendBuffer();

  delay(d);
  // Line 2
  u8g2.drawPixel(38, 59);
  u8g2.drawPixel(38, 60);
  // Line 3
  u8g2.drawPixel(67, 50);
  u8g2.drawPixel(68, 50);
  u8g2.drawPixel(69, 50);
  u8g2.drawPixel(69, 51);
  u8g2.drawPixel(70, 51);
  u8g2.drawPixel(71, 51);
  u8g2.drawPixel(71, 52);
  // Line 4
  u8g2.drawPixel(90, 44);
  u8g2.drawPixel(90, 45);
  u8g2.drawPixel(91, 45);
  u8g2.drawPixel(92, 45);
  u8g2.drawPixel(93, 45);
  u8g2.drawPixel(93, 46);
  u8g2.drawPixel(94, 46);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(39, 59);
  u8g2.drawPixel(39, 60);
  u8g2.drawPixel(40, 59);
  u8g2.drawPixel(40, 60);
  u8g2.drawPixel(41, 59);
  u8g2.drawPixel(41, 60);
  // Line 3
  u8g2.drawPixel(72, 52);
  u8g2.drawPixel(73, 52);
  u8g2.drawPixel(73, 53);
  u8g2.drawPixel(74, 53);
  u8g2.drawPixel(75, 53);
  u8g2.drawPixel(75, 54);
  u8g2.drawPixel(76, 54);
  u8g2.drawPixel(77, 54);
  u8g2.drawPixel(77, 55);
  // Line 4
  u8g2.drawPixel(95, 46);
  u8g2.drawPixel(96, 46);
  u8g2.drawPixel(96, 47);
  u8g2.drawPixel(97, 47);
  u8g2.drawPixel(98, 47);
  u8g2.drawPixel(99, 47);
  u8g2.drawPixel(99, 48);
  u8g2.drawPixel(100, 48);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(42, 60);
  u8g2.drawPixel(42, 61);
  u8g2.drawPixel(43, 60);
  u8g2.drawPixel(43, 61);
  u8g2.drawPixel(44, 60);
  u8g2.drawPixel(44, 61);
  u8g2.drawPixel(45, 60);
  u8g2.drawPixel(45, 61);
  u8g2.drawPixel(46, 60);
  u8g2.drawPixel(46, 61);
  // Line 3
  u8g2.drawPixel(78, 55);
  u8g2.drawPixel(79, 55);
  u8g2.drawPixel(79, 56);
  u8g2.drawPixel(80, 56);
  u8g2.drawPixel(81, 56);
  u8g2.drawPixel(81, 57);
  u8g2.drawPixel(82, 57);
  u8g2.drawPixel(83, 57);
  u8g2.drawPixel(83, 58);
  u8g2.drawPixel(84, 58);
  // Line 4
  u8g2.drawPixel(101, 48);
  u8g2.drawPixel(101, 49);
  u8g2.drawPixel(102, 49);
  u8g2.drawPixel(103, 49);
  u8g2.drawPixel(103, 50);
  u8g2.drawPixel(104, 50);
  u8g2.drawPixel(105, 50);
  u8g2.drawPixel(105, 51);
  u8g2.drawPixel(106, 51);
  u8g2.drawPixel(107, 51);
  u8g2.drawPixel(107, 52);
  u8g2.drawPixel(108, 52);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(47, 61);
  u8g2.drawPixel(47, 62);
  u8g2.drawPixel(48, 61);
  u8g2.drawPixel(48, 62);
  u8g2.drawPixel(49, 61);
  u8g2.drawPixel(49, 62);
  u8g2.drawPixel(50, 61);
  u8g2.drawPixel(50, 62);
  // Line 3
  u8g2.drawPixel(85, 58);
  u8g2.drawPixel(85, 59);
  u8g2.drawPixel(86, 59);
  u8g2.drawPixel(87, 59);
  u8g2.drawPixel(87, 60);
  u8g2.drawPixel(88, 60);
  // Line 4
  u8g2.drawPixel(109, 52);
  u8g2.drawPixel(109, 53);
  u8g2.drawPixel(110, 53);
  u8g2.drawPixel(111, 53);
  u8g2.drawPixel(111, 54);
  u8g2.drawPixel(112, 54);
  u8g2.drawPixel(113, 54);
  u8g2.drawPixel(113, 55);
  u8g2.drawPixel(114, 55);

  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(51, 61);
  u8g2.drawPixel(51, 62);
  u8g2.drawPixel(52, 62);
  u8g2.drawPixel(52, 63);
  u8g2.drawPixel(53, 62);
  u8g2.drawPixel(53, 63);
  // Line 3
  u8g2.drawPixel(89, 60);
  u8g2.drawPixel(89, 61);
  u8g2.drawPixel(90, 61);
  u8g2.drawPixel(91, 61);
  // Line 4
  u8g2.drawPixel(115, 55);
  u8g2.drawPixel(115, 56);
  u8g2.drawPixel(116, 56);
  u8g2.drawPixel(117, 56);
  u8g2.drawPixel(117, 57);
  u8g2.drawPixel(118, 57);
  u8g2.drawPixel(119, 57);
  u8g2.drawPixel(119, 58);


  u8g2.sendBuffer();
  delay(d);
  // Line 2
  u8g2.drawPixel(54, 62);
  u8g2.drawPixel(54, 63);
  u8g2.drawPixel(55, 63);
  u8g2.drawPixel(56, 63);
  // Line 3
  u8g2.drawPixel(91, 62);
  u8g2.drawPixel(92, 62);
  u8g2.drawPixel(92, 63);
  u8g2.drawPixel(93, 63);
  // Line 4
  u8g2.drawPixel(120, 58);
  u8g2.drawPixel(121, 58);
  u8g2.drawPixel(121, 59);
  u8g2.drawPixel(122, 59);
  u8g2.drawPixel(123, 59);

  u8g2.sendBuffer();
  delay(d);
  // Line 4
  u8g2.drawPixel(123, 60);
  u8g2.drawPixel(124, 60);
  u8g2.drawPixel(125, 60);
  u8g2.drawPixel(125, 61);

  u8g2.sendBuffer();
  delay(d);
  // Line 4
  u8g2.drawPixel(126, 61);
  u8g2.drawPixel(127, 61);
  u8g2.drawPixel(127, 62);

  u8g2.sendBuffer();
  
  u8g2.drawStr(79,12,"Plume");
  u8g2.drawStr(38,24,"Experiment");
  u8g2.sendBuffer();

}
