"""
============================
Tracked TMS nifti image data server
Receive dA/dt field from 3DSlicer, predict the E-field and send data back to 3DSlicer
============================
"""

import pyigtl  # pylint: disable=import-error
import os
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
import time


server = pyigtl.OpenIGTLinkServer(port=18944, local_server=True)

timestep = 0
script_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_path, '../data/Example1/')
cond_path = os.path.join(data_path, 'conductivity.nii.gz')
print(cond_path)
cond = nib.load(cond_path)
cond_data = cond.get_fdata()

xyz = cond_data.shape
cond_data = np.reshape(cond_data,([xyz[0], xyz[1], xyz[2], 1]))
print(cond_data.shape)


model_path = os.path.join(script_path,'../model/isomodel.pth.tar')

#model_path = '/Users/lipeng/Documents/Python/pyigtl/pyigtl_examples/models/retrained_isocond_epoch_400.pth.tar'



# load CNN model
in_channels = 4
out_channels = 3
base_n_filter = 16

# needs nvidia driver version 510 for cuda 11.6
# deactivates cuda uncomment to use cpu:
# torch.cuda.is_available = lambda : False
use_cuda = torch.cuda.is_available()
print(use_cuda)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('using', device)

net = Modified3DUNet(in_channels, out_channels, base_n_filter)
net = net.float()
checkpoint = torch.load(model_path,map_location='cpu')
# loading all tensors onto GPU 0:
# checkpoint = torch.load(model_path,map_location='cuda:0')
new_state_dict = OrderedDict()
for k, v in checkpoint['model_state_dict'].items():
    #name = k 
    name = k[7:] # remove `module.`
    new_state_dict[name] = v
# load params
net.load_state_dict(new_state_dict)  





while True:
    if not server.is_connected():
        # Wait for client to connect
        sleep(0.01)
        # print('not connected')
        continue

    messages = server.get_latest_messages()
    for message in messages:

        #get start time
        st = time.time()

        magvec = message.image
        magvec = np.transpose(magvec, axes=(2, 1, 0, 3))
        #print(cond_data.shape)
        #print(magvec.shape)

        inputData = np.concatenate((cond_data, magvec*100), axis=3)
        inputData = inputData.transpose(3, 0, 1, 2)
        size = np.array([1, 4,  xyz[0], xyz[1], xyz[2]])
        inputData = np.reshape(inputData,size)
        inputData = np.double(inputData)
        inputData = torch.from_numpy(inputData)
        # call the network:
        outputData = net(inputData.float())
        outputData = outputData.detach().numpy()
        outputData = outputData.transpose(2, 3, 4, 1, 0)
        outputData = np.reshape(outputData,([xyz[0], xyz[1], xyz[2], 3]))
        outputData = np.transpose(outputData, axes=(2, 1, 0, 3))
        image_message = pyigtl.ImageMessage(outputData, device_name="pyigtl_data")
        server.send_message(image_message)

        # get the end time
        et = time.time()

        # get the execution time
        elapsed_time = et - st
        print('Execution time:', elapsed_time, 'seconds')



