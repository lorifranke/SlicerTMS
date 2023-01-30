import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
from vtk.util.numpy_support import numpy_to_vtk
import timeit

class Mapper():

    @staticmethod
    def map(loader, time=True):

        matrixFromFid = vtk.vtkMatrix4x4()
        loader.markupsPlaneNode.GetObjectToWorldMatrix(matrixFromFid)
        loader.transformNode.SetMatrixTransformToParent(matrixFromFid)
        loader.transformNode.UpdateScene(slicer.mrmlScene)


        if time:
            start = timeit.default_timer()

        # the update transform based on the old transfrom

        
        # rotate the scalar magnetic field (magnorm)

        # if loader.showMag:  #only show scalar magnetic (magnorm) field
        #     matrix_current = vtk.vtkMatrix4x4()
        #     matrix_current_inv = vtk.vtkMatrix4x4()
        #     loader.magnormNode.GetIJKToRASMatrix(matrix_current)
        #     matrix_current_inv.Invert(matrix_current, matrix_current_inv)
        #     matrix_update1 = vtk.vtkMatrix4x4()
        #     matrix_update1.Multiply4x4(loader.coilDefaultMatrix, matrix_current_inv, matrix_update1)
        #     matrix_update2 = vtk.vtkMatrix4x4()
        #     matrix_update2.Multiply4x4(matrixFromFid, matrix_update1, matrix_update2)
        #     # loader.efieldNode.Copy(loader.magNode)
        #     loader.magnormNode.ApplyTransformMatrix(matrix_update2)
        #     Mapper.mapElectricfieldToMesh(loader.magnormNode, loader.modelNode)

        # else:  #predict the E-field and show the scalar E-field

        DataVec = loader.magfieldGTNode.GetTransformFromParent().GetDisplacementGrid()
        DataVec.SetOrigin(0, 0, 0)
        DataVec.SetSpacing(1, 1, 1)


        matrix_current = vtk.vtkMatrix4x4() # current transform of the magnetic vector field
        matrix_current.Multiply4x4(matrixFromFid, loader.coilDefaultMatrix, matrix_current)

        matrix_current_inv = vtk.vtkMatrix4x4()
        matrix_current_inv.Invert(matrix_current,matrix_current_inv)
        combined_tfm = vtk.vtkMatrix4x4()

        matrix_ref = vtk.vtkMatrix4x4()
        loader.conductivityNode.GetIJKToRASMatrix(matrix_ref)
        img_ref = loader.conductivityNode.GetImageData()

        matrix_ref.Multiply4x4(matrix_current_inv, matrix_ref, combined_tfm)


        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(DataVec)
        reslice.SetInformationInput(img_ref)
        reslice.SetInterpolationModeToLinear()
        reslice.SetResliceAxes(combined_tfm)
        reslice.TransformInputSamplingOff()
        reslice.Update()
        DataOut = reslice.GetOutput()

        xyz = DataOut.GetDimensions()
        
        # # rotate DataOut vectors
        DataOut_np = vtk_to_numpy(DataOut.GetPointData().GetScalars())
        # # transposed of the rotation matrix
        RotMat_transp = np.array([[matrixFromFid.GetElement(0,0), matrixFromFid.GetElement(1,0),  matrixFromFid.GetElement(2,0)],
                                   [matrixFromFid.GetElement(0,1), matrixFromFid.GetElement(1,1),  matrixFromFid.GetElement(2,1)],
                                   [matrixFromFid.GetElement(0,1), matrixFromFid.GetElement(1,1),  matrixFromFid.GetElement(2,1)]])
        # # rotate the vector field
        DataOut_np_rot = np.matmul(DataOut_np, RotMat_transp)
        # # reshape the numpy array
        DataOut_np_rot = np.reshape(DataOut_np_rot,(xyz[0], xyz[1], xyz[2], 3))
        VTK_array = numpy_to_vtk(DataOut_np_rot.ravel(), deep=True, array_type=vtk.VTK_DOUBLE)
        DataOut.GetPointData().SetScalars(VTK_array)
        DataOut.GetPointData().GetScalars().SetNumberOfComponents(3)

        loader.magfieldNode.SetAndObserveImageData(DataOut)
    
        loader.IGTLNode.PushNode(loader.magfieldNode)


        # time in seconds:
        if time:
            stop = timeit.default_timer()
            execution_time = stop - start
            print("Resampling + Mapping Executed in " + str(execution_time) + " seconds.")



    @staticmethod
    def mapElectricfieldToMesh(scalarNode, brainNode):

        # get the scalar range from image scalars
        rng = scalarNode.GetImageData().GetScalarRange()
        fMin = rng[0]
        fMax = rng[1]

        # Transform the model into the volume's IJK space
        modelTransformerRasToIjk = vtk.vtkTransformFilter()
        transformRasToIjk = vtk.vtkTransform()
        m = vtk.vtkMatrix4x4()
        scalarNode.GetRASToIJKMatrix(m)
        transformRasToIjk.SetMatrix(m)
        modelTransformerRasToIjk.SetTransform(transformRasToIjk)
        modelTransformerRasToIjk.SetInputConnection(brainNode.GetMeshConnection())

        probe = vtk.vtkProbeFilter()
        probe.SetSourceData(scalarNode.GetImageData())
        probe.SetInputConnection(modelTransformerRasToIjk.GetOutputPort())
        # transform model back to ras
        modelTransformerIjkToRas = vtk.vtkTransformFilter()
        modelTransformerIjkToRas.SetTransform(transformRasToIjk.GetInverse())
        modelTransformerIjkToRas.SetInputConnection(probe.GetOutputPort())
        modelTransformerIjkToRas.Update()


        brainNode.SetAndObserveMesh(modelTransformerIjkToRas.GetOutput())

        probedPointScalars = probe.GetOutput().GetPointData().GetScalars()

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(probe.GetOutputPort())

        # activate scalars
        brainNode.GetDisplayNode().SetActiveScalarName('ImageScalars')
        ### if fiber bundle, then scalars need to be set different:
        fibers = slicer.util.getNode('fibers')
        fibers.GetDisplayNode().SetColorMode(fibers.GetDisplayNode().colorModeScalarData)
        fibers.GetDisplayNode().SetAndObserveColorNodeID(slicer.util.getNode('ColdToHotRainbow').GetID())
        # # We only want to see the lines of the fibers first, not the tubes:
        fibers.GetTubeDisplayNode().SetVisibility(False)
        # select color scheme for scalars
        brainNode.GetDisplayNode().SetAndObserveColorNodeID(slicer.util.getNode('ColdToHotRainbow').GetID())
        brainNode.GetDisplayNode().ScalarVisibilityOn()
        brainNode.GetDisplayNode().SetScalarRange(fMin, fMax)
        # color legend for brain scalars:
        colorLegendDisplayNode = slicer.modules.colors.logic().AddDefaultColorLegendDisplayNode(brainNode)
        colorLegendDisplayNode.SetTitleText("EVec")
        colorLegendDisplayNode.SetLabelFormat("%7.8f")


    @staticmethod
    def modifyIncomingImage(loader):
        matrix_ref = vtk.vtkMatrix4x4()
        loader.conductivityNode.GetIJKToRASMatrix(matrix_ref)
        loader.pyigtlNode.ApplyTransformMatrix(matrix_ref)
        # this part will need to be done with the resampling (it only maps the incoming pyigtl image to the brain):
        Mapper.mapElectricfieldToMesh(loader.pyigtlNode, loader.modelNode)
        Mapper.mapElectricfieldToMesh(loader.pyigtlNode, loader.fiberNode)

