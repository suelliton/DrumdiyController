#classe responsável por desenhar os spinners de controle de nota e pin
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.uix.label import Label
from kivy.app import App
from model import Channel
from pony.orm import *
from pony.orm.dbproviders import sqlite
Builder.load_file('kv/controlspinner.kv')
class ControlSpinner(BoxLayout):
    def __init__(self,**kwargs):
        super(ControlSpinner,self).__init__(**kwargs)
    @db_session
    def on_modify(self,text):
        print("texts on modyfi",text)
        mainwindow = App.get_running_app().root
        if mainwindow:
            if self.id == "Pin":
                print("entrou no spinner pin")
                mainwindow.channel_master.pin = int(text.split("A")[1])

            elif self.id == "Note":
                print("entrou no spinner note")
                mainwindow.channel_master.note = int(text.split(" ")[0])
                if mainwindow.ser.isOpen():
                    mainwindow.sendNote(mainwindow.channel_master.pin ,text.split(" ")[0])
                #vai ser melhor colocar todas variaveis importantes na mais pra acessar de aulquer lugar
            mainwindow.channel_master.save()
            mainwindow.selected.saved = False
class Teste(App):
    def build(self):
        return ControlSpinner()


if __name__ == "__main__":
    Teste(title = "ControlSpinner class").run()
