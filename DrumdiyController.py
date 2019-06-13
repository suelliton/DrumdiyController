
from __future__ import print_function
#from ctypes import *
#from kivy.deps import sdl2, glew
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
#from kivy.uix.gridlayout import GridLayout
#from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.label import Label
#from kivy.uix.image import Image
from kivy.uix.popup import Popup
#from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
#from knob import Knob
import _thread as thread
#from PIL import Image as Im
import serial
import serial.tools.list_ports
import rtmidi_python as rtmidi
from kivy.core.window import Window
from kivy import Config
import time
#from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Rectangle,Line,Color
from model import Channel
from threading import Thread
from kivy.clock import Clock
from kivy.properties import ObjectProperty,ListProperty,BooleanProperty
from kivy.graphics.texture import Texture
import struct
#import cython
#import pyximport
import subprocess
#pyximport.install()
#from util import read_serial
#import smtplib
#import psutil as ps

Config.set('graphics', 'resizable', '1')
Config.write()
Window.size = (1296, 550)
Config.set('graphics', 'window_state', 'visible')
Config.write()
Config.set('graphics', 'center', '1')
Config.write()
midi_out = rtmidi.MidiOut(b'out')

#from controlknob import ControlKnob
#from controlspinner import ControlSpinner
from selected import Selected
from commons import BoxForGrid,LabelForGrid,ImageButton,PopupAlert
from popupaddchannel import PopupAddChannel

from kivy.lang.builder import Builder
Builder.load_file('kv/drumdiycontroller.kv')


class MainWindow(BoxLayout):
    ser = ObjectProperty()
    #channel_master = ObjectProperty()#ultimo canal clicado
    active = BooleanProperty()
    serial_ports = ListProperty()
    midi_ports = ListProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initCanvas() #cria e e instancia variaveis canvas que serão usadas posteriormente como retangulo de seleção por exemplo
        self.initVariables()     #cria e inicializa variaveis globais
        self.initSettings()   #preenche configurações e campos inicialmente, usa thread para acelerar a abertura do app
        self.initUI() # desenha todos os elementos da aplicação por meio de chamadas de metodos e instanciação de classes
    def initCanvas(self):
        with self.canvas:
            self.retangle_selection= Rectangle(size = (1,1),pos=(1,1))
            self.line_selection = Line(width=1,pos=(2,2))
            self.canvas_cc = Rectangle(size=(0,0),pos=(0,0))
            self.canvas_note = Rectangle(size=(0,0),pos=(0,0))
    def initVariables(self):
        self.selected_box = None #boxlayout que guarda os
        self.channel_master = None
        self.selected_image = ""
        self.active = False
        self.monitor = False
        self.monitor_cc = False
        self.list_channels = []
        self.auto_send = 0
        self.pieces = ["bumbo","caixa","chimbal","hhc","splash","crash","china","ride","bell","rotomtom","tom8","tom10","tom12","surdo16","block","hhc3"]
        self.vel = 0
        self.note = 0
        self.cmd = 0
        self.count_barHHC = 0
        self.ser = serial.Serial()
        self.selected = None
        self.dict_boxs = dict()
        self.active_auto  = False
        self.Q =  1
        self.touches = 0
    def initSettings(self):
        self.make_thread(self.load_serial_spinner())
        self.make_thread(self.load_midi_spinner())


    def initUI(self):
        self.set_grid_channels()
        if self.channel_master != None:
            self.selected=Selected(self.channel_master)
            self.ids.container_selected.add_widget(self.selected)

    def set_grid_channels(self):
        self.canvas.remove(self.line_selection)#limpa o clicado
        self.list_channels = Channel.select().order_by(Channel.id) #busca os channels
        self.ids.grid.clear_widgets()#limpa a grid
        for channel in self.list_channels:#itera nos canais
            self.insert_channel_in_grid(channel)

    def insert_channel_in_grid(self,channel):
        box = BoxForGrid(id=str(channel.id),orientation="vertical")

        label = LabelForGrid(text=channel.name,color=(1,1,1,1),size_hint=(1,None),size=(60,20), pos_hint={'center_x': .5, 'center_y': .5})
        box.add_widget(label)
        image = ImageButton(on_press=self.make_thread_click_image,id=str(channel.id),source=channel.image)
        box.add_widget(image)
        box_bottom = BoxLayout(orientation="horizontal",size_hint=(1,None),height=10)
        box_bottom.add_widget(Label())
        image_mute = ImageButton(id=str(channel.id),on_press=self.silent_channel,source="resources/icons/icons_no_silence.png" if channel.active else "resources/icons/icons_silence.png",size_hint=(.2,None),size=(20,20), pos_hint={'center_x': .9, 'center_y': 1})
        box_bottom.add_widget(image_mute)
        box.add_widget(box_bottom)
        self.ids.grid.add_widget(box)
        self.dict_boxs[channel.note] = box
        if channel.selected:
            self.channel_master = channel
            self.selected_box = box

    def silent_channel(self,image):
        print("mutou ",image.id)
        channel = Channel.get(Channel.id==int(image.id))
        channel.active = not channel.active
        channel.save()
        if self.ser.isOpen():
            if not channel.active:
                self.sendGain(channel.pin,0)
                if channel.note == 4:
                    self.sendThreshold(channel.pin,100)
                image.source = "resources/icons/icons_no_silence.png"
            else:
                self.sendGain(channel.pin,int(self.selected.dict_controls["Gain"].value))
                if channel.note == 4:
                    self.sendThreshold(channel.pin,self.selected.dict_controls["Threshold"].value)
                image.source = "resources/icons/icons_silence.png"


    def silent_all_channels(self):
        self.make_thread(self.thread_progress())
        list_channels = Channel.select().order_by(Channel.id)
        hhc = 0
        for channel in list_channels:
            if channel.note == 4: hhc = channel.pin
            channel.active = False
            channel.save()
        for i in range(16):
            if self.ser.isOpen():
                self.sendGain(i,0.0)
                if i == hhc:
                    self.sendThreshold(i,100.0)
                print("zerou")

        self.selected.set_values(self.channel_master)
        #self.selected = Selected(self.channel_master)
        #self.ids.container_selected.clear_widgets()
        #self.ids.container_selected.add_widget(self.selected)
    def make_thread_click_image(self,image):#thread pra ajudar no ganho de desempenho e velocidade do click
        print("Selecionou novo canal")
        self.make_thread(self.click_image_window(image))

    def click_image_window(self, image):
        self.remove_frame()
        self.insert_frame(image.parent)#aqui mudei, to passando o box pai da imagem pra selecionar a caixa toda
        self.set_new_selected(image)
        self.set_values_selected()
    def make_thread(self,function):
        t = Thread(target=function)
        t.start()

    def show_popup_add_channel(self):
        if self.line_selection: self.remove_frame() #apago logo a linha
        self.selected_image = "" #reseta estado da imagem pra não haver erros de regras de negocio
        popup = PopupAddChannel(self)#psso a grid como parametro pra poder preenchela com o elemento novo
        popup.open()


    def dialog_remove_channel(self):
        box = BoxLayout()
        from functools import partial
        popup = PopupAlert(title ="Deseja remover o canal "+self.channel_master.name+" ?" ,size_hint=(None,None),size=(300,100), content =box )
        btn_yes = Button(text="Sim",background_color=(.1,1,.1,1),size_hint=(.5,None),size=(100,30),on_press=partial(self.remove_channel_in_database,popup))
        btn_no = Button(text="Não",background_color=(1,.1,.1,1),size_hint=(.5,None),size=(100,30),on_press=popup.dismiss)
        box.add_widget(btn_yes)
        box.add_widget(btn_no)
        popup.open()

    def remove_channel_in_database(self,popup,btn):
        popup.dismiss()
        self.channel_master.delete_instance()
        if self.selected_box:
            self.ids.grid.remove_widget(self.selected_box)
        self.list_channels = Channel.select().order_by(Channel.id)
        if len(self.list_channels) > 0:
            self.channel_master = self.list_channels[len(self.list_channels)-1]
            self.channel_master.selected = True
            self.set_values_selected()
            self.remove_frame()
            #self.set_background_channel()
        else:
            self.set_grid_channels()


    def insert_frame(self,image):#coloca borda quando clica no canal
        with self.canvas:
            #Color(0.1,0.45,1,.7) azul
            Color(1, .45, .1, 1) #laranja
            self.line_selection = Line(width=2,rectangle = (image.x,image.y,image.width,image.height))

    def remove_frame(self):
        self.canvas.remove(self.line_selection)

    def set_new_selected(self,image):
        #mudo o status do antigo canal selecionado pra false
        self.channel_master.selected = False
        #busco o novo canal que foi clicado no banco e seto as coordenadas do frame
        new_channel = Channel.get(Channel.id==int(image.id))
        new_channel.selected = True
        new_channel.x = image.x
        new_channel.y = image.y
        new_channel.width = image.width
        new_channel.height = image.height
        self.channel_master = new_channel
        self.selected_box = image.parent


    def set_values_selected(self):
        #self.ids.container_selected.clear_widgets()
        #self.selected=Selected(self.channel_master)
        #self.ids.container_selected.add_widget(self.selected)
        self.selected.set_values(self.channel_master)


    def On(self,button):
        print("Ligado!")
        self.active = not self.active
        self.on_off_serial()


    def on_off_serial(self):
        if self.active:
            thread.start_new_thread(self.read_midi,())
            try:
                self.ser = serial.Serial(self.ids.spinner_serial.text, 115200, 8, "N", 2, timeout=None)
            except:
                popup = Popup(title="Ocorreu um erro ao ativar, verifique conexão com Arduino e porta serial selecionada",content=None,size_hint=(None,None),size=(600,80))
                popup.open()
                self.active =  False
                print("Abortou a ativação por erros")
        elif self.ser.isOpen():
            self.ser.close()
    """
    def initialize_channels_params(self):
        while not self.ser.isOpen():
            pass

        for channel in self.list_channels:
            if channel.active:
                self.sendGain(channel.pin,float(channel.gain))
            else:
                self.sendGain(channel.pin,0.0)"""

    def read_midi(self):

        self.enable_midi(self.ids.spinner_midi.text)
        #self.initialize_channels_params()
        #t = Thread(target=self.metter,args=())
        #t.start()
        while self.active:
            #self.cmd,self.note,self.vel = read_serial(self.ser)
            #midi_out.send_message([self.cmd, self.note, self.vel])
            if self.ser.isOpen():
                rxData = self.ser.read(1)
                if len(rxData) <= 0:
                    return
                cmd = rxData[0]
                rxData = self.ser.read(2)
                note = rxData[0]
                vel = rxData[1]

                midi_out.send_message([cmd, note, vel])  # Note on"""


                if self.monitor and note != 4:
                    thread.start_new_thread(self.metter,(vel,note))
                if self.monitor_cc and note == 4:
                    thread.start_new_thread(self.metter_cc,(vel,))
                if self.active_auto:
                    self.q_learning(note,vel)



    def q_learning(self,note,velocity):
        if self.selected.checked_control.id == "Gain":
            state = self.selected.dict_controls["Gain"].value
            self.executaAcao(state,velocity,"Gain",100,105)
            slinha = self.selected.dict_controls["Gain"].value
            self.Q = (1 + (slinha - state)*2)/3

        elif  self.selected.checked_control.id == "Threshold":

            if velocity >100:
                correction = velocity-30.0
            elif 70 > velocity < 100:
                correction = velocity-20.0
            elif 50 > velocity < 70:
                correction = velocity-10.0
            elif 25 > velocity < 50:
                correction = velocity-5.0
            else :
                correction = velocity-1.0
            if correction > 2:
                self.selected.dict_controls["Threshold"].value = int(correction)
                self.sendThreshold(self.channel_master.pin,int(correction))



    def executaAcao(self, state,velocity,control,min,max):
        if self.Q >= 0 and self.Q <=127:
            if velocity < min:
                self.selected.dict_controls[control].value = state+self.Q
                self.sendGain(self.channel_master.pin,state+self.Q)
            elif velocity >=max:
                self.selected.dict_controls[control].value = state-self.Q
                self.sendGain(self.channel_master.pin,state-self.Q)

    def metter_cc(self,vel):
        box = self.dict_boxs[4]
        try:
            box.canvas.remove(self.canvas_cc)
            with box.canvas:
                Color(1,.5,.1,.5)
                self.canvas_cc=Rectangle(size=(box.size[0],vel),pos=box.pos)
        except:
            pass
    def metter(self,vel,note):
        try:
            box = self.dict_boxs[note]
            with box.canvas:
                Color(1,.5,.1,.5)
            for i in range(vel,0,-10):
                with box.canvas:
                    instance=Rectangle(size=(box.size[0],i),pos=box.pos)
                time.sleep(.02)
                box.canvas.remove(instance)
        except:
            pass



    def enable_midi(self,port_midi):
        index = 0
        for port in midi_out.ports:
            if port_midi == str(port, "utf-8"):
                midi_out.close_port()
                midi_out.open_port(index)
            index = index + 1

    def next(self, dt):
        if self.count_barHHC >=450:
            self.count_barHHC = 0
            self.canvas.remove(self.progress_barHHC)
            print("Success")
            return False
        else:
            if self.count_barHHC !=0:
                self.canvas.remove(self.progress_barHHC)
            self.count_barHHC +=50
            with self.canvas:
                Color(1,.2,.2,1)
                self.progress_barHHC = Rectangle(size=(self.count_barHHC,20),pos=(730,50))

    def thread_progress(self):
        Clock.schedule_interval(self.next, 1/100)
    def sendToArduino(self,pin,note,retrigger,mask,scan,threshold,gain):
        self.sendMask(self.channel_master.pin,mask)
        self.sendScan(self.channel_master.pin,scan)
        self.sendThreshold(self.channel_master.pin,threshold)
        self.sendGain(self.channel_master.pin,gain)
        self.sendRetrigger(self.channel_master.pin,retrigger)
        self.sendNote(self.channel_master.pin,note)
        self.sendChannel(self.channel_master.pin,pin)#inconsistência verificar pin e channel
        self.sendXgroup(self.channel_master.pin,0)
        self.sendXtalk(self.channel_master.pin,0)
        self.sendCurveForm(self.channel_master.pin,100)
        self.sendCurve(self.channel_master.pin,0)
    def sendMask(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x03, int(value), 0xF7
        txMask = struct.pack("B"*len(data), *data)
        self.ser.write(txMask)
    def sendScan(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x02, int(value), 0xF7
        txScan = struct.pack("B"*len(data), *data)
        self.ser.write(txScan)

    def sendThreshold(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x01, int(
            value), 0xF7
        txThreshold = struct.pack("B"*len(data), *data)
        self.ser.write(txThreshold)

    def sendGain(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x09, int(value), 0xF7
        txGain = struct.pack("B"*len(data), *data)
        self.ser.write(txGain)

    def sendRetrigger(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x04, int(
            value), 0xF7
        txRetrigger = struct.pack("B"*len(data), *data)
        self.ser.write(txRetrigger)

    def sendNote(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x00, int(value), 0xF7
        txNote = struct.pack("B"*len(data), *data)
        self.ser.write(txNote)

    def sendChannel(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x0E, 0, 0xF7, int(
            value)
        txChannel = struct.pack("B"*len(data), *data)
        self.ser.write(txChannel)

    def sendXgroup(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x07, value, 0xF7
        txXgroup = struct.pack("B"*len(data), *data)
        self.ser.write(txXgroup)

    def sendXtalk(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x06, value, 0xF7
        txXtalk = struct.pack("B"*len(data), *data)
        self.ser.write(txXtalk)

    def sendCurveForm(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x08, value, 0xF7
        txCurveForm = struct.pack("B"*len(data), *data)
        self.ser.write(txCurveForm)

    def sendCurve(self, pinSend, value):
        data = 0xF0, 0x77, 0x04, pinSend, 0x05, value, 0xF7
        txCurve = struct.pack("B"*len(data), *data)
        self.ser.write(txCurve)
    def get_serial_ports(self):
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        if len(ports) == 0:
            ports.append("None")
        return ports

    def get_midi_ports(self):
        ports = []
        for port in midi_out.ports:
            ports.append(str(port, "utf-8"))
        if len(ports) == 0:
            ports.append("None")
        return ports

    def make_thread(self,function):
        t = Thread(target=function)
        t.start()
    def load_serial_spinner(self):
        self.serial_ports = self.get_serial_ports()
    def load_midi_spinner(self):
        self.midi_ports = self.get_midi_ports()


    def sendSketch(self):
        if self.ids.spinner_serial.text != "":
            try:
                subprocess.call('avrdude -q -V -p atmega2560 -C avrdude.conf -D -c wiring -b 115200 -P '+self.ids.spinner_serial.text+' -U flash:w:build-mega2560/sketch_microdrum.cpp.hex:i')
            except:
                popup = Popup(title='Erro', content=Label(text='Não conseguiu programar o Arduino'),
                          size_hint=(None, None), size=(400, 100))
                popup.open()
        else:
            popup = Popup(title='Nenhum Arduino conectado!', content=Label(text='Selecione a porta serial'),
                          size_hint=(None, None), size=(300, 100))
            popup.open()




class DrumDiyController(App):
    def build(self):
        return MainWindow()

    def on_stop(self):
        dict = self.get_running_app().root.selected.dict_controls
        self.save(dict)

    def save(self,dict):
        channel = self.get_running_app().root.channel_master
        channel.pin = int(dict["Pin"].text.split("A")[1])
        channel.note = int(dict["Note"].text.split(" ")[0])
        channel.retrigger = int(dict["Retrigger"].value)
        channel.mask = int(dict["Mask"].value)
        channel.scan = int(dict["Scan"].value)
        channel.threshold = int(dict["Threshold"].value)
        channel.gain = int(dict["Gain"].value)
        channel.save()


if __name__ == "__main__":
    DrumDiyController(title = "DrumDiy Controller 2").run()
