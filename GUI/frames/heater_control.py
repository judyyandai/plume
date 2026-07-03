# Frame for Heating Control Panel

import tkinter as tk
from tkinter import ttk
from GUI.frames.container_frame import ContainerFrame
from GUI.widgets.entry_box import EntryBox

class HeatingControlFrame(ContainerFrame):
    def __init__(self, parent, heater, data_manager):
        super().__init__(parent, "PID Heater Control Panel")

        self.heater = heater
        self.data_manager= data_manager

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


        self.entry_Kp = EntryBox(self, "K_p", self.data_manager.V_Kp, self.data_manager, self.set_Kp)
        self.entry_Ki = EntryBox(self, "K_i", self.data_manager.V_Ki, self.data_manager, self.set_Ki)
        self.entry_Kd = EntryBox(self, "K_d", self.data_manager.V_Kd, self.data_manager, self.set_Kd)

        self.entry_Kd.disable()

    
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


    def set_Kp(self):
        """
        DESCRIPTION:
            Sends the new Kp value to heater box + saves it to the Tkinter variable.
            Kp is the proportional constant in the PID heater system.
        PARAMETERS
            None.
        RETURN: 
            None.
        """
        self.entry_Kp.on_enter() 
        self.heater.set_coeff("Kp", self.data_manager.V_Kp)

    def set_Ki(self):
        """
        DESCRIPTION:
            Sends the new Ki value to heater box + saves it to the Tkinter variable.
            Ki is the integral constant in the PID heater system.
        PARAMETERS
            None
        RETURN: 
            None.
        """
        self.entry_Ki.on_enter() 
        self.heater.set_coeff("Ki", self.data_manager.V_Ki)

    def set_Kd(self):
        """
        DESCRIPTION:
            Sends the new Kd value to heater box + saves it to the Tkinter variable.
            Kd is the derivative constant in the PID heater system.
        PARAMETERS
            None.
        RETURN: 
            None.
        """
        self.entry_Kd.on_enter() 
        self.heater.set_coeff("Kd", self.data_manager.V_Kd)