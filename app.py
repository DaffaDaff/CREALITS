import kivy

scale = 1
width = 480 *scale
height = 320 *scale

from kivy.config import Config
Config.set('graphics', 'width', f'{width}')
Config.set('graphics', 'height', f'{height}')
Config.set('graphics', 'resizable', False) 
Config.set('graphics', 'fullscreen', 0)

from kivy.core.text import LabelBase
LabelBase.register(name='Inter', 
                   fn_regular='asset/font/Inter-Regular.ttf')
LabelBase.register(name='Inter-Bold', 
                   fn_regular='asset/font/Inter-Bold.ttf')
LabelBase.register(name='Inter-SemiBold', 
                   fn_regular='asset/font/Inter-SemiBold.ttf')
LabelBase.register(name='Inter-Medium', 
                   fn_regular='asset/font/Inter-Medium.ttf')

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty

class WindowManager(ScreenManager):
    pass

class StartScreen(Screen):
    pass

class LoginScreen(Screen):
    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        app.config.read(app.get_application_config('user.ini'))

        usr = app.config.getdefault(app.username, 'Username', ' ')
        pas = app.config.getdefault(app.username, 'Password', ' ')

        if (usr == app.username and pas == app.password):
            self.manager.current = 'homeScreen'

        app.config.write()
    

class SignupScreen(Screen):
    def do_signup(self, signupText, passwordText):
        app = App.get_running_app()

        app.username = signupText
        app.password = passwordText

        app.config.read(app.get_application_config('user.ini'))

        if(not app.config.has_section(app.username)):
            self.manager.current = 'genderScreen'


        app.config.write()

class GenderScreen(Screen):
    def do_select(self, genderText):
        app = App.get_running_app()
        
        app.config.adddefaultsection(app.username)
        app.config.set(app.username, 'Username', app.username)
        app.config.set(app.username, 'Password', app.password)
        app.config.set(app.username, 'Gender', genderText)
        
        app.config.write()

        self.manager.current = 'homeScreen'

class HomeScreen(Screen):
    username = StringProperty(None)

    def on_enter(self):
        app = App.get_running_app()
        self.username = f'Welcome, {app.username}'

from kivy.lang import Builder
kv = Builder.load_file('app.kv')

from kivy.app import App

class CrealitsApp(App):
    username = StringProperty(None)
    password = StringProperty(None)

    def build(self):
        return kv

CrealitsApp().run()