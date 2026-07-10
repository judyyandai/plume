from threading import Event, Thread, Lock
import threading
import time
import numpy as np
from PIL import Image
from logic.Plupy.image import image
import logic.devices.pyCurlModel as qTune

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
        # When we are not taking a measurement Q-Tune is on internal triggering so change it to external
        if option == "Q-Tune":
            qTune.gallopModeExternal()
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

                true_delay = self.get_pirl_timestamp(self.data_tdc)
                flash_voltage = self.osc_TDS2014C.get_value(2) # flash lamp voltage from oscilloscope
                pulse_voltage = self.osc_TDS2014C.get_value(3) # pirl split beam voltage from oscilloscope
                print(f"Plume lifetime: {true_delay} ns")
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
        flashdelay_s = self.dataManager.V_FlashDelay_us.get() *10**(-6) # reading and converting to seconds
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
    

    def sort_tdc(self, tdc_counts, tdc_channels):
        """
        DESCRIPTION:
            Sort the TDC timestamp data into a single dictionary with all the timestamps organized by channel. 
        PARAMETERS
            tdc_counts: lists of integers. Each represents time in nanoseconds since the start of TDC recording when an electrical signal was received.
            tdc_channels: list of channel numbers. Each timestamp in tdc_counts belongs to the channel corresponding to the index in tdc_channels.
        RETURN: 
            result: dictionary in the format {"flash PD":[], "PIRL PD":[]}, where the lists are filled with the timestamps in nanoseconds
            
        """
        result = {"flash PD": [], "teensy": [], "PIRL PD": [], "TTL Out": []} #r read and soft 
        for i in range(len(tdc_counts)):
            if tdc_channels[i] == ["CH4"]:
                result["flash PD"].append(tdc_counts[i])
                
            if tdc_channels[i] == ["CH3"]:
                result["teensy"].append(tdc_counts[i])
        
            if tdc_channels[i] == ["CH1"]:
                result["PIRL PD"].append(tdc_counts[i])
        
            if tdc_channels[i] == ["CH2"]:
                result["TTL Out"].append(tdc_counts[i])
        print(result)
        return result
    

    def camera_control(self, local_image):
        """
        DESCRIPTION:
            Attempts to retrieve the image buffer from the camera within a finite timeout. 
            If a buffer is available, it is copied onto the 2d array created in the 
            experimental thread. The image is then displayed on the GUI.
        PARAMETERS:
            local_image: the 2d array created in the experimental thread.
        RETURN:
            nONE
        """
        image = None   
        running_time = 0
        print("camera control start")
        # Attempt to retrieve image buffer within a finite timeout
        # Return when fail
        while image is None:
            image = self.cam.get_image("image", save = False) 
            time.sleep(0.05)
            running_time = running_time + 0.05
            if running_time >= 2:
                print("Could not retrieve image, camera_control returning None")
                return
        
        if image is not None:
            print("There's an image to display")
            print(image)
            image = np.rot90(image)
            
            # Note that these modification are made to the image displayed
            # on the GUI, not to the raw image
            # C_img = image() #!!! once image stuff is implemented
            # image_scale = C_img.add_scale_bar(image, 4095)
            # image_norm = (image_scale / 16).astype(np.uint8)
            # image_resized = self.resize_image(Image.fromarray(image_norm), self.image_label.winfo_width(), self.image_label.winfo_height())
            # img = image_resized
            
            # Copying raw image buffer onto the 2D array local to experimental thread
            local_image[:] = image

            # Displaying the modified image
            #self.photo = ImageTk.PhotoImage(img)
            #self.window.after(0, lambda: self.image_label.configure(image = self.photo)) #!!! do this in GUI
            
            #update class variable right after displaying the image
            self.currImage = image
            
            return
        

    def resize_image(self, image, max_width, max_height):
        """
        DESCRIPTION:
            Function to resize image. Depending on the proportion of the width and height of the original image 
            and maximum height&width of the original image, the resized image could be constrain by width or height
        PARAMETERS:
            image: image to be resized
            max_width: Max width of resized image
            max_height: Max height of resized image
        RETURN:
            Resized image. 
        """
        image_ratio = image.width / image.height
        frame_ratio = max_width / max_height

        if frame_ratio > image_ratio:
            # Constrain by height
            new_height = max_height
            new_width = int(new_height * image_ratio)
        else:
            # Constrain by width
            new_width = max_width
            new_height = int(new_width / image_ratio)

        return image.resize((new_width, new_height), Image.LANCZOS)


    def get_pirl_timestamp(self, data):
        """
        DESCRIPTION:
            Return the time in nanoseconds at which the PIRL ablation pulse occurs. Because many PIRL pulses are recorded by the TDC, this function returns the relevant one to our process. 
            It simply returns whichever is closest in time to the flash lamp.
        PARAMETERS
            data: a dictionary with the timestamps corresponding to each channel. 
        RETURN: 
            result: the time in nanoseconds since the TDC started recording at which the ablation pulse fired.
        """
        result = 0
        pirl_timestamps = data["PIRL PD"]
        pirl_diffs  = [data["flash PD"][-1] - stamp for stamp in pirl_timestamps]
        
        abs_pirl_diffs = [abs(diff) for diff in pirl_diffs]
        
        result_index = abs_pirl_diffs.index(min(abs_pirl_diffs))
        result = pirl_diffs[result_index]
        return result