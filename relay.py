#!thermo/bin/python

import RPi.GPIO as GPIO
import sys
import time
import os

RELAY = 21

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY, GPIO.OUT)

def turnOnHeating():
    GPIO.output(RELAY,GPIO.HIGH)

def turnOffHeating():
    GPIO.output(RELAY,GPIO.LOW)


def getStatus():
	if (GPIO.input(RELAY) == 1):
		return 'ON'
	else: return 'OFF'

def gpioCleanUp():
    GPIO.output(RELAY, False)
    GPIO.cleanup()

