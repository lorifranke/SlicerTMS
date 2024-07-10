# SlicerTMS - A Visualization Tool for the neuronavigation software 3DSlicer for real-time Transcranial Magnetic Stimulation (TMS)

<img src="https://github.com/lorifranke/SlicerTMS/blob/main/client/SlicerTMS/Resources/Icons/SlicerTMS.png" title="TMS" width=350>
Transcranial magnetic stimulation (TMS) requires accurate placement of the TMS coil to stimulate specific brain areas for individual patients. This placement calculation can be expensive, but a simulation environment can help. To connect to a deep neural network (DNN)-based estimation for an induced electric field, we developed this real-time TMS visualization module that renders the predicted electric field on a brain surface model collected from a patient's MRI scans. This prototype is an extension of the open-source medical imaging software 3D Slicer.

## Download and Installation:

<table>
<tr>
<td valign="middle" width="200"><a href="https://slicer.org"><img src="https://www.slicer.org/assets/img/3D-Slicer-Mark.svg" title="Download Slicer here!" width=150></a></td>
<td valign="top" width="800"><b> 1. 3D Slicer</b></a><br> Download the free, open-source neuronavigation software 3D Slicer from http://slicer.org for your OS. SlicerTMS will only work with 5.0.3 or newer version. Slicer documentation can be found here as well: https://slicer.readthedocs.io/
</tr>

<tr>
<td valign="middle" width="200"><img src="https://docs.github.com/assets/cb-20363/images/help/repository/code-button.png" width=150></a></td>
<td valign="top" width="800"><b> 2. SlicerTMS Repository</b></a><br> Clone this Github repository to your local computer. Here you can find instructions how to clone a repo: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
</tr>

<tr>
<td valign="middle" width="200"><img src="https://docs.monai.io/projects/label/en/latest/_images/monai-label-plugin-favorite-modules-1.png" title="Install SlicerTMS"></a></td>
<td valign="top" width="800"><b> 3. Install SlicerTMS extension in 3DSlicer</b></a><br> Start Slicer. Go to Edit --> Application Settings --> Developer --> Check the enable developer mode. Then, Go to Developer tools (also in settings now with newer version) --> Extension Wizard --> Click Select the extension and select the cloned repository folder with the SlicerTMS.py file from your local computer. Alternatively, you can install SlicerTMS in the Application settings under Modules. You can add the path to the application by clicking the two arrows on the right of the window and selecting 'Add'.
</tr>

<tr>
<td valign="middle" width="200"><img src="https://raw.githubusercontent.com/openigtlink/SlicerOpenIGTLink/master/OpenIGTLinkIF.png" title="Install Extension" width=150></a></td>
<td valign="top" width="800"><b> 4. Install OpenIGTLinkIF extension</b></a><br> Install the Plugin 'SlicerOpenIGTLink' with Slicer's Extension Manager. The data will be transferred from the deep learning model through the built-in 3D Slicer module OpenIGTLinkIF and then visualized with our TMS tool in real time.
</tr>


<tr>
<td valign="middle" width="200"><img src="https://avatars.githubusercontent.com/u/15898279?s=200&v=4" title="Install Extension" width=150></a></td>
<td valign="top" width="800"><b> 4. Install SlicerDMRI extension</b></a><br> Install the Plugin 'SlicerDMRI' (http://dmri.slicer.org/) with Slicer's Extension Manager. The tractography data and fiber files will be visualized with this extension and allows for selection of an ROI.
</tr>

<tr>
<td valign="middle" width="200"><img src="https://user-images.githubusercontent.com/38534852/204691323-f271a2e1-79fa-4187-b3ed-123129391bce.png" width=150></a></td>
<td valign="top" width="800"><b> 6. Select your data </b></a><br> You will find a folder called data by navigating to the local cloned SlicerTMS repository. The current version contains a patient examples, Example1. The example folders contain the coils, electric field, and magnetic field files of the TMS, as well as skin and brain meshes. Also, each folder has a model.pth.tar file which is a pre-trained PyTorch model. You can exchange these files with your own examples and models. If you encounter issues with Example 1, whch might happen because the files might be too large for github, please download another folder called Example4 provided here and put it into your data folder: https://drive.google.com/drive/folders/1B5km0f9KaJ622DLrdA2nTg-NmOrpbkeS?usp=drive_link
</tr>

<tr>
<td valign="middle" width="200"> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Conda_logo.svg/2560px-Conda_logo.svg.png"> </a></td>
<td valign="top" width="800"><b> 7. Environment to run the CNN and TMS module </b></a><br> Please make sure that you have the correct environment and libraries to run the neural network model. You will need to configure your libraries according to you GPU (if you don't have a GPU, the model will run by default on your CPU). We included an environment.yml file that can be imported into anaconda. If you create your own environment, make sure to install the libraries vtk, pyigtl and nibabel. Please also see the conda website for how to activate an environment: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html 
</tr>

<tr>
<td valign="middle" width="200">
<img src="https://user-images.githubusercontent.com/38534852/204690660-075547c3-0ebe-4dc6-bc5f-7aa5ed595e64.png"></a></td>
<td valign="top" width="800"><b> 8. Run Slicer TMS </b></a><br> Open your command line and navigate to the folder <code>SlicerTMS/server</code>. After the correct libraries have been installed in the environment, start the CNN model prediction by typing <code>python server.py Example1</code> to run the data from the Example1 folder (or <code>python server.py Example2</code> for Example2, or <code>python server.py Example3</code> for Example3, etc. if you have multiple subjects). Please do NOT close the terminal window and open 3D Slicer now. After opening 3DSlicer navigate to the dropdown menu <em>Welcome to Slicer</em> and select the module TMS --> Slicer TMS Module and then click on <em>Load Example</em>.
</tr>
</table>

Additionally, we will integrate a connection to transfer data between the neuronavigation platform 3D Slicer and a web browser using secure WebSockets. This web-based application simulates the brain with an interactive TMS-coil in augmented reality using WebXR-enabled devices. You will need an Android Phone that supports AR core for this. WebXR needs https, so either generate local certificate (https://blog.anvileight.com/posts/simple-python-http-server/) and make modifications in the WebServer.py file. Your computer/device that runs SlicerTMS needs to be in the same network as the phone device. You then need to start the WebServer inside SlicerTMS with the button. On the phone open your web broser and navigate to https://localhost:2016 by replacing localhost with your IP address. Alternatively you wish to use a USB cable to connect to the device running SlicerTMS (dev mode). For USB: On the phone: Enable Developer tools (https://developer.android.com/studio/debug/dev-options) and USB debugging (description here: https://developer.chrome.com/docs/devtools/remote-debugging/), then run chrome://inspect#devices in the browser on your computer and it should detect USB connected devices.

## Demo ##

#### Mapping of E-field on brain surface with 3D and 2D views ####
<img src="https://user-images.githubusercontent.com/38534852/229613057-88c2eb4e-567a-4207-ae42-cde6bb3d7bb3.gif" width="500">

#### Mapping of E-field on tractography with ROI selection ####
<img src="https://user-images.githubusercontent.com/38534852/216507462-fe0fffb4-1f41-4f35-89c0-f5b869b2f945.gif" width="500" alt="SlicerTMS Module with Efield mapped on fiber tracts">


## Affiliations and Sponsors ##
<a href="https://www.brighamandwomens.org/"><img src="https://www.brighamandwomens.org/assets/BWH/core/sprites/vectors/bwh-logo.svg" alt="Brigham and Womens Hospital" width="200"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="http://hms.harvard.edu"><img src="http://xtk.github.io/hms_logo.png" alt="Harvard Medical School" title="Harvard Medical School" width="200"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://www.umb.edu"><img src="https://upload.wikimedia.org/wikipedia/commons/0/04/UMass_Boston_logo.png" width="80" ></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://isomics.com/"><img src="https://isomics.com/isomics-logo-text-horizontal-700.png" alt="Isomics" title="Isomics" width="150"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://www.nih.gov/"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c8/NIH_Master_Logo_Vertical_2Color.png?20130312195925" alt="NIH Funding" width="100"></a>

## License ##
Copyright (c) 2023 The SlicerTMS Developers. SlicerTMS is licensed under General Public License: <a href="https://opensource.org/license/gpl-3-0/" target="_blank">https://opensource.org/license/gpl-3-0/</a>
  
## Publications ##

News: SlicerTMS accepted at MICCAI 2024 - to appear!

Please cite us here (current version):
 ```
@article{franke2023slicertms,
  title={SlicerTMS: Interactive Real-time Visualization of Transcranial Magnetic Stimulation using Augmented Reality and Deep Learning},
  author={Franke, Loraine and Park, Tae Young and Luo, Jie and Pieper, Steve and Ning, Lipeng and Haehn, Daniel},
  journal={arXiv preprint arXiv:2305.06459},
  year={2023}
}
```

More:
```
@article{park2024review,
  title={A review of algorithms and software for real-time electric field modeling techniques for transcranial magnetic stimulation},
  author={Park, Tae Young and Franke, Loraine and Pieper, Steve and Haehn, Daniel and Ning, Lipeng},
  journal={Biomedical Engineering Letters},
  volume={14},
  number={3},
  pages={393--405},
  year={2024},
  publisher={Springer}
}
```


[![DOI](https://zenodo.org/badge/548629306.svg)](https://zenodo.org/badge/latestdoi/548629306)
