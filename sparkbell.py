#!/usr/bin/env python
 
import os
import RPi.GPIO as GPIO
import picamera
from time import sleep
from picamera import PiCamera 
from requests_toolbelt import MultipartEncoder
import requests
import datetime as dt
import config

#GPIO Basics
print 'Checking GPIO status of pin 23, a value of 1 is good'
#GPIO.cleanup() 
GPIO.setmode(GPIO.BCM)
# GPIO 23 set up as input. It is pulled up to stop false signals  
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(4, GPIO.OUT)

#GPIO.input(23)
print GPIO.input(23)

#take a picture
def camera():

	print 'Taking a picture of who rang the doorbell'
	camera = PiCamera()
	camera.resolution = (800, 600)
	camera.hflip = True
	camera.vflip = True
	camera.annotate_background = picamera.Color('black')
	timedate = dt.datetime.now().strftime('%H:%M:%S %d-%m-%Y')
	camera.annotate_text = 'Front Door @ ' + timedate
	camera.capture('camera.png', format='png')
	print 'Sending a preview to the local monitor'
	camera.close()
	print 'Camera function complete'

#Detect Button push using debounce protection of RPi.GPIO
def buttonPress():
	print 'Waiting for you to push the doorbell'
	button = GPIO.input(23)
	while button  == 1 :
		GPIO.wait_for_edge(23, GPIO.RISING, bouncetime=200)
		print 'Thanks for pushing the doorbell'
		os.system('aplay doorbell.wav')
		print 'Starting the camera function'
		camera()
		#raspistill()
		print 'Starting the sendSpark function'
		sendSpark()

def sendSpark():
	print 'Forming up the Spark message with attachment'
	filepath    = 'camera.png'  
	filetype    = 'image/png'
	roomId      = config.roomId
	token	    = config.token
	url         = "https://api.ciscospark.com/v1/messages"  
  	
	
	my_fields={'roomId': roomId,   
        	'text': 'Hi, looks like this person just rang the doorbell. See details above' ,  
           	'files': ('screenshot.jpg', open(filepath, 'rb'), filetype)  
           	}  
	m = MultipartEncoder(fields=my_fields)  
	r = requests.post(url, data=m,  
                  headers={'Content-Type': m.content_type,  
                           'Authorization': 'Bearer ' + token})  
		
	#print r.json()  
	print 'Message sent to Spark room'
buttonPress()

GPIO.cleanup() 
