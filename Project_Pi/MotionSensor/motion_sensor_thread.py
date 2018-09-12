#    Copyright 2018 Karl Redmond
#    Filename: motion_sensor_thread.py
#    Author:   Karl Redmond
#    Date:     18/04/2018
#    Brief:    This is the thread file which controls
#              the motion sensor and image capture through the camera

###### Dependencies
import my_twilio
import RPi.GPIO as GPIO
import picamera
import requests
import os
import time
from datetime import datetime, timedelta

###### Set the state to armed on startup with notifications enabled
armed = False
notifications = False

###### Initialize camera
camera = picamera.PiCamera()
GPIO.setwarnings(False)

##### The GPIO pins can be set to BOARD, or BCM. The basic difference is
##### that BOARD uses the location of the pins, whereas BCM has specific
##### name for each pin, which can get confusing, however diagrams are available
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)    ## Set Pin to read output from PIR motion sensor

## Thread for handling motion sensor events, SMS message and Post to pythonanywhere
def thread_for_motion_sensor():
    period = timedelta(minutes=1)
    next_time = datetime.now()
    while True:
        if armed: ##is the system fully armed  
            i = GPIO.input(11)     ## When output from motion sensor is LOW
            if i == 0:
                print("No intruders" , i, armed)
                time.sleep(0.1)
            elif i == 1:           ## When output from motion sensor is HIGH
                print("Intruder Detected" , i)
                #### In a live environment, the image gets sent to cloud storage,
                #### however for demonstration it is configured in a local environment
                #url = "https://karlredmond.pythonanywhere.com/motion_detected"
                url = "http://192.168.1.33:5000/motion_detected"
                loop_value = True
                camera.capture("image.jpg")
                data = { 'PiLocation' : "Unum Lab",'date' : datetime.now().strftime('%Y-%m-%d'), 'time': datetime.now().strftime('%H:%M:%S')}
                while loop_value: ## Keep trying request until server response with correct image size
                    file = open('/home/pi/Desktop/Project/MotionSensor/image.jpg', 'rb')
                    if str(requests.post(url, files={'image' : file}, data = data).text) == str(os.stat('/home/pi/Desktop/Project/MotionSensor/image.jpg').st_size):
                        print('Same Size')
                        loop_value = False
                        file.close()
                if next_time <= datetime.now() and notifications: ##are notifications enabled, and has it been longer than "5 minutes"
                    next_time = datetime.now()+period
                    # wont work on local host environment as it need connection to the internet
                    #message = my_twilio.client.messages.create(body="Motion has been detected in the Unum Lab. Have a look at whats going on here: https://karlredmond.pythonanywhere.com", to="+353834409854", from_="+353861802301")
                    print("Send Message")# wont work on local host environment(message.sid)
                time.sleep(1)