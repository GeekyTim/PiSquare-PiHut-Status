#!/usr/bin/env python3

import toml

from lib import pslistener, pihutstatus


def startserver():
    clientlist = {}

    configuration = toml.load("configs/configuration.toml")
    listeningport = configuration['port']

    for client in configuration['clients']:
        hat = configuration['clients'][client]['hat']
        clientdef = configuration['clients'][client]['io']

        hatclass = None

        if hat == 'PiHut-Status':
            hatclass = pihutstatus.PiHutStatus(hat, clientdef)

        clientlist[hat] = hatclass

    listener = pslistener.PSListener("", listeningport, clientlist)
    listener.start()


if __name__ == "__main__":
    startserver()
