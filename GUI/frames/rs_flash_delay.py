from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip
import tkinter as tk

class RSFlashDelay(ContainerFrame):
    def __init__(self, parent, data_manager, pg_control_frame, flash_delay_series):
        super().__init__(parent, "Run Series: Vary Flash Delay")

        self.data_manager = data_manager
        self.pg_control_frame = pg_control_frame
        self.flash_delay_series = flash_delay_series

        ToolTip(self, "series flash delay")

        # Creating Widgets
        self.start_delay_us = EntryBox(self, "Start [μs]", self.data_manager.V_start_delay_us, self.data_manager, self.run_series, send = False)
        self.data_manager.V_start_delay_us.trace_add("write", self.update_flash_measurement_count)

        self.stop_delay_us = EntryBox(self, "Stop [μs]", self.data_manager.V_stop_delay_us, self.data_manager, self.run_series, send = False)
        self.data_manager.V_stop_delay_us.trace_add("write", self.update_flash_measurement_count)

        self.interval_us = EntryBox(self, "Step [μs]", self.data_manager.V_interval_us, self.data_manager, self.run_series, send = False)
        self.data_manager.V_interval_us.trace_add("write", self.update_flash_measurement_count)

        self.meas_per_delay = EntryBox(self, "Measurements per flash delay:", self.data_manager.V_meas_per_delay, self.data_manager, self.run_series, send = False)
        self.data_manager.V_meas_per_delay.trace_add("write", self.update_flash_measurement_count)

        # run series button
        self.b_series = tk.Button(self, text = "Run Series Measurement", command = self.run_series)
        self.b_series.pack(anchor = "nw", side = "left", pady=40, padx = 20)
        self.L_flash_num_measurements = tk.Label(self, wraplength = 175)
        self.L_flash_num_measurements.pack(side = tk.LEFT)
        self.V_flash_num_measurements = tk.IntVar()
        self.update_flash_measurement_count()
        #self.b_series.config(state = 'disabled')



    def update_flash_measurement_count(self, *args): 
        """
        DESCRIPTION:
            Display the number of measurements that will be performed for a given start, stop, step, and measurements per chosen. Purely for convenience.
        PARAMETERS
            None.
        RETURN: 
            None.
        """
        try:
            n = ((self.data_manager.V_stop_delay_us.get() - self.data_manager.V_start_delay_us.get())
                 //self.data_manager.V_interval_us.get()+1) * self.data_manager.V_meas_per_delay.get()
        
            self.V_flash_num_measurements.set(n)
            self.L_flash_num_measurements.config(text = f"No. of measurements: {self.V_flash_num_measurements.get()}")
        except ZeroDivisionError:
            self.L_flash_num_measurements.config(text = f"Cannot have step size be 0 - the series will never terminate!")



    def run_series(self):
        """
        DESCRIPTION:
            Run a series of plume measurements, varying flash delay in defined steps. 
        PARAMETERS:
            None.
        RETURN:
            None
        """
        # Sets parameters to whatever is in the text bar
        self.start_delay_us.on_enter()
        self.stop_delay_us.on_enter()
        self.interval_us.on_enter()
        self.meas_per_delay.on_enter()
        
        #set_params
        self.flash_delay_series.set_V_times_run(0)
        total_measurements = self.V_flash_num_measurements.get()
        print('total measurements:', total_measurements)
        
        self.pg_control_frame.entry_FlashDelay.entry.delete(0,"end")
        self.pg_control_frame.entry_FlashDelay.entry.insert(0,self.data_manager.V_start_delay_us.get())
        self.data_manager.V_FlashDelay_us.set(self.data_manager.V_start_delay_us.get()) 
        
        self.b_series.config(text ="Running flash delay series.", fg = "red")
        self.flash_delay_series.toggle() 
        
        return