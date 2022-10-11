import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *


class tms(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Slicer TMS Module"
        self.parent.categories = ["TMS"]
        self.parent.dependencies = []
        self.parent.contributors = [""]
        self.parent.helpText = ""
        self.parent.acknowledgementText = ""
        self.parent = parent


class tmsWidget(ScriptedLoadableModuleWidget):
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.guiMessages = True
        self.consoleMessages = True

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # self.logic = tmsLogic(logMessage=self.logMessage)

        self.collapsibleButton = ctk.ctkCollapsibleButton()
        self.collapsibleButton.text = "TMS Process"
        self.layout.addWidget(self.collapsibleButton)
        self.formLayout = qt.QFormLayout(self.collapsibleButton)

        self.fiducialButton = qt.QPushButton("1. (Re)Start", self.collapsibleButton)
        self.formLayout.addRow(self.fiducialButton)
        self.fiducialButton.clicked.connect(onLoadButton)

        self.evecButton = qt.QPushButton("Show Evec", self.collapsibleButton)
        self.formLayout.addRow(self.evecButton)
        # self.evecButton.clicked.connect(self.onEvecButton)

        # disable OPENIGT tracker for now/testing
        # self.connectButton = qt.QPushButton("2. Start Tracker", self.collapsibleButton)
        # self.formLayout.addRow(self.connectButton)
        # self.connectButton.clicked.connect(self.onOpenIGTLLinkStart)
        #
        # self.trackerStartedButton = qt.QPushButton("3. Apply transform", self.collapsibleButton)
        # self.formLayout.addRow(self.trackerStartedButton)
        # self.trackerStartedButton.clicked.connect(self.onTrackerHasStarted)

        self.initialScalarArray = None

        self.layout.addStretch(1)

        self.collapsibleButton2 = ctk.ctkCollapsibleButton()
        self.collapsibleButton2.text = "WebServer"
        self.layout.addWidget(self.collapsibleButton2)
        self.formLayout2 = qt.QFormLayout(self.collapsibleButton2)

        # start button
        self.startServerButton = qt.QPushButton("Start Server")
        self.startServerButton.toolTip = "Start web server with the selected options."
        self.formLayout2.addRow(self.startServerButton)
        # self.startServerButton.connect('clicked()', self.logic.start)
        # replace logic with server stuff

        # stop button
        self.stopServerButton = qt.QPushButton("Stop Server")
        self.stopServerButton.toolTip = "Stop web server"
        self.formLayout2.addRow(self.stopServerButton)
        # self.stopServerButton.connect('clicked()', self.logic.stop)

        # open browser page
        self.localConnectionButton = qt.QPushButton("Open static page in external browser")
        self.localConnectionButton.toolTip = "Open a connection to the server on the local machine with your system browser."
        self.formLayout2.addRow(self.localConnectionButton)
        # self.localConnectionButton.connect('clicked()', self.openLocalConnection)

        self.log = qt.QTextEdit()
        self.log.readOnly = True
        self.formLayout2.addRow(self.log)
        self.logMessage('<p>Status: <i>Idle</i>\n')