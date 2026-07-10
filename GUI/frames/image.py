import tkinter as tk

class ImageFrame(tk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Image Display", padx=0, pady=0)
        self.pack(side = tk.RIGHT, anchor = "ne", padx=5, pady=5, fill="both", expand=True)

        #!!! do we need the save current button

        # Frame for displaying parametesr about bubble
        Time_frame =  tk.Frame(self, padx=0, pady=0)
        Time_frame.pack(side="top", padx=0, pady=0)
        self.time_label = tk.Label(Time_frame, text = "")
        self.time_label.pack(side=tk.LEFT, padx=5)
        
        # Frame for displaying the picture
        Picture_frame = tk.Frame(self, padx=10, pady=10)
        Picture_frame.pack(side="bottom", padx=20, pady=20, fill="both", expand=True)
        self.image_label = tk.Label(Picture_frame, text="")
        self.image_label.pack(fill = "both", expand = True)



        
    def update_text(self, true_delay, flash_voltage, pulse_voltage, pulse_energy, pressure = 0, firing_delay = 0):
        display_message = f"Plume lifetime: {true_delay} ns\nFlash Voltage = {flash_voltage:.3f} V \n Pressure = {pressure:.3e} mbar \n Current Pulse Voltage =  {pulse_voltage:.3f} V \n Firing Delay = {firing_delay:.2f} us \n Pulse Energy(J) = {pulse_energy}"
        self.time_label.configure(text = display_message , font = ("Roboto", 12))

    def update_text_invalid(self):
        self.time_label.configure(text = "INVALID" , font = ("Roboto", 12))