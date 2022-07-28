#!/usr/bin/python3

from phue import Bridge

dimmable = "Dimmable light"
colour = "Extended color light"


class Hue:
    """
    Controls the Hue Lights
    """

    def __init__(self, bridge, lampname):
        """
        IMPORTANT: If running for the first time:
            Uncomment the self.__bridge.connect() line
            Press item on bridge
            Run the code
        This will save your connection details in ~/.python_hue
        Delete that file if you change bridges

        Type of Lights handled:
            Extended color light
            Dimmable light

        param bridge:
        param lampname:
        return:
        """
        self.__lampname = lampname
        self.__lampstatus = None

        # Connect to the bridge
        try:
            self.__bridge = Bridge(bridge)
            # self.__bridge.connect()  # Uncomment to connect to the bridge <<<<<<<<<<
        except:
            print("Unable to connect to the bridge")
            exit()

        alllights = self.__bridge.get_light_objects('name')

        if lampname in alllights:
            lights = self.__bridge.get_light(self.__lampname)
            self.__lamptype = lights['type']
        else:
            print("Error: Lamp unknown")
            exit()

        self.getstatus

    def _getstatus(self):
        """
        Get the status of a room BEFORE the alert is set, so it can be returned to that state
        """
        lampjson = self.__bridge.get_light(self.__lampname)

        if lampjson['state']['on']:
            self.__lampstatus = 'on'
        else:
            self.__lampstatus = 'off'

        return self.__lampstatus

    def _switch(self, status):
        setstatus = False
        if status == 'toggle':
            if self._getstatus() == 'off':
                setstatus = True
        elif status == 'on':
            setstatus = True

        if self.__lamptype == dimmable:
            self._switch_dimmable(setstatus)
        elif self.__lamptype == colour:
            self._switch_colour(setstatus)

    def _switch_dimmable(self, status):
        self.__bridge.set_light(self.__lampname, {'transitiontime': 0, 'on': status, 'bri': 254})

    def _switch_colour(self, status):
        self.__bridge.set_light(self.__lampname, {'transitiontime': 0, 'on': status, 'hue': 0, 'sat': 0, 'bri': 254})

    @property
    def getname(self):
        return self.__lampname

    @property
    def getstatus(self):
        return self._getstatus()

    def turnon(self):
        return self._switch('on')

    def turnoff(self):
        return self._switch('off')

    def toggle(self):
        return self._switch('toggle')
