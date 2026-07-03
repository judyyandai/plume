# Frame for Folder/Saving, lens height, lens focal length in the scrollbar

import tkinter as tk
from tkinter import ttk
from GUI.widgets.entry_box import EntryBox

class FolderFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.folder_frame = tk.Frame(self.inputsFrame)

        self.folder_entry_frame = tk.Frame(self.folder_frame)
        self.folder_entry_frame.pack(padx = 5, pady = 5)
        self.folder_label = tk.Label(self.folder_entry_frame, text= "Folder")
        self.folder_label.pack(side=tk.LEFT, padx=5)
        self.folder_entry = tk.Entry(self.folder_entry_frame, width = 40)
        self.folder_entry.insert(0, self.folder.get())
        self.folder_entry.pack(side=tk.LEFT, fill = 'x')

        # focal_length = EntryBox(self, "Lens focal length [mm]", self.V_lens)
        # lens_height = EntryBox(self, "Lens height [mm]", self.V_lens_height)