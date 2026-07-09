from threading import Event
#!!! pretty sure this is not needed

class PulseGenerator():
    def __init__(self):
        self.e_PulseGenerator = Event()



    def toggle(self):
        self.e_PulseGenerator.set()