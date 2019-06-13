#Boxlayout responsável por conter label de propriedade, label de valor e knob para controle de parâmetros
#sua função principal será setar variaveis na mainwindow de propriedades de configuração além de setar diretamente
#os valores individuais no arduino e no banco
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from myknob import MyKnob
from kivy.lang.builder import Builder
Builder.load_file('kv/controlknob.kv')

class ControlKnob(BoxLayout):
    def __init__(self,**kwargs):
        super(ControlKnob,self).__init__(**kwargs)

class Teste(App):
    def build(self):
        return ControlKnob()


if __name__ == "__main__":
    Teste(title = "ControlKnob class").run()
