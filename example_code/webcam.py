#!/usr/bin/python
import pygame, sys
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
import math, operator
from itertools import izip
from daemon import runner
#import numpy
#import pyaudio
#import analyse

#for name in vars(pyaudio): print(name)

class App():
   
   def __init__(self):
      pygame.init()
      pygame.camera.init()
      
      previousFileName = None
      fileMaxCount = 50
      threshold = 50
      cam = pygame.camera.Camera("/dev/video0",(width,height))
      cam.start()
      time.sleep(2)#let the camera settle

# Initialize PyAudio
#pyaud = pyaudio.PyAudio()

# Open input stream, 16-bit mono at 44100 Hz
# On my system, device 4 is a USB microphone
#stream = pyaud.open(
#    format = pyaudio.paInt16,
#    channels = 1,
#    rate = 44100,
#    input_device_index = 2,
#    input = True)




while True:
   # Read raw microphone data
   #rawsamps = stream.read(1024)
   # Convert raw data to NumPy array
   #samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
   # Show the volume and pitch
   #print("loudness : " + analyse.loudness(samps) + "pitch : " + analyse.musical_detect_pitch(samps))
   
   image = cam.get_image()
   fileName = str(count) +'.jpg'
   pygame.image.save(image,fileName)
   print("finished taking photo " + fileName)
   if (previousFileName is None):
      previousFileName = fileName
      count = (count + 1) % fileMaxCount
      continue;
      
   i_1 = ImageOps.equalize(ImageOps.autocontrast(Image.open(fileName).convert("L")))
   i_1 = ImageOps.posterize(Image.fromarray(ndimage.gaussian_filter(i_1, 8),"L"),1)
   i1 = i_1.histogram()
   i_2 = ImageOps.equalize(ImageOps.autocontrast(Image.open(previousFileName).convert("L")))
   i_2 = ImageOps.posterize(Image.fromarray(ndimage.gaussian_filter(i_2, 8),"L"),1)
   i2 = i_2.histogram()
   

   # calculate rms
   rms = math.sqrt(reduce(operator.add,map(lambda a,b: (a-b)**2, i1, i2))/len(i1))
   print(str(rms))
   isDiff = rms > threshold
   
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
      i_1.save(str(count ) +'_1.jpg')
      i_2.save(str(count ) +'_2.jpg')
      msg = MIMEMultipart()
      msg.attach(MIMEImage(file(fileName).read(),name=os.path.basename(fileName)))
      msg.attach(MIMEImage(file(previousFileName).read(),name=os.path.basename(previousFileName)))
      msg.attach(MIMEImage(file(str(count ) +'_1.jpg').read(),name=os.path.basename(str(count ) +'_1.jpg')))
      msg.attach(MIMEImage(file(str(count ) +'_2.jpg').read(),name=os.path.basename(str(count ) +'_2.jpg')))
      print("read file")
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
         print("Unexpected error:", sys.exc_info()[0])
   previousFileName = fileName
   #time.sleep(1) 
   count = (count + 1) % fileMaxCount
cam.stop()
