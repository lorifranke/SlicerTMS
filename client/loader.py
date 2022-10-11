import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *


class loader:
    def onLoadButton(self):
        slicer.mrmlScene.Clear()

        # 1. Brain:
        brainModelFile = self.resourcePath('UI/gm.stl')
        self.modelNode = slicer.modules.models.logic().AddModel(brainModelFile,
                                                                slicer.vtkMRMLStorageNode.CoordinateSystemRAS)

        # 2. TMS coil:
        coil = self.resourcePath('UI/fig8coil.stl')
        self.coilNode = slicer.modules.models.logic().AddModel(coil, slicer.vtkMRMLStorageNode.CoordinateSystemRAS)
        # 3. Skin model:
        skin = self.resourcePath('UI/skin.stl')
        self.skinNode = slicer.modules.models.logic().AddModel(skin, slicer.vtkMRMLStorageNode.CoordinateSystemRAS)
        skinDisplayNode = self.skinNode.GetDisplayNode()
        skinDisplayNode.SetOpacity(0.3)

        # Set transform on the coil and resize it:
        parentTransform = vtk.vtkTransform()
        scale = [3.0, 3.0, 3.0]
        parentTransform.Scale(scale[0], scale[1], scale[2])
        self.coilNode.ApplyTransformMatrix(parentTransform.GetMatrix())

        # Add a plane to the scene
        self.markupFiducials = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'Coil')
        self.markupFiducials.SetOrigin([0, 0, 110])
        self.markupFiducials.SetNormalWorld([0, 0, -10])
        self.markupFiducials.SetAxes([.5, 0, 0], [0, .5, 0], [0, 0, .5])
        self.markupFiducials.SetAxes([.5, 0, 0], [0, .5, 0], [0, 0, .5])
        self.markupFiducials.GetMarkupsDisplayNode().SetHandlesInteractive(True)
        self.markupFiducials.GetMarkupsDisplayNode().SetRotationHandleVisibility(1)
        self.markupFiducials.GetMarkupsDisplayNode().SetTranslationHandleVisibility(1)
        self.markupFiducials.GetDisplayNode().SetSnapMode(slicer.vtkMRMLMarkupsDisplayNode.SnapModeToVisibleSurface)
        # Plane visible:
        self.markupFiducials.SetDisplayVisibility(1)

        self.transformNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLLinearTransformNode())
        # attach the MRML Transform to the loaded coil:
        self.coilNode.SetAndObserveTransformNodeID(self.transformNode.GetID())
        self.showField = False
        # initial update
        # self.onHandlesModified()
        self.markupFiducials.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.onHandlesModified)

        # load imageNodes
        mag = self.resourcePath('UI/No31_Magstim_70mm_Fig8_normE.nii.gz')  # No31_Magstim_70mm_Fig8_normE.nii.gz')
        t = self.resourcePath('UI/test_cond_2mm.nii.gz')
        ev = self.resourcePath('UI/E_vec.nii.gz')

        ev_nii = nib.load(ev)
        Data = ev_nii.get_fdata()
        Data = np.transpose(Data, axes=(2, 1, 0, 3))

        self.refNode = slicer.util.loadVolume(t)
        self.magNode = slicer.util.loadVolume(mag)

        m = vtk.vtkMatrix4x4()
        self.magNode.GetIJKToRASMatrix(m)
        slicer.util.addVolumeFromArray(Data, ijkToRAS=m, name='Evec', nodeClassName='vtkMRMLVectorVolumeNode')
        self.EvecNode_orig = slicer.util.getNode('vtkMRMLVectorVolumeNode1')

        self.TestSampleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
        self.TestSampleNode.Copy(self.refNode)
        self.TestSampleNode.SetName('TestSample')

        self.EfieldNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
        self.EfieldNode.Copy(self.magNode)
        self.EfieldNode.SetName('Efield_rot')

        self.EevecNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLVectorVolumeNode')
        self.EevecNode.SetName('Evec_rot')

        self.TfmNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLGridTransformNode')