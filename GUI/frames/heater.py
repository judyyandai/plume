import tkinter as tk
from tkinter import messagebox
from threading import Event, Thread
import time
from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip

class HeatingFrame(ContainerFrame):
    def __init__(self, parent, heater, data_manager):
        """
        ! contains some logic
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

        self.V_temp1C = tk.DoubleVar(value = 0.0) 
        self.V_temp2C = tk.DoubleVar(value = 0.0) 
        self.V_avg_temp = tk.DoubleVar(value = 0.0)
        self.V_PID_val = tk.DoubleVar(value = 0.0)

        self.e_heaterOn = Event()
        self.e_checkHeater = Event()
        self.e_checkHeater.set()

        self.T_check_heater = Thread(target = self.check_heater, name = "T_check_temp")
        self.T_check_heater.start()

        # Turn Heater On Button
        self.b_pidOnOff = tk.Button(self, 
                                    text = "Turn Heater ON", 
                                    command = self.heater_toggle,
                                    font = 'Roboto 12')
        self.b_pidOnOff.pack(anchor = 'w', padx = 10, pady = 10)
        ToolTip(self.b_pidOnOff, "PID on off")

        if self.heater.connection is None:
            tk.Label(self, 
                     text = "Heater not connected - please check your connect (software and hardware), and then restart.", 
                     font = "Roboto 12 bold").pack()
            self.b_pidOnOff.config(state = 'disabled')

    
        self.heater_status_text = tk.StringVar(value = f"CURRENT Temps: \nTemp 1: {self.V_temp1C} degC\nTemp 2: {self.V_temp2C} degC\nAvg: {self.V_avg_temp} degC")
        self.tempLabel = tk.Label(self, textvariable=self.heater_status_text, font = "Roboto 16")
        self.tempLabel.pack(padx = 10, pady = 10)

        self.entry_target_temp = EntryBox(self, "Target Temperature [deg C]: ", self.data_manager.V_target_temp_C, self.data_manager, self.set_target_temp)
        ToolTip(self.entry_target_temp.label, "target temp")

        self.entry_Kp = EntryBox(self, "K_p", self.data_manager.V_Kp, self.data_manager, self.set_Kp)
        self.entry_Ki = EntryBox(self, "K_i", self.data_manager.V_Ki, self.data_manager, self.set_Ki)
        self.entry_Kd = EntryBox(self, "K_d", self.data_manager.V_Kd, self.data_manager, self.set_Kd)

        self.entry_Kd.disable()
    
    def heater_toggle(self):
        """
        DESCRIPTION:
            Calls toggle function on heater and updates GUI.
        """
        self.e_heaterOn.set() if not self.e_heaterOn.is_set() else self.e_heaterOn.clear()

        if self.e_heaterOn.is_set():
            self.heater.start()
        else:
            self.heater.stop()

        self.update_b_pidOnOff()
    
    def update_b_pidOnOff(self):
        """
        DESCRIPTION:
            Updates the heater on/off button.
        """
        if self.e_heaterOn.is_set():
            self.b_pidOnOff.config(text = "PID ON", fg = 'red')
        else:
            self.b_pidOnOff.config(text = "Turn PID ON", fg = "black")
    


    def set_Kp(self):
        """
        DESCRIPTION:
            Sends the new Kp value to heater object + saves it to the config.json.
            Kp is the proportional constant in the PID heater system.
        """
        self.entry_Kp.on_enter() 
        self.heater.set_coeff("Kp", self.data_manager.V_Kp.get())

    def set_Ki(self):
        """
        DESCRIPTION:
           Sends the new Ki value to heater object + saves it to the config.json.
            Ki is the integral constant in the PID heater system.
        """
        self.entry_Ki.on_enter() 
        self.heater.set_coeff("Ki", self.data_manager.V_Ki.get())

    def set_Kd(self):
        """
        DESCRIPTION:
            Sends the new Kd value to heater object + saves it to the config.json.
            Kd is the derivative constant in the PID heater system.
        """
        self.entry_Kd.on_enter() 
        self.heater.set_coeff("Kd", self.data_manager.V_Kd.get())


    def set_target_temp(self, suppress_popup = False):
        """
        DESCRIPTION:
            Send new target temperature to the heater object. First check that it is not above the max alloweable temperature, and confirm with the user. 
        PARAMETERS
            suppress_popup: Defaults to False. If True, there will be no pop-up asking to confirm target_temp.
            
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


    def check_heater(self):
        """
        ! PROBLEM: This function is having trouble exiting when we boot down the GUI.S
        DESCRIPTION:
            Polls the heater via serial communication, and then updates the GUI display to show these temperatures.
        PARAMETERS
            None.
        RETURN: 
            None.
            
        """
        i = 0 # for debugging. 
        while self.e_checkHeater.is_set():
            i+=1
            # print(f"In the loop: {i}")
            try:
                t1_val = self.V_temp1C
                t2_val = self.V_temp2C
                t1, t2 = self.heater.read_temps(t1_val, t2_val)
            except:
                t1, t2 = self.V_temp1C, self.V_temp2C
            
            # read_temps() requires the current temps because it returns those if there's an error in reading the 
            # serial message. 
            self.V_temp1C = t1 # the label should update by itself in the GUI. 
            
            self.V_temp2C = t2
            self.V_PID_val = self.heater.check_PID_val()
            avg = (self.V_temp1C + self.V_temp2C)/2
            self.V_avg_temp = round(avg, 2)
            try:
                self.heater_status_text.set(f"CURRENT Temps: \nTemp 1: {self.V_temp1C} degC\nTemp 2: {self.V_temp2C} degC\nAvg: {self.V_avg_temp} degC\nPID %: {self.V_PID_val}") #! any way to do this without a separate string here?
            except:
                self.heater_status_text.set(f"CURRRENT Temps: \n Working on it! Check GUI.check_heater() function.")
           
            time.sleep(0.05)
        print("exiting check_heater now!")
        return
    
    def close_check_heater(self):
            if hasattr(self, "T_check_heater") and self.T_check_heater.is_alive():
                print("Waiting for heater thread to close . . ")
                self.T_check_heater.join(timeout = 5)
                if self.T_check_heater.is_alive():
                    print("T_check_heater did not exit in time!")
                else:
                    print("T_check_heater successfully closed")  