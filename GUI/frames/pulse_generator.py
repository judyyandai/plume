import tkinter as tk
from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip

class PulseGeneratorFrame(ContainerFrame):
    def __init__(self, parent, data_manager, pg):
        """
        DESCRIPTION:
            Class used to create the pulse generator panel which contains:
                - flash delay and delay between triggers entry
                - autocorrect option
        PARAMETERS:
            parent - (tk.Frame) the frame this frame is placed in
            data_manager - (dataManager) accesses and updates config.json files
            pg - (Pulse Generator) object that handles the state of the pulse generator
        """
        super().__init__(parent, "Pulse Generator Control")
        
        self.container = parent
        self.data_manager = data_manager
        self.pg = pg

        # Creating widgets
        self.entry_FlashDelay = EntryBox(self, "Flash Delay [μs]", self.data_manager.V_FlashDelay_us, self.data_manager, self.pg_setup)
        ToolTip(self.entry_FlashDelay.label, "flash delay")
        
        self.entry_DelayBetweenTriggers = EntryBox(
            self, 
            "Delay Between Triggers [μs]", 
            self.data_manager.V_DelayBetweenTriggers, 
            self.data_manager, 
            self.set_DelayBetweenTriggers)
        ToolTip(self.entry_DelayBetweenTriggers.label, "lead delay")
        
        self.B_autocorrector = self.create_checkbox(
            self, 
            "Autocorrect (median over 10 laser shots)", 
            self.data_manager.V_autocorrector, 
            checkbox_command = self.autocorrector_update)
        ToolTip(self.B_autocorrector, "autocorrector")



    def pg_setup(self):
        """
        DESCRIPTION:
            Enter the flash delay into config.json.
        """
        self.entry_FlashDelay.on_enter()



    def update_flash_delay(self, delay_new):
        self.entry_FlashDelay.entry.delete(0,"end")
        self.entry_FlashDelay.entry.insert(0,delay_new)
        self.entry_FlashDelay.on_enter()

        

    def set_DelayBetweenTriggers(self):
        """
        DESCRIPTION:
            Enter the delay between triggers into config.json, and send it to the teensy.
        """
        self.entry_DelayBetweenTriggers.on_enter()
        #DelayBetweenTriggers = self.data_manager.V_DelayBetweenTriggers.get()      #!!! go to pg file in logic before teensy
        #self.teensy.delayBetweenTriggers(DelayBetweenTriggers)



    def create_checkbox(self, frame, label_text, variable, checkbox_command, anc = "w", side = tk.LEFT):
        """
        DESCRIPTION:
            Function to create Checkbutton widgets.
        PARAMETERS:
            frame: The frame to pack the widget into
            label_text: The text for the label
            variable: The Variable associated with the checkbox
        RETURN:
            Checkbox tkinter widget that can be manipulated later
        """
        # Creating frame
        checkbox_frame = tk.Frame(frame)
        checkbox_frame.pack(anchor=anc, pady=5)
        
        # Creating Checkbox
        checkbox = tk.Checkbutton(checkbox_frame, text=label_text, variable=variable, command = checkbox_command)
        checkbox.pack(side=side, padx=5)
        return checkbox

    # !!! autocorrector 
    def autocorrector_update(self):
        self.data_manager.update_config_file()