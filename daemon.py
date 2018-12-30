#!/home/pi/thermostat/thermo/thermo/bin/python

from flask import *
from flask_bootstrap import Bootstrap
from datetime import *


import dht22
import relay
import weather

import os
import sys
import sqlite3
import time
import signal
import subprocess



bspath = os.path.abspath(__file__)
#dname = os.path.dirname(abspath)
#os.chdir(dname)

class thermoDaemon(object):

    def signal_handler(self, sig, fram):
        relay.gpioCleanUp()
        print("Quitting...and cleaning up the GPIO ports...")
        sys.exit(0)



    def __init__(self):

        sqlite3.register_adapter(bool, str)
        sqlite3.register_converter("BOOLEAN", lambda v: 'T' in v)

        ##############################
        
        self.thermConn = sqlite3.connect("/home/pi/thermostat/thermo/database/thermostat.db", 
                            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
                            check_same_thread=False) #use this to save datetime
        self.thermConn.row_factory = sqlite3.Row # returned rows can be called with case-insensitive column names
        self.thermCursor= self.thermConn.cursor()

        ##############################

        self.sensorConn = sqlite3.connect("/home/pi/thermostat/thermo/database/sensor.db", 
                            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
                            check_same_thread=False) #use this to save datetime
        self.sensorConn.row_factory = sqlite3.Row # returned rows can be called with case-insensitive column names
        self.sensorCursor= self.sensorConn.cursor()

        ##############################
        
        #self.config = self.thermCursor.execute('SELECT * FROM thermostat').fetchone() 
        
        #currentWeather = weather.getCurrentWeather()
        #self.WeatherlastUpdate = currentWeather[2]
        #self.currentOutsideTemp = currentWeather[0]
    
    def update_main_sensor(self):

        
        temphum = dht22.getTempHum()
        sensorValues = []
        sensorValues.append((0,
                            temphum[1],
                            temphum[0],
                            datetime.now()))

        self.sensorCursor.executemany('INSERT OR REPLACE INTO sensors VALUES(?,?,?,?)', sensorValues)
        self.sensorConn.commit()

    def run(self):

        self.thermostatMode = 0
#        self.mainTemp = 0

        while True:

            weather.getCurrentWeather()    
#            self.prevTemp = self.mainTemp
#            self.mainTemp = dht22.getTempHum()[1]
#            if self.mainTemp < 0:
#                self.mainTemp = prevTemp
#                continue

            self.update_main_sensor()
            
            self.secondSensor = self.sensorCursor.execute('SELECT * FROM sensors WHERE id=1').fetchone()
            self.mainSensor = self.sensorCursor.execute('SELECT * FROM sensors WHERE id=0').fetchone()

            self.secondTemp = self.secondSensor['temperature']
            self.mainTemp = self.mainSensor['temperature']

            self.relayMode = relay.getStatus()
            
            self.status = self.thermCursor.execute('SELECT * from thermostat').fetchone()

            self.thermostatMode = self.status['status']
            self.targetTemp = self.status['target_temp']
            


            if (self.thermostatMode == 0 and self.relayMode == "ON"):
                relay.turnOffHeating()
                print("Relay is on but heating is turned off....turning off heating")

            if (self.thermostatMode == 1 and self.relayMode == "OFF" and (self.targetTemp > self.mainTemp and self.targetTemp > self.secondTemp)):
                relay.turnOnHeating()
                print("Turning on heating, beacuse:", self.thermostatMode, self.relayMode, self.targetTemp, self.mainTemp, self.secondTemp) 
            
            if (self.thermostatMode == 1 and self.relayMode == "ON" and (self.targetTemp < self.mainTemp or self.targetTemp < self.secondTemp)):
                relay.turnOffHeating()
                print("Turning off heating, beacuse:", self.thermostatMode, self.relayMode, self.targetTemp, self.mainTemp, self.secondTemp) 
            else:
                if (self.thermostatMode == 0 and self.relayMode == "OFF"):
                    print("Idle")
            time.sleep(5)




if __name__ == "__main__":
        print("Thermostat Daemon")
        daemon = thermoDaemon()
        daemon.run()
