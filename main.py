# Main function to run the Plume GUI application
# created by Judy Dai and Robyn Astridge; major work done by Enzo Picini, Chloe Lawson, Kenny Lai, Gabriel Caribe, and Daniel Pinto

from GUI.main_window import MainWindow
from logic.Plupy import Plupy as pl


def start(devices):
    """Intialize and start the Plume Application"""
    gui = MainWindow(device_connections=devices)
    gui.mainloop()



with pl.initialize_all() as devices:
   start(devices)