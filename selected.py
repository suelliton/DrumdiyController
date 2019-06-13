from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.label import Label
from kivy.app import App
from kivy.graphics import *
from PIL import Image as Im
from pony.orm import *
from pony.orm.dbproviders import sqlite
from model import Channel
from controlknob import ControlKnob
from controlknob2 import ControlKnob2
from controlspinner import ControlSpinner
from threading import Thread
from kivy.properties import BooleanProperty
Builder.load_file('kv/selected.kv')
class Selected(BoxLayout):
    saved = BooleanProperty()
    def __init__(self,channel,**kwargs):
        super(Selected,self).__init__(**kwargs)
        print("canal selecionado ",channel.name)
        self.dict_controls = {}
        self.back_image = None
        self.saved = True
        self.checked_control  = None
        properties = {"Mask":channel.mask,"Scan":channel.scan,
        "Retrigger":channel.retrigger,"Threshold":channel.threshold,"Gain":channel.gain}

        self.notes = ["4 (HHC Chimbal)","7 (Chimbal Borda)","8 (Chimbal Centro)","9 (Chimbal Cúpula)","36 (Bumbo)","37 (Caixa RimShot)","38 (Caixa Centro)",
        "42 (Caixa Aro)","60 (Condução)","61 (Condução Cupula)","62 (Condução Borda)","65 (Tom 4 Centro)","67 (Tom 3 Centro)","69 (Tom 2 Centro)","71 (Tom 1 Centro)",
        "77 (Crash 1)","79 (Crash 2)","81 (Crash 3)","3 (HHC 2)","5 (Caixa CCpos Fechado)","6 (Caixa CCpos Aberto)","39 (Caixa RimShot dbi)","40 (Caixa Centro dbi)","43 (Caixa Shallow Now)",
                                "44 (Aro)","66 (Tom 4 RimShot)","68 (Tom 3 RimShot)","70 (Tom 2 RimShot)","72 (Tom 1 RimShot)","63 (Condução Choke)","78 (Crash 1 Choke)","80 (Crash 2 Choke)","82 (Crash 3 Choke)",""]

        self.pins = ["A0","A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12","A13","A14","A15"]

        self.ids.grid_controlknobs.clear_widgets()
        self.ids.grid_controlspinners.clear_widgets()

        self.ids.name_channel.text = channel.name

        controlspinner_pin = ControlSpinner(id="Pin")
        controlspinner_pin.ids.label.text = "Pin"
        controlspinner_pin.ids.spinner.values = self.pins
        controlspinner_pin.ids.spinner.text = "A"+str(channel.pin)
        #controlspinner_pin.ids.spinner.id = "Pin"
        self.ids.grid_controlspinners.add_widget(controlspinner_pin)
        self.dict_controls["Pin"] = controlspinner_pin.ids.spinner#adiciona no dicionario pra sobrecrever depois

        controlspinner_note = ControlSpinner(id="Note")
        controlspinner_note.ids.label.text = "Nota"
        controlspinner_note.ids.spinner.values = self.notes
        controlspinner_note.ids.spinner.text = str(channel.note)
        #controlspinner_note.ids.spinner.id = "Note"
        self.ids.grid_controlspinners.add_widget(controlspinner_note)
        self.dict_controls["Note"] = controlspinner_note.ids.spinner

        for key in properties.keys():
            if key != "Gain" and key != "Threshold":
                controlknob = ControlKnob(id=key)
                controlknob.ids.label_control.text = key
                controlknob.ids.knob_control.value = properties[key]
                controlknob.ids.knob_control.id = key #troca o id knob pelo nome da propriedade scan mask gain etc
                self.dict_controls[key] = controlknob.ids.knob_control
                self.ids.grid_controlknobs.add_widget(controlknob)
            else:
                controlknob2 = ControlKnob2(id=key)
                controlknob2.ids.label_control.text = key
                controlknob2.ids.knob_control.value = properties[key]
                controlknob2.ids.knob_control.id = key #troca o id knob pelo nome da propriedade scan mask gain etc
                controlknob2.ids.checkbox.id = key #troca o id checked pelo nome da propriedade scan mask gain etc
                self.dict_controls[key] = controlknob2.ids.knob_control
                self.ids.grid_controlknobs.add_widget(controlknob2)

        self.set_initial_background_channel(channel)

    def set_values(self,channel):
        self.ids.name_channel.text = channel.name
        self.dict_controls["Gain"].value = channel.gain
        self.dict_controls["Mask"].value = channel.mask
        self.dict_controls["Scan"].value = channel.scan
        self.dict_controls["Threshold"].value = channel.threshold
        self.dict_controls["Retrigger"].value = channel.retrigger
        self.dict_controls["Note"].text = str(channel.note)
        self.dict_controls["Pin"].text = "A"+str(channel.pin)
        self.set_background_channel(channel)

    def set_background_channel(self,channel):
        back = self.ids.image_background_channel
        if self.back_image != None:
            back.canvas.before.remove(self.back_image)
        with back.canvas.before:
            self.back_image=Rectangle(source=channel.image, pos=back.pos,size=self.get_image_size(channel.image))
        print("pos  ",back.pos)
        print("size  ",back.size)

    def set_initial_background_channel(self,channel):
        back = self.ids.image_background_channel
        with back.canvas.before:
            self.back_image = Rectangle(source=channel.image, pos= (750, 20),size= self.get_image_size(channel.image))

    def get_image_size(self,src):
        im = Im.open(src)
        return im.size
    def save(self):
        mainwindow = App.get_running_app().root
        t = Thread(target=mainwindow.thread_progress())
        t.start()
        pin = self.dict_controls["Pin"].text.split("A")[1]#solução pra pegar só o numero
        note = self.dict_controls["Note"].text.split(" ")[0]
        retrigger = self.dict_controls["Retrigger"].value
        mask = self.dict_controls["Mask"].value
        scan = self.dict_controls["Scan"].value
        threshold = self.dict_controls["Threshold"].value
        gain = self.dict_controls["Gain"].value
        if mainwindow.ser.isOpen():
            mainwindow.sendToArduino(pin,note,retrigger,mask,scan,threshold,gain)
        self.update_channel_in_database(pin,note,retrigger,mask,scan,threshold,gain)


    def update_channel_in_database(self,pin,note,retrigger,mask,scan,threshold,gain):
        mainwindow = App.get_running_app().root
        mainwindow.channel_master.pin = int(pin)
        mainwindow.channel_master.note = int(note)
        mainwindow.channel_master.retrigger = int(retrigger)
        mainwindow.channel_master.mask = int(mask)
        mainwindow.channel_master.scan = int(scan)
        mainwindow.channel_master.threshold = int(threshold)
        mainwindow.channel_master.gain = int(gain)
        self.saved = True

    def select_auto(self,check):

        if self.checked_control != None:
            self.checked_control.active = False
            if check.id == self.checked_control.id:
                check.active = False

        self.checked_control = check
        if self.checked_control.active == False:
            mainwindow = App.get_running_app().root
            mainwindow.active_auto = False
        else:
            mainwindow = App.get_running_app().root
            mainwindow.active_auto = True

        print("check ",check.id )



class Teste(App):
    def build(self):
        return Selected()


if __name__ == "__main__":
    Teste(title = "Selected class").run()
