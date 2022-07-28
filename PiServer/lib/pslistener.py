import json
import selectors
import socket
import threading
import types


class PSListener(threading.Thread):
    def __init__(self, devicename, port, clientlist):
        self.__devicename = devicename
        self.__port = port
        self.__clientlist = clientlist

        self.__selector = selectors.DefaultSelector()

        self.__listeningsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__listeningsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse socket
        self.__listeningsocket.bind(("", self.__port))
        self.__listeningsocket.listen()
        self.__listeningsocket.setblocking(False)
        self.__selector.register(self.__listeningsocket, selectors.EVENT_READ, data=None)

        # print(self.__clientlist)
        # print(f"Listening on {self.__port}")

        super(PSListener, self).__init__()

    def run(self):
        try:
            while True:
                events = self.__selector.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.__accept_connection(key.fileobj)
                    else:
                        self.__client_handler(key, mask)

        except Exception as ex:
            print(f"Something terrible has happened. {ex}. Exiting.")
        finally:
            self.__selector.close()

    def __client_handler(self, key, mask):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read

            if recv_data:
                messagestr = recv_data.decode()
                messagereceived = json.loads(messagestr)
                client = messagereceived['client']

                if client in self.__clientlist:
                    payload = messagereceived['payload']
                    response = self.__clientlist[client].handlerequest(payload)
                    if response is not None:
                        data.outb = response
                        mask = selectors.EVENT_WRITE
            else:
                # print(f"Closing connection to {data.addr}")
                self.__selector.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb.encode())  # Should be ready to write
                data.outb = data.outb[sent:]

    def __accept_connection(self, serversocket):
        connection, address = serversocket.accept()  # Should be ready to read
        # print(f"Accepted connection from {address}")
        connection.setblocking(False)
        data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.__selector.register(connection, events, data=data)
