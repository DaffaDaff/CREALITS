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
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rotate
from kivy.graphics.texture import Texture
import numpy as np
import cv2

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
        self.ids['status'].text = ''

        if (usr == app.username and pas == app.password):
            self.manager.current = 'homeScreen'
        else:
            self.ids['status'].text = 'Username or Password Incorrect'

        app.config.write()
    

class SignupScreen(Screen):
    def do_signup(self, signupText, passwordText):
        app = App.get_running_app()

        app.username = signupText
        app.password = passwordText

        app.config.read(app.get_application_config('user.ini'))

        self.ids['status'].text = ''

        if(not app.config.has_section(app.username)):
            self.manager.current = 'genderScreen'
        else:
            self.ids['status'].text = 'Username Already Taken'


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

    def on_pre_enter(self):
        app = App.get_running_app()
        self.username = f'Welcome, {app.username}'

class AgeScreen(Screen):
    def start(self, age, weight):
        app = App.get_running_app()

        app.age = age
        app.weight = weight

        self.manager.current = 'cameraScreen'

class CameraScreen(Screen):
    img = Image()

    def on_pre_enter(self):
        self.cap = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        ret, frame = self.cap.read()
        if ret:
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            
            self.img.texture = image_texture

    def capture(self):
        ret, frame = self.cap.read()
        if ret:
            App.get_running_app().img = frame
            self.manager.current = 'loadingScreen'

class SpinningLoader(Widget):
    def __init__(self, start, end, col, **kwargs):
        super().__init__(**kwargs)
        self.angle_start = start
        self.angle_end = end
        with self.canvas:
            self.color = Color(col[0], col[1], col[2], col[3])
            self.line = Line(circle=(self.center_x, self.height, 20, self.angle_start, self.angle_end), width=3)

        Clock.schedule_interval(self.update, 1 / 60.)

    def update(self, dt):
        self.angle_start += 6 % 360
        self.angle_end += 6 % 360
        self.line.circle = (self.center_x, self.height, 30, self.angle_start, self.angle_end)

class LoadingScreen(Screen):
    def on_pre_enter(self):
        self.layout = self.ids['layout']
        self.layout.add_widget(SpinningLoader(0, 10, (0.6, 0.6, 0.6, 1)))
        self.layout.add_widget(SpinningLoader(72, 82, (0.6, 0.6, 0.6, 1)))
        self.layout.add_widget(SpinningLoader(144, 154, (0.6, 0.6, 0.6, 1)))
        self.layout.add_widget(SpinningLoader(216, 226, (0.6, 0.6, 0.6, 1)))
        self.layout.add_widget(SpinningLoader(288, 298, (0.6, 0.6, 0.6, 1)))

    def on_enter(self):
        pass

from kivy.lang import Builder
kv = Builder.load_file('app.kv')

from kivy.app import App

class CrealitsApp(App):
    username = StringProperty(None)
    password = StringProperty(None)
    age = NumericProperty(0)
    weight = NumericProperty(0)
    img = np.zeros(2)

    def build(self):
        return kv

CrealitsApp().run()