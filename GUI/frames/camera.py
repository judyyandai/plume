# Frame for camera settings

from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip


class CameraFrame(ContainerFrame):
    def __init__(self, parent, data_manager):
        """
        DESCRIPTION:
            Class used to create the camera panel which contains:
                - camera gain entry
        PARAMETERS:
            parent - (tk.Frame) the frame this frame is placed in
            data_manager - (dataManager) accesses and updates config.json files
        """
        super().__init__(parent, "Thor Labs Camera")

        self.data_manager = data_manager

        self.entry_Camera_Gain = EntryBox(
            frame = self, 
            label_text = "Camera Gain", 
            variable = self.data_manager.V_CamGain,
            data_manager = self.data_manager,
            function = self.set_cam_gain, 
            send= True)
        ToolTip(self.entry_Camera_Gain.label, "cam gain")
        
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