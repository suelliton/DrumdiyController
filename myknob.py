from kivy.app import App
from knob import Knob
from pony.orm import *

class MyKnob(Knob):
    def __init__(self,**kwargs):
        super(MyKnob,self).__init__(**kwargs)
    def on_knob(self,value):

        mainwindow = App.get_running_app().root
        if mainwindow:
            if mainwindow.ser.isOpen():
                print("Serial Aberta")
                if self.id == "Gain":
                    mainwindow.sendGain(mainwindow.channel_master.pin,value)
                elif self.id == "Mask":
                    mainwindow.sendMask(mainwindow.channel_master.pin,value)
                elif self.id == "Scan":
                    mainwindow.sendScan(mainwindow.channel_master.pin,value)
                elif self.id == "Retrigger":
                    mainwindow.sendRetrigger(mainwindow.channel_master.pin,value)
                elif self.id == "Threshold":
                    mainwindow.sendThreshold(mainwindow.channel_master.pin,value)

            else:
                print("Serial Fechada")

            mainwindow.selected.saved = False





class Teste(App):
    def build(self):
        return MyKnob()


if __name__ == "__main__":
    Teste(title = "ControlSpinner class").run()
