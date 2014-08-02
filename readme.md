This is the source code that runs on my Raspberry-Pi-powered whiteboard drawing bot. I have put it up here in case anyone is interested in seeing how it works (or maybe using it themselves.)

In order to use this code, you will have to do a few things:
* Install [Occidentalis][occidentalis] v0.2 (or just install the Occidentalis kernel)
* Install Node.js (I used [node_arm][node_arm])
* Download the Adafruit I2C and MCP230XX libraries (available [here][adafruitlibs]) and place them in the same directory as these files
* Install [Parsley][parsley]

[occidentalis]:https://learn.adafruit.com/adafruit-raspberry-pi-educational-linux-distro/occidentalis-v0-dot-2
[node_arm]:https://github.com/nathanjohnson320/node_arm
[adafruitlibs]:https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code/tree/master/Adafruit_MCP230xx
[parsley]:https://pypi.python.org/pypi/Parsley

DrawDriver.py contains the code that interfaces directly with the servo, the MCP23017 and the stepper motors. DrawInterpreter.py keeps track of the pen position and uses Parsley to interpret a command string and move the motors appropriately. DrawServer.py and DrawServer.js communicate with each other using Unix domain sockets; the Javascript file accepts POST requests and sends them to the Python script, which passes the commands to an instance of DrawInterpreter.