#    Copyright 2018 Karl Redmond
#    Filename: pirtest.py
#    Author:   Karl Redmond
#    Date:     18/04/2018
#    Brief:    This is the Server File(Flask) which runs on the Raspberry Pi
#              The purpose of this server is to detect motion using a motion sensor attached
#              This server also catches requests sent by the user to control appliances on the
#              permises, as well asplaying verbal voice files sent by the user of Home SecuriPi

######## Dependencies############
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from threading import Thread
import RPi.GPIO as GPIO
import pygame
import motion_sensor_thread
import os
import json

######## Set General Purpose Output Pins to the desired state##########

GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, GPIO.HIGH)

######## Configure Upload file directory for images taken by the camera######
UPLOAD_FOLDER = 'static/MotionSensorImages'

######## Only allow jpg and wav files to be received from requests ###### 
ALLOWED_EXTENSIONS = set(['jpg', 'wav'])

app = Flask(__name__)
CORS(app) ##needed to allow pythonanywhere to communicate with this server

#### set the thread target, this thread was necessary to allow the server to
#### accept requests while the motion sensor is still running
thread = Thread(target = motion_sensor_thread.thread_for_motion_sensor)

### Start the motion sensor thread #########
thread.start()

##### This function checks the extions of file with reference to ALLOWED_EXTENSIONS
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

##### This endpoint recevies unique wav files recorded by the user
##### and plays them through the audio jack of the PI
@app.route('/mic_test', methods=['GET', 'POST'])
def mic_test():
    print('Somewhere')
    if request.method == 'POST':
        if 'file' not in request.files:
            print("File Not in Request")
            return "Woopsie, no file found"
        file = request.files['file']
        if file.filename == '':
            print("No Selected File")
            return "Woopsie, no selected file"
        if file and allowed_file(file.filename):
            print("where we want to be")
            data = request.form
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            print(str(os.stat))
            pygame.mixer.init()
            pygame.mixer.music.load(app.config['UPLOAD_FOLDER'] + "/"+ file.filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
    return 'Error In Playing Sound File'

##### This method allows the user to disarm the System,
##### meaning the System will no longer take pictures
##### if in a disarmed state. The user can also re-arm the system
@app.route('/arm_system', methods=['GET', 'POST'])
def arm_system():
    j=json.loads(request.get_data(as_text=True))
    if  j['data']['data'] == 'true':
        motion_sensor_thread.armed = True
        print("System Armed")
    else:
        motion_sensor_thread.armed = False
        print("System Disarmed")
    return "OK"
    ##### This code was for testing in a local environment
    #if(request.get_data(as_text=True) == "true"):
     #   motion_sensor_thread.armed = True
      #  print("System Armed")
    #else:
     #   motion_sensor_thread.armed = False
      #  print("System Disarmed")
    #return "OK"
    
##### This method allows the user to enable/disable notificaitons,
##### In a disabled state, the system will keep taking pictures
##### but will not send notifications
@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    j=json.loads(request.get_data(as_text=True))
    if  j['data']['data'] == 'true':
        motion_sensor_thread.notifications = True
        print("enabled notifications")
    else:
        motion_sensor_thread.notifications = False
        print("disabled notifications")
    return "OK"

##### This method allows the user to turn On/Off a Light,
##### by setting the output of the relative pin to a HIGH/LOW state
@app.route('/light', methods=['GET', 'POST'])
def light():
    j=json.loads(request.get_data(as_text=True))
    if  j['data']['data'] == 'true':
        GPIO.output(13, GPIO.LOW)
        print("LIGHT OFF")
    else:
        GPIO.output(13, GPIO.HIGH)
        print("LIGHT ON")
    return "OK"

#### This method allows a user to open/close a solenoid door lock
#### By sending a HIGH or LOW signal to a relay, the solenoid circuit
#### is completed or broken
@app.route('/release', methods=['GET', 'POST'])
def release():
    pygame.mixer.init()
    pygame.mixer.music.load(app.config['UPLOAD_FOLDER'] + "/dogBarking.wav")
    j=json.loads(request.get_data(as_text=True))
    if  j['data']['data'] == 'true':
        GPIO.output(15, GPIO.HIGH)
        print("DOGDOOR LOCKED")
    else:
        GPIO.output(15, GPIO.LOW)
        print("DOGS RELEASED")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
    return "OK"
    
#### This method returns the state of the "System", "Notifications",
#### "Dogs" and "Light". This is utilized through ajax calls made to this
#### function, which the browser uses to ensure the user always knows what
#### state the system is currently in, as there may be more than one user at the same time.
@app.route('/getState', methods=['GET', 'POST'])
def getState():
    return jsonify(armed=motion_sensor_thread.armed, notifications=motion_sensor_thread.notifications, light=GPIO.input(13), dogs=GPIO.input(15))


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(host = '0.0.0.0', port = 8089)
    thread.join()
    
