import kivy

scale = 1
width = 480 *scale
height = 320 *scale

from kivy.config import Config
Config.set('graphics', 'width', f'{width}')
Config.set('graphics', 'height', f'{height}')
Config.set('graphics', 'resizable', False) 

from kivy.core.text import LabelBase
LabelBase.register(name='Sugo-Pro', 
                   fn_regular='asset/font/Sugo-Pro-Display-Regular-trial.ttf')

from kivy.uix.screenmanager import Screen, ScreenManager

class WindowManager(ScreenManager):
    pass

class StartScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

from kivy.lang import Builder
kv = Builder.load_file('builder/main.kv')

from kivy.app import App

class CrealitsApp(App):
    def build(self):
        return kv

CrealitsApp().run()