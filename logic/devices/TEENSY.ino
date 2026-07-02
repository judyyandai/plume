/*
June - July 2025, Hamburg. 
Written by Daniel Pinto, largely refactored and modified from previous work by Kenny Lai, Chloe Lawson, and Enzo Picinni

How to read this code

*/

#include <digitalWriteFast.h> // note that digitalWrite fast is ONLY better than digitalWrite() IFF the pin number is a constant at compile time, 
// otherwise it's effectively the same
#include <string>


// Input Pins
const byte in_uno = 2; //* These need to be constants for digitalWriteFast to be faster
const byte in_q23 = 4;
const byte in_pirl_pd = 6; 

// Output Pins
const byte out_pg =3; // GET THIS NUMBER FROM GABRIEL
const byte out_shutter = 12; 
const byte outWinCamD = 10;
const byte outUcLaserTrigger = 11;
const byte out_qTune = 5; // Temporary pin for the Q-Tune
// const byte tester_pin = 12; 


String command; // used to store commands from the computer
//*GOOD TO KNOW: 'volatile' keyword tells the compiler to NOT 'optimise' access to any of these variables. 
//* What does that mean? It means that it makes sure to write the variable to memory (RAM) each time it's changed, 
//* rather than keep is 'close by', cached in a register. This is good for interrupt


//f_ in front of a variable stands for 'flag' - these are flipped on/off by interrupts to activate code that runs in the main loop. 
volatile bool qtune = false;
volatile bool on = false; 
volatile bool long_window = true; 
volatile bool f_receive_uno = false; // true means uno interrupt received
volatile bool f_detach_pg = false; 
volatile bool pre_cycle = true; // It takes two 'cycles' to take a picture. A cycle := a pair of laser pulses separated by either 2 ms or 8ms. The first cycle (the pre_cycle) is used to open the shutter, 

//the second cycle is when we send the TTL to the pulse generator to take a picture. pre_cycle tracks which we're in at a given moment. 

int lead_delay = 201;// how long between Q23 trigger received and microchip trigger sent out, in microseconds;  
int detach_time; // the detach time needs to vary
int mode = 3;

int short_window_time = 1500; 
int long_window_time = 27500;

int lastTrigger = 0; // for keeping track of time when firing the Q-Tune in a loop (every 1 second)
unsigned long currentMicros = 0;

volatile int shot_counter = 0;  // 
volatile bool should_count = false; 
volatile int shot_request=1; 


//* timer object names are completely arbitrary to cause less confusion. Just know that you need a new timer object if you want to run
//* a timer on a separate ISR, and make sure you .begin() and .end() the correct timer. 
IntervalTimer timer1; 
IntervalTimer timer2; 
IntervalTimer timer3; 
IntervalTimer timer4; // was used by uno, not used anymore
IntervalTimer timer5; 
IntervalTimer timer6; 
IntervalTimer timer7; 
//IntervalTimer shutterTimer2; 
// and to make sure the microchip pulse is long enough


//FUNCTION DECLARATIONS

void measure(); 
void receive_uno(); 
void end_pg_pulse(); 
void end_shutter_pulse();
void pg(); 
void shutter(bool self_terminating);
void attachingInterrupt(); 
void end_laser_trigger(); 
void make_trigger_pulse(); 
void laser_trigger(); 
void update_values();
void make_trigger_pulse_qtune();
void end_laser_trigger_qtune();
void measure_qtune();
// void qtune_loop(); 
int long_window_calculator(int desired_period, int mode);
// void tester_pin_on(); 
// void tester_pin_off(); 

//////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1); // any serial process will timeout and return whatever they have after 1ms = 1000us because of this command


  pinMode(in_uno, INPUT);
  pinMode(in_q23, INPUT);
  pinMode(in_pirl_pd, INPUT);

  pinMode(out_shutter, OUTPUT); 
  pinMode(outWinCamD, OUTPUT);
  pinMode(outUcLaserTrigger, OUTPUT);
  pinMode(out_qTune, OUTPUT);
  // pinMode(tester_pin, OUTPUT); 
  pinMode(out_pg, OUTPUT);


  attachInterrupt(digitalPinToInterrupt(in_q23), laser_trigger, RISING);
  attachInterrupt(digitalPinToInterrupt(in_uno), receive_uno, RISING); 
  attachInterrupt(digitalPinToInterrupt(in_pirl_pd), measure, RISING); 
  Serial.println("setup() complete"); 
}

void loop() {
 
  update_values(); 

  // qtune_loop();

} 

/*
void qtune_loop(){
  if (qtune_on) {
      // currentMicros = micros(); // grab current time in microseconds (once for efficiency)

      if (micros() - lastTrigger >= 1000000) { // has 1s passed since last trigger pulse?
        make_trigger_pulse_qtune(); // if yes, send a trigger pulse to the Q-Tune
        lastTrigger = micros(); // record current time in microseconds
        }


      if (micros() - lastTrigger < 4000) { // has 4ms passed since last trigger pulse?

        if (long_window) { // only run if long_window wasn't already false
          // Serial.println("< 4000, long_window = false");
          long_window = false; // make long window false
          
        }
      }

      else{

        if (!long_window) { // only run if long_window wasn't already true
          // Serial.println(">= 4000, long_window = true");
          long_window = true; // make long_window true
          
        }
      }
    }
  }
*/

void measure(){
  // pg();
  if (on){
    if (f_receive_uno && !long_window){
      // tester_pin_on(); 
      // Serial.println("f_receive_uno is true");
      // Serial.println("long_window is false");
      if(pre_cycle){
        // Serial.println("inside pre_cycle"); 
        pre_cycle = false; 
        if (mode ==3){
          shutter(true); // terminate the shutter pulse after 52ms
        }
        
      }
      else{
        pre_cycle = true; 
        f_receive_uno = false; // we don't want to send multiple measure pusles
        if (mode == 4){
          shutter(true); 
        }
        pg(); 
      }
      }
    if (f_receive_uno && long_window){
      Serial.println("long_window is true");
      }
    }
  }

void measure_qtune(){
  if(qtune){
    make_trigger_pulse_qtune();
    pg();
  }
}

void receive_uno(){ // see main loop for what f_receive_uno does
  f_receive_uno = true; 
  measure_qtune();
}

void end_pg_pulse(){
  digitalWriteFast(out_pg, LOW); 
  // Serial.println("End pg pulse"); 
  timer3.end(); 
}
void end_shutter_pulse(){
  
  digitalWriteFast(out_shutter, LOW); 
  // Serial.println("End shutter pulse"); 
  timer6.end(); 
}
void pg(){ // pg stands for pulse generator
  digitalWriteFast(out_pg, HIGH); 
  timer3.begin(end_pg_pulse, 5); // 5 us wide TTL pulse to pulse generator
  f_detach_pg = true; 
}

void shutter(bool self_terminating){
  digitalWriteFast(out_shutter, HIGH); 
  // Serial.println("staritng shutter pulse"); 
  if (self_terminating){
    timer6.begin(end_shutter_pulse, 52000); //! Check datasheet for mininimum time open. Here it spends 52ms open
  
  }
  // else the user must terminate with the end_shutter_pulse() function, when they want it.
}





void attachingInterrupt(){
  attachInterrupt(digitalPinToInterrupt(in_q23), laser_trigger, RISING);
  timer1.end();
}
void end_laser_trigger(){
  digitalWriteFast(outUcLaserTrigger, LOW);
  digitalWriteFast(outWinCamD, LOW);
  timer2.end();
}
void make_trigger_pulse(){
  digitalWriteFast(outUcLaserTrigger, HIGH);
  digitalWriteFast(outWinCamD, HIGH);
  timer2.begin(end_laser_trigger,100); // this whole line makes the voltage pulse last for 100 us
}

void end_laser_trigger_qtune(){
  digitalWriteFast(out_qTune, LOW);
  timer2.end();
}
void make_trigger_pulse_qtune(){
  digitalWriteFast(out_qTune, HIGH);
  timer2.begin(end_laser_trigger_qtune,100); // this whole line makes the voltage pulse last for 100 us
}

void laser_trigger(){
  // this entire function is 'wrapped' in on, which is switched with the stop/start command
  if (on){ 
      // actually do the shot
      long_window = !long_window; // on first shot, it's FALSE (which we want)
      Serial.println("long window just got flipped!");
      detachInterrupt(in_q23); 
      delayMicroseconds(lead_delay);
      make_trigger_pulse(); 


      if(shot_counter >= shot_request){
        end_shutter_pulse(); 
        Serial.println("have closed shutter"); 
        // since we've finished our stint, set everything back to defaults. 
        shot_counter = 0; 
        shot_request = 1; 
        should_count = false; 
      }
      if (long_window && should_count && shot_counter == 0){ // it's the first time, so open up the shutter
        shutter(false); // we want it to NOT terminate the shutter signal by itself 
        shot_counter =1; // incrementhe first time manually. A little cumbersome but should work for now.
        Serial.println("have called shutter()"); 
      }
      if (should_count && shot_counter>=1){
        shot_counter++;
      }

      // detach time stuff
      if (mode ==3 or mode ==4){
        if (!long_window){ // NOT long_window = the shorter window
        detach_time = short_window_time; 
        }else if (long_window){ // measure window is the longer wait
        detach_time = long_window_time; 
        }
      }
      
      timer1.begin(attachingInterrupt, detach_time);
      
  }   
}

// void tester_pin_on(){
//   digitalWriteFast(tester_pin, HIGH); 
//   timer7.begin(tester_pin_off, 500); 
// }

// void tester_pin_off(){
//   digitalWriteFast(tester_pin, LOW); 
//   timer7.end(); 
// }



void update_values(){
  /*
  Function entirely for reading in serial commands to change variables. Valid commands are:

  (1) "start" - starts the laser firing
  (2) "stop" - stops the laser firing
  (3) "measure:true" - sets measure to true, begins measuring mode - NO LONGER SUPPORTED
  (4) "measure:false" - sets measure to false, stops measuring mode (technically ANYTHING measure:XXX) will turn off the laser
  (5) "ld:XXX" - sets lead delay (ld) to XXX number specified in comand
  (6) "mode:3" or "mode:4" - sets the mode to 3 or 4
  
  */
  if(Serial.available()){
    command = Serial.readStringUntil('\n');
    ///////////////////////////
    int indexDelimiter = command.indexOf(":");
    String key_word = command.substring(0,indexDelimiter);
    String value = command.substring(indexDelimiter + 1,-1);
   
    
   
    String return_message; 
    if (command == "on"){
      on = true;
      shot_counter = 0; // used in mode 2 mode only. 
      Serial.println("TEENSY: turning laser on.");
    }
    else if (command == "off"){
      on = false;
      Serial.println("TEENSY: turning laser off. ");
    }
    else if (command == "q-tune please"){
      Serial.println("TEENSY: laser is Q-Tune.");
      qtune = true;
    }
    else if (command == "q-tune please no"){
      Serial.println("TEENSY: laser is PIRL");
      qtune = false;
    }
    else if (command == "measure"){
      Serial.println("TEENSY: teensy no longer supports 'measure' command. UNO must signal high to measure!"); 
    }
    else if (key_word == "lead_delay"){
      lead_delay = value.toInt(); 
      Serial.print("TEENSY: Changed lead delay to ");
      Serial.println(lead_delay);
    }
    else if (key_word == "mode"){
      if (value == "?"){
        Serial.println(mode);
      } else {
        mode = value.toInt();
        if (mode == 3){
          short_window_time = 1500; 
          long_window_time = 27500; 
        }
        if (mode == 4){
          short_window_time = 7500; 
          long_window_time = 21500; 
        }
        return_message = "TEENSY mode changed to: " + value;
        Serial.println(return_message);

      }
      

    } 
    else if (key_word == "shot_count"){
      Serial.println("string received."); 
      shot_request = value.toInt(); 
      shot_counter = 0; 
      should_count = true; 
    }
    else if (key_word == "Q23TriggerIgnoreWindow"){
      if (mode == 0){
        detach_time = value.toInt(); 

      }
      else{
        Serial.println("TEENSY: mode 0 required to change trigger ignore window!");
      }
    }
    else if (key_word == "desired_period"){
      long_window_time = long_window_calculator(value.toInt(), mode); 
    }
    else if (key_word == "on"){
      if(value == "?"){
        Serial.println(on); 
      }
    }
    else {
      Serial.println("TEENSY: Command does not exist!");
    }
  }

}


int long_window_calculator(int desired_period, int mode){
  // takes the desired period [us] between pairs of pulses as well as whether we're in mode 3 or 4 and returns how long the long_window_time should beA
  int result; 
  if (mode ==3){
    result = desired_period - 2500; 
  }
  else if (mode ==4){
    result = desired_period - 8500; 
  }
  else {
    result = 27500; // default to 30ms total period in the case we're not in 3 or 4. 
  }
  return result; 
}
