# Frame for laser options (pIRL or Q-Tune)
import tkinter as tk
from GUI.frames.container_frame import ContainerFrame


class LaserOptionFrame(ContainerFrame):
    def __init__(self,parent):
        super().__init__(parent, "Laser Option")

        option_row = tk.Frame(self)
        option_row.pack(anchor="w", pady=(15, 15))

        tk.Radiobutton(
            option_row,
            text="Q-Tune",
        ).pack(anchor="w")

        tk.Radiobutton(
            option_row,
            text="PIRL",
        ).pack(anchor="w")