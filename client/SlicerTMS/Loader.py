import os
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import nibabel as nib
import numpy as np

import Mapper as M


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
        self.markupsPlaneNode = None

        self.conductivityNode = None
        self.magfieldNode = None
        self.efieldNode = None
        self.efieldVectorNode = None

    def callMapper(self, param1=None, param2=None):
        '''
        '''
        M.Mapper.map(self)


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
        markupsPlaneNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode', 'Coil')
        markupsPlaneNode.SetOrigin([0, 0, 110])
        markupsPlaneNode.SetNormalWorld([0, 0, -10])
        markupsPlaneNode.SetAxes([.5, 0, 0], [0, .5, 0], [0, 0, .5])
        markupsPlaneNode.SetAxes([.5, 0, 0], [0, .5, 0], [0, 0, .5])
        markupsPlaneNode.GetMarkupsDisplayNode().SetHandlesInteractive(True)
        markupsPlaneNode.GetMarkupsDisplayNode().SetRotationHandleVisibility(1)
        markupsPlaneNode.GetMarkupsDisplayNode().SetTranslationHandleVisibility(1)
        markupsPlaneNode.GetDisplayNode().SetSnapMode(slicer.vtkMRMLMarkupsDisplayNode.SnapModeToVisibleSurface)
        markupsPlaneNode.SetDisplayVisibility(1)
        
        loader.markupsPlaneNode = markupsPlaneNode

        loader.transformNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLLinearTransformNode())
        loader.coilNode.SetAndObserveTransformNodeID(loader.transformNode.GetID())
        

        #
        # 4. Other stuff
        #

        # load magfield
        loader.magfieldNode = slicer.util.loadVolume( os.path.join( loader.data_directory, loader._magfield_file ) )


        # load efield TODO remove nibabel
        ev_nii = nib.load(  os.path.join( loader.data_directory, loader._efield_file ) ) 
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



        # interaction hookup
        loader.markupsPlaneNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, loader.callMapper)

        # call one time
        loader.callMapper()

        return loader




