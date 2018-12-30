#!thermo/bin/python

import relay
import time

relay.turnOnHeating()
time.sleep(1)
relay.turnOffHeating()

print(relay.getStatus())
relay.gpioCleanUp()
