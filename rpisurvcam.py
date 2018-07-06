#!/usr/bin/python3

from gpiozero import MotionSensor
from picamera import PiCamera
import time
import os
import subprocess

#check for internet access
import urllib3

import logging
logging.basicConfig(filename='./rpicam.log', level=logging.DEBUG)

#for email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#configs file
from myconfig import *

#set pin number for motion sensor
sensor_pin = MotionSensor(4)
camera = PiCamera()
#set timezone
os.environ['TZ'] = 'Europe/Vilnius'


def main():
    while True:
        sensor_pin.wait_for_motion()
        if sensor_pin.motion_detected:
            send_sms()
            send_pics()
            time.sleep(5)
            clear_img_dir()
        sensor_pin.wait_for_no_motion()

def send_pics():
    if not internet_on():
        logging.info(time.strftime('%H:%M:%S'))
        return
    for i in range(3):
        camera.capture('/home/pi/images/image_{}.jpeg'.format(time.strftime('%H:%M:%S')))
        time.sleep(2)

    msg = MIMEMultipart()

    #from_email, to_email, email_msg from myconfig.py file
    msg['From'] = from_email
    msg['To'] = to_email
    body = email_msg

    msg.attach(MIMEText(body, 'plain'))

    for filename in os.listdir('/home/pi/images/'):
        attachment = open('/home/pi/images/{}'.format(filename), 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_email_pass)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def clear_img_dir():
    for filename in os.listdir('/home/pi/images'):
        os.rename('/home/pi/images/{}'.format(filename), '/home/pi/sentimages/{}'.format(filename))

def send_sms():
    subprocess.call(['/usr/bin/python3', '/home/pi/scripts/sms/sms.py'])

def internet_on():
    try:
        http = urllib3.PoolManager()
        response = http.request('GET', 'www.netbsd.org')
        if response.status == 200:
            return True
        else:
            return False
    except:
        return False


if __name__ == '__main__':
    main()
