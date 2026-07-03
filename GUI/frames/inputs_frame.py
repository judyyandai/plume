# Frame for Input Values

import tkinter as tk
from tkinter import ttk
from GUI.frames.container_frame import ContainerFrame

class InputsFrame(ContainerFrame):
    def __init__(self, parent):
        super().__init__(parent, "File")