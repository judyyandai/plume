import tkinter as tk
from PIL import Image, ImageTk

class ImageFrame(tk.LabelFrame):
    def __init__(self, parent, data_manager):
        super().__init__(parent, text="Image Display", padx=0, pady=0)
        self.pack(side = tk.RIGHT, anchor = "ne", padx=5, pady=5, fill="both", expand=True)


        self.data_manager = data_manager
        self.save_current_callback = None

        


        # Make folder Entry frame
        self.folder_entry_frame = tk.Frame(self)
        self.folder_entry_frame.pack(padx = 5, pady = 5)

        # Make save check
        save_check = tk.Checkbutton(self, text="Save", variable=self.data_manager.V_save)
        save_check.pack(side = "top", anchor = 'w', pady = 5, padx = 5)

        self.folder_entry = tk.Entry(self.folder_entry_frame,
                                     width = 40)
        self.folder_entry.insert(0, self.data_manager.folder.get())
        self.folder_entry.pack(side=tk.LEFT, fill = 'x')

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

        #save current image button
        currSave_button = tk.Button(self, text="Save Current", command=self.save_current)
        currSave_button.pack(anchor = "nw",side = "left", pady=40, padx = 20)


    def save_current(self):
        if self.save_current_callback:
            self.save_current_callback()

    def get_folder_entry(self):
        return self.folder_entry.get()


    def update_text(self, true_delay, flash_voltage, pulse_voltage, pulse_energy, pressure = 0, firing_delay = 0):
        display_message = f"Plume lifetime: {true_delay} ns\nFlash Voltage = {flash_voltage:.3f} V \n Pressure = {pressure:.3e} mbar \n Current Pulse Voltage =  {pulse_voltage:.3f} V \n Firing Delay = {firing_delay:.2f} us \n Pulse Energy(J) = {pulse_energy}"
        self.time_label.configure(text = display_message , font = ("Roboto", 12))

    def update_text_invalid(self):
        self.time_label.configure(text = "INVALID" , font = ("Roboto", 12))

    def update_photo_display(self, image):
        image_resized = self.resize_image(Image.fromarray(image))
        self.photo = ImageTk.PhotoImage(image_resized)
        self.image_label.configure(image = self.photo)

    def resize_image(self, image):
        """
        DESCRIPTION:
            Function to resize image. Depending on the proportion of the width and height of the original image 
            and maximum height&width of the original image, the resized image could be constrain by width or height
        PARAMETERS:
            image: image to be resized
            max_width: Max width of resized image
            max_height: Max height of resized image
        RETURN:
            Resized image. 
        """
        max_width = self.image_label.winfo_width()
        max_height = self.image_label.winfo_height()

        image_ratio = image.width / image.height
        frame_ratio = max_width / max_height
        if frame_ratio > image_ratio:
            # Constrain by height
            new_height = max_height
            new_width = int(new_height * image_ratio)
        else:
            # Constrain by width
            new_width = max_width
            new_height = int(new_width / image_ratio)

        return image.resize((new_width, new_height), Image.LANCZOS)

