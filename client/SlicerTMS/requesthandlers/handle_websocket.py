import json
import sys
import time
import numpy
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

try:
    import urlparse
except ImportError:
    import urllib


    class urlparse(object):
        urlparse = urllib.parse.urlparse
        parse_qs = urllib.parse.parse_qs

from typing import Union, Optional, Awaitable
from tornado.websocket import WebSocketHandler
from requesthandlers import header_builder
import sys
sys.path.append('..')


class SlicerWebSocketHandler(WebSocketHandler):
    def logMessage(self, message):
        print(message)

    def check_origin(self, origin):
        return True

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        return super().open(*args, **kwargs)

    def on_close(self) -> None:
        super().on_close()

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        # print("Coil Position Matrix:")
        # self.logMessage(message)
        self.on_pose(message)
        if message == 'get_coil_position':
            # you can access slicer code here
            self.write_message('1.2323 3.34324 5.34324')

    def on_pose(self, message):
        p = urlparse.urlparse(message)
        q = urlparse.parse_qs(p.query)
        try:
            transformMatrix = list(map(float, q['m'][0].split(',')))
        except KeyError:
            transformMatrix = None
        try:
            quaternion = list(map(float, q['q'][0].split(',')))
        except KeyError:
            quaternion = None
        try:
            position = list(map(float, q['p'][0].split(',')))
        except KeyError:
            position = None

        # slicer.util.getNode('vtkMRMLMarkupsPlaneNode1').SetDisplayVisibility(0)
        nodes = slicer.mrmlScene.GetNodesByName('tracker')
        if nodes.GetNumberOfItems() > 0:
            # self.coil = slicer.util.getNode('fig8coil')
            self.coil = slicer.util.getNode('vtkMRMLMarkupsPlaneNode1')
            self.tracker = nodes.GetItemAsObject(0)
        else:
            self.tracker = slicer.vtkMRMLLinearTransformNode()
            self.tracker.SetName('tracker')
            slicer.mrmlScene.AddNode(self.tracker)
            # self.coil = slicer.util.getNode('fig8coil')
            self.coil = slicer.util.getNode('vtkMRMLMarkupsPlaneNode1')
            self.coil.SetAndObserveTransformNodeID(self.tracker.GetID())
        m = vtk.vtkMatrix4x4()
        self.tracker.GetMatrixTransformToParent(m)
        # self.markup.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.onHandlesModified)
        # every time the transform changes execute show evec

        if transformMatrix:
            for row in range(3):
                for column in range(3):
                    m.SetElement(row, column, transformMatrix[3 * row + column])
                    m.SetElement(row, column, transformMatrix[3 * row + column])
                    m.SetElement(row, column, transformMatrix[3 * row + column])

        if position:
            for row in range(3):
                m.SetElement(row, 3, position[row])

        if quaternion:
            qu = vtk.vtkQuaternion['float64']()
            qu.SetW(quaternion[0])
            qu.SetX(quaternion[1])
            qu.SetY(quaternion[2])
            qu.SetZ(quaternion[3])
            m3 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            qu.ToMatrix3x3(m3)
            for row in range(3):
                for column in range(3):
                    m.SetElement(row, column, m3[row][column])

        self.tracker.SetMatrixTransformToParent(m)
        # this method needs to be called to update the efield on the brain:
        slicer.modules.SlicerTMSWidget.onHandlesModified()
        # slicer still crashes when the method is called!
