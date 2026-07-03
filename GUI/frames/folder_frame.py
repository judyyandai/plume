# Frame for Folder/Saving, lens height, lens focal length in the scrollbar

import tkinter as tk
from tkinter import ttk
from GUI.widgets.entry_box import EntryBox

class FolderFrame(tk.Frame):
    def __init__(self, parent, data_manager):
        super().__init__(parent)

        self.data_manager = data_manager

        folder_frame = tk.Frame(parent)

        # Make Entry frame
        self.folder_entry_frame = tk.Frame(folder_frame)
        self.folder_entry_frame.pack(padx = 5, pady = 5)

        # Make label
        self.folder_label = tk.Label(self.folder_entry_frame, text= "Folder")
        self.folder_label.pack(side=tk.LEFT, padx=5)

        # Make Entry Box
        self.folder_entry = tk.Entry(self.folder_entry_frame, width = 40)
        self.folder_entry.pack(side=tk.LEFT, fill = 'x')

        self.entry_focal_length = EntryBox(frame = folder_frame, 
                                     label_text = "Lens focal length [mm]", 
                                     variable = self.data_manager.V_lens, 
                                     data_manager = self.data_manager,
                                     function = self.set_lens_focal_length,
                                     send = True)
        self.entry_lens_height = EntryBox(frame = folder_frame, 
                                    label_text = "Lens height [mm]", 
                                    variable = self.data_manager.V_lens_height, 
                                    data_manager = self.data_manager,
                                    function = self.set_lens_height,
                                    send = True)
    
        folder_frame.pack(anchor="w", pady=5)
        
    def set_lens_focal_length(self):
        """
        DESCRIPTION:
            Sets new focal length
        PARAMETERS
            None.
        RETURN: 
            None.
        """
        self.entry_focal_length.on_enter()
        print(f"Lens focal length set to {self.data_manager.V_lens}mm")

    def set_lens_height(self):
        """
        DESCRIPTION:
            Sets new focal length
        PARAMETERS
            None.
        RETURN: 
            None.
        """
        self.entry_lens_height.on_enter()
        print(f"Lens height set to {self.data_manager.V_lens_height}mm")