import tkinter as tk
from tkinter import messagebox

class EntryBox:
    def __init__(self, frame, label_text, variable, data_manager, function = None, send = True, width = 10):
        """
        DESCRIPTION: 
            Wrapper class for tk.Entry, tk.Label, and tk.Button. Allows user to create a single object that holds them all. 
        PARAMETERS:
            frame           (tk.Frame) frame object in which the objects are packed.
            label_text      (str) text for the label
            variable        (tkinter Variable) tkinter variable meant to store the value
            data_manager    (dataManager) where the value is stored
            function        (function) function to run
        """
        self.variable = variable
        self.function = function
        self.data_manager = data_manager
        self.entry_frame = tk.Frame(frame)
        self.entry_frame.pack(anchor = 'w', pady = 5)
        # Label
        self.label = tk.Label(self.entry_frame, text = label_text)
        self.label.pack(side = tk.LEFT, padx = 5)
        # Entry Box
        self.entry = tk.Entry(self.entry_frame, width = width)
        self.entry.insert(0, str(variable.get())) # put the variable value in the box
        self.entry.pack(side = tk.LEFT)
        self.entry.bind("<Return>", lambda event: self.on_enter(variable, self))
        # Send Button
        if send:
            self.send_button = tk.Button(self.entry_frame, 
                                         text = "Send", 
                                         command = function)
            self.send_button.pack(side = tk.LEFT)
        self.disabled = False
    
    def on_enter(self):
        """
        DESCRIPTION:
            Updates Tkinter variable associated with the EntryBox. Calls update_config_file to update config.json. Triggered with every 'Enter' and 'Send' if used correctly.
        PARAMETERS:
            variable: The tkinter variable to be updated with the new value.
            entrybox: The EntryBox object containing the entry object containing the new value
        RETURN:
            None
            
        """
        try:
            value = float(self.entry.get())
            self.variable.set(value)
            self.data_manager.update_config_file() # updates config file. 
            print(f"Value set to: {value}")
        except ValueError:
            messagebox.showinfo(title ="Invalid Input", message = "Please enter a valid input and try again!")
            print("Invalid input. Please enter a valid number.")
            self.entry.delete(0, tk.END)  # Optionally, clear the entry after invalid input
    def disable(self):
        """
        DESCRIPTION:
            Grey out all parts of EntryBox, including the entry, the send button, and the label. 
        PARAMETERS:
            None
        RETURN:
            None
        """
        if not self.disabled:
            self.disabled = True
            self.entry.config(state = 'disabled')
            self.label.config(state = 'disabled')
            if self.send_button:
                self.send_button.config(state = 'disabled')
    def enable(self):
        """
        DESCRIPTION:
            Un-grey out all parts of EntryBox, including the entry, the send button, and the label. 
        PARAMETERS:
            None
        RETURN:
            None
        """
        if self.disabled:
            self.disabled = False
            self.entry.config(state = 'normal')
            self.label.config(state = "normal")
            if self.send_button:
                self.send_button.config(state = 'normal')