import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import sys
import Loader as L
import SlicerWebServer as W


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
        self.websv = W.SlicerWebServer(logMessage=self.logMessage)

        # IGTL connections
        self.IGTLNode = slicer.vtkMRMLIGTLConnectorNode()
        slicer.mrmlScene.AddNode(self.IGTLNode)
        self.IGTLNode.SetName('TextConnector')
        self.IGTLNode.SetTypeClient('localhost', 18945)
        # this will activate the the status of the connection:
        self.IGTLNode.Start()
        # self.IGTLNode.RegisterIncomingMRMLNode(self.textNode)
        self.IGTLNode.PushOnConnect()

        self.textNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTextNode', 'TextMessage')
        self.textNode.SetForceCreateStorageNode(True)
        observer = self.textNode.AddObserver(slicer.vtkMRMLTextNode.TextModifiedEvent, self.newText)

    def newText(self, caller, event):
        self.t = slicer.mrmlScene.GetNodeByID('vtkMRMLTextNode1')
        self.example_path = self.t.GetText()
        self.setupButtons(self.example_path)

    def setupButtons(self, example_path):
        self.collapsibleButton = ctk.ctkCollapsibleButton()
        self.collapsibleButton.text = "TMS Visualization"
        self.layout.addWidget(self.collapsibleButton)
        self.formLayout = qt.QFormLayout(self.collapsibleButton)
        
        slicer.modules.tractographydisplay.widgetRepresentation().activateWindow()
        self.loadExampleButton = qt.QPushButton("Load Example", self.collapsibleButton)
        self.formLayout.addRow(self.loadExampleButton)
        # we need to pass the selected example from the command line with the example path:
        self.loadExampleButton.clicked.connect(lambda: L.Loader.loadExample(self.example_path))

        self.fiberButton = qt.QCheckBox("Show Fibers", self.collapsibleButton)
        # self.fiberButton.checked = False
        self.formLayout.addRow(self.fiberButton)
        self.fiberButton.stateChanged.connect(L.Loader.showFibers)

        self.initialScalarArray = None

        self.layout.addStretch(1)


        ### WEBSERVER ####
        self.collapsibleButton2 = ctk.ctkCollapsibleButton()
        self.collapsibleButton2.text = "WebServer"
        self.layout.addWidget(self.collapsibleButton2)
        self.formLayout2 = qt.QFormLayout(self.collapsibleButton2)

        # start button
        self.startServerButton = qt.QPushButton("Start Server")
        self.startServerButton.toolTip = "Start web server with the selected options."
        self.formLayout2.addRow(self.startServerButton)
        self.startServerButton.clicked.connect(self.websv.start)

        # # stop button
        self.stopServerButton = qt.QPushButton("Stop Server")
        self.stopServerButton.toolTip = "Stop web server"
        self.formLayout2.addRow(self.stopServerButton)
        self.stopServerButton.connect('clicked()', self.websv.stop)

        # open browser page
        self.localConnectionButton = qt.QPushButton("Open static page in external browser")
        self.localConnectionButton.toolTip = "Open a connection to the server on the local machine with your system browser."
        self.formLayout2.addRow(self.localConnectionButton)
        self.localConnectionButton.connect('clicked()', self.websv.openLocalConnection)

        self.log = qt.QTextEdit()
        self.log.readOnly = True
        self.formLayout2.addRow(self.log)
        # self.logMessage('<p>Status: <i>Idle</i>\n')


    def logMessage(self, *args):
        if self.consoleMessages:
            for arg in args:
                print(arg)
        if self.guiMessages:
            if len(self.log.html) > 1024 * 256:
                self.log.clear()
                self.log.insertHtml("Log cleared\n")
            for arg in args:
                self.log.insertHtml(arg)
            self.log.insertPlainText('\n')
            self.log.ensureCursorVisible()
            self.log.repaint()

