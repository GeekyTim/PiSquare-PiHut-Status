from lib import tplink, hue
import json


class PiHutStatus:
    def __init__(self, name, definition):
        self.__name = name
        self.__thisclient = []

        for item in definition:
            itemdef = definition[item]
            itemtype = itemdef['type']
            itemclass = None

            if itemtype == 'tplink':
                itemclass = tplink.TPLink(itemdef['psalias'], itemdef['host'])
            elif itemtype == 'hue':
                itemclass = hue.Hue(itemdef['host'], itemdef['psalias'])

            self.__thisclient.append((itemdef['psalias'], itemdef['host'], itemclass))

    def handlerequest(self, payload):
        print("handling request", payload)
        action = payload['action']
        button = payload['button']
        response = None

        if action == 'requeststatus':
            itemstatus = self.getstatus(button)
            print(button, itemstatus)
            if itemstatus is not None:
                response = json.dumps({"client": self.__name, "payload": {"button": button, "status": itemstatus}},
                                      separators=(',', ':'))

        elif action == 'changestate':
            itemstatus = payload['status']
            if itemstatus == '':  # The status is not known yet
                self.setstatus(button, 'toggle')
                itemstatus = self.getstatus(button)
            else:
                self.setstatus(button, itemstatus)

            response = json.dumps({"client": self.__name, "payload": {"button": button, "status": itemstatus}},
                                  separators=(',', ':'))

        return response

    def getstatus(self, itemname):
        itemstatus = None

        for item in self.__thisclient:
            if item[0] == itemname:
                itemstatus = item[2].getstatus
                break

        return itemstatus

    def setstatus(self, button, status):
        for item in self.__thisclient:
            if item[0] == button:
                if status == 'on':
                    item[2].turnon()
                elif status == 'off':
                    item[2].turnoff()
                else:
                    item[2].toggle()
                break
