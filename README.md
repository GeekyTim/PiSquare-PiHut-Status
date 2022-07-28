# PiSquare - Using the PiHut Status Board
## Control a PiHut Status board on an SB Components PiSquare (Pico)

The original code that came with the PiSquare was pretty rudimentary to say the least! Stupidly, I had assumed that 
the PiSquare would come with some configurable software which would allow interaction with HATs. It sort of does, 
but far too basic.

The purpose for this project was to investigate and write code for a Raspberry Pi and the PiSquare. I chose one of 
the simplest HATs I had - the [PiHut Status board](https://thepihut.com/products/status-board-pro). It consists of 5 
buttons and 10 LEDs (5 red and 5 green). The task I chose was to control some lights and plugs in my cabin, and see 
the status of each. The lights are Philips Hue, and plugs are TP-Link - both of which have Python libraries 
([phue](https://github.com/studioimaginaire/phue) and [kasa](https://github.com/python-kasa/python-kasa)).

## Raspberry Pi Code

1. Copy the PiServer folder over to your Raspberry Pi.
2. Install the following required python libraries (usually pip3 install *library*):
   1. toml
   2. phue
   3. python-kasa
3. Edit the configuration.toml file (in the 'configs' folder) to define the names of your lamps and plugs.
4. Run pisquare-server.py

## PiSquare Code (MicroPython)

MicroPython has already been installed on the PiSquare, so you should be able to copy this code over straight away.

1. Copy the three files over to your PiSquare
2. Rename 'psconfig_template.py' to 'psconfig.py'
3. Edit psconfig.py and change the values appropriately, leaving pinconvertion alone.
4. Install the picozero library.
5. Run main.py

## How It Works

### Raspberry Pi Server
The server software will read the configuration file (in [TOML](https://toml.io/en/) format). You should be able 
to define more than one HAT configuration, so you can use multiple PiSquares with one Pi server (untested). 

The three values (psalias, type and host) define the 'name' of each button, the type of device it is controlling and 
a 'host' value used within each 'handler'.

Each HAT will require its own library to handle the input/output for a particular HAT. The server will instantiate a 
class object for each HAT before starting the 'Listener' code.

The 'Listener' code is (hopefully!) generic, and is just used for handling the input from the PiSquare. Currently, 
that traffic is always started from the PiSquare, with a response to each request being sent back to the PiSquare. I 
hope to expand that later, so it can also start a conversation from the Pi.

The PiHutStatus class sets up and handles all the messages coming from the PiSquare. The definition is supplied from 
the configuration.toml file.  If you write your own HAT handler code, you need to ensure you include the 
'handlerequest' method which takes the messages sent from the PiSquare and does whatever you want it to!

### The PiSquare Client
The PiSquare client code in main.py is mostly HAT specific. However, it does include one piece of generic code which 
handles the PiSquare's connection to Wi-Fi and the sending/receiving of messages to/from the Pi.

### The Message Format
Python handles the conversion between Python dictionaries and JSON really well, so I am using JSON so send 
information between the PiSquare and Pi.

The general format is:

    {'client': 'clientname', 'payload': {payload}}`

The structure of the *payload* depends on the 'action' required. For this HAT, it is either 'requeststatus' or 
'changestate'.

The format of the 'changestate' action, which turns a lamp/plug on/off or toggles the state, is:

    {'action': 'changestate', 
     'button': 'whichbutton',
     'status': 'on/off/toggle'}

The format of the 'requeststatus' action, which requests the current state of the lamp/plug (on or off)

    {'action': 'requeststatus', 
     'button': 'whichbutton'}

For your own HATs, you can define the payload however you wish!

### Conclusion
The PiSquare is not perfect, but with a bit of wrangling I have got it in shape and able to handle a simple hat, 
with a bunch of reusable code for the communications side. Comms still needs a bit of work (e.g. initialise a 
conversation from the Pi), but this is hopefully a good enough start for most to begin to most HATs.