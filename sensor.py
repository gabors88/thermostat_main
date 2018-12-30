#!thermo/bin/python

import dht22
import time
import sys
import os

#from datetime import *
import urllib2



class sensorDaemon(object):
    


    def __init__(self):
        
        self.temperature = dht22.getTempHum()[1]
        self.humidity = dht22.getTempHum()[0]
        self.server = sys.argv[1]
        self.id = sys.argv[2]


    def run(self):


        while True:
            
            self.temperature = dht22.getTempHum()[1]
            self.humidity = dht22.getTempHum()[0]

# @app.route('/sensor/update/<int:id>/<float:temp>/<float:hum>', methods=['GET'])
# http://server:8000/sensor/update/1/21.5/50.0

            url = 'http://' + self.server + '/sensor/update/' + self.id + '/' + str(self.temperature) + '/' + str(self.humidity)
            respn = urllib2.urlopen(url)

            if respn is None:
                print "error while getting url"

            else:
                print "successful update"


            time.sleep(5)



if __name__ == "__main__":
    print("Sensor Daemon")
    daemon = sensorDaemon()
    daemon.run()

    
