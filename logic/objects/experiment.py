from threading import Event, Thread, Lock
import threading
import time
import numpy as np

class Experiment:
    def __init__(self, vacuum_meter, data_manager, pg, teensy, osc_TDS2014C, osc_DPO2024B, cam, uno, coherent):
        """
        DESCRIPTION:

        PARAMETERS:

        """
        # Event to track if the experiment is running or not
        self.e_experimentOn = Event()
        self.E_cam = Event()
        self.E_valid = Event()

        self.vacuumMeter = vacuum_meter
        self.dataManager = data_manager
        self.pg = pg
        self.teensy = teensy
        self.osc_TDS2014C = osc_TDS2014C
        self.osc_DPO2024B = osc_DPO2024B
        self.cam = cam
        self.uno = uno
        self.coherent = coherent



    def stop(self):
        self.e_experimentOn.clear()


    def start(self, total_measurements, mode, option):
        self.e_experimentOn.set()
        self.T_Pressure = Thread(target=self.vaccum_monitoring, name = "T_Pressure")
        self.T_Pressure.start()
    
        
        self.T_Experiment = Thread(target=self.experiment, args=(option, total_measurements, mode), name = "T_Experiment")
        self.T_Experiment.start()


    def vaccum_monitoring(self):
        """
        DESCRIPTION:
            Target function of the T_Pressure thread. Continuously read the pressure inside the vacuum chamber until the experimental thread flag is off.

        """
        while self.e_experimentOn.is_set():
            try:
                self.pressure = self.vacuumMeter.readChannel(1)
            except:
                pass


    def experiment(self, option, total_measurements = 0, mode = None):
        """
        DESCRIPTION:
            Target function of the T_Experiment thread. Triggers Arduino Uno, which then starts TDC and starts Teensy measure mode. Teensy then coordinates the shutter opening, flash lamp and camera triggers. 
        PARAMETERS
            option: one of 'Q-Tune" or "PIRL"
            total_measurements: Defaults to 0. If nonzero, then one of the run series options may run.
            mode: Defaults to None. If "rs" then run flash delay series. If "ps" run power series.
        RETURN: 
            None
        """
        print("Setting up devices for experiment.")
        current_prepulse_mode = self.flash_camera_power_setup(option)
        print("Waiting for device connections.")
        print("loading", end = "")
        for i in range(10): # sleep for 10 seconds to get all devices connected
            time.sleep(1)
            print(".", end = "")
        print("")
        print("Setup complete, starting Experiment loop")
        i=0

        #######################################################
        while self.e_experimentOn.is_set():
            i+=1
            print(f"loop: {i}") 
         
            a=time.time()
            self.flash_delay_s = self.dataManager.V_FlashDelay_us.get() *10**(-6)# Get flash delay in config file
            # self.folder.set(self.folder_entry.get()) #!!! get folder somehow

            if self.E_cam.is_set(): # Checking if some of the settings changed with the camera and updating it
                gain = self.dataManager.V_CamGain.get()
                self.cam.change_gain(gain)
                self.E_cam.clear()
                print("GUI Camera gain set and event cleared.")
            image = np.zeros((2448,2048), dtype=np.uint16) # creating a zero array with dimensions of the image - passed to camera thread.
            # new image buffer is copied into here. 
            # Doing it this way 'allows the camera thread update variable value in this thread without pausing execution'
            self.pg.run() #activate PG
            if current_prepulse_mode: #Checking if there should be a prepulse or not
                self.start_command = "start2\n"
            else:
                self.start_command = "start\n"
            # Start the uno then wait for the UNO to return the TDC time stamps    
            tdc_counts, tdc_channels, (ch1_counts, ch2_counts, ch3_counts, ch4_counts) = self.uno.start(self.start_command)
            self.data_tdc = self.sort_tdc(tdc_counts, tdc_channels) # turns the tdc buffer into useable stuff

            camera_thread = Thread(target = self.camera_control, args=(image,), name = "camera_thread") # starting a new thread for the camera process
            camera_thread.start()
            camera_thread.join()

            valid_measurement = len(self.data_tdc["flash PD"]) > 0 and len(self.data_tdc["PIRL PD"]) >= 2
            #####################################################
            if valid_measurement:
                self.E_valid.set()

                true_delay = self.get_pirl_timestamp(self.data_tdc, self.flash_delay_s)
                flash_voltage = self.osc_TDS2014C.get_value(2) # flash lamp voltage from oscilloscope
                pulse_voltage = self.osc_TDS2014C.get_value(3) # pirl split beam voltage from oscilloscope
                pulse_energy = 0
                try:
                    pulse_energy = self.coherent.readValues()
                except:
                    print("Experiment: Couldn't find Pulse Energy! Proceeding anyway.")

                with self.visa_lock:
                    firing_delay = float(self.osc_DPO2024B.get_value(2)) * 1e6


                # !!! displaying images and values
            else: # Invald data
                self.E_valid.clear()
                # self.window.after(0, lambda: self.time_label.configure(text = "INVALID")) #!!! get this in the GUI
                time.sleep(0.4)

            #stop pulse generator
            print("NUMBER OF ACTIVE THREADS: " + str(threading.active_count()))
            self.pg.stop()

            b=time.time()
            print("run time: " +str(b-a))

            #!!! stuff for run series

        # Disarm the camera when the experimental thread ends
        self.cam.camera.disarm() 
        self.cam.close_camera()  
        
        # With the experimental thread ended, the user can choose to start experiment again
        print("Experimental thread ended.")



    def flash_camera_power_setup(self, option):
        """
        DESCRIPTION:
            Do some pre-experiment configuration for the flash, camera, and laser power.
        PARAMETERS:
            None.
        RETURN: 
            current_prepulse_mode: Boolean whether we are in prepulse mode or not
        """
        exposure = 27
        flashdelay_s = self.V_FlashDelay_us.get() *10**(-6) # reading and converting to seconds
        current_prepulse_mode = self.dataManager.V_PrePulse.get() 
        self.pg.setup(flashdelay_s, current_prepulse_mode, exposure, option)

      
        if option == "PIRL":
            DelayBetweenTriggers = self.dataManager.V_DelayBetweenTriggers.get( ) # Setting the delay between Q2&Q3 trigger and uc laser trigger
            self.teensy.delayBetweenTriggers(DelayBetweenTriggers) 
            #!!! IF TIME please make this Lock() object an attriibute of hte oscilloscope class, and include 'with Lock:' on every commmunication method
            self.visa_lock = Lock()  #used for all visa comms with the oscilloscope

            with self.visa_lock:
                self.osc_TDS2014C.recall(9) # Recall setting 9 on TDS2014C oscilloscope
                self.osc_TDS2014C.setup(1, 1, "MAXImum")  # Let the first measurement probe the maximum voltage value of the first channel

                self.osc_DPO2024B.recall(8) #Recall setting 8 on DPO2024B       
        # q1c_now = self.dataManager.V_q1c.get() # store the current q1c value
        gain = self.dataManager.V_CamGain.get() # camera gain
        
        self.cam.set_params(exposure, gain, 1, 1)
        self.cam.arm_camera()
        print("flash_camera_power_setup() complete.")
        return current_prepulse_mode