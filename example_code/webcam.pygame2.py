#!/usr/bin/python
import pygame, sys
from pygame.locals import *
import pygame.camera
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib
from PIL import Image, ImageChops
import math, operator

pygame.init()
pygame.camera.init()

count = 0   
width = 1024
height = 860
previousFileName = None

while True:
   cam = pygame.camera.Camera("/dev/video0",(width,height))
   cam.start()
   image = cam.get_image()
   cam.stop()
   fileName = str(count ) +'.jpg'
   pygame.image.save(image,fileName)
   print("finished taking photo " + fileName)
   if (previousFileName is None):
      previousFileName = fileName
      count = count + 1
      continue;
      
      
   h1 = Image.open(fileName).histogram()
   h2 = Image.open(previousFileName).histogram()
   # h = ImageChops.difference(image1, image2).histogram()

   # calculate rms
   rms = math.sqrt(reduce(operator.add,map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
   isDiff = rms > 100
   print(str(rms))
   
   if (isDiff):
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
   
   time.sleep(1) 
   count = count + 1
      
