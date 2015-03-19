#!/usr/bin/python
import pygame
import sys
from pygame.locals import *
import pygame.camera
import os
import time
from scipy import ndimage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib
from PIL import Image, ImageChops, ImageOps
import math
import operator
from itertools import izip
from daemon import runner
import logging
import logging.handlers
import traceback
from threading import Thread

class App():

	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/home/pi/robot/example_code/webcam2.out'
		self.stderr_path = '/home/pi/robot/example_code/webcam2.err'
		self.pidfile_path = '/var/run/webcam2.pid'
		self.pidfile_timeout = 5
		
	def sendMail(self, image, background, thresholded, diffAmount):
		pygame.image.save(image, "image.jpg")
		pygame.image.save(background, "background.jpg")
		pygame.image.save(thresholded, "thresholded.jpg")
		msg = MIMEMultipart()
		msg['Subject'] = 'Intruder - (' + diffAmount + ')' 
		msg.attach(MIMEImage(file("image.jpg").read(),name=os.path.basename(image1)))
		msg.attach(MIMEImage(file("background.jpg").read(),name=os.path.basename(image2)))
		msg.attach(MIMEImage(file("thresholded.jpg").read(),name=os.path.basename(image3)))
		print("attached files for email")
		# to send
		try:
			s = smtplib.SMTP('smtp.gmail.com:587')
			s.ehlo()
			s.starttls()
			s.login('ronnie.day1@gmail.com','couxL2G3')
			s.sendmail('ronnie.day@hotmail.co.uk',['ronnie.day@hotmail.co.uk'], msg.as_string())
			s.quit()
			print("Successfully sent email")
		except:
			print(traceback.format_exc())
			
	def run(self):
		count = 0   
		size = (320,240)
		print("runner started")
		pygame.init()
		pygame.camera.init()
		cam = pygame.camera.Camera("/dev/video0",size)
		cam.start()
		time.sleep(2)#let the camera settle
		print("camera started")
		bgSamples = 5
		bg = []
		thresholded = pygame.surface.Surface(size)
		
		while True:
			image = cam.get_image()
      			if (len(bg) != bgSamples):
			  bg.append(image)
			  continue;
			
			background = pygame.transform.average_surfaces(bg)
		
			similarPixels = pygame.transform.threshold(thresholded,image,(0,255,0),(30,30,30),(0,0,0),1,background)
			diff = size[0]*size[1] - similarPixels
			isDiff = diff > 100

			if (isDiff):
				print("diff " + str(diff))
				t = Thread(target=self.sendMail, args =[image, background, thresholded, diff])
				t.start()
			#else: #reset the background collection 
			#	bg.pop(0)
			#	bg.append(image)
		#cam.stop()

try:
	app = App()
	print("created app")
	logger = logging.getLogger("WebCam")
	logger.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	handler = logging.handlers.RotatingFileHandler("/home/pi/robot/example_code/webcam.log", maxBytes=100000, backupCount=2)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	print ("created logger")
	daemon_runner = runner.DaemonRunner(app)
	daemon_runner.daemon_context.files_preserve=[handler.stream]
	daemon_runner.do_action()
except:
	print(traceback.format_exc())
