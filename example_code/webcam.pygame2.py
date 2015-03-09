#!/usr/bin/python
import pygame, sys
from pygame.locals import *
import pygame.camera
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

pygame.init()
pygame.camera.init()

count = 0   
width = 1024
height = 860

while count < 5:

   cam = pygame.camera.Camera("/dev/video0",(width,height))
   cam.start()
   image = cam.get_image()
   cam.stop()
   pygame.image.save(image,str(count ) +'.jpg')
   time.sleep(1) 

msg = MIMEMultipart()
msg.attach(MIMEImage(file("0.jpg").read()))

# to send
mailer = smtplib.SMTP()
mailer.connect()
mailer.sendmail("ronnie.day@hotmail.co.uk", "ronnie.day@rbccm.com", msg.as_string())
mailer.close()

