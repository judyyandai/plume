import sys
from GUI import MainWindow
import tkinter as tk
from tkinter import ttk



def start():
    """Intialize and start the Plume Application"""
    gui = MainWindow()

    gui.mainloop()



start()