# Main function to run the Plume GUI application
# created by Judy Dai and Robyn Astridge, major work done by Enzo Picini, Chloe Lawson, Kenny Lai, Gabriel Caribe, and Daniel Pinto

from GUI.main_window import MainWindow


def start():
    """Intialize and start the Plume Application"""
    gui = MainWindow()

    gui.mainloop()



start()