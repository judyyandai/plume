import sys
import os
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
import numpy as np


class thor_camera:
    def __init__(self):
        """
        class for thorlabs compact scientific camera model CS505MU1 
        
        CLASS ELEMENTS:
            None
        """
        pass
    
    def windows_set_up(self):
        """
        (Adapted From Thorlabs Library)
        DESCRIPTION:
            Set up the path to the dlls folder on the computer, which the code need to access in order to function correctly
        
        PARAMETERS:
            None
        
        RETURNS:
            None
        """
        try:
            is_64bits = sys.maxsize > 2**32
            relative_path_to_dlls = '.' + os.sep + 'dlls' + os.sep
        
            if is_64bits:
                relative_path_to_dlls += 'Native_64_lib'
            else:
                relative_path_to_dlls += '32_lib'
                
            absolute_path_to_file_directory = os.path.dirname(os.path.abspath(__file__))
            
            absolute_path_to_dlls = os.path.abspath(absolute_path_to_file_directory + os.sep + relative_path_to_dlls)
        
            os.environ['PATH'] = absolute_path_to_dlls + os.pathsep + os.environ['PATH']
        
            try:
                os.add_dll_directory(absolute_path_to_dlls)
            except AttributeError:
                pass
        except ImportError:
            configure_path = None
        
    def set_params(self, exp, gain, frames, mode):
        """
        DESCRIPTION:
            Sets the exposture and mode of the camera
        
        PARAMETERS:
            exp - exposure time in microseconds
            gain - image gain in decibels. ranging from 0 to 48
            frames - sets the frams per trigger, 1 for trigger 0 for continuous and multiple for many shots per trigger
            mode - set as 1 for hardware trigger, 2 for bulb mode and 0 for software trigger 
        
        RETURNS
            None
        """
        self.windows_set_up()
            
        with TLCameraSDK() as sdk:
            available_cameras = sdk.discover_available_cameras()
            if len(available_cameras) < 1:
                print("no cameras detected")
            
            with sdk.open_camera(available_cameras[0]) as camera:
                camera.exposure_time_us = exp  # Set exposure
                camera.gain = camera.convert_decibels_to_gain(gain)
                camera.frames_per_trigger_zero_for_unlimited = frames
                camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
                camera.operation_mode = mode # Set operation Mode
                
    def change_gain(self, gain):
        """
        DESCRIPTION:
            Sets the exposture and mode of the camera
        
        PARAMETERS:
            exp - exposure time in microseconds
            gain - image gain in decibels. ranging from 0 to 48
            frames - sets the frams per trigger, 1 for trigger 0 for continuous and multiple for many shots per trigger
            mode - set as 1 for hardware trigger, 2 for bulb mode and 0 for software trigger 
        
        RETURNS
            None
        """
        self.windows_set_up()
        self.camera.gain = self.camera.convert_decibels_to_gain(gain)
        print(f"plupy change_gain: Changed gain to {gain}")

    def arm_camera(self):
        """
        DESCRIPTION: 
            Arm the camera so that it is waiting for a trigger
        
        PARAMETERS:
            None
            
        RETURNS:
            None
        

        """
        global sdk, available_cameras
        self.windows_set_up()
        sdk = TLCameraSDK()
        available_cameras = sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            print("no cameras detected")
        
        
        self.camera = sdk.open_camera(available_cameras[0])

        # Configure frames per trigger (1 for asynchronous triggered acquisition mode)
        #self.camera.frames_per_trigger_zero_for_unlimited = 1

        # Arm the camera
        self.camera.arm(frames_to_buffer=2) 
        
    def get_image(self, filename, save = True):
        """
        DESCRIPTION: 
            When run with hardware trigger parameters will continue to run until hardware trigger is recieved and photo is taken. The Image
            is saved in the image folder with the name "filename.npy"
        
        PARAMETERS:
            filename: name of the file to be saved
            
        RETURNS:
            return array of the raw image
        """
        global sdk, available_cameras
        
        frame = self.camera.get_pending_frame_or_null()

        if frame is not None:
            #print("frame #{} received!".format(frame.frame_count))
            frame.image_buffer
            raw_image = np.copy(frame.image_buffer)

        else:
            return None
        

        # Because we are using the 'with' statement context-manager, disposal has been taken care of.



        #save the raw image
        if save:
            # Save directory for raw images and processed images
            raw_save_dir = "Z:/Users/coop/Chloe_Enzo_2024/Raw_Images"
            raw_file_path = os.path.join(raw_save_dir, filename)
            np.save(raw_file_path, raw_image)
        
        
        # Intensity Image

        return raw_image
    
    def close_camera(self):
        """
        DESCRIPTION: 
            Disposes the camera
        
        PARAMETERS:
            None
            
        RETURNS:
            None
        """
        global sdk, available_cameras
        self.camera.dispose()
        sdk.dispose()

        