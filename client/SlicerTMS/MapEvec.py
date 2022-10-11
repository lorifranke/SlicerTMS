import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *


class MapEvec:

    def __init__(self):
        '''
        '''
        pass

    def onHandlesModified(self, param1=None, param2=None):
        matrixFromFid = vtk.vtkMatrix4x4()
        self.markupFiducials.GetObjectToWorldMatrix(matrixFromFid)
        self.transformNode.SetMatrixTransformToParent(matrixFromFid)
        self.transformNode.UpdateScene(slicer.mrmlScene)

        if self.showField:
            start = timeit.default_timer()

            # the update transform based on the old transfrom
            matrix_ref = vtk.vtkMatrix4x4()
            self.magNode.GetIJKToRASMatrix(matrix_ref)

            matrix_current = vtk.vtkMatrix4x4()
            matrix_current_inv = vtk.vtkMatrix4x4()

            self.EfieldNode.GetIJKToRASMatrix(matrix_current)
            matrix_current_inv.Invert(matrix_current, matrix_current_inv)

            matrix_update1 = vtk.vtkMatrix4x4()
            matrix_update1.Multiply4x4(matrix_ref, matrix_current_inv, matrix_update1)

            matrix_update2 = vtk.vtkMatrix4x4()
            matrix_update2.Multiply4x4(matrixFromFid, matrix_update1, matrix_update2)

            # self.EfieldNode.Copy(self.magNode)
            self.EfieldNode.ApplyTransformMatrix(matrix_update2)

            tfm_mov = vtk.vtkMatrix4x4()
            self.EfieldNode.GetIJKToRASMatrix(tfm_mov)

            mov_img = self.EfieldNode.GetImageData()

            tfm_ref = vtk.vtkMatrix4x4()
            self.refNode.GetIJKToRASMatrix(tfm_ref)
            combined_tfm = vtk.vtkMatrix4x4()
            tfm_mov_inv = vtk.vtkMatrix4x4()
            tfm_mov.Invert(tfm_mov, tfm_mov_inv)
            tfm_mov.Multiply4x4(tfm_mov_inv, tfm_ref, combined_tfm)

            brain = slicer.util.getNode('gm')

            # self.EevecNode.Copy(self.EvecNode_orig)
            self.EevecNode.ApplyTransformMatrix(matrix_update2)

            # reslice image

            ref_img = self.refNode.GetImageData()
            reslice = vtk.vtkImageReslice()
            reslice.SetInputData(mov_img)
            reslice.SetInformationInput(ref_img)
            # print(reslice.SetInformationInput)
            reslice.SetInterpolationModeToLinear()
            reslice.SetResliceAxes(combined_tfm)
            reslice.TransformInputSamplingOff()

            reslice.Update()
            self.TestSampleNode.Copy(self.refNode)
            self.TestSampleNode.SetName('TestSample')
            self.TestSampleNode.SetAndObserveImageData(reslice.GetOutput())

            self.mapEvecToMesh(self.EfieldNode, brain)

            # time in seconds:
            stop = timeit.default_timer()
            execution_time = stop - start
            print("Resampling + Mapping Executed in " + str(execution_time) + " seconds.")


    def createVTK4x4matrix(self, numpyarray): # helper function to change numpy arrays into 4x4 VTK matrices
        vtkmatrix = vtk.vtkMatrix4x4()
        for i in np.arange(4):
            for j in np.arange(4):
                vtkmatrix.SetElement(i,j, numpyarray[i,j])
        return vtkmatrix


    def mapEvecToMesh(self, inputVolume, outputVolume):
        global probedPointScalars

        # get the scalar range from image scalars
        rng = inputVolume.GetImageData().GetScalarRange()
        fMin = rng[0]
        fMax = rng[1]

        # Transform the model into the volume's IJK space
        modelTransformerRasToIjk = vtk.vtkTransformFilter()
        transformRasToIjk = vtk.vtkTransform()
        m = vtk.vtkMatrix4x4()
        transformRasToIjk.SetMatrix(m)
        modelTransformerRasToIjk.SetTransform(transformRasToIjk)
        modelTransformerRasToIjk.SetInputConnection(outputVolume.GetMeshConnection())

        probe = vtk.vtkProbeFilter()
        probe.SetSourceData(inputVolume.GetImageData())
        probe.SetInputConnection(modelTransformerRasToIjk.GetOutputPort())
        # transform model back to ras
        modelTransformerIjkToRas = vtk.vtkTransformFilter()
        modelTransformerIjkToRas.SetTransform(transformRasToIjk.GetInverse())
        modelTransformerIjkToRas.SetInputConnection(probe.GetOutputPort())
        modelTransformerIjkToRas.Update()
        outputVolume.SetAndObserveMesh(modelTransformerIjkToRas.GetOutput())

        probedPointScalars = probe.GetOutput().GetPointData().GetScalars()

        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(probe.GetOutputPort())

        # activate scalars
        outputVolume.GetDisplayNode().SetActiveScalarName('ImageScalars')
        # select color scheme for scalars
        outputVolume.GetDisplayNode().SetAndObserveColorNodeID(slicer.util.getNode('ColdToHotRainbow').GetID())
        outputVolume.GetDisplayNode().ScalarVisibilityOn()
        outputVolume.GetDisplayNode().SetScalarRange(fMin, fMax)
