
from kivy.graphics.texture import Texture
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class ImageButton(ButtonBehavior, Image):
    pass
class PopupAlert(Popup):
    def __init__(self,**kwargs):
        super(PopupAlert,self).__init__(**kwargs)

class BoxForGrid(BoxLayout):
    def __init__(self,**kwargs):
        super(BoxForGrid,self).__init__(**kwargs)

class LabelForGrid(Label):
    def __init__(self,**kwargs):
        super(LabelForGrid,self).__init__(**kwargs)



def getTexture2(self,color1,color2,orientation):
    if orientation == "v":
        self.texture = Texture.create(size=(1,2), colorfmt='rgba')#matris 2 quadrantes
    elif  orientation == "h":
        self.texture = Texture.create(size=(2,1), colorfmt='rgba')#matris 2 quadrantes
    p = color1 + color2# + p3_color + p4_color
    buf = bytes(p)
    self.texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
    return self.texture

def getTexture3(color1,color2,color3,orientation):
    if orientation == "v":
        texture = Texture.create(size=(1,3), colorfmt='rgba')#matris 2 quadrantes
    elif  orientation == "h":
        texture = Texture.create(size=(3,1), colorfmt='rgba')#matris 2 quadrantes
    p = color1 + color2 + color3 #+ p4_color
    buf = bytes(p)
    texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
    return texture

def update_rect(self, *args):
    self.rect.size = self.size
    self.rect.pos = self.pos
