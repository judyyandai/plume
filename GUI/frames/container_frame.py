# Parent Class for all frames in the GUI
# Creates border and label for each frame

import tkinter as tk


class ContainerFrame(tk.LabelFrame):
    def __init__(self, container, title):
        super().__init__(container, text = title, font = "Roboto 16", padx = 10, pady=0)

        self.pack(anchor= "w", padx = 10, pady = 10)
