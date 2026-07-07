from threading import Event

class PulseGenerator():
    def __init__(self):
        self.e_PulseGenerator = Event()



    def toggle(self):
        self.e_PulseGenerator.set()