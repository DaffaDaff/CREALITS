import kivy
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivy.graphics.texture import Texture
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.vkeyboard import VKeyboard
import numpy as np
import cv2
from picamera2 import Picamera2
import os.path

scale = 1
width = 480 *scale
height = 320 *scale

from kivy.config import Config
import configparser

conf = configparser.ConfigParser()
conf.read('crealits.ini')

Config.set('graphics', 'width', f'{width}')
Config.set('graphics', 'height', f'{height}')
Config.set('graphics', 'resizable', False) 
Config.set('graphics', 'fullscreen', conf['Default']['Fullscreen'])

from kivy.core.text import LabelBase
LabelBase.register(name='Inter', 
                   fn_regular='asset/font/Inter-Regular.ttf')
LabelBase.register(name='Inter-Bold', 
                   fn_regular='asset/font/Inter-Bold.ttf')
LabelBase.register(name='Inter-SemiBold', 
                   fn_regular='asset/font/Inter-SemiBold.ttf')
LabelBase.register(name='Inter-Medium', 
                   fn_regular='asset/font/Inter-Medium.ttf')

class WindowManager(ScreenManager):
    pass

class StartScreen(Screen):
    pass

class LoginScreen(Screen):
    def on_enter(self, *args):
        self.keyboard = Keyboard()
        return super().on_enter(*args)
    
    def on_focus(self, instance, value, is_numeric=False):
        if value:
            self.add_widget(self.keyboard)
            self.keyboard.keyboard.setup_mode_dock()
            self.keyboard.input = instance
        else:
            self.remove_widget(self.keyboard)

    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        if loginText == "xxx":
            app.stop()

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
    def on_enter(self, *args):
        self.keyboard = Keyboard()
        return super().on_enter(*args)
    
    def on_focus(self, instance, value, is_numeric=False):
        if value:
            self.add_widget(self.keyboard)
            self.keyboard.keyboard.setup_mode_dock()
            self.keyboard.input = instance
        else:
            self.remove_widget(self.keyboard)
    def do_signup(self, signupText, passwordText):
        app = App.get_running_app()



        app.username = signupText
        app.password = passwordText

        app.config.read(app.get_application_config('user.ini'))

        self.ids['status'].text = ''

        if signupText == "xxx":
            self.ids['status'].text = 'Username Already Taken'

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
    def on_enter(self, *args):
        self.keyboard = Keyboard()
        return super().on_enter(*args)
    
    def on_focus(self, instance, value, is_numeric=False):
        if value:
            self.add_widget(self.keyboard)
            self.keyboard.keyboard.setup_mode_dock()
            self.keyboard.input = instance
            self.keyboard.is_numeric = is_numeric
        else:
            self.remove_widget(self.keyboard)

    def start(self, age, weight):
        app = App.get_running_app()

        if age :
            app.age = age
        if weight:
            app.weight = weight

        self.manager.current = 'cameraScreen'

class CameraScreen(Screen):
    img = Image()

    def on_pre_enter(self):
        resolution = (3280, 2464)
        roi = (0, 0, 3280, 2464)
        #self.cap = cv2.VideoCapture(0)
        self.camera = Picamera2()
        config = self.camera.create_still_configuration(buffer_count=4, main={"size": resolution}, lores={"size": resolution}, display="lores", controls={"ScalerCrop": roi})
        self.camera.configure(config)
        self.camera.start()

        #self.camera.set_controls({"AfMode": 1 ,"AfTrigger": 0})

        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        # CAPTURE
        frame = self.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (width, height))

        # CONTOUR
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        i = 0
        for contour in contours:
            if len(contour) > 0:
                i+=1
                if(i==8):
                    continue
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(frame, center, radius, (0, 255, 0), 2)

        # DISPLAY
        buf = frame.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        
        self.img.texture = image_texture

    def capture(self):
        frame = self.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (width, height))
        
        i = 0
        while os.path.isfile(f'/home/pi/CREALITS/train_data/{i}.jpeg'):
              i+=1
        cv2.imwrite(f'/home/pi/CREALITS/train_data/{i}.jpeg', frame)
        #self.manager.current = 'loadingScreen'

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

class Keyboard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.input = None
        self.is_numeric = False

        self.keyboard = VKeyboard(on_key_up = self.key_up)

        self.add_widget(self.keyboard)
        

    def key_up(self, keyboard, keycode, *args):
        if not self.input:
            return

        if isinstance(keycode, tuple):
            keycode = keycode[1]
        
        if keycode == 'backspace':
            self.input.text = self.input.text[:-1]
        elif keycode == 'spacebar':
            self.input.text = f'{self.input.text} '
        elif len(keycode) == 1:
            if self.is_numeric and not keycode.isnumeric():
                return
            self.input.text = f'{self.input.text}{keycode}'

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

if __name__ == "__main__":
    CrealitsApp().run()
