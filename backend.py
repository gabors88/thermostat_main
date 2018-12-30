#!/home/pi/thermostat/thermo/thermo/bin/python

from flask import *
from flask_bootstrap import Bootstrap

import dht22
import relay

import os
import sys
import sqlite3
from datetime import * 


app = Flask(__name__)
#Bootstrap(app)

SENSOR_LIST = ()
PATH = "/home/pi/thermostat/thermo"

###################################################
sqlite3.register_adapter(bool, str)
sqlite3.register_converter("BOOLEAN", lambda v: 'T' in v)

# TABLES: status, schedule, settings
thermConn = sqlite3.connect("/home/pi/thermostat/thermo/database/thermostat.db", 
                            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, #use this to save datetime
                            check_same_thread=False)
# returned rows can be called with case-insensitive column names
thermConn.row_factory = sqlite3.Row
thermCursor = thermConn.cursor()

#CONFIG = thermCursor.execute('SELECT * FROM settings').fetchone()


sensorConn = sqlite3.connect("/home/pi/thermostat/thermo/database/sensor.db", 
                            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, #use this to save datetime
                            check_same_thread=False)


sensorConn.row_factory = sqlite3.Row
sensorCursor = sensorConn.cursor()

#####################################################
#
#UPDATE thermostat SET status = 1, target_temp = 21 WHERE id = 1;
#
#UPDATE sensors SET temperature = 21.5, humidity = 50.2 WHERE id = 1;
#
#
#####################################################

@app.route('/', methods=['GET'])
def webroot():

    mainTemp = dht22.getTempHum()[1]
    mainHum = dht22.getTempHum()[0]
    relayStatus = relay.getStatus()
    
    heatingStatus = thermCursor.execute('SELECT * from thermostat').fetchone()
    
    secondSensor = sensorCursor.execute('SELECT * from sensors').fetchone()


    return render_template("index.html", main_temperature = mainTemp,
                            main_humidity = mainHum,
                            second_temperature = secondSensor['temperature'],
                            second_humidity = secondSensor['humidity'],
                            relay_status = relayStatus,
                            heating_status = "On" if heatingStatus['status'] == 1 else "Off"
                            )

@app.route('/status/relay', methods=['GET'])
def status_relay():
    return relay.getStatus()
    
@app.route('/relay/<int:status>', methods=['GET'])
def relay_on_off(status):
    if (status == 1):
#        relay.turnOnHeating()
        thermCursor.execute('UPDATE thermostat SET status = 1 WHERE id = 1;')
        thermConn.commit()
        return 'On'
    else: 
#        relay.turnOffHeating()
        thermCursor.execute('UPDATE thermostat SET status = 0 WHERE id = 1;')
        thermConn.commit()
        return 'Off'

@app.route('/_status', methods=['GET'])
def _status():

    sensor_fail = False

#    mainTemp = dht22.getTempHum()[1]
#    mainHum = dht22.getTempHum()[0]
    relayStatus = relay.getStatus()
    
    heatingStatus = thermCursor.execute('SELECT * from thermostat').fetchone()
    mainSensor = sensorCursor.execute('SELECT * from sensors WHERE id=0').fetchone()
    secondSensor = sensorCursor.execute('SELECT * from sensors WHERE id=1').fetchone()
    
    sensor_last_update = datetime.strptime(secondSensor['last_update'], "%Y-%m-%d %H:%M:%S.%f")
    if (datetime.now() - sensor_last_update).seconds > 60:
        sensor_fail = True

    heating_status = relay.getStatus()
    currentWeather = thermCursor.execute('Select * from weather').fetchone()
    
    if (request.user_agent.browser == "iOSapp"):

        return jsonify(
                main_temperature = mainSensor['temperature'],
                main_humidity = mainSensor['humidity'],
                relay_status = relayStatus,
                heating_status = heatingStatus['status'] ,
                heating_target_temperature = heatingStatus['target_temp'],
                second_temperature = secondSensor['temperature'],
                second_humidity = secondSensor['humidity'],
                current_weather_temp = currentWeather['current_temperature'],
                current_weather_summary = currentWeather['current_summary']
                )
    else: 
        html = '<div id="updateContainer"> \
            <div id="main_temperature">{main_temperature}</div>\
            <div id="main_humidity">{main_humidity}</div>\
            <div id="relay_status">{relay_status}</div>\
            <div id="heating_status">{heating_status}</div>\
            <div id="heating_target_temperature">{heating_target_temperature}</div>\
            <div id="second_temperature">{second_temperature}</div>\
            <div id="second_humidity">{second_humidity}</div>\
            <div id="current_weather_temp">{current_weather_temp}</div>\
            <div id="current_weather_icon">{current_weather_icon}</div>\
            <div id="current_weather_summary">{current_weather_summary}</div>\
            </div>'.format( 
                    main_temperature = mainSensor['temperature'],
                    main_humidity = mainSensor['humidity'],
                    relay_status = "<img src=\"static/img/fire1.png\" width=\"35\" height=\"35\" >"if relayStatus == "ON" else "<img src=\"static/img/cool.jpg\" width=\"35\" height=\"35\">",
                    heating_status = "On" if heatingStatus['status'] == 1 else "Off",
                    heating_target_temperature = heatingStatus['target_temp'],
                    second_temperature = secondSensor['temperature'] if sensor_fail == False else "<font color=\"grey\">%s</font>" % secondSensor['temperature'],
                    second_humidity = secondSensor['humidity'],
                    current_weather_temp = currentWeather['current_temperature'],
                    current_weather_icon = "<i class=\"wi wi-%s\"></i> " % currentWeather['current_icon'] ,
                    current_weather_summary = currentWeather['current_summary'],
                    )
        return html


@app.route('/target_temp/<string:targettemp>', methods=['GET'])
def target_temp(targettemp):

    targetTemp = float(targettemp)
    if (targetTemp > 5 and targetTemp < 45):
    
        thermCursor.execute('UPDATE thermostat SET target_temp = ? WHERE id = ?;', (targetTemp, 1))
        thermConn.commit()
    return targettemp


@app.route('/sensor/update/<int:id>/<float:temp>/<float:hum>', methods=['GET'])
def sensor_update(id, temp, hum):
    
    if (id < 0 or temp < 0 or hum < 0):
        return "error - valid data needed"
    

    sensorValues = []

    sensorValues.append((id,
                        temp,
                        hum,
                        datetime.now()))
    sensorCursor.executemany('INSERT OR REPLACE INTO sensors VALUES(?,?,?,?)', sensorValues)
    sensorConn.commit()

    return "ok"








if __name__ == "__main__":
    app.run("0.0.0.0", port=8000, debug=True)




