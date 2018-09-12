from flask import Flask, render_template, request, session
import random
from datetime import datetime
from collections import Counter


app = Flask(__name__)

@app.route('/')
@app.route('/game')
def game() -> 'html':
    session['startTime'] = datetime.now()
    return render_template('game.html', title = 'Home Security')

@app.route('/motion_detected')
def motionDetected():
    print("Sucess!!")
    return render_template('result.html', title="Motion Detected")

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0', debug=True)
    
