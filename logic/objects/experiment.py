from threading import Event, Thread, Lock
import threading
import time
import numpy as np
from PIL import Image
from logic.Plupy.image import image as pl_img
import logic.devices.pyCurlModel as qTune
import os
import logic.Plupy.Plupy as pl


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
        self.image_callback = None
        self.text_callback = None
        self.text_callback_invalid = None

        self.vacuumMeter = vacuum_meter
        self.dataManager = data_manager
        self.pg = pg
        self.teensy = teensy
        self.osc_TDS2014C = osc_TDS2014C
        self.osc_DPO2024B = osc_DPO2024B
        self.cam = cam
        self.uno = uno
        self.coherent = coherent



    

    def start(self, total_measurements, mode, option, folder):
        self.T_Pressure = Thread(target=self.vaccum_monitoring, name = "T_Pressure")
        self.T_Pressure.start()
    
        
        self.T_Experiment = Thread(target=self.experiment, args=(option, folder, total_measurements, mode), name = "T_Experiment")
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


    def experiment(self, option, folder, total_measurements = 0, mode = None):
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
        self.folder = folder
        self.dataManager.update_config_file()
        print("Setup complete, starting Experiment loop")
        i=0

        lifetimesCalibration = []

        #######################################################
        while self.e_experimentOn.is_set():
            i+=1
            print(f"loop: {i}") 
         
            a=time.time()
            self.flash_delay_s = self.dataManager.V_FlashDelay_us.get() *10**(-6)# Get flash delay in config file

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
                lifetimesCalibration.append(true_delay)
                flash_voltage = self.osc_TDS2014C.get_value(2) # flash lamp voltage from oscilloscope
                pulse_voltage = self.osc_TDS2014C.get_value(3) # pirl split beam voltage from oscilloscope
                pulse_energy = 0
                try:
                    pulse_energy = self.coherent.readValues()
                except:
                    print("Experiment: Couldn't find Pulse Energy! Proceeding anyway.")

                #with self.visa_lock:
                 #   firing_delay = float(self.osc_DPO2024B.get_value(2)) * 1e6

                if self.text_callback:
                    self.text_callback(
                    true_delay = true_delay, 
                    flash_voltage = flash_voltage, 
                    pulse_voltage = pulse_voltage,
                    pulse_energy = pulse_energy)
                delay_set_ns = round(self.flash_delay_s*10**9) 
                
                self.curr_true_delay = true_delay
                self.curr_flash_voltage = flash_voltage
                self.curr_p_voltage = pulse_voltage
                self.curr_prepulse_mode = current_prepulse_mode
                self.curr_delay_set_ns = delay_set_ns
                self.laser = option
                #self.curr_firing_delay = firing_delay

                if self.dataManager.V_save.get():# if save button pressed
                    # Wait until the image buffer is copied onto the local 
                    # image variable
                    # Start a transisent camera thread
                    time.sleep(0.2)
                    # If the image variable isn't updated then there is a
                    # retrival error. I found that it is beneficial to 
                    # wait a bit after the error occur. Usually error occur 
                    # when you used up all threads, so waiting a bit allow
                    # more threads to be freed up. 
                    # Note to the future interns, there are better ways 
                    # to solve this issue.
                    if(np.all(image == 0)):
                        print("Saving fail, image retrieval error")
                        time.sleep(3)
                    else:
                        # Depending on the mode, there are different saving
                        # format. In either case, a saving thread would be 
                        # created for EACH set of measurment data and image
                        if mode == "ps":
                            self.T_Saving = Thread(
                                target=self.saving, 
                                name = "T_Saving", 
                                args = (os.path.join(self.folder, "q1c" + str(self.q1c_now)),
                                        true_delay,
                                        delay_set_ns, 
                                        image, 
                                        flash_voltage,
                                        pulse_voltage,
                                        current_prepulse_mode,
                                        option))
                        else:
                            self.T_Saving = Thread(
                                target=self.saving, 
                                name = "T_Saving", 
                                args = (self.folder,
                                        true_delay,
                                        delay_set_ns,
                                        image, 
                                        flash_voltage,
                                        pulse_voltage,
                                        current_prepulse_mode,
                                        option))
                      
                        self.T_Saving.start()
                        self.T_Saving.join()
                        
                        # Again, artificially insert delay to not use up all
                        # threads
                        time.sleep(0.2)
                            
                

                # !!! displaying images and values
            else: # Invald data
                self.E_valid.clear()
                if self.text_callback_invalid:
                    self.text_callback_invalid()
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

        # Put Q-Tune back into internal triggering
        qTune.gallopModeInternal()  
        
        # With the experimental thread ended, the user can choose to start experiment again
        print("Experimental thread ended.")


    def save_current(self):
        """
        DESCRIPTION:
            Creates T_SavingCurrent thread that runs self.saving() function to save images as they are taken.
        PARAMETERS
            None.
        RETURN: 
            None.
            
        """
        HandPickedFolder = os.path.join(self.folder,"handpicked")
        os.makedirs(HandPickedFolder, exist_ok=True)
        self.T_SavingCurrent = Thread(
            name = "T_SavingCurrent", 
            target=self.saving, 
            args = (HandPickedFolder,
                    self.curr_true_delay,
                    self.curr_delay_set_ns,
                    self.currImage,
                    self.curr_flash_voltage,
                    self.curr_p_voltage,
                    self.curr_prepulse_mode,
                    self.laser))
        self.T_SavingCurrent.start()
        self.T_SavingCurrent.join()


    def saving(self, folder, delay_true, delay_set, image, voltage, p_voltage, isPrePulse, laser, firingDelay = 0):
        #A thread function that save the data currently display on the GUI
        # self.ImageFolder = self.ImageFolder_entry.get()
        # self.DataFolder = self.DataFolder_entry.get()
        
        """
        DESCRIPTION:
            Target function of the thread T_SavingCurrent. 
        PARAMETERS
            delay_true: The true, measured flash delay (i.e. plume lifetime)
            delay_set: The set/requested flash delay
            image: The image object to be saved. 
            voltage: The photodiode voltage recorded
            p_voltage: ???? Need to investigated
            folder: The filepath to save the image to.
            isPrePulse: Boolean. Was it a prepulse or no prepulse plume
            firingDelay: Delay between falling edge of the microchip trigger signal and the actual pirl pulse.
        RETURN: 
            None.
            
        """
        try:
            #save the current image before it is replaced
            image_copy = np.copy(image)
            
            ImageFolder =  os.path.join(folder, "images")
            DataFolder =  os.path.join(folder, "data")
            
            os.makedirs(ImageFolder, exist_ok=True)
            os.makedirs(DataFolder, exist_ok=True)
            
            filename = pl.get_file_name(delay_set, delay_true)
            q1c = self.dataManager.V_q1c.get()
            lens = self.dataManager.V_lens.get()
            lens_height = self.dataManager.V_lens_height.get()
            #pressure = self.pressure
            with open(DataFolder + "/" + filename + ".csv", "w") as file:
                file.write("Set Delay(ns), True Delay(ns), Voltage(V), q1c, lens focal length(mm), lens height(mm), pressure(mbar), Pulse Voltage (V), Prepulse, Firing Delay, Laser")
                file.write("\n")
                file.write(f"{delay_set},{delay_true},{voltage},{q1c},{lens},{lens_height},{0},{p_voltage},{isPrePulse}, {firingDelay}, {laser}")
            file_path = os.path.join(ImageFolder, filename)
    
            # Saving Image as .npy file
            np.save(file_path, image_copy)
            
            # Create a sample image array (if you don't already have one)
            im_array = (image_copy / np.max(image_copy) * 255).astype(np.uint8)
            im = Image.fromarray(im_array, mode='L')  # Convert to grayscale
            # Define the output folder and file path
            os.makedirs(os.path.join(ImageFolder, "Fast_Loading"), exist_ok=True)
            png_file_path = os.path.join(ImageFolder, "Fast_Loading", filename + ".png")
            
            
            # Save the image as PNG with DPI metadata
            im.save(png_file_path, format="PNG", dpi=(150, 150))  # 150 DPI for reasonable scaling
            
            print("finished saving!!!")
        except:
           print("Saving Error")


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
        self.q1c_now = self.dataManager.V_q1c.get() # store the current q1c value
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
            C_img = pl_img()
            image_scale = C_img.add_scale_bar(image, 4095)
            image_norm = (image_scale / 16).astype(np.uint8)
            
            
            # Copying raw image buffer onto the 2D array local to experimental thread
            local_image[:] = image

            # Displaying the modified image
            if self.image_callback:
                self.image_callback(image_norm)
            
            self.currImage = image
            return
        

    


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
    

 