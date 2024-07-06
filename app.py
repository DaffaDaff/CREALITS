import kivy
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivy.graphics.texture import Texture
from kivy.uix.vkeyboard import VKeyboard
import numpy as np
import cv2
from picamera2 import Picamera2
import csv
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from kivy.garden.graph import Graph, MeshLinePlot

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

        size = 34
        centers = [[226,276], [327, 227], [123,224], [341, 122], [128, 113], [244, 58]]

        for center in centers:
            cv2.circle(frame, center, size, (0, 0, 255), 2)

        # DISPLAY
        buf = frame.tostring()
        image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte') 
        
        self.img.texture = image_texture

    def capture(self):
        app = App.get_running_app()
        frame = self.camera.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (width, height))

        app.RGBs = []
        size = 34
        # [bottom middle], [bottom right], [bottom left], [top right], [top left], [top middle]
        centroid = [[226,276], [327, 227], [123,224], [341, 122], [128, 113], [244, 58]]

        for center in centroid:
            cv2.circle(frame, center, size, (0, 0, 255), 2)

            start_x = max(center[0] - size // 2, 0)
            start_y = max(center[1] - size // 2, 0)
            end_x = min(center[0] + size // 2, frame.shape[1])
            end_y = min(center[1] + size // 2, frame.shape[0])

            cropped = frame[start_y:end_y, start_x:end_x]

            mean_color = cv2.mean(cropped)[:3]
            app.RGBs.append(mean_color)

        self.manager.current = 'previewScreen'

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
        app = App.get_running_app()
        with open('CREALITS_train.csv', mode='a') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

            row = [item for col in app.RGBs for item in col]
            row.append(app.age)
            row.append(app.weight)
            writer.writerow(row)
            csv_file.close()
        
        with open('CREALITS_train.csv', mode='r') as csv_file:
            reader = list(csv.reader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL))

            data = np.zeros((len(reader), 6, 3))
            album = np.zeros((len(reader)))
            creat = np.zeros((len(reader)))

            for row in range(len(reader)):
                for i in range(0, 18):
                    data[row, int(i/3), int(i%3)] = reader[row][i]
                
                album[row] = reader[row][18]
                creat[row] = reader[row][19]
            
            converted_data = np.zeros((len(reader), 2, 3))

            for i in range(len(reader)):
                converted_data[i, 0, 0] = (data[i, 0, 0] + data[i, 1, 0] + data[i, 2, 0]) / 3 
                converted_data[i, 0, 1] = (data[i, 0, 1] + data[i, 1, 1] + data[i, 2, 1]) / 3 
                converted_data[i, 0, 2] = (data[i, 0, 2] + data[i, 1, 2] + data[i, 2, 2]) / 3 
                converted_data[i, 1, 0] = (data[i, 3, 0] + data[i, 4, 0] + data[i, 5, 0]) / 3 
                converted_data[i, 1, 1] = (data[i, 3, 1] + data[i, 4, 1] + data[i, 5, 1]) / 3 
                converted_data[i, 1, 2] = (data[i, 3, 2] + data[i, 4, 2] + data[i, 5, 2]) / 3 

            csv_file.close()
            
        app.model = [LinearRegression(), LinearRegression(), LinearRegression(), LinearRegression(), LinearRegression(), LinearRegression()]
        app.pred = []
        app.test = []

        

        for i in range(2):
            X = data[:, i, :]

            if i == 0:
                if album == 0:
                    continue
                y = album
            else:
                if creat == 0:
                    continue
                y = creat

            # Split data into training and test sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Create and train the model
            app.model[i] = LinearRegression()
            app.model[i].fit(X_train, y_train)

            # # Make predictions
            y_pred = app.model[i].predict(X_test)

            # # Evaluate the model
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            predicted_values = y_pred

            # Create a graph widget
            app.graph_widget = Graph(
                xlabel='Predicted Values', ylabel='R/G/B', x_ticks_minor=1,
                x_ticks_major=1, y_ticks_major=1,
                y_grid_label=True, x_grid_label=True, padding=5,
                xlog=False, ylog=False, x_grid=True, y_grid=True, xmin=0, xmax=10, ymin=0, ymax=255
            )
            # Create a plot
            plot = MeshLinePlot(color=[1, 0, 0, 1])
            plot.points = list(zip(predicted_values, X_test[:][0]))
            plot = MeshLinePlot(color=[0, 1, 0, 1])
            plot.points = list(zip(predicted_values, X_test[:][1]))
            plot = MeshLinePlot(color=[0, 0, 1, 1])
            plot.points = list(zip(predicted_values, X_test[:][2]))
            app.graph_widget.add_plot(plot)

        self.manager.current = "calibrationScreen"




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

class PreviewScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()

        for i in range(6):
            self.ids[f'rgb{i}'].text = str(app.RGBs[i])

class CalibrationScreen(Screen):
    def on_enter(self, *args):
        app = App.get_running_app()

        self.ids['layout'].add_widget(app.graph_widget)

        return super().on_enter(*args)

from kivy.lang import Builder
kv = Builder.load_file('app.kv')

from kivy.app import App

class CrealitsApp(App):
    username = StringProperty(None)
    password = StringProperty(None)
    age = NumericProperty(0)
    weight = NumericProperty(0)
    img = np.zeros(2)
    RGBs = [[255,0,0], [0,255,0], [0,0,255], [0,255,255], [255,0,255], [255,255,0]]

    def build(self):
        return kv

if __name__ == "__main__":
    CrealitsApp().run()
