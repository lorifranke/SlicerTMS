import os
import socket
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import numpy as np
from requesthandlers import *
from slicerserver.server import Server

secure = False


class SlicerWebServer:
    def __init__(self, logMessage=None):
        if not logMessage:
            pass
        else:
            self.logMessage = logMessage
        self.port = 2016
        self.server = None
        self.logFile = '/tmp/WebServerLogic.log'
        # self.docroot = "/Users/lorainefranke/Documents/github/SlicerTMS/client/SlicerTMS/docroot"
        self.docroot = os.path.join(os.path.dirname(slicer.modules.slicertms.path), './docroot')
        # self.docroot = data_directory.encode('utf-8')

    def start(self):
        # webserver = SlicerWebServer()
        global secure
        """Setting up the webserver"""
        self.stop()
        self.port = Server.findFreePort(self.port)
        self.logMessage("Starting server on port %d" % self.port)
        self.logMessage('docroot: %s' % self.docroot)
        authpath = (os.path.join(os.path.dirname(slicer.modules.slicertms.path), './auth')).encode('utf-8')
        try:
            t = open(authpath + b"/cert.pem")
            t = open(authpath + b"/key.pem")
            certfile = authpath + b"/cert.pem"
            keyfile = authpath + b"/key.pem"
            secure = True
            t = None
        except FileNotFoundError:
            print("No Certificate/Key found, server will run in insecure mode")
            certfile = None
            keyfile = None
        except:
            print("Unknown error, server will run in insecure mode")
            certfile = None
            keyfile = None
        self.server = Server(docroot=self.docroot, server_address=("", self.port), logFile=self.logFile, logMessage=self.logMessage, certfile=certfile, keyfile=keyfile)
        self.server.start()
        # return webserver

    def logMessage(self, *args):
        for arg in args:
            print("Logic: " + arg)

    def stop(self):
        if self.server:
            self.server.stop()

    @staticmethod
    def openLocalConnection():
        if secure:
            qt.QDesktopServices.openUrl(qt.QUrl('https://localhost:2016'))
        else:
            qt.QDesktopServices.openUrl(qt.QUrl('http://localhost:2016'))



