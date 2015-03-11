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
import traceback
from threading import Thread

class App():

	def __init__(self):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/home/pi/robot/example_code/webcam.out'
		self.stderr_path = '/home/pi/robot/example_code/webcam.err'
		self.pidfile_path = '/var/run/webcam.pid'
		self.pidfile_timeout = 5

	def sendMail(self, image1, image2, image3, image4):
		msg = MIMEMultipart()
		msg.attach(MIMEImage(file(image1).read(),name=os.path.basename(image1)))
		msg.attach(MIMEImage(file(image2).read(),name=os.path.basename(image2)))
		msg.attach(MIMEImage(file(image3).read(),name=os.path.basename(image3)))
		msg.attach(MIMEImage(file(image4).read(),name=os.path.basename(image4)))
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
		width = 320
		height = 240
		previousFileName = None
		fileMaxCount = 50
		print("runner started")
		pygame.init()
		pygame.camera.init()
		cam = pygame.camera.Camera("/dev/video0",(width,height))
		cam.start()
		time.sleep(2)#let the camera settle
		print("camera started")
		rmsQueue = [50]
		rmsQueueMax = 100
		
		while True:
			image = cam.get_image()
			fileName = str(count) + '.jpg'
			pygame.image.save(image,fileName)
			#print("finished taking photo " + fileName)
			if (previousFileName is None):
				previousFileName = fileName
				count = (count + 1) % fileMaxCount
				continue

			i_1 = ImageOps.equalize(ImageOps.autocontrast(Image.open(fileName).convert("L")))
			i_1 = ImageOps.posterize(Image.fromarray(ndimage.gaussian_filter(i_1, 8),"L"),1)
			i1 = i_1.histogram()
			i_2 = ImageOps.equalize(ImageOps.autocontrast(Image.open(previousFileName).convert("L")))
			i_2 = ImageOps.posterize(Image.fromarray(ndimage.gaussian_filter(i_2, 8),"L"),1)
			i2 = i_2.histogram()
			
			rms = math.sqrt(reduce(operator.add,map(lambda a,b: (a - b) ** 2, i1, i2)) / len(i1))
			rmsQueue.insert(0,rms)
			if (len(rmsQueue) > rmsQueueMax):
				rmsQueue.pop(len(rmsQueue)-1)
			averageRms = sum(rmsQueue) / len(rmsQueue)
			print("current rms :" + str(rms) + "average rms:" + str(averageRms))
			isDiff = rms > (averageRms * 4)

			if (isDiff):
				i_1.save(str(count) + '_1.jpg')
				i_2.save(str(count) + '_2.jpg')
				t = Thread(target=self.sendMail, args =[fileName, previousFileName, str(count) + '_1.jpg', str(count) + '_2.jpg'])
				t.start()
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
	print(traceback.format_exc())
