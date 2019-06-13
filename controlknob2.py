from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from myknob import MyKnob
from kivy.lang.builder import Builder
Builder.load_file('kv/controlknob2.kv')

class ControlKnob2(BoxLayout):
    def __init__(self,**kwargs):
        super(ControlKnob2,self).__init__(**kwargs)

class Teste(App):
    def build(self):
        return ControlKnob()


if __name__ == "__main__":
    Teste(title = "ControlKnob class").run()
