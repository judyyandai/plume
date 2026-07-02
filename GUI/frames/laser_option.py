# Frame for laser options

import tkinter as tk
from GUI.frames.container_frame import ContainerFrame
from GUI.frames.laser_control import LaserControlFrame


class LaserOptionFrame(ContainerFrame):
    def __init__(self,parent,laser, on_option_changed):
        super().__init__(parent, "Laser Option")
        self.laser = laser
        self.on_option_changed = on_option_changed

        option_row = tk.Frame(self)
        option_row.pack(anchor="w", pady=(15, 15))

        # Default to PIRL selected
        self.laser_option_value = tk.StringVar(value = "PIRL")

        #Q-Tune and PIRL radio buttons
        tk.Radiobutton(
            option_row,
            text="Q-Tune",
            variable=self.laser_option_value,
            command=self.change_laser_option,
            value="Q-Tune"
        ).pack(anchor="w")

        tk.Radiobutton(
            option_row,
            text="PIRL",
            variable=self.laser_option_value,
            command=self.change_laser_option,
            value="PIRL"
        ).pack(anchor="w")


    def change_laser_option(self):
        option = self.laser_option_value.get()
        self.laser.change_option(option)
        self.on_option_changed()