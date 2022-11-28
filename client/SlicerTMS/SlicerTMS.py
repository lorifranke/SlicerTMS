import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import Loader as L
import Mapper as M


class SlicerTMS(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Slicer TMS Module"
        self.parent.categories = ["TMS"]
        self.parent.dependencies = []
        self.parent.contributors = [""]
        self.parent.helpText = ""
        self.parent.acknowledgementText = ""
        self.parent = parent


class SlicerTMSWidget(ScriptedLoadableModuleWidget):
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.guiMessages = True
        self.consoleMessages = True
        self.showGMButton = None


    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        # self.logic = tmsLogic(logMessage=self.logMessage)

        self.collapsibleButton = ctk.ctkCollapsibleButton()
        self.collapsibleButton.text = "TMS Visualization"
        self.layout.addWidget(self.collapsibleButton)
        self.formLayout = qt.QFormLayout(self.collapsibleButton)

        # script_path = os.path.dirname(os.path.abspath(__file__))
        # client_path = os.path.join(script_path, '../../server/server.py')

        self.loadExampleButton = qt.QPushButton("1. Load Example", self.collapsibleButton)
        self.formLayout.addRow(self.loadExampleButton)
        self.loadExampleButton.clicked.connect(L.Loader.loadExample1)

        # self.loadExampleButton2 = qt.QPushButton("Load Example 2", self.collapsibleButton)
        # self.formLayout.addRow(self.loadExampleButton2)
        # # param1 = True
        # # self.loadExampleButton2.clicked.connect(lambda: L.Loader.loadExample2(self,param1))
        # self.loadExampleButton2.clicked.connect(L.Loader.loadExample2)

        self.showGMButton = qt.QCheckBox("Show Brain Surface", self.collapsibleButton)
        self.showGMButton.checked = True
        self.formLayout.addRow(self.showGMButton)

        # self.fiberButton = qt.QCheckBox("Show Fibers", self.collapsibleButton)
        # # self.fiberButton.checked = True
        # self.formLayout.addRow(self.fiberButton)
        # self.fiberButton.stateChanged.connect(L.Loader.loadFibers)


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
        # self.logMessage('<p>Status: <i>Idle</i>\n')

