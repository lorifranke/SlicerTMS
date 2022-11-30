# SlicerTMS - A Visualization Tool for the neuronavigation software 3DSlicer for real-time Transcranial Magnetic Stimulation (TMS)

<img src="https://github.com/lorifranke/SlicerTMS/blob/main/client/SlicerTMS/Resources/Icons/SlicerTMS.png" title="TMS" width=350>
Transcranial magnetic stimulation (TMS) requires accurate placement of the TMS coil to stimulate specific brain areas for individual patients. This placement calculation can be expensive, but a simulation environment can help. To connect to a deep neural network (DNN)-based estimation for an induced electric field, we developed this real-time TMS visualization module that renders the predicted electric field on a brain surface model which is
collected from a patient's MRI scans. This prototype is an extension of the open-source medical imaging software 3D Slicer.

## Download and Installation:

<table>
<tr>
<td valign="middle" width="200"><a href="https://slicer.org"><img src="https://www.slicer.org/assets/img/3D-Slicer-Mark.svg" title="Download Slicer here!" width=100></a></td>
<td valign="top" width="800"><b>1. 3D Slicer</b></a><br> Download the free open-source neuronavigation software 3D Slicer from http://slicer.org for your OS. The current stable version is 5.0.3. SlicerTMS will only work with the newest Slicer version. A Slicer documentation can be found here as well: https://slicer.readthedocs.io/
</tr>

<tr>
<td valign="middle" width="200"><img src="https://docs.github.com/assets/cb-20363/images/help/repository/code-button.png" width=150></a></td>
<td valign="top" width="800"><b>2. SlicerTMS Repository</b></a><br> Clone this Github repository to your local computer. Here you can find instructions how to clone a repo: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
</tr>

<tr>
<td valign="middle" width="200"><img src="https://docs.monai.io/projects/label/en/latest/_images/monai-label-plugin-favorite-modules-1.png" title="Install SlicerTMS" width=150></a></td>
<td valign="top" width="800"><b>3. Install SlicerTMS extension in 3DSlicer</b></a><br> Start Slicer. Go to Edit --> Application Settings --> Developer --> Check the enable developer mode. Then, Go to Developer tools --> Extension Wizard --> Click Select extension and select the cloned repository folder with the SlicerTMS.py file from your local computer. Altenatively, you can install SlicerTMS in the Application settings under Modules. You can add the path to the application by clicking the two arrows on the right of the window and select 'Add'.
</tr>

<tr>
<td valign="middle" width="200"><img src="https://raw.githubusercontent.com/openigtlink/SlicerOpenIGTLink/master/OpenIGTLinkIF.png" title="Install Extension" width=150></a></td>
<td valign="top" width="800"><b>4. Install OpenIGTLinkIF extension</b></a><br> 4. Install the Plugin 'SlicerOpenIGTLink' with Slicer's Extension Manager.
</tr>

<tr>
<td valign="middle" width="200"></a></td>
<td valign="top" width="800"><b>5. Select your data </b></a><br> By navigating to the local cloned SlicerTMS repository your will find a folder with data. The current version contains two different patient examples, Example1 and Example2. 
</tr>
</table>

At first, the data is transferred from the deep learning model through a built-in 3D Slicer module called OpenIGTLinkIF and then visualized with our TMS tool in real-time. Additionally, we integrated a connection to transfer data between the neuronavigation platform 3D Slicer and a web browser using secure WebSockets. This web-based application simulates the brain with an interactive TMS-coil in augmented reality using WebXR-enabled devices.

## Demo ##


## Affiliations and Sponsors ##
<a href="https://www.brighamandwomens.org/"><img src="https://www.brighamandwomens.org/assets/BWH/core/sprites/vectors/bwh-logo.svg" alt="Brigham and Womens Hospital" width="200"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="http://hms.harvard.edu"><img src="http://xtk.github.io/hms_logo.png" alt="Harvard Medical School" title="Harvard Medical School" width="200"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://www.umb.edu"><img src="https://www.umb.edu/assets/images/UMASSB0STON_ID_blue.png?1560890493" width="80" ></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://isomics.com/"><img src="https://isomics.com/isomics-logo-text-horizontal-700.png" alt="Isomics" title="Isomics" width="150"></a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="https://www.nih.gov/"><img src="https://upload.wikimedia.org/wikipedia/commons/c/c8/NIH_Master_Logo_Vertical_2Color.png?20130312195925" alt="NIH Funding" width="100"></a>

## License ##
Copyright (c) 2022 The SlicerTMS Developers. SlicerTMS is licensed under the MIT License: <a href="http://www.opensource.org/licenses/mit-license.php" target="_blank">http://www.opensource.org/licenses/mit-license.php</a>
  
## Publications ##
