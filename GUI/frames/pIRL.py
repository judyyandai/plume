from GUI.frames.container import ContainerFrame
from GUI.widgets.entry_box import EntryBox
from GUI.widgets.tool_tip import ToolTip

class pIRLFrame(ContainerFrame):
    def __init__(self, parent, data_manager):
        super().__init__(parent, "pIRL")
        self.parent = parent
        self.data_manager = data_manager

        # Creating widgets
        self.entry_q1c = EntryBox(self, "q1c", self.data_manager.V_q1c, self.data_manager, self.set_pirl_q1c)
        ToolTip(self.entry_q1c.label, 'q1c')


    def set_pirl_q1c(self):
        """
        DESCRIPTION:
            Retrieve the q1c value from the entry box, and then change the q1c value via serial communication to the PIRL.
        PARAMETERS:
            None
        RETURN:
            None
        """
        
        self.entry_q1c.on_enter()
        q1c_value = self.data_manager.V_q1c.get()
        # self.pirl.q1c(q1c_value)     !!! implement