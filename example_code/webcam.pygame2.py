#!/usr/bin/python
import pygame, sys
from pygame.locals import *
import pygame.camera
import os
import time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib
from PIL import Image, ImageChops, ImageOps
import math, operator
from itertools import izip

pygame.init()
pygame.camera.init()

count = 0   
width = 320
height = 240
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
      
      
   i1 = ImageOps.posterize(ImageOps.equalize(ImageOps.autocontrast(Image.open(fileName).convert("L"))),1).histogram()
   i2 = ImageOps.posterize(ImageOps.equalize(ImageOps.autocontrast(Image.open(previousFileName).convert("L"))),1).histogram()
   

   # calculate rms
   rms = math.sqrt(reduce(operator.add,map(lambda a,b: (a-b)**2, i1, i2))/len(i1))
   print(str(rms))
   isDiff = rms > 300
   
   #i1 = Image.open(fileName)
   #i2 = Image.open(previousFileName)
   #pairs = izip(i1.getdata(), i2.getdata())
   #if len(i1.getbands()) == 1:
    # for gray-scale jpegs
   #   dif = sum(abs(p1-p2) for p1,p2 in pairs)
   #else:
   #   dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
 
   #ncomponents = i1.size[0] * i1.size[1] * 3
  # percentDiff = (dif / 255.0 * 100) / ncomponents
   #print("Difference (percentage):", percentDiff)
   #isDiff = percentDiff > 2
   
   if (isDiff):
      i1.save(str(count ) +'_1.jpg')
      i2.save(str(count ) +'_2.jpg')
      msg = MIMEMultipart()
      msg.attach(MIMEImage(file(fileName).read(),name=os.path.basename(fileName)))
      msg.attach(MIMEImage(file(str(count ) +'_1.jpg').read(),name=os.path.basename(str(count ) +'_1.jpg')))
      msg.attach(MIMEImage(file(str(count ) +'_2.jpg').read(),name=os.path.basename(str(count ) +'_2.jpg')))
      print("read file")
      # to send
      try:
         s = smtplib.SMTP('smtp.gmail.com:587')
         s.ehlo()
         s.starttls()
         s.login('ronnie.day1@gmail.com','couxL2G3')
         s.sendmail('ronnie.day@rbccm.com',['ronnie.day@hotmail.co.uk'], msg.as_string())
         s.quit()
         print("Successfully sent email")
      except:
         print("Unexpected error:", sys.exc_info()[0])
   
   time.sleep(1) 
   count = count + 1
      
