# Frame for Folder/Saving, lens height, lens focal length in the scrollbar

import tkinter as tk
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip
from GUI.frames.container import ContainerFrame

class LensFrame(ContainerFrame):
    def __init__(self, parent, data_manager):
        """
        DESCRIPTION:
            Class used to create the lens panel which contains:
                - lens focal length and height entry
        PARAMETERS:
            parent - (tk.Frame) the frame this frame is placed in
            data_manager - (dataManager) accesses and updates config.json files
        """
        super().__init__(parent, "Lens")

        self.data_manager = data_manager

        # Make Entry Boxes
        self.entry_focal_length = EntryBox(frame = self, 
                                     label_text = "Lens focal length [mm]", 
                                     variable = self.data_manager.V_lens, 
                                     data_manager = self.data_manager,
                                     function = self.set_lens_focal_length,
                                     send = True)
        self.entry_lens_height = EntryBox(frame = self, 
                                    label_text = "Lens height [mm]", 
                                    variable = self.data_manager.V_lens_height, 
                                    data_manager = self.data_manager,
                                    function = self.set_lens_height,
                                    send = True)
    
        ToolTip(self.entry_lens_height.label, "lens height")
        ToolTip(self.entry_focal_length.label, "focal length")
        


    def set_lens_focal_length(self):
        """
        DESCRIPTION:
            Sets new focal length
        """
        self.entry_focal_length.on_enter()
        print(f"Lens focal length set to {self.data_manager.V_lens}mm")



    def set_lens_height(self):
        """
        DESCRIPTION:
            Sets new focal length
        """
        self.entry_lens_height.on_enter()
        print(f"Lens height set to {self.data_manager.V_lens_height}mm")


    