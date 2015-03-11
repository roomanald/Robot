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

class App():
	count = 0   
	width = 320
	height = 240
	previousFileName = None
	fileMaxCount = 50
	threshold = 50

	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/home/pi/robot/example_code/webcam.out'
		self.stderr_path = '/home/pi/robot/example_code/webcam.err'
		self.pidfile_path = '/var/run/webcam.pid'
		self.pidfile_timeout = 5
		pygame.init()
		pygame.camera.init()
		self.cam = pygame.camera.Camera("/dev/video0",(self.width,self.height))
		self.cam.start()
		time.sleep(2)#let the camera settle

	def sendMail(self, image1, image2, image3, image4):
		msg = MIMEMultipart()
		msg.attach(MIMEImage(file(image1).read(),name=os.path.basename(image1)))
		msg.attach(MIMEImage(file(image2).read(),name=os.path.basename(image2)))
		msg.attach(MIMEImage(file(image1).read(),name=os.path.basename(image1)))
		msg.attach(MIMEImage(file(image2).read(),name=os.path.basename(image2)))
		logger.info("read file")
		# to send
		try:
			s = smtplib.SMTP('smtp.gmail.com:587')
			s.ehlo()
			s.starttls()
			s.login('ronnie.day1@gmail.com','couxL2G3')
			s.sendmail('ronnie.day@hotmail.co.uk',['ronnie.day@hotmail.co.uk'], msg.as_string())
			s.quit()
			logger.info("Successfully sent email")
		except:
			logger.info("Unexpected error:", sys.exc_info()[0])

	def run(self):
		print("runner started")
		while True:
			image = self.cam.get_image()
			self.fileName = str(count) + '.jpg'
			pygame.image.save(image,self.fileName)
			logger.info("finished taking photo " + self.fileName)
			if (self.previousFileName is None):
				self.previousFileName = self.fileName
				self.count = (self.count + 1) % self.fileMaxCount
				continue

			i_1 = ImageOps.equalize(ImageOps.autocontrast(Image.open(self.fileName).convert("L")))
			i_1 = ImageOps.posterize(Image.fromarray(ndimage.gaussian_filter(i_1, 8),"L"),1)
			i1 = i_1.histogram()
			i_2 = ImageOps.equalize(ImageOps.autocontrast(Image.open(self.previousFileName).convert("L")))
			i_2 = ImageOps.posterize(Image.fromarray(ndimage.gaussian_filter(i_2, 8),"L"),1)
			i2 = i_2.histogram()
			
			rms = math.sqrt(reduce(operator.add,map(lambda a,b: (a - b) ** 2, i1, i2)) / len(i1))
			logger.info(str(rms))
			isDiff = rms > threshold

			if (isDiff):
				i_1.save(str(self.count) + '_1.jpg')
				i_2.save(str(self.count) + '_2.jpg')
				sendmail(self.fileName, self.previousFileName, str(self.count) + '_1.jpg', str(self.count) + '_2.jpg')
			previousFileName = fileName
			count = (count + 1) % fileMaxCount
			#cam.stop()

try:
	app = App()
	print("created app")
	logger = logging.getLogger("WebCam")
	logger.setLevel(logging.INFO)
	formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
	handler = logging.FileHandler("/home/pi/robot/example_code/webcam.log")
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	print ("created logger")
	daemon_runner = runner.DaemonRunner(app)
	daemon_runner.daemon_context.files_preserve=[handler.stream]
	daemon_runner.do_action()
except:
	print("Unexpected error:", sys.exc_info()[0])
