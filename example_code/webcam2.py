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

	def __init__(self, logger):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/home/pi/robot/example_code/webcam2.out'
		self.stderr_path = '/home/pi/robot/example_code/webcam2.err'
		self.pidfile_path = '/var/run/webcam2.pid'
		self.pidfile_timeout = 5
		self.logger = logger
		
	def sendMail(self, image, background, thresholded, diffAmount):
		#pygame.image.save(image, "image.jpg")
		#pygame.image.save(background, "background.jpg")
		#pygame.image.save(thresholded, "thresholded.jpg")
		msg = MIMEMultipart()
		msg['Subject'] = 'Intruder - (' + str(diffAmount) + ')' 
		msg.attach(MIMEImage(pygame.image.tostring(image),name="image.jpg"))
		msg.attach(MIMEImage(pygame.image.tostring(background),name="background.jpg"))
		msg.attach(MIMEImage(pygame.image.tostring(thresholded),name="thresholded.jpg"))
		self.logger.debug("attached files for email")
		# to send
		try:
			s = smtplib.SMTP('smtp.gmail.com:587')
			s.ehlo()
			s.starttls()
			s.login('ronnie.day1@gmail.com','couxL2G3')
			s.sendmail('ronnie.day@hotmail.co.uk',['ronnie.day@hotmail.co.uk'], msg.as_string())
			s.quit()
			self.logger.info("Successfully sent email")
		except:
			self.logger.error(traceback.format_exc())
			
	def run(self):
		count = 0   
		size = (320,240)
		self.logger.info("runner started")
		pygame.init()
		pygame.camera.init()
		cam = pygame.camera.Camera("/dev/video0",size)
		cam.start()
		time.sleep(2)#let the camera settle
		self.logger.info("camera started")
		bgSamples = 20
		bg = []
		thresholded = pygame.surface.Surface(size)
		pixelDiffThreshold = 100
		
		while True:
			image = cam.get_image()
      			if (len(bg) != bgSamples):
			  bg.append(image)
			  continue;
			
			background = pygame.transform.average_surfaces(bg)
		
			similarPixels = pygame.transform.threshold(thresholded,image,(0,255,0),(30,30,30),(0,0,0),1,background)
			diff = size[0]*size[1] - similarPixels
			isDiff = diff > pixelDiffThreshold
			
			self.logger.debug("diff " + str(diff))
			
			if (isDiff):
				self.logger.info("diff "  + str(diff) + " greater than threshold " + str(pixelDiffThreshold))
				t = Thread(target=self.sendMail, args =[image, background, thresholded, diff])
				t.start()
				
			#integrate into the background. 
			bg.pop(0)
			bg.append(image)
		#cam.stop()

try:

	logger = logging.getLogger("WebCam")
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	handler = logging.handlers.RotatingFileHandler("/home/pi/robot/example_code/webcam.log", maxBytes=100000, backupCount=2)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	print ("created logger")
	app = App(logger)
	logger.info("created app")
	daemon_runner = runner.DaemonRunner(app)
	daemon_runner.daemon_context.files_preserve=[handler.stream]
	daemon_runner.do_action()
except:
	print(traceback.format_exc())
