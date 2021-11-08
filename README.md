# ADS-Group-G - COMP8240 Project

This repository serves as a replication of the *Deep High-Resolution Representation Learning for Human Pose Estimation (CVPR 2019)* research for the Applications of Data Science Unit (COMP8240) - Major Project of Group G. Members of the group include:
* David Dela Cruz
* Rigel Ng
* Srikar Parimi
* Shreyas Kumar Singh

## Important Links:
- [Deep High-Resolution Representation Learning for Human Pose Estimation (CVPR 2019) - Original Repository](https://github.com/leoxiaobin/deep-high-resolution-net.pytorch)
- [2017 COCO Validation Dataset](http://images.cocodataset.org/zips/val2017.zip)
- [ADS - Group G Dataset](https://drive.google.com/file/d/1xMaP9Oaxt1RoZeTdjxieXb2ay-gwjjim/view?usp=sharing)
- [COCO HRNet Models](https://drive.google.com/file/d/1-MN3Xq8dWmICeehbcPUn2DW5rGTB92cn/view?usp=sharing)

## Instructions
1. Download Datasets required for replication
    - Download [ADS - Group G Dataset](https://drive.google.com/file/d/1xMaP9Oaxt1RoZeTdjxieXb2ay-gwjjim/view?usp=sharing) and export data/ folder into main repository directory
    - If replication of Original Research results on 2017 COCO Validation Dataset, download dataset here: [2017 COCO Validation Dataset](http://images.cocodataset.org/zips/val2017.zip). Once downloaded, kindly unzip and move images to 'data/coco/images/val2017/

2. Download Pre-trained Models: [COCO HRNet Models](https://drive.google.com/file/d/1-MN3Xq8dWmICeehbcPUn2DW5rGTB92cn/view?usp=sharing) and extport models/ folder into main repository directory
3. Create 'output/' and 'log/' folders in main reposiory
4. Open ADS-GroupG.ipynb Jupyter Notebook and run commands
    - Notebook was done using Google Colab.
    - If running Jupyter Notebook locally, kindly skip Google Mount code block. 

## Main Scripts
- tools/json_coco_formatter.py - Re-formats the DataTorch.io exported JSON file and updated image filenames
    - Input requirements are: **DataTorch.io COCO JSON File** \& **Image Dataset Directory**
    - Script was written to execute on Mac-OS or Linux based devices.
- tools/test.py - Predicts Estimated Keypoints and creates output JSON file in output/ folder.
    - Input requirements are: **YAML Config File (experiments/ folder)** \& **Pre-trained Model**
