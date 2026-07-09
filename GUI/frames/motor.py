from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip
import tkinter as tk
from tkinter import messagebox

class MotorFrame(ContainerFrame):
    def __init__(self, parent, data_manager, motor):
        """
        DESCRIPTION:
            Class used to create the motor panel which contains:
                - up/down/left/right buttons
                - distance entry
                - current possition display
                - description about the panel
        PARAMETERS:
            parent - (tk.Frame) the frame this frame is placed in
            data_manager - (dataManager) accesses and updates config.json files
            motor - (Motor) object that handles the state of the motor
        """
        super().__init__(parent, "Motor Control Panel")
        
        self.container = parent
        self.data_manager = data_manager
        self.motor = motor

        # Creating widgets
        self.step_frame = tk.Frame(self)
        self.step_frame.grid(row=0, column=6, padx=5, pady=0)

        self.entry_MotorStepDistance = EntryBox(self.step_frame, "Distance [mm]", self.data_manager.V_MotorStepDistance, self.data_manager, self.motor_setup)
        ToolTip(self.entry_MotorStepDistance.label, "motor distance")

        # position_label_text is the text that gets displayed on the label; doing it this way updates the label dynamically
        position_frame = tk.Frame(self)
        position_frame.grid(row=1, column=6)
        self.position_label_text = tk.StringVar(
            value = f"Current Position:\nx position: {self.data_manager.V_curr_x_position.get()} mm\ny position: {self.data_manager.V_curr_y_position.get()} mm")
        self.position_label = tk.Label(position_frame, textvariable=self.position_label_text, justify="left")
        self.position_label.pack(fill = "x", padx = 2, pady = 2)
        position_description_frame = tk.Frame(self)
        position_description_frame.grid(row=2, column=6, padx=5, pady=5)
        position_description = (f"This position describes the sample location relative to when it was centered on [date]."
                                 f"x it positive towards the room with the DEM, and negative in the opposite direction." 
                                 f"y is positive towards the camera and negative towards the flash lamp."
                                  f"\nCURRENT SAFE MAX AND MIN VALUES ARE" 
                                  f"\nX={self.data_manager.max_x}mm, X={self.data_manager.min_x}mm, Y={self.data_manager.max_y}mm, Y={self.data_manager.min_y}mm")
        tk.Label(position_description_frame, text=position_description,  font = "Roboto 10", justify = "left", wraplength = 300).pack(fill = "x", padx = 2, pady = 2)
        # Info hover button

        hover_button_frame = tk.Frame(self)
        hover_button_frame.grid(row=4, column=6, padx=5, pady=5)
        

        recentering_instruction = tk.Label(hover_button_frame, text="Recentering Instructions (rightclick) ℹ️ ", fg = "blue", font=("Arial", 11))
        recentering_instruction.pack(padx = 2, pady = 2)
        ToolTip(recentering_instruction, "motor info text")
        
        # Motor buttons
        self.create_button(self, "˄", [1,1], self.motor_up)
        self.create_button(self, "˅", [3,1], self.motor_down)
        self.create_button(self, "˂", [2,0], self.motor_left)
        self.create_button(self, "˃", [2,2], self.motor_right)

        # Add visuals to motor movement directions
        self.motor_pictures(self)


    def motor_setup(self):
        """
        DESCRIPTION:
            Retrieves the motor step distance value from the entry box, and saves it.   
        """
        self.entry_MotorStepDistance.on_enter()


    def move_motor_with_limits(self, sign, direction):
        """
        DESCRIPTION:
            Move the motor in the desired direction. Updates and saves the motors current position, and ensures it doesn't exceed
            its max and min movement range for both the x and y directions.
        PARAMETERS
            sign: integer must be -1 for negative directions (left & down) or +1 for positive directions (right & up)
            direction: string. "x" or "y" are valid.

        """
        try:
            dist = self.data_manager.V_MotorStepDistance.get()
            if direction == "x":
                new_x_pos = self.data_manager.V_curr_x_position.get() + sign*dist
                if (new_x_pos > self.data_manager.min_x) and (new_x_pos < self.data_manager.max_x):
                    self.data_manager.V_curr_x_position.set(new_x_pos)
                    self.data_manager.update_config_file()
                    print(f"Current x position set to: {new_x_pos}mm")
                    if sign == 1:
                        self.motor.right(dist)
                    elif sign == -1:
                        self.motor.left(dist)
                    else:
                        print("Please enter a valid sign! Motor position not moved")
                        old_x_pos = new_x_pos - sign*dist
                        self.data_manager.V_curr_x_position.set(old_x_pos)
                        self.data_manager.update_config_file()
                    self.position_label_text.set(
                        f"Current Position: \nx position: {self.data_manager.V_curr_x_position.get()} mm\ny position: {self.data_manager.V_curr_y_position.get()} mm")
                else:
                    messagebox.showinfo(
                        title ="Motor Position Out of Range", 
                        message = (f"You tried moving the motor too far!" 
                                   f"\nThe max and min x distances are {self.data_manager.max_x}mm and {self.data_manager.min_x}mm respectively" 
                                   f"\nThe max and min y distances are {self.data_manager.max_y}mm and {self.data_manager.min_y}mm respectively" 
                                   f"\nYou tried setting the position x = {new_x_pos}mm and y = {self.data_manager.V_curr_y_position.get()}mm" 
                                   f"\n Please decrease the distance or switch directions and try again."))
            elif direction == "y":
                new_y_pos = self.data_manager.V_curr_y_position.get() + sign*dist
                if (new_y_pos > self.data_manager.min_y) and (new_y_pos < self.data_manager.max_y):
                    self.data_manager.V_curr_y_position.set(new_y_pos)
                    self.data_manager.update_config_file()
                    print(f"Current y position set to: {new_y_pos}mm")
                    if sign == 1:
                        self.motor.back(dist)
                    elif sign == -1:
                        self.motor.forward(dist)
                    else:
                        print("Please enter a valid sign! Motor position not moved")
                        old_y_pos = new_y_pos - sign*dist
                        self.data_manager.V_curr_y_position.set(old_y_pos)
                        self.data_manager.update_config_file()
                    self.position_label_text.set(f"Current Position: \nx position: {self.data_manager.V_curr_x_position.get()} mm\ny position: {self.data_manager.V_curr_y_position.get()} mm")
                else:
                    messagebox.showinfo(
                        title ="Motor Position Out of Range", 
                        message = f"You tried moving the motor too far!" 
                        f"\nThe max and min x distances are {self.data_manager.max_x}mm and {self.data_manager.min_x}mm respectively" 
                        f"\nThe max and min y distances are {self.data_manager.max_y}mm and {self.data_manager.min_y}mm respectively" 
                        f"\nYou tried setting the position x = {self.data_manager.V_curr_x_position.get()}mm and y = {new_y_pos}mm" 
                        f"\n Please decrease the distance or switch directions and try again.")
            else:
                print("Please enter a valid direction! Options are 'x' and 'y'. The motor was not moved")
        except ValueError:
            messagebox.showinfo(title ="Invalid Input", message = "Please enter a valid input and try again!")
            print("Invalid input. Please enter a valid number.")


    def motor_up(self):
        """
        DESCRIPTION:
            Move the motor towards the camera by a predefined amount.

        """
        self.move_motor_with_limits(1, 'y')

    def motor_down(self):
        """
        DESCRIPTION:
            Moves the motor towards the flash lamp by a predefined amount.
        """
        self.move_motor_with_limits(-1, 'y')
    
    def motor_left(self):
        """
        DESCRIPTION:
            Moves the motor away from the room with the Electron Microscope (DEM) by a predefined amount.
        """
        self.move_motor_with_limits(-1, 'x')
        
    
    def motor_right(self):
        """
        DESCRIPTION:
            Moves the motor towards the room with the Electron Microscope (DEM) by a predefined amount.
        """
        self.move_motor_with_limits(1, 'x')       
        

    def create_button(self, frame, label_text, position, command):
        """
        DESCRIPTION:
            Function to create custom button widgets.
        PARAMETERS:
            frame: The frame to pack the widget into
            label_text: The text for the label
            posiion: list with 2 elements to indicate the grid position on the frame
            command: function associated with the button
        """
        # Creating frame
        button_frame = tk.Frame(frame)
        button_frame.grid(row=position[0], column=position[1], padx=5, pady=5)
        
        # Creating Button
        Button = tk.Button(button_frame, text=label_text, command=command)
        Button.grid(row=0, column=0, padx=5, pady=5)


    def motor_pictures(self, Motor_frame):
        """
        DESCRIPTION: 
            creates and places the little pictures that are displayed by the motor driver movement, to help the user navigate
        PARAMETERS:
            Motor_frame: frame where the rest of the motor movement buttons are
        """
        self.motor_canvas_top = tk.Canvas(Motor_frame, width=40, height=30)
        self.motor_canvas_top.grid(row=0, column=1, padx=1, pady=1)
        self.motor_canvas_top.create_polygon(10, 17, 30, 17, 30, 7, 25, 7, 25, 3, 15, 3, 15, 7, 10, 7, 
                                         outline="black", width=2, fill='') # Camera Outline
        self.motor_canvas_top.create_oval(17, 8, 23, 14, outline="black", width=2, fill='') # Camera Lens
        self.motor_canvas_top.create_text(20, 23, text="Camera", font="Gerogia 8")

        self.motor_canvas_center = tk.Canvas(Motor_frame, width=40, height=40)
        self.motor_canvas_center.grid(row=2, column=1, padx=1, pady=1)
        self.motor_canvas_center.create_text(20, 20, text="Sample\nHere", font="Gerogia 8 italic", justify="center")
        
        self.motor_canvas_bottom = tk.Canvas(Motor_frame, width=30, height=50)
        self.motor_canvas_bottom.grid(row=4, column=1, padx=1, pady=1)
        self.motor_canvas_bottom.create_polygon(2, 38, 2, 42, 10, 42, 14, 45, 14, 35, 10, 38,  
                                         outline="black", width=2, fill='') # Flashlight
        self.motor_canvas_bottom.create_line(16, 37, 20, 30, width=2, fill='black') # Flashlight Flash 1
        self.motor_canvas_bottom.create_line(16, 40, 24, 40, width=2, fill='black') # Flashlight Flash 2
        self.motor_canvas_bottom.create_line(16, 43, 20, 50, width=2, fill='black') # Flashlight Flash 2
        self.motor_canvas_bottom.create_text(15, 15, text="Flash\nLamp", font="Gerogia 8")

        self.motor_canvas_right = tk.Canvas(Motor_frame, width=30, height=70)
        self.motor_canvas_right.grid(row=2, column=3, padx=1, pady=1)
        self.motor_canvas_right.create_rectangle(10, 47, 23, 68, outline="black", width=2, fill='') # Door
        self.motor_canvas_right.create_line(17, 57, 21, 57, width=1, fill='black') # Door Handle
        self.motor_canvas_right.create_rectangle(12, 49, 15, 55, outline="black", width=1, fill='') # Door Detail Top Left
        self.motor_canvas_right.create_rectangle(17, 49, 20, 55, outline="black", width=1, fill='') # Door Detail Top Right
        self.motor_canvas_right.create_rectangle(12, 59, 15, 65, outline="black", width=1, fill='') # Door Detail Bottom Left
        self.motor_canvas_right.create_rectangle(17, 59, 20, 65, outline="black", width=1, fill='') # Door Detail Bottom Right
        self.motor_canvas_right.create_text(15, 25, text="Room\nWith\nDEM", font="Gerogia 8", justify="center")