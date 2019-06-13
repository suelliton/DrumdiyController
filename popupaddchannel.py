from kivy.uix.popup import Popup
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from commons import ImageButton,PopupAlert
from kivy.graphics import Color,Line
from model import Channel
import peewee
Builder.load_file('kv/popupaddchannel.kv')



class PopupAddChannel(Popup):
    def __init__(self,gridchannels, **kwargs):
        super(PopupAddChannel,self).__init__(**kwargs)
        self.pieces = ["bumbo","caixa","chimbal","hhc","splash","crash","china","ride","bell","rotomtom","tom8","tom10","tom12","surdo16","block","hhc3"]
        with self.canvas:
            Color(0.1,0.45,1)
            self.line_selection = Line(width=3,rectangle = (0,0,0,0))
        self.selected_canvas = self.canvas #usado para guardar o canvas do ultimo elemento clicado para apaalo se precisar
        self.selected_image = ""
        self.gridchannels = gridchannels
        for piece in self.pieces:
            box = BoxLayout()
            image = ImageButton(on_press=self.click_image_popup,id=piece,source="resources/images/PNG/"+piece+".png")
            box.add_widget(image)
            self.ids.grid_images_add_channel.add_widget(box)

    def click_image_popup(self, image):
        self.selected_canvas.remove(self.line_selection)#remove o anterior selecionado
        self.selected_canvas = image.canvas#guarda o canvas do atual
        self.selected_image = image.id
        print("imagem selecionada",self.selected_image)
        with image.canvas:#seleciona o novo
            self.line_selection = Line(width=3,rectangle = (image.x,image.y,image.width,image.height))


    def validate_and_save_channel(self):
        name = self.ids.name_new_channel.text
        type = 0
        if self.ids.type_new_channel.text == "Piezo":
            type = 0
        elif self.ids.type_new_channel.text == "HHC":
            type = 2
        else:
            type = 1
        alert = PopupAlert(title="Warning!",size_hint=(None,None),size=(200,100))
        if name == "" :
            alert.add_widget(Label(text="Please add a channel name"))
            alert.open()
        elif self.selected_image == "":
            alert.add_widget(Label(text="Please select a channel icon"))
            alert.open()
        else:
            self.save_channel_in_database(name,type,self.selected_image)

    def save_channel_in_database(self,name,type,selected_image):
        mainwindow = App.get_running_app().root

        #try:
        if Channel.select().count() > 0:
            selected_channel = Channel.get(Channel.selected==True)
            if selected_channel:
                selected_channel.selected = False
                print("tinha um canal selecionado anteriormente")

        self.gridchannels.channel_master = Channel.create(name = name, type = type ,pin = 1, note = 38, threshold = 10, scan = 20, mask = 20,
        retrigger = 7, gain = 15, curve = 0,curveform = 100, xtalk = 0,xtalkgroup = 0,
        image = "resources/images/PNG/"+selected_image+".png",x= 0.0,y= 0.0,width= 0.0,height= 0.0,selected= True,active=True)

        self.dismiss()
        self.gridchannels.list_channels = Channel.select().order_by(Channel.id)
        #adiciona canal no grid
        self.gridchannels.insert_channel_in_grid(self.gridchannels.channel_master)
        self.gridchannels.set_values_selected()



class Teste(App):
    def build(self):
        return PopupAddChannel()


if __name__ == "__main__":
    Teste(title = "PopupAddChannel class").run()
