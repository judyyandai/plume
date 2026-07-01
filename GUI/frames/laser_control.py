#Frame for laser control panel
import tkinter as tk
from GUI.frames.container_frame import ContainerFrame

class LaserControlFrame(ContainerFrame):
    def __init__(self, parent):
        super().__init__(parent, "Laser Control Panel")

        # Row 1: Start Laser and Begin Measuring buttons
        row_1 = tk.Frame(self)
        row_1.pack(anchor="w", pady=(10, 0))

        self.start_laser_button = tk.Button(
            row_1,
            text="Start Laser",
            font=("Roboto", 16)
        )
        self.start_laser_button.pack(side="left", padx=20)

        self.measure_button = tk.Button(
            row_1,
            text="Begin Measuring",
            font=("Roboto", 16)
        )
        self.measure_button.pack(side="left", padx=20)

        #Row 2: Radio buttons for laser mode (Regular Pulse or Gallop)
        row_2 = tk.Frame(self)
        row_2.pack(anchor="w", pady=(15, 15))

        # Regular pulse mode button
        regular_pulse_button = tk.Radiobutton(row_2, text = "Regular Pulse")
        regular_pulse_button.pack(anchor = 'nw', side = 'top')

        # !!! Frequency dropdown menu and shot count request

        # Gallop mode button
        gallop_button = tk.Radiobutton(row_2, text = "Gallop (for experiment)")
        gallop_button.pack(anchor = 'nw', side = 'top')

        # !!! Prepulse modes

