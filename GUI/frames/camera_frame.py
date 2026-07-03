# Frame for camera settings

import tkinter as tk
from tkinter import ttk
from GUI.frames.container_frame import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from tkinter import messagebox

class CameraFrame(ContainerFrame):
    def __init__(self, parent, data_manager):
        super().__init__(parent, "Thor Labs Camera")

        self.data_manager = data_manager

        self.entry_Camera_Gain = EntryBox(
            frame = self, 
            label_text = "Camera Gain", 
            variable = self.data_manager.V_CamGain,
            data_manager = self.data_manager,
            function = self.set_cam_gain, 
            send= True)
        
    def set_cam_gain(self):
        """
        DESCRIPTION:
            Retrieves the camera gain and pedal width values from the entry boxes, and sets a flag to trigger the camera event in the experimental thread.    
        PARAMETERS:
            None
        RETURN:
            None
        """
        self.entry_Camera_Gain.on_enter()
        # self.E_cam.set()