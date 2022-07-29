import socket
import asyncio
from kasa import SmartPlug


class TPLink:
    def __init__(self, alias, plugname):
        self.__plug = None
        self.__alias = alias

        try:
            ipaddress = socket.gethostbyname(plugname)
            self.__plug = SmartPlug(ipaddress)
        except Exception as e:
            print(f"Unable to connect to {plugname}: {e}")

        self.loop = asyncio.get_event_loop()

    async def _getstatus(self):
        await self.__plug.update()  # Request the update

        if self.__plug.is_on:
            status = 'on'
        else:
            status = 'off'

        return status

    async def _switch(self, status):
        await self.__plug.update()  # Request the update

        if status == 'on':
            await self.__plug.turn_on()
        elif status == 'off':
            await self.__plug.turn_off()
        elif status == 'toggle':
            if self.__plug.is_on:
                await self.__plug.turn_off()
            else:
                await self.__plug.turn_on()

    async def _name(self):
        await self.__plug.update()
        return self.__plug.alias

    @property
    def getname(self):
        return self.loop.run_until_complete(self._name())

    @property
    def getstatus(self):
        return self.loop.run_until_complete(self._getstatus())

    def turnon(self):
        return self.loop.run_until_complete(self._switch('on'))

    def turnoff(self):
        return self.loop.run_until_complete(self._switch('off'))

    def toggle(self):
        return self.loop.run_until_complete(self._switch('toggle'))
