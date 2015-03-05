#!/usr/bin/python
import pygame, sys
from pygame.locals import *
import pygame.camera
import time

pygame.init()
pygame.camera.init

count = 0
while count < 5:
   width = 640
   height = 480
   cam = pygame.camera.Camera("/dev/video0",(width,height))
   cam.start()
   image = cam.get_image()
   cam.stop()
   pygame.image.save(image,str(count ) +'.jpg')
   
   time.sleep(1) 
