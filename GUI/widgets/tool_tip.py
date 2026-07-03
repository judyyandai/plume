import tkinter as tk

class ToolTip:
    """
    DESCRIPTION:
        Class used to create a user help message whenver they right click or Ctrl + hover over a specified button. 
        Can be used with any tkinter widget to help the user on the GUI. 

    PARAMETERS:
        widget - any Tkinter widget object. 
        text - text you'd like displayed
        wraplength - how wide the message box is, default is 300. 
    """ 
    def __init__(self, widget, text, wraplength = 300):
        self.widget = widget
        self.message = tooltip_messages[text]
        self.wraplength = wraplength
        self.tooltip_window = None
        # binding the hover event


        self.widget.bind('<Control-Enter>', self.enter)
        self.widget.bind('<Button-3>', self.enter)
        # you need to ctrl + hover, or right click to see the message
        self.widget.bind('<Leave>', self.leave)

    
        
    def enter(self, event):
        if not self.tooltip_window:
            x_pos, y_pos, width, height = self.widget.bbox("insert")
            x_pos += self.widget.winfo_rootx() + 25
            y_pos += self.widget.winfo_rooty() + 20
            self.tooltip_window = tk.Toplevel(self.widget, borderwidth=1, relief = 'solid') # creates a frame around self.widget? I'm not sure
            self.tooltip_window.wm_overrideredirect(True) # don't know what this does ..
            self.tooltip_window.wm_geometry("+%d+%d" % (x_pos, y_pos))
            label = tk.Label(self.tooltip_window, text = self.message, justify = 'left', wraplength=self.wraplength)
            label.pack(ipadx = 1)



    def leave(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
        


# these are all the messages you see on the various tooltips
tooltip_messages = {"LaserStart":"Starts the laser. \nThis button sends the string 'on' to the Teensy, to begin firing the laser in the mode you specify below. If you press again, it sends 'off' to turn the laser off. Remember that laser firing is handled by the Teensy, and that all the PC does it tell the Teensy to start or stop.", 
                   "Measure":"Starts taking data once laser is firing. \nIs done by starting the Experiment() function. The laser must already be on before you start measuring. This function will, approximately once a second, tell the Teensy to and Arduino to work together and coordinate a picture: Start TDC logging, open the shutter, and fire the camera and flash lamp. Experiment() will then also retrieve the image from the camera and display and save it - it's where all the magic happens!",
                   "regular_pulse_button":"Sends laser pulses at regular intervals, with constant spacing.", 
                   "prr dropdown": "Specify the frequency you want to fire at - going about 200 Hz isn't recommended, as the laser tends to only be able to run at the frequency for about half a minute before stopping.", 
                   "gallop mode":"Sends a consecutive pair of lasers - with either 2ms or 8ms spacing as specified below. The first laser is called the 'prepulse,' and the following laser is called the 'ablation pulse.' Currently this is hardcoded to fire at 66.6 Hz.", 
                   "shot count":"Use this feature when beam profiling - will open the laser for the number of laser pulses you specify.", 
                   "q1c":"This is laser power. 1250 is recommend max, 1600 is the highest you should EVER set it (but don't set it to that).",
                   "focal length": "Used for file naming purposes only. Specifiy the focal length of the lens used, as this is an important factor that affects the plume formation.", 
                   "lens height":"Used for file naming purposes only. Specify how far the lens was from the sample, as this is also an important factor that affects the plume formation. This is a general optics concept you should ask Sascha about if you don't understand. (NOTE: The definition of lens height may be subject to change. Make sure to ask Sascha about how he would define lens height)", 
                   "autocorrector": "The autocorrector adjusts the Delay Between Triggers for optimal laser performance. See Delay Between Trigger tip for more info on what this is. The autocorrector uses a simple control loop that takes the median result over 10 laser pulses.", 
                   "lead delay":"Delay Between Triggers is the time in microseconds between when the teensy receives a Q23 signal from the pirl (see the report for what this is) and when it sends a high signal to the pirl to fire the laser. It is there with the purpose of optimizing laser performance. Delay Between triggers will vary in optimal value between 150μs and 200μs, depending on the mode of operation of the laser. Using the autocorrector helps ensure optimal pirl operation.", 
                   "flash delay":"Flash delay is the time in microseconds between when the ablation pulse hits and we actually take our picture - it is effectively plume lifetime. It's important to note that you can't completely control flash delay - there's a considerable variability in what actual firing delay you actually get. Read the report on why this is true.", 
                   "cam gain": "The gain on the Thorlabs scientific camera. 20 has been all I've ever needed to use (Daniel).", 
                   "motor distance": "Step size of the motor in millimetres.", 
                   "motor info text":"Take the following steps to set a new \"zero\" position for the sample platform:\n1. Move the platform to the desired location using the arrows\n2. Go into the config.json file, find the two floats in the second row that are in the same columns as curr_x_position and curr_y_position and change them both to 0.0\n3. Save the config.json file and reopen GUI.py",
                   "prepulse":"Puts a 2ms spacing between laser pulses in a 'pair' - the shutter will open and let BOTH laser pulses through, the first one considered the 'prepulse' and the second considered the 'ablation pulse' (because it's the one we actually record)", 
                   "no prepulse":"Puts an 8ms spacing between laser pulses in a 'pair'. The shutter takes ~6ms to open. In this mode, ONLY the ablation pulse goes through, and the shutter begins opening after the prepulse is blocked by it.",
                   "PID on off": "Turns the heater on and off.",
                   "target temp":"Set the target temp for the PID heater. The software by default has a max temp you can request, you can change this in the config.json file.",
                   "Kp":"The proportional constant for the PID heater controller. Wikipedia explains PID controllers well.",
                   "Ki":"The integral constant for the PID heater controller.Wikipedia explains PID controllers well.",
                   "Kd":"Kd is currently disabled. Derivative terms are frequently left unused in PID controllers due their sensitivity to sensor noise, which is what we've done here.",
                    "series flash delay":"Use this panel to run a series of measurements where FLASH DELAY varies, effectively seeing the plume at different stages in its lifetime. Set the START, STOP, and STEP to choose where the series of measurements begins, ends, and how much to increment by. Then enter MEASUREMENTS PER DELAY to choose how many pictures should be taken at each FLASH DELAY setting.",
                    "series power delay":"""Use this panel to run a series of measurements where pIRL LASER POWER (q1c) varies. Set the START, STOP, and STEP to choose where the series of measurements begins, ends, and how much to increment by. Then enter MEASURE PER POWER to choose how many pictures should be taken at each POWER setting.""",
                    "profiling":"This panel was put in to enable the usage of the custom pinhole-xy-stage beam profiler that Sascha proposed to Gabe and Dan in July 2025, but that we never had time to actually build. As such this is a useless button lol - Daniel, August 2025 ",
                    "qTune_option_button": "This will switch the laser to the Q-Tune, which we know is functioning properly at the moment. Clicking this will also stop the current laser from running (if it is on).",
                    "pirl_option_button": "This will switch the laser to the PIRL, which we know is not functioning properly at the moment. Clicking this will also stop the current laser from running (if it is on)"


                   }        