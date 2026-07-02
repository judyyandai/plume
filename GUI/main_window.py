# Plume experiment GUI main window

import tkinter as tk
from tkinter import ttk
from GUI.frames.laser_option import LaserOptionFrame
from GUI.frames.laser_control import LaserControlFrame

from logic.laser import Laser


class MainWindow(tk.Tk):
     def __init__(self):# and device_connections"
        """
        DESCRIPTION:
            Initializes the main window of the GUI, sets up the layout, and initializes necessary components.
        CLASS ELEMENTS:
            window: Tkinter object for the root window, must be created by tk.Tk()
        """

        super().__init__()
        self.title("Plume GUI 2026")
        self.geometry("1100x1300")

        # Experiment tab, currently there are no other tabs, but future expansions may include additional tabs for other functionalities.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand = True, fill = 'both')
        self.Experiment_Frame = tk.Frame(self.notebook, width = 1700, height = 1440)
        self.Experiment_Frame.pack()
        self.notebook.add(self.Experiment_Frame, text = "Experiment")

        # Frames
        laser = Laser() # Create an instance of the Laser class to manage the laser state.
        self.laserOptionFrame = LaserOptionFrame(
            parent=self.Experiment_Frame, 
            laser=laser, 
            on_option_changed = self.option_changed)
        self.laserControlFrame = LaserControlFrame(parent=self.Experiment_Frame, laser=laser)


     def option_changed(self):
        """
        DESCRIPTION:
            When laser is option is changed in the Laser Option Frame,
            Laser Control Frame is updated accordingly.
        """
        self.laserControlFrame.update_b_beginMeasure()