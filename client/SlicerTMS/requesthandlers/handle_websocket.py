import json
import sys
import time
import numpy
import json
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util import numpy_support
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import zlib
import base64


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

    def on_message(self, message):
        # print("Coil Position Matrix:")
        # self.logMessage(message)
        # self.on_pose(message)
        if message == "get_node":
            self.on_get_node(message)
        else:
            self.on_pose(message)
        # if message == 'get_coil_position':
        #     # you can access slicer code here
        #     self.write_message('1.2323 3.34324 5.34324')

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

        print('accessing markupsplane node now')
        # slicer.util.getNode('vtkMRMLMarkupsPlaneNode1').SetDisplayVisibility(0)
        nodes = slicer.mrmlScene.GetNodesByName('tracker')
        if nodes.GetNumberOfItems() > 0:
            self.coilfid = slicer.util.getNode('vtkMRMLMarkupsPlaneNode1')
            self.coilfid.SetOrigin([0, 0, 0]) # need to reset the position because in the loader with set the coil to [0, 0, 110] as default
            self.tracker = nodes.GetItemAsObject(0)
        else:
            self.tracker = slicer.vtkMRMLLinearTransformNode()
            self.tracker.SetName('tracker')
            slicer.mrmlScene.AddNode(self.tracker)
            self.coilfid = slicer.util.getNode('vtkMRMLMarkupsPlaneNode1')
            self.coilfid.SetOrigin([0, 0, 0]) # need to reset the position because in the loader with set the coil to [0, 0, 110] as default
            self.coilfid.SetAndObserveTransformNodeID(self.tracker.GetID())
            # self.coil = slicer.modules.models.logic().GetMRMLScene().GetNodesByName('coil') # this is the 3d coil model
            self.coil = slicer.util.getNode('coil')
            self.coil.SetAndObserveTransformNodeID(self.tracker.GetID())
            print('tracking the coil!')

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
        # slicer.modules.SlicerTMSWidget.onHandlesModified()
        # slicer.modules.slicertms.onHandlesModified()


    def on_get_node(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        print('CALLED GETNODE!')
        self.gm = slicer.util.getNode('gm')
        polyData = self.gm.GetPolyData()

        # Create a vtkPolyDataWriter object
        writer = vtk.vtkPolyDataWriter()

        # Set the input data to the polydata
        writer.SetInputData(polyData)

        # Write the binary data directly to a string
        writer.WriteToOutputStringOn()

        # Write the binary data
        writer.Write()

        # Get the binary data as a string
        binary_data = writer.GetOutputString()
        
        # Convert binary_data to bytes
        binary_data = bytes(binary_data, 'utf-8')

        self.write_message(binary_data)

        # # Compress the binary data using zlib
        # compressed_data = zlib.compress(binary_data)

        # # Encode the compressed data to a string
        # encoded_data = base64.b64encode(compressed_data)

        # # Send the encoded data through the websocket
        # self.write_message(encoded_data)



        ### APPROACH 1:
        # # Create a vtkJSONWriter object
        # writer = vtk.vtkJSONDataSetWriter()
        # # Set the input data to the polydata
        # writer.SetInputData(polyData)
        # # Update the writer
        # writer.Update() # this makes slicer crash
        # # Get the output data
        # output = writer.GetOutput()
        # # Convert the vtkDataObject to a python dictionary
        # data = json.loads(output.toJSON())
        # # Print the JSON data
        # print(json.dumps(data))


        ######## APPROACH 2:
        # # Convert vtkPolyData to vtkTable
        # polyDataToTable = vtk.vtkPolyDataToTable()
        # polyDataToTable.SetInputData(polyData)
        # polyDataToTable.Update()

        # table = polyDataToTable.GetOutput()

        # # Write vtkTable to JSON file with compression
        # jsonWriter = vtk.vtkJSONDataSetWriter()
        # jsonWriter.SetInputData(table)
        # jsonWriter.SetCompression(True)
        # jsonWriter.WriteToOutputStringOn()
        # jsonWriter.Update()
        # json_string = jsonWriter.GetOutputString()
        # json_data = json.loads(json_string)
        # print(json_data)
        # self.write_message(json_data)

        #### APPROACH 3 with downsampling:

        # self.gm = slicer.util.getNode('gm')
        # mesh_data = self.gm.GetPolyData() # Get the mesh data from the mesh node
        # # downsample the mesh before sending it
        # decimate = vtk.vtkDecimatePro()
        # decimate.SetInputData(mesh_data)
        # decimate.SetTargetReduction(0.9) # set the target reduction factor to 0.9
        # decimate.Update()
        # decimated_mesh = decimate.GetOutput()
        # points = decimated_mesh.GetPoints().GetData()
        # points_np = vtk_to_numpy(points)
        # cells = decimated_mesh.GetPolys().GetData()
        # cells_np = vtk_to_numpy(cells)
        # json_mesh = json.dumps({"points":points_np.tolist(),"cells":cells_np.tolist()})
        # print(json_mesh)
        # self.write_message(json_mesh)



