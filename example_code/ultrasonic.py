import RPi.GPIO as GPIO
import time 
GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

print "Distance measurement in progress"

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)


GPIO.output(TRIG,False)
print "Waiting for sensor to settle"
time.sleep(2)


GPIO.setup(TRIG,True)
time.sleep(0.0001)
GPIO.setup(TRIG,False)

while GPIO.input(ECHO)==0
  pulse_end = time.time()
  
pulse_duration = pulse_end - pulse_start

distance = pulse_duration * 17150

distance = round(distance,2)

print "Distance : ", distance, "cm"

GPIO.cleanup()
