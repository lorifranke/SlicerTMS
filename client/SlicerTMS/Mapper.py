import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import timeit

class Mapper:

    @staticmethod
    def map(loader, time=True):

        matrixFromFid = vtk.vtkMatrix4x4()
        loader.markupsPlaneNode.GetObjectToWorldMatrix(matrixFromFid)
        loader.transformNode.SetMatrixTransformToParent(matrixFromFid)
        loader.transformNode.UpdateScene(slicer.mrmlScene)


        if time:
            start = timeit.default_timer()

        # the update transform based on the old transfrom
        matrix_orig = vtk.vtkMatrix4x4()
        loader.magfieldNode.GetIJKToRASMatrix(matrix_orig)

        matrix_current = vtk.vtkMatrix4x4()
        matrix_current_inv = vtk.vtkMatrix4x4()

        loader.efieldNode.GetIJKToRASMatrix(matrix_current)
        matrix_current_inv.Invert(matrix_current, matrix_current_inv)

        matrix_update1 = vtk.vtkMatrix4x4()
        matrix_update1.Multiply4x4(matrix_orig, matrix_current_inv, matrix_update1)

        matrix_update2 = vtk.vtkMatrix4x4()
        matrix_update2.Multiply4x4(matrixFromFid, matrix_update1, matrix_update2)

        # loader.efieldNode.Copy(loader.magNode)
        loader.efieldNode.ApplyTransformMatrix(matrix_update2)



        # resample
        tfm_mov = vtk.vtkMatrix4x4()
        loader.efieldNode.GetIJKToRASMatrix(tfm_mov)
        tfm_mov_inv = vtk.vtkMatrix4x4()
        tfm_mov.Invert(tfm_mov, tfm_mov_inv)
        mov_img = loader.efieldNode.GetImageData()


        matrix_conductivity = vtk.vtkMatrix4x4()
        loader.conductivityNode.GetIJKToRASMatrix(matrix_conductivity)

        combined_tfm = vtk.vtkMatrix4x4()
        tfm_mov.Multiply4x4(tfm_mov_inv, matrix_conductivity, combined_tfm)


        conductivity_image = loader.conductivityNode.GetImageData()
        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(mov_img)
        reslice.SetInformationInput(conductivity_image)
        # print(reslice.SetInformationInput)
        reslice.SetInterpolationModeToLinear()
        reslice.SetResliceAxes(combined_tfm)
        reslice.TransformInputSamplingOff()
        reslice.Update()



        brainNode = slicer.util.getNode('gm')
        Mapper.mapElectricfieldToMesh(loader.efieldNode, brainNode)

        # time in seconds:
        if time:
            stop = timeit.default_timer()
            execution_time = stop - start
            print("Resampling + Mapping Executed in " + str(execution_time) + " seconds.")



    @staticmethod
    def mapElectricfieldToMesh(efieldNode, brainNode):

        # get the scalar range from image scalars
        rng = efieldNode.GetImageData().GetScalarRange()
        fMin = rng[0]
        fMax = rng[1]

        # Transform the model into the volume's IJK space
        modelTransformerRasToIjk = vtk.vtkTransformFilter()
        transformRasToIjk = vtk.vtkTransform()
        m = vtk.vtkMatrix4x4()
        efieldNode.GetRASToIJKMatrix(m)
        transformRasToIjk.SetMatrix(m)
        modelTransformerRasToIjk.SetTransform(transformRasToIjk)
        modelTransformerRasToIjk.SetInputConnection(brainNode.GetMeshConnection())

        probe = vtk.vtkProbeFilter()
        probe.SetSourceData(efieldNode.GetImageData())
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
        # select color scheme for scalars
        brainNode.GetDisplayNode().SetAndObserveColorNodeID(slicer.util.getNode('ColdToHotRainbow').GetID())
        brainNode.GetDisplayNode().ScalarVisibilityOn()
        brainNode.GetDisplayNode().SetScalarRange(fMin, fMax)




