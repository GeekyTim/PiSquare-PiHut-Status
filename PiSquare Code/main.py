from picozero import LED, Button
import psconfig
import pisquarecomms
import ujson
import utime

buttonleds = {'floodlight': ('GPIO14', 'GPIO4', 'GPIO17', ''),
              'computer'  : ('GPIO19', 'GPIO27', 'GPIO22', ''),
              'Monitor'   : ('GPIO15', 'GPIO10', 'GPIO9', ''),
              'Ikea'      : ('GPIO26', 'GPIO11', 'GPIO5', ''),
              'Desk'      : ('GPIO18', 'GPIO6', 'GPIO13', '')}

pin = 0
greenled = 1
redled = 2
itemstate = 3


def setleds(button, status):
    if button is not None:
        statusdata = list(buttonleds[button])
        statusdata[itemstate] = status
        buttonleds[button] = statusdata

        if status == 'on':
            buttonleds[button][greenled].off()
            buttonleds[button][redled].on()
        elif status == 'off':
            buttonleds[button][greenled].on()
            buttonleds[button][redled].off()
        else:
            buttonleds[button][greenled].off()
            buttonleds[button][redled].off()


def ispressed():
    buttonpressed = None

    for name in buttonleds:
        isactive = buttonleds[name][pin].is_active

        if isactive:
            buttonpressed = name
            break

    if buttonpressed is not None:
        statusdata = list(buttonleds[buttonpressed])
        status = statusdata[itemstate]

        if status == 'on':
            status = 'off'
        elif status == 'off':
            status = 'on'

        buttonjson = {"action": "changestate", "button": buttonpressed, "status": status}
        buttontext = ujson.dumps(buttonjson, separators=(',', ':'))
        pscomms.sendData(buttontext)
        setleds(buttonpressed, status)

        response = None
        while response is None:
            response = pscomms.ReceiveData()


def getstatus():
    for name in buttonleds:
        datajson = {"action": "requeststatus", "button": name}
        datatext = ujson.dumps(datajson, separators=(',', ':'))
        pscomms.sendData(datatext)

        response = None
        while response is None:
            response = pscomms.ReceiveData()

        rjson = ujson.loads(response)

        if rjson['client'] == psconfig.thisdevice:
            payload = rjson['payload']

            button = payload['button']
            status = payload['status']
            setleds(button, status)


def initialise():
    for name in buttonleds:
        button = Button(psconfig.pinconvertion[buttonleds[name][0]])
        button.when_pressed = ispressed  # Event
        ledred = LED(psconfig.pinconvertion[buttonleds[name][1]])  # Red LED
        ledgreen = LED(psconfig.pinconvertion[buttonleds[name][2]])  # Green LED
        buttonleds[name] = (button, ledred, ledgreen, '')
        setleds(name, '')


initialise()
pscomms = pisquarecomms.PSComms(psconfig.wifi_ssid, psconfig.wifi_password, psconfig.controlserver,
                                psconfig.controlserverport, psconfig.thisdevice)
getstatus()

timestamp = utime.time()
refresh = psconfig.refresh

while True:
    pscomms.ReceiveData()
    utime.sleep(0.5)
    if utime.time() - timestamp > refresh:
        getstatus()
        timestamp = utime.time()
