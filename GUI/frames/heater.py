import tkinter as tk
from tkinter import messagebox
from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip

class HeatingFrame(ContainerFrame):
    def __init__(self, parent, heater, data_manager):
        """
        DESCRIPTION:
            Class used to create the heating control panel which contains:
                - turn on/off button
                - entry boxes for Kp, Ki, Kd
        PARAMETERS:
            parent - (tk.Frame) the frame heating control frame is placed in
            heater - (Heater) handles the state of the heater
            data_manager - (dataManager) accesses and updates config.json files
        """
        super().__init__(parent, "PID Heater Control Panel")

        self.heater = heater
        self.data_manager= data_manager

        # Turn Heater On Button
        self.b_pidOnOff = tk.Button(self, 
                                    text = "Turn Heater ON", 
                                    command = self.heater_toggle,
                                    font = 'Roboto 12')
        self.b_pidOnOff.pack(anchor = 'w', padx = 10, pady = 10)
        ToolTip(self.b_pidOnOff, "PID on off")

        # if self.heater.connection is None:
        #     tk.Label(self.heater_control_panel, 
        #              text = "Heater not connected", 
        #              font = "Roboto 12 bold").pack()
        #     self.b_pidOnOff.config(state = 'disabled')

        placeholder = 0.0
        self.heaterStatusText = tk.StringVar(value = f"Current Values: \n {placeholder} degrees Celsius")
        self.tempLabel = tk.Label(self, textvariable=self.heaterStatusText, font = "Roboto 16")
        self.tempLabel.pack(padx = 10, pady = 10)

        self.entry_target_temp = EntryBox(self, "Target Temperature [deg C]: ", self.data_manager.V_target_temp_C, self.data_manager, self.set_target_temp)
        ToolTip(self.entry_target_temp.label, "target temp")

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
        self.heater.set_coeff("Kp", self.data_manager.V_Kp.get())

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
        self.heater.set_coeff("Ki", self.data_manager.V_Ki.get())

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
        self.heater.set_coeff("Kd", self.data_manager.V_Kd.get())

    def set_target_temp(self, suppress_popup = False):
        """
        DESCRIPTION:
            Send new target temperature to the heater. First check that it is not above the max alloweable temperature, and confirm with the user. 
        PARAMETERS
            suppress_popup: Defaults to False. If True, there will be no pop-up asking to confirm target_temp.
        RETURN: 
            None.
            
        """
        old_val = self.data_manager.V_target_temp_C.get()
        if not suppress_popup:
            if not messagebox.askyesno(title = "Target temp selection", message = f"Confirm target temp: {self.entry_target_temp.entry.get()}"):
                return # they didn't want to do it, so just leave the function

        try:
            within_safety_temp = float(self.entry_target_temp.entry.get()) <= float(self.data_manager.V_max_target_temp.get())
            if within_safety_temp:
                self.entry_target_temp.on_enter()
                self.heater.target_temp(self.data_manager.V_target_temp_C.get())
            else:
                self.entry_target_temp.entry.delete(0, "end")
                self.entry_target_temp.entry.insert(0, old_val) # set the box back to what it was before. 
                messagebox.showinfo(message = f"Max temp is set to {self.data_manager.V_max_target_temp.get()} deg C. Change this in config.json.")

        except Exception as e:
            print(f"Error in GUI.set_target_temp: {e}. Likely invalid input. ")