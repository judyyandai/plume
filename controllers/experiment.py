from threading import Event

class ExperimentController:
    def __init__(self, experiment, image_frame):
        self.experiment = experiment
        self.image_frame = image_frame

        self.folder = image_frame.get_folder_entry()

        self.experiment.image_callback = self.on_image
        self.experiment.text_callback = self.on_text
        self.experiment.text_callback_invalid = self.on_text_invalid
        self.image_frame.save_current_callback = self.on_save_current


    def stop(self):
        self.experiment.e_experimentOn.clear()

    def start(self,  total_measurements, mode, option):
        self.experiment.e_experimentOn.set()
        self.experiment.start(total_measurements, mode, option, self.folder)


    def on_image(self, image):
        self.image_frame.after(0, lambda: self.image_frame.update_photo_display(image))

    def on_text(self, true_delay, flash_voltage, pulse_voltage, pulse_energy):
        self.image_frame.after(0, lambda: self.image_frame.update_text(true_delay, flash_voltage, pulse_voltage, pulse_energy))

    def on_text_invalid(self):
         self.image_frame.after(0, lambda: self.image_frame.update_text_invalid())

    def on_save_current(self):
        self.experiment.save_current()

    def experiment_is_set(self):
        return self.experiment.e_experimentOn.is_set()
    
