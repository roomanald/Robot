#!/usr/bin/python
import pygame
from pygame.locals import *
import os
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib
import math
import operator
from daemon import runner
import logging
import logging.handlers
import traceback
from threading import Thread
import noisedetector
import movementdetector
import pygameHelper


class Guard():

	def __init__(self, logger):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/home/pi/robot/example_code/guard.out'
		self.stderr_path = '/home/pi/robot/example_code/guard.err'
		self.pidfile_path = '/var/run/guard.pid'
		self.pidfile_timeout = 5
		self.logger = logger
		self.issmtpsetup = False
		self.imageSize = (320,240)
		
	def sendMail(msg):
		# to send
		self.initialisesmtp()
		try:
			self.s.sendmail('ronnie.day@hotmail.co.uk',['ronnie.day@hotmail.co.uk'], msg.as_string())
			self.logger.info("Successfully sent email")
		except:
			self.logger.error(traceback.format_exc())
			self.issmtpsetup = False
	
	def initialisesmtp(self):
		if (self.issmtpsetup):
			return
		
		try:
			self.s = smtplib.SMTP('smtp.gmail.com:587')
			self.s.ehlo()
			self.s.starttls()
			self.s.login('ronnie.day1@gmail.com','couxL2G3')
			self.s.connect()
			self.issmtpsetup = True
		except:
			self.logger.error("failed to setup smtp" + traceback.format_exc())
			self.issmtpsetup = False
	
	def movementDetected(self, image, background, thresholded,diff):
		self.logger.info("movementDetected")
		imageMem = pygameHelper.convertPygameSurfaceToMemoryStream(image, self.imageSize)
		backgroundMem = pygameHelper.convertPygameSurfaceToMemoryStream(background, self.imageSize)
		thresholdMem = pygameHelper.convertPygameSurfaceToMemoryStream(thresholded, self.imageSize)
		
		msg = MIMEMultipart()
		msg['Subject'] = 'Movement detected diff= (' + str(diff) + ')'
		msg.attach(MIMEImage(imageMem.getvalue(),name="image.jpg"))
		msg.attach(MIMEImage(backgroundMem.getvalue(),name="background.jpg"))
		msg.attach(MIMEImage(thresholdMem.getvalue(),name="thresholded.jpg"))
		t = Thread(target=self.sendMail, args =[msg])
		t.start()
		return
	
	def noiseDetected(self, noise, averageNoise):
		self.logger.info("noiseDetected")
		msg = MIMEMultipart()
		msg['Subject'] = 'Noise detected diff= (' + str(noise) + ') average noise =(' + str(averageNoise) +')'
		t = Thread(target=self.sendMail, args =[msg])
		t.start()
		return
	
	def run(self):
		self.logger.info("runner started")
		
		sampleCount = 50
		pixelDiffThreshold = 1000
		noiseDiffThreshold = 5
		
		self.movementDetector = movementdetector.MovementDetector(self.logger,self.movementDetected, sampleCount,  pixelDiffThreshold, self.imageSize)
		movementThread = Thread(target=self.movementDetector.start)
		movementThread.start()
		
		self.noiseDetector = noisedetector.NoiseDetector(self.logger, self.noiseDetected, sampleCount, noiseDiffThreshold)
		noiseThread = Thread(target=self.noiseDetector.start)
		noiseThread.start()

try:

	logger = logging.getLogger("Guard")
	logger.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	handler = logging.handlers.RotatingFileHandler("/home/pi/robot/example_code/guard.log", maxBytes=100000, backupCount=2)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	
	sl = StreamToLogger(logger, logging.INFO)
	sys.stdout = sl
	sl = StreamToLogger(logger, logging.ERROR)
	sys.stderr = sl
	
	app = Guard(logger)
	logger.info("created app")
	daemon_runner = runner.DaemonRunner(app)
	daemon_runner.daemon_context.files_preserve=[handler.stream]
	daemon_runner.do_action()
except:
	print(traceback.format_exc())
