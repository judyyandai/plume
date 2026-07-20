
class ExperimentController:
    def __init__(self, experiment, laser_frame, image_frame, pg_frame, rsfd_frame):
        self.experiment = experiment
        self.laser_frame = laser_frame
        self.image_frame = image_frame
        self.pg_frame = pg_frame
        self.rsfd_frame = rsfd_frame

        self.folder = image_frame.get_folder_entry()

        self.experiment.image_callback = self.on_image # experiment: image aquired -> image_frame : display image
        self.experiment.text_callback = self.on_text # experiment : valid plume parameters aquired -> image_frame : display parameters
        self.experiment.text_callback_invalid = self.on_text_invalid # experiment : invalid plume -> image_frame : display text "INVALID"
        self.experiment.flash_delay_callback = self.on_flash_delay # experiment : flash delay in run series needs to be updated -> pg_frame : update flash delay
        self.experiment.rsfd_done_callback = self.rsfd_done # experiment : flash delay series is completed -> rsfd_frame : update button

        self.image_frame.save_current_callback = self.on_save_current # image_frame : save current button is pressed -> experiment : saves

        self.laser_frame.experiment_start_callback = self.start # laser_frame : begin measuring is pressed -> experiment : start
        self.laser_frame.experiment_stop_callback = self.stop # laser_frame : stop experiment is pressed -> experiment : stop

        self.rsfd_frame.rsfd_start_callback = self.start_rsfd # rsfd_frame : begin series is pressed -> experiment : begin experiment with mode "rs"
        self.rsfd_frame.rsfd_stop_callback = self.stop_rsfd

        self.laser_frame.rsfd_enable_callback = self.rsfd_enable
        self.laser_frame.rsfd_disable_callback = self.rsfd_disable


    def stop(self):
        self.experiment.stop()

    def start(self, total_measurements, mode, option):
        self.experiment.start(total_measurements, mode, option, self.folder)

    def start_rsfd(self, total_measurements, mode, option):
        self.start(total_measurements, mode, option)
        self.laser_frame.disable_panel()

    def stop_rsfd(self):
        self.stop()
        self.laser_frame.update_frame()

    def rsfd_enable(self):
        self.rsfd_frame.b_series.config(state = 'normal')

    def rsfd_disable(self):
        self.rsfd_frame.b_series.config(state = 'disabled')

    def on_image(self, image):
        self.image_frame.after(0, lambda: self.image_frame.update_photo_display(image))

    def on_text(self, true_delay, flash_voltage, pulse_voltage, pulse_energy):
        self.image_frame.after(0, lambda: self.image_frame.update_text(true_delay, flash_voltage, pulse_voltage, pulse_energy))

    def on_text_invalid(self):
         self.image_frame.after(0, lambda: self.image_frame.update_text_invalid())

    def on_save_current(self):
        self.experiment.save_current()

    def rsfd_done(self):
        self.rsfd_frame.done()

    def on_flash_delay(self, delay_new):
        self.pg_frame.update_flash_delay(delay_new)

    def experiment_is_set(self):
        return self.experiment.e_experimentOn.is_set()
    
