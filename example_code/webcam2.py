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
import cStringIO
import numpy
import pyaudio
import analyse


class App():

	def __init__(self, logger):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/home/pi/robot/example_code/webcam2.out'
		self.stderr_path = '/home/pi/robot/example_code/webcam2.err'
		self.pidfile_path = '/var/run/webcam2.pid'
		self.pidfile_timeout = 5
		self.logger = logger
		self.issmtpsetup = False
		
	def sendMail(self, image, background, thresholded, diffAmount, volume):
		#pygame.image.save(image, "image.jpg")
		#pygame.image.save(background, "background.jpg")
		#pygame.image.save(thresholded, "thresholded.jpg")
		imstring = pygame.image.tostring(image,"RGB")
		im = Image.fromstring("RGB", (320,240), imstring)
		memfim = cStringIO.StringIO()
		im.save(memfim, "JPEG")
		
		bgstring = pygame.image.tostring(background,"RGB")
		bg = Image.fromstring("RGB", (320,240), bgstring)
		memfbg = cStringIO.StringIO()
		bg.save(memfbg, "JPEG")
		
		tstring = pygame.image.tostring(thresholded,"RGB")
		t = Image.fromstring("RGB", (320,240), tstring)
		memft = cStringIO.StringIO()
		t.save(memft, "JPEG")
		
		msg = MIMEMultipart()
		msg['Subject'] = 'Image diff= (' + str(diffAmount) + ') Loudness = (' + str(volume) +')'
		msg.attach(MIMEImage(memfim.getvalue(),name="image.jpg"))
		msg.attach(MIMEImage(memfbg.getvalue(),name="background.jpg"))
		msg.attach(MIMEImage(memft.getvalue(),name="thresholded.jpg"))
		self.logger.debug("attached files for email")
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
		pixelDiffThreshold = 1000
		bgVolume = []
		volumeDiffThreshold = 3
		# Initialize PyAudio
		pyaud = pyaudio.PyAudio()
		sampleRate = int(pyaud.get_device_info_by_index(0)['defaultSampleRate'])
		self.logger.debug("sampleRate = " + str(sampleRate))
		# Open input stream, 16-bit mono at 44100 Hz
		stream = pyaud.open(
			format = pyaudio.paInt16,
			channels = 1,
			rate = 48000,
			input = True)
		
		while True:
			
			try:
				# Read raw microphone data
				rawsamps = stream.read(8192)
				# Convert raw data to NumPy array
				samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
				# Show the volume and pitch
				volume = analyse.loudness(samps)#, analyse.musical_detect_pitch(samps)
			except IOError: 
      				self.logger.debug("dropped mic frame")
      				
			
			image = cam.get_image()
			
			
      			if (len(bg) != bgSamples or len(bgVolume) != bgSamples):
			  bg.append(image)
			  bgVolume.append(volume)
			  self.logger.debug("creating buffers, volume= " + str(len(bgVolume)) + " images=" + str(len(bg)))
			  continue;
			
			background = pygame.transform.average_surfaces(bg)
		
			similarPixels = pygame.transform.threshold(thresholded,image,(0,255,0),(30,30,30),(0,0,0),1,background)
			diff = size[0]*size[1] - similarPixels
			isDiff = diff > pixelDiffThreshold
			
			self.logger.debug("image diff " + str(diff))
			averageLoudness = sum(bgVolume) / float(len(bgVolume))
			isLoud = abs(volume) - abs(averageLoudness) > volumeDiffThreshold
			self.logger.debug("volume diff " + str(diff))
			
			if (isDiff or volume):
				self.logger.debug("diff "  + str(diff) + " greater than threshold " + str(pixelDiffThreshold))
				self.logger.debug("volume "  + str(volume) + " greater than threshold " + str(volumeDiffThreshold))
				t = Thread(target=self.sendMail, args =[image, background, thresholded, diff, volume])
				t.start()
				
			#integrate into the background. 
			bg.pop(0)
			bg.append(image)
		#cam.stop()

try:

	logger = logging.getLogger("WebCam")
	logger.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	handler = logging.handlers.RotatingFileHandler("/home/pi/robot/example_code/webcam.log", maxBytes=100000, backupCount=2)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	app = App(logger)
	logger.info("created app")
	daemon_runner = runner.DaemonRunner(app)
	daemon_runner.daemon_context.files_preserve=[handler.stream]
	daemon_runner.do_action()
except:
	print(traceback.format_exc())
