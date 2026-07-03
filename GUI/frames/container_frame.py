# Parent Class for all frames in the GUI
# Creates border and label for each frame

import tkinter as tk


class ContainerFrame(tk.LabelFrame):
    def __init__(self, container, title):
        """
        DESCRIPTION:
            Parent class used to create a general labelled frame.
        PARAMETERS:
            container - (tk.Frame) the frame this frame is placed in
            title - the title displayed on the frame
        """
        super().__init__(container, text = title, font = "Roboto 16", padx = 10, pady=0)

        self.pack(anchor= "w", padx = 10, pady = 10)
