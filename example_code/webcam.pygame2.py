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

while True:
   cam = pygame.camera.Camera("/dev/video0",(width,height))
   cam.start()
   image = cam.get_image()
   cam.stop()
   fileName = str(count ) +'.jpg'
   pygame.image.save(image,fileName)
   print("finished taking photo " + fileName)

   msg = MIMEMultipart()
   msg.attach(MIMEImage(file(fileName).read()))

   print("read file")
   # to send
   try:
      s = smtplib.SMTP('smtp.gmail.com:587')
      s.ehlo()
      s.starttls()
      s.login('ronnie.day1@gmail.com','couxL2G3')
      s.sendmail('ronnie.day@rbccm.com',['ronnie.day@rbccm.com'], msg.as_string())
      s.quit()
      print("Successfully sent email")
   except:
      print("Unexpected error:", sys.exc_info()[0])
   time.sleep(300) 
   count = count + 1
