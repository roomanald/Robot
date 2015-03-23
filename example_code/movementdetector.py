import pygame
from pygame.locals import *
import pygame.camera
import logging
import time

class MovementDetector:
	def __init__(self, logger, movementCallback, sampleCount, pixelDiffThreshold, imageSize):
		self.logger = logger
		self.movementCallback = movementCallback
		self.sampleCount = sampleCount
		self.pixelDiffThreshold = pixelDiffThreshold
		self.imageSize = imageSize
		self.bg = []
		pygame.init()
		pygame.camera.init()
		self.cam = pygame.camera.Camera("/dev/video0",self.imageSize)

	def start(self):
	
		thresholded = pygame.surface.Surface(self.imageSize)
		self.cam.start()
		time.sleep(2)#let the camera settle
		
	        while True:
			image = self.cam.get_image()
			if (len(self.bg) != self.sampleCount):
				self.bg.append(image)
				self.logger.debug("filling image buffer count=" + str(len(self.bg)))
				continue;
				    
		        background = pygame.transform.average_surfaces(self.bg)
		        
		        similarPixels = pygame.transform.threshold(thresholded,image,(0,255,0),(30,30,30),(0,0,0),1,background)
		        
			diff = self.imageSize[0]*self.imageSize[1] - similarPixels
			isDiff = diff > self.pixelDiffThreshold
			
			if (isDiff):
			    movementCallback(image, background, thresholded, diff)
		        
		        self.bg.pop(0)
		        self.bg.append(image)
	        
	def stop(self):
		self.cam.stop()
	    
