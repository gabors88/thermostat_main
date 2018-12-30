#!thermo/bin/python


import forecastio
import sys
import os
import time
from datetime import datetime
import sqlite3

#########################################

api_key = "f1bd57e9e6838eb22b5a26526e2eebba"
lat = 47.4821
lng = 19.1575

#########################################

sqlite3.register_adapter(bool, str)
sqlite3.register_converter("BOOLEAN", lambda v: 'T' in v)


        
weatherConn = sqlite3.connect("/home/pi/thermostat/thermo/database/thermostat.db",
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
        check_same_thread=False) #use this to save datetimeself.weatherConn.row_factory = sqlite3.Row # returned rows can be called with case-insensitive column names
#weatherCursor= weatherConn.cursor()

weatherConn.row_factory = sqlite3.Row
weatherCursor = weatherConn.cursor()

########################################


#thermCursor.execute('UPDATE thermostat SET status = 0 WHERE id = 1;')
#heatingStatus = thermCursor.execute('SELECT * from thermostat').fetchone()


#current.temperature
#current.icon
#current.summary
#lastupdate


def getCurrentWeather():
    
    weather_current = [] 
    weather = weatherCursor.execute('SELECT * from weather').fetchone()
  
   # test = datetime.now()
   # weatherCursor.execute('UPDATE weather SET last_update = ? WHERE id = ?;', (test,1))
   # weatherConn.commit()
    
    
    #print weather['last_update']
    if (weather['last_update'] == "None") :
        
        weatherCursor.execute('UPDATE weather SET last_update = ? WHERE id = ?;', (datetime.now(), 1))
        weatherConn.commit()
#2018-11-14 20:23:28.391946
#%Y-%m-%d %H:%M:%S.%f
    last_u = weather['last_update']
    last_update = datetime.strptime(last_u, "%Y-%m-%d %H:%M:%S.%f")
    #print weather['last_update']
    #print last_update
 #   print (datetime.now() - last_update).seconds
    if (datetime.now() - last_update).seconds > 300:
        

       #error handling!!
        try:
            forecast = forecastio.load_forecast(api_key, lat, lng)
            current = forecast.currently()

            weather_current.append(( 1,
                                    current.temperature,
                                    current.icon,
                                    current.summary,
                                    datetime.now()
                                    ))



            weatherCursor.executemany('INSERT OR REPLACE INTO weather VALUES(?,?,?,?,?)', weather_current)
       #return (current.temperature, current.icon, self.lastUpdate)
            weatherConn.commit()
        except:
            print("Error while getting weather info:", sys.exc_info()[0])
    return


#getCurrentWeather()
        #print current.temperature
        #print current.summary
        #print current.icon
