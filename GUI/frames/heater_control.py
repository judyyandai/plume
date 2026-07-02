# Frame for Heating Control Panel

import tkinter as tk
from tkinter import ttk
from GUI.frames.container_frame import ContainerFrame
from GUI.widgets.entry_box import EntryBox

class HeatingControlFrame(ContainerFrame):
    def __init__(self, parent, heater):
        super().__init__(parent, "PID Heater Control Panel")

        self.heater = heater

        # Turn Heater On Button
        self.b_pidOnOff = tk.Button(self, 
                                    text = "Turn Heater ON", 
                                    command = self.heater_toggle,
                                    font = 'Roboto 12')
        self.b_pidOnOff.pack(anchor = 'w', padx = 10, pady = 10)

        # if self.heater.connection is None:
        #     tk.Label(self.heater_control_panel, 
        #              text = "Heater not connected", 
        #              font = "Roboto 12 bold").pack()
        #     self.b_pidOnOff.config(state = 'disabled')

        placeholder = 0.0
        self.heaterStatusText = tk.StringVar(value = f"Current Values: \n {placeholder} degrees Celsius")
        self.tempLabel = tk.Label(self, textvariable=self.heaterStatusText, font = "Roboto 16")
        self.tempLabel.pack(padx = 10, pady = 10)

        self.V_Kp = tk.DoubleVar(value = 1)
        self.V_Ki = tk.DoubleVar(value = 1)
        self.V_Kd = tk.DoubleVar(value = 1)

        self.entry_Kp = EntryBox(self, "K_p", self.V_Kp, heater.set_Kp)
        self.entry_Ki = EntryBox(self, "K_i", self.V_Ki, heater.set_Ki)
        self.entry_Kd = EntryBox(self, "K_d", self.V_Kd, heater.set_Kd)
    
    def heater_toggle(self):
        self.heater.toggle()
        self.update_b_pidOnOff()
    
    def update_b_pidOnOff(self):
        if self.heater.e_heaterOn.is_set():
            self.b_pidOnOff.config(text = "Turn Heater OFF")
            print("Heater turned on")
        else:
            self.b_pidOnOff.config(text = "Turn Heater ON")
            print("Heater turned off")