import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import nibabel as nib


class Loader:

    def __init__(self, data_directory):

        self.data_directory = data_directory
        
        self._graymatter_file = 'gm.stl'
        self._coil_file = 'coil.stl'
        self._coil_scale = 3
        self._skin_file = 'skin.stl'
        self._efield_file = 'efield.nii.gz'
        self._conductivity_file = 'conductivity.nii.gz'
        self._magfield_file = 'magfield.nii.gz'

        self.modelNode = None
        self.coilNode = None
        self.skinNode = None
        self.markupFiducials = None

        self.conductivityNode = None
        self.magfieldNode = None
        self.efieldNode = None
        self.efieldVectorNode = None


    @staticmethod
    def loadExample1(self):

        data_directory = os.path.join(os.path.dirname(slicer.modules.slicertms.path), '../../data/Example1/')

        loader = Loader(data_directory)

        slicer.mrmlScene.Clear()

        #
        # 1. Brain:
        #
        brainModelFile = os.path.join( loader.data_directory, loader._graymatter_file )
        loader.modelNode = slicer.modules.models.logic().AddModel(brainModelFile,
                                                                slicer.vtkMRMLStorageNode.CoordinateSystemRAS)
        

        #
        # 2. Skin model:
        #
        skin = os.path.join( loader.data_directory, loader._skin_file )
        loader.skinNode = slicer.modules.models.logic().AddModel(skin, slicer.vtkMRMLStorageNode.CoordinateSystemRAS)
        skinDisplayNode = loader.skinNode.GetDisplayNode()
        skinDisplayNode.SetOpacity(0.3)



        #
        # 3. TMS coil:
        #
        coil = os.path.join( loader.data_directory, loader._coil_file )
        
        loader.coilNode = slicer.modules.models.logic().AddModel(coil, slicer.vtkMRMLStorageNode.CoordinateSystemRAS)
        
        # Set transform on the coil and resize it:
        parentTransform = vtk.vtkTransform()
        parentTransform.Scale(loader._coil_scale, loader._coil_scale, loader._coil_scale)
        
        loader.coilNode.ApplyTransformMatrix(parentTransform.GetMatrix())

        # Add a plane to the scene
        markupFiducials = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'Coil')
        markupFiducials.SetOrigin([0, 0, 110])
        markupFiducials.SetNormalWorld([0, 0, -10])
        markupFiducials.SetAxes([.5, 0, 0], [0, .5, 0], [0, 0, .5])
        markupFiducials.SetAxes([.5, 0, 0], [0, .5, 0], [0, 0, .5])
        markupFiducials.GetMarkupsDisplayNode().SetHandlesInteractive(True)
        markupFiducials.GetMarkupsDisplayNode().SetRotationHandleVisibility(1)
        markupFiducials.GetMarkupsDisplayNode().SetTranslationHandleVisibility(1)
        markupFiducials.GetDisplayNode().SetSnapMode(slicer.vtkMRMLMarkupsDisplayNode.SnapModeToVisibleSurface)
        markupFiducials.SetDisplayVisibility(1)
        
        loader.markupFiducials = markupFiducials

        loader.transformNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLLinearTransformNode())
        loader.coilNode.SetAndObserveTransformNodeID(loader.transformNode.GetID())
        

        #
        # 4. Other stuff
        #

        # load magfield
        loader.magfieldNode = slicer.util.loadVolume( os.path.join( loader.data_directory, loader._magfield_file ) )


        # load efield TODO remove nibabel
        ev_nii = nib.load( slicer.util.loadVolume( os.path.join( loader.data_directory, loader._efield_file ) ) )
        ev_nii_data = ev_nii.get_fdata()
        ev_nii_data = np.transpose(ev_nii_data, axes=(2, 1, 0, 3))

        # transform 
        m = vtk.vtkMatrix4x4()
        loader.magfieldNode.GetIJKToRASMatrix(m)
        slicer.util.addVolumeFromArray(ev_nii_data, ijkToRAS=m, name='Evec', nodeClassName='vtkMRMLVectorVolumeNode')
        loader.efieldVectorNode = slicer.util.getNode('vtkMRMLVectorVolumeNode1') # TODO generalize


        # load conductivity
        loader.conductivityNode = slicer.util.loadVolume( os.path.join( loader.data_directory, loader._conductivity_file ) )
        

        loader.efieldNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
        loader.efieldNode.Copy(loader.magfieldNode)
        loader.efieldNode.SetName('Efield_rot')


        return loader


        # interaction hookup
        #self.markupFiducials.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self.onHandlesModified)


