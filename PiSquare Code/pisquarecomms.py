from machine import UART
import utime
import ujson


class PSComms:
    def __init__(self, ssid, password, controlserver, controlserverport, thisdevice):
        self.__uart = UART(1, 115200)  # Default Baud rate
        self.__ssid = ssid
        self.__password = password
        self.__controlserver = controlserver
        self.__controlserverport = controlserverport
        self.__thisdevice = thisdevice
        self.__thisdeviceip = ""

        print("Connecting to Wi-Fi")
        self.__wificonnect()
        print("Connected to Wi-Fi with IP address:", self.getipaddress)
        utime.sleep(1)
        print("Connecting to the control server:", self.__controlserver)
        self.__connectserver()
        print("Connected to server:", self.__controlserver)

    def __wificonnect(self):
        self.__uart.write('+++')
        utime.sleep(1)

        if self.__uart.any() > 0:
            self.__uart.read()

        self.__sendCMD("AT", "OK")
        self.__sendCMD("AT+CWMODE=3", "OK")
        self.__sendCMD("AT+CWJAP=\"" + self.__ssid + "\",\"" + self.__password + "\"", "OK", 20000)
        self.__thisdeviceip = self.__getipaddress()

    def __getipaddress(self):
        response = self.__sendCMD("AT+CIFSR", "OK")

        # Interpret the response from requesting an IP address
        res = str(response)[1:-1]
        split = res.split(",")
        split = split[3].replace('"', "")
        split = split.split("+")
        ipaddress = split[0][:-4]
        return ipaddress

    def __closeconnection(self):
        self.__sendCMD("AT+CIPCLOSE=1", "OK")

    def __connectserver(self):
        """ Try and connect to the server """
        while True:
            # Set up a TCP connection to the control server
            self.__sendCMD("AT+CIPSTART=\"TCP\",\"" + self.__controlserver + "\"," + self.__controlserverport, "OK",
                           10000)
            self.__sendCMD("AT+CIPMODE=1", "OK")  # Use Wi-Fi connection
            ack = self.__sendCMD("AT+CIPSEND", ">")  # About to send data
            if ack:
                break

    def __sendCMD(self, cmd, ack, timeout=2000):
        self.__uart.write(cmd + '\r\n')
        lst = []
        t = utime.ticks_ms()
        while (utime.ticks_ms() - t) < timeout:
            acknowledgement = self.__uart.read()
            if acknowledgement is not None:
                acknowledgement = acknowledgement.decode()
                # if the IP address is being requested, store the data
                if cmd == "AT+CIFSR":
                    lst.append(acknowledgement)

                # If the expected response comes back, return the data
                if acknowledgement.find(ack) >= 0:
                    if not lst:
                        return True
                    else:
                        return lst
        return False

    @property
    def getipaddress(self):
        return self.__thisdeviceip

    def sendData(self, data):
        payload = ujson.loads(data)
        datajson = {"client": self.__thisdevice, "payload": payload}
        print(datajson)
        datatext = ujson.dumps(datajson, separators=(',', ':'))

        self.__uart.write(datatext.encode())

    def ReceiveData(self):
        data = self.__uart.read()

        if data is not None:
            data = data.decode()
            print(data)
            return data
        return None
