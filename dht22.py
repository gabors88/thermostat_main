#!thermo/bin/python

import RPi.GPIO as GPIO
import Adafruit_DHT
import sys
import os
import time


DHT22_PIN = 4
DHT22_CORRECTION = -0.373296

GPIO.setmode(GPIO.BCM)
GPIO.setup(DHT22_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#ERROR check needed!!!

def getTempHum():
        
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, DHT22_PIN, retries=15, delay_seconds=0.5, correction=DHT22_CORRECTION) 

    if humidity is not None and temperature is not None:
        return (round(humidity, 1), round(temperature,1))
        #return humidity, temperature
    else:
        return (0.0, 0.0)


    GPIO.cleanup()


#print(getTempHum())
