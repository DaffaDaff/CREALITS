import kivy

scale = 1
width = 480 *scale
height = 320 *scale

from kivy.config import Config
Config.set('graphics', 'width', f'{width}')
Config.set('graphics', 'height', f'{height}')
Config.set('graphics', 'resizable', False) 
Config.set('graphics', 'fullscreen', 1)

from kivy.core.text import LabelBase
LabelBase.register(name='Sugo-Pro', 
                   fn_regular='asset/font/Sugo-Pro-Display-Regular-trial.ttf')

from kivy.uix.screenmanager import Screen, ScreenManager

class WindowManager(ScreenManager):
    pass

class StartScreen(Screen):
    pass

class LoginScreen(Screen):
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        self.manager.current = 'startScreen'

        app.config.read(app.get_application_config())
        app.config.write()

from kivy.lang import Builder
kv = Builder.load_file('app.kv')

from kivy.app import App

class CrealitsApp(App):
    def build(self):
        return kv

CrealitsApp().run()