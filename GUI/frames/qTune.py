from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox

class QTuneFrame(ContainerFrame):
    def __init__(self, parent, data_manager, laser):
        """
        DESCRIPTION:
            Class used to create the Q-Tune panel which contains:
                - wavelength and pump energy level entries
        PARAMETERS:
            parent - (tk.Frame) the frame this frame is placed in
            data_manager - (dataManager) accesses and updates config.json files
            laser - (Laser) handles the state of the laser
        """
        super().__init__(parent, 'Q-Tune')
        self.parent = parent
        self.data_manager = data_manager
        self.laser = laser

        self.entry_qTune_wavelength = EntryBox(self, "Q-Tune Wavelength (nm)", self.data_manager.V_qTune_wavelength, self.data_manager, self.set_qTune_wavelength)
        self.entry_qTune_pump = EntryBox(self, "OPO Pump Energy Level (%)", self.data_manager.V_qTune_pump, self.data_manager, self.set_qTune_pump)
        # !!! tool tip


    def set_qTune_wavelength(self):
        """
        DESCRIPTION:
            Updates the qtune wavelength from the entry box, and calls the change on the laser object.

        """
        self.entry_qTune_wavelength.on_enter()
        qTune_wavelength = self.data_manager.V_qTune_wavelength.get()
        self.laser.change_qTune_wavelength(qTune_wavelength)
        

    def set_qTune_pump(self):
        """
        DESCRIPTION:
            Updates the OPO Pump Energy Level from the entry box, and calls the change on the laser object.

        """
        
        self.entry_qTune_pump.on_enter()
        qTune_pump = self.data_manager.V_qTune_pump.get()
        self.laser.change_qTune_pump(qTune_pump)