
# Copyright     2018 Karl Redmond
# Filename:     Project.py
# Author:       Karl Redmond
# Description:  Fourth Year Project
#               This project aims to implement a Home Security Solution which
#               monitors motion around a property, takes pictures on detection
#               of motion, stores the images and, notifies the users.
#               The users can then view the images and make decisions on what
#               to do next through a various number of functionalities, such
#               as providing a means to communicate verbally, turn on/off a
#               light in an effort to mimic movement in the house,
#               and finally to provide the ability to open a dog cage, thus
#               releasing any dogs contained with in. Obviously, if the user
#               doesnt have any dogs, the door release could be set up to open
#               the front door if it was found that the image shows a trusted
#               individual
# Brief:        This server is set up for a localhost environment,
#               mimicking the actual live server on Pythonanywhere,
#               this was done for demonstration purposes.

##=========== Dependencies ==============#
from flask import Flask, redirect, render_template, request, url_for, Response, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
#from flask_cors import CORS, cross_origin


##========== Database connection, on the live host, all attributes are different(Username, password etc.)========#

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="karlredmond",
    password="Password2",
    hostname="karlredmond.mysql.pythonanywhere-services.com",
    databasename="karlredmond$PiProject",
)

app = Flask(__name__)

#=========== Allow cross origin requests, as requests come from the Raspberry Pi to this server=======#
#CORS(app)

#========== Configuration ===========#
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
UPLOAD_FOLDER = '/home/karlredmond/mysite/static/MotionSensorImages'
VOICE_FOLDER = '/home/karlredmond/mysite/static/VoiceMessages'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VOICE_FOLDER'] = VOICE_FOLDER
ALLOWED_EXTENSIONS = set(['jpg', 'wav'])
SecuriPi = "http://149.153.104.171:9870" # This is for demo,live it uses DDNS,http://karlredmond.gotdns.com:8089 http://192.168.1.35:8089"
CloudServer = "https://karlredmond.pythonanywhere.com" #This is for demonstration, live is https://karlredmond.pythonanywhere.com "http://192.168.1.33:5000"
db = SQLAlchemy(app)

#========= Motion sensor Model ===============#
class Motion_Sensor_Image(db.Model):
    __tablename__ = "motion_sensor_images"
    id = db.Column(db.Integer, primary_key=True)
    pi_location = db.Column(db.String(4096))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    filename = db.Column(db.String(4096))

##=====================Check if File extension allowed=========================

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

##=====================Home route, returning home page and latest database entry==================================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Motion_Sensor_Image.query.order_by('-id').first())
    return redirect(url_for('index'))

##====================Motion Sensor endpoint, images taken on Raspberry Pi get sent here=======================

@app.route('/motion_detected', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'image' not in request.files:
            print("File not in request!!")
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            data = request.form
            filename = secure_filename(data['PiLocation'] + data['date'] + data['time'] + '.png')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = Motion_Sensor_Image(pi_location=data['PiLocation'], date = data['date'], time = data['time'], filename =  '/static/MotionSensorImages/' + filename)
            db.session.add(image)
            db.session.commit()
            return str(os.stat(app.config['UPLOAD_FOLDER'] + '/' + filename).st_size)
    return 404

#========Audio endpoint for forwarding HTTP to Pi, audio messages get sent here first, via HTTPS ===================

@app.route('/mic_test', methods=['GET', 'POST'])
def upload_mic_file():
    print("In request mic test")
    if request.method == 'POST':
        print("in POST")
        # check if the post request has the file part
        if 'file' not in request.files:
            print("File not in request!!")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return "No selected file"
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), 'rb') as f: r = requests.post(SecuriPi + "/mic_test", files={'file': f})
            return "OK"
    return "Fail"


##========================Audio endpoint for forwarding to Pi Pre Recorded===================

@app.route('/mic_test_pre', methods=['GET', 'POST'])
def upload_mic_file_pre():
    print("In request mic test")
    if request.method == 'POST':
        print("in POST")
        if request.get_data():
            print(request.get_data(as_text = True))
            filename = "" + request.get_data(as_text = True) + ".wav"
            with open(os.path.join(app.config['VOICE_FOLDER'], filename), 'rb') as f: r = requests.post(SecuriPi + "/mic_test", files={'file': f})
            return "OK"
    return "Fail"

##===============Return History of Images to Browser=================

@app.route("/history", methods=["GET", "POST"])
def history():
    if request.method == "GET":
        return render_template("history.html", comments=Motion_Sensor_Image.query.all())
    return redirect(url_for('history'))

##===============Retreive Latest Image and Jsonify response for AJAX=================

@app.route("/update_image", methods=["GET", "POST"])
def update_image():
    return_value = Motion_Sensor_Image.query.order_by('-id').first()
    return jsonify(test=return_value.filename, pi_location=return_value.pi_location, date=str(return_value.date), time=str(return_value.time))

##===============Arm/Disarm System, Enable/Disable Notifications=================

@app.route("/notifications", methods=["GET", "POST"])
def notifications():
    data={"data":{"data":request.get_data(as_text=True)}}
    r = requests.post(SecuriPi + "/notifications", json=data)
    return "OK"

@app.route("/arm_system", methods=["GET", "POST"])
def arm_system():
    data={"data":{"data":request.get_data(as_text=True)}}
    r = requests.post(SecuriPi + "/arm_system", json=data)
    return "OK"

##=============== Turn On/Off Light && Release Dogs =================

@app.route("/light", methods=["GET", "POST"])
def light():
    data={"data":{"data":request.get_data(as_text=True)}}
    r = requests.post(SecuriPi + "/light", json=data)
    return "OK"

@app.route("/release", methods=["GET", "POST"])
def release():
    data={"data":{"data":request.get_data(as_text=True)}}
    r = requests.post(SecuriPi + "/release", json=data)
    return "OK"

##=============== System Status Endpoint, returning current state of system =================

@app.route("/getState", methods=["GET", "POST"])
def getState():
    r = requests.post(SecuriPi + "/getState")
    return jsonify(r.content.decode('utf-8'))


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=9870)
            # This was used fo HTTPS in local Environment
            # ssl_context=('/Users/BeckiKarl/server.crt', '/Users/BeckiKarl/server.key'))

