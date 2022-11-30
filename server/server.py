"""
============================
Tracked TMS nifti image data server
Receive dA/dt field from 3DSlicer, predict the E-field and send data back to 3DSlicer
============================
"""

import pyigtl  # pylint: disable=import-error
import os
import sys
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from math import cos, sin, pi
from time import sleep
import numpy as np
import glob
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import nibabel as nib
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.nn.parallel
import torch.optim as optim
from torch.optim import lr_scheduler
from collections import OrderedDict
from model import Modified3DUNet
from numpy import linalg as LA
import time

class ServerTMS():
    def __init__(self, f = None):
        self.setFile(f)
        self.getF(self)

        server = pyigtl.OpenIGTLinkServer(port=18944, local_server=True)
        text_server = pyigtl.OpenIGTLinkServer(port=18945, local_server=True)
        string_message = pyigtl.StringMessage(f, device_name="TextMessage")
        text_server.send_message(string_message)

        timestep = 0
        script_path = os.path.dirname(os.path.abspath(__file__))
        # model_path = os.path.join(script_path,'../model/model_iso.pth.tar')
        model_path = os.path.join(script_path, str(f) + '/model.pth.tar')

        # load CNN model
        in_channels = 4
        out_channels = 3
        base_n_filter = 16

        # needs nvidia driver version 510 for cuda 11.6
        # deactivates cuda uncomment to use cpu:
        # torch.cuda.is_available = lambda : False
        use_cuda = torch.cuda.is_available()
        print('Cuda available: ', use_cuda)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print('Using device:', device)

        net = Modified3DUNet(in_channels, out_channels, base_n_filter)
        net = net.float()
        if torch.cuda.is_available():
            # loading all tensors onto GPU 0:
            checkpoint = torch.load(model_path, map_location='cuda:0')
        else:
            checkpoint = torch.load(model_path, map_location='cpu')

        new_state_dict = OrderedDict()
        for k, v in checkpoint['model_state_dict'].items():
            #name = k 
            name = k[7:] # remove `module.`
            new_state_dict[name] = v
        # load params
        net.load_state_dict(new_state_dict) 
        if torch.cuda.is_available():
            net = net.cuda() 
        else:
            pass


        data_path = os.path.join(script_path, '../data/')
        ex_path = os.path.join(script_path, self.file)
        cond_path = os.path.join(ex_path, 'conductivity.nii.gz')
        # print(cond_path)
        cond = nib.load(cond_path)
        cond_data = cond.get_fdata()

        xyz = cond_data.shape
        cond_data = np.reshape(cond_data,([xyz[0], xyz[1], xyz[2], 1]))
        print('Image shape:', cond_data.shape)



        while True:
            if not server.is_connected():
                # Wait for client to connect
                sleep(0.01)
                # print('not connected')
                continue

            messages = server.get_latest_messages()
            for message in messages:
                magvec = message.image
                magvec = np.transpose(magvec, axes=(2, 1, 0, 3))

                inputData = np.concatenate((cond_data, magvec*100), axis=3)
                inputData = inputData.transpose(3, 0, 1, 2)
                size = np.array([1, 4,  xyz[0], xyz[1], xyz[2]])
                inputData = np.reshape(inputData,size)
                inputData = np.double(inputData)

                #get start time to test CNN execution time
                st = time.time()
                inputData_gpu = torch.from_numpy(inputData).to(device)
                # get the end time
                et = time.time()

                outputData = net(inputData_gpu.float())
                outputData = outputData.cpu()
                outputData = outputData.detach().numpy()
                outputData = outputData.transpose(2, 3, 4, 1, 0)
                outputData = np.reshape(outputData,([xyz[0], xyz[1], xyz[2], 3]))
                outputData = np.transpose(outputData, axes=(2, 1, 0, 3))
                outputData = LA.norm(outputData, axis = 3)

                image_message = pyigtl.ImageMessage(outputData, device_name="pyigtl_data")
                server.send_message(image_message)

                # get the execution time
                elapsed_time = et - st
                print('Execution time CNN:', elapsed_time, 'seconds')

    def setFile(self, file):
        self.file = file

    @staticmethod
    def getF(self):
        # sys.stdout = open("test.txt", "w")
        print('Selected Example:' + f + '\n' + 'Please start 3DSlicer')
        return f

if len(sys.argv) > 1:
    f = '../data/' + str(sys.argv[1]) + '/'
else:
    f = '../data/Example1/'

server = ServerTMS(f)
# server.setFile('../data/Example2/')
