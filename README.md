# Indigoplugin for DeepQuestAI

This is now the beginning of a plugin for DeepQuestAI or DeepStackAI 

DeepQuestAI is an interesting local AI detection API AI engine.
https://deepquestai.com/

This plugin deeply ties in with BlueIris plugin (where new updated Plugin version is needed), it then uses indigo 7+ Broadcast ability to communicate between plugins.

You need to install and setup DeepStackAI.
Windows, Mac versons available - with local usage for current plugin requirements
An API number is needed, but can be freely installed.

On my now growing testing works very well.
Is all local, which is both positive and negative:
Positive - have images to use and keep / Cars/ People saved forever if wanted
         - No security issues
         - Seems faster than off site options (like Sentry on BI)
Negative - need CPU cycles to run the detection

Setup

1. Install DeepStack, run and activate with your API code on html website.  
Start DeepStack Server - recognition only API needed, pick port to run on 
Plugin Defaults to 7183

##### Plugin Needs Pillow installed/PIL for image control
##### pip install pillow

2. Install Plugin and setup with PluginConfig

Enter the ipaddress of your DeepStateAI API
Enter the port that you are using.

3.  Make sure running BlueIris Plugin version >1.1.12 and above
Enable within BlueIris plugin, the Broadcast setting

# DeepStateAI Plugin

## Plugin Config Settings:

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig1.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig1.png)

IP Address:  IP address of computer where deepStackAI running, or localhost
Port: Port of DeepStackAI service
Enabled Cameras:
BlueIris Cameras that are enabled for image checking.
Overriding Camera selection, can select all, and then within multiple triggers further define.

SuperCharge Detection:
This setting, pulls multiple images from BlueIris and chucks them all at the DeepStackAI API if enabled.
Images Number: Once camera trigger - the number of images to pull
Seconds Apart:  The numbers of seconds apart

eg.
SuperCharge Enabled:
Motion/Camera triggered.
DeepQuestAI will pull 5 images, 2 seconds apart one after another and send to DeepQuest API for image recognition.

Obviously the number of cameras enabled, and speed of DeepStack will be very important here

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig2.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig2.png)


Warning:
Currently checks and if > Abort Image Time seconds behind image/checking will delete image and move on.

If velocity of Deepstate improving (eg. getting quicker) will continue without deleting
Additionally:
If image is a supercharge/additional image and the current processing delay is >1/2 total Abort time, will start skipping every 2nd supercharge image



### Enabled HTTP Image Server

This is the 2nd major functionality of plugin - runs a local web server to server Plugin Images to ControlPages
Enable/Port used

Then can go to, any of the objectType name to display

http://192.168.1.19:4142/car.html
http://192.168.1.19:4142/person.html
http://192.168.1.19:4142/bench.html
etc..etc..


(192.168.1.19 - is local Indigo IP address)

As Refreshing URL within control page to show the last Image detected/Saved
If Page refreshed (and simply action replace Controlpage with self) Will move on to next image etc.etc.

Actions - to Reset Images to Zero

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateImageServer.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateImageServer.png)


## Images Saved

Plugin saves all Images in users documents directory/Indigo-DeepQuestAI, or as selected with PluginConfig

New:
Will ONLY save images if a matching Indigo Device exists.

eg: Indigo Device DeepState Object == Car
Will save all images found of object = Car
& vice versa

Will trigger however, without any devices existing - just won't save images.


Within Cars/Faces always saves a copy of the whole Image (with bounding red box and Confidence in top left)
Also saves a cropped Copy of the Person/Car

Will shortly add ability to date/move/keep images for as long as wanted.



## Plugin:
Has One Device

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateDeviceOptions.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateDeviceOptions.png)


DeepState Object Device:
Choose between Vehicle and Person and Other - for everything else.
Enter the desired confidence for this Object.
When found the Device will be updated with details, including Image link

## Has One Trigger:

This is likely the main usage:
Edit Event Settings:
- Select the object Type that trigger is looking for Person versus Car
- Select the confidence interval to use eg. 0.6
- Select the Cameras you are using for this trigger, one or many
- Select the don't retrigger within this time period eg. 10 seconds or 120 seconds etc

Then usual indigo conditions, action groups apply.
eg.
person found, do this etc.

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateTriggersObject.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateTriggersObject.png)



## Actions

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateActions.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateActions.png)



ChangeLog:

Better late than Never!

0.4.1
Change to download images threading, don't thread first or single image, thread the rest
Remove some more logging
Fixs download URL to work correctly with large images/slow internet
Add some examples from ipcam forums

0.4.0
Add Bytes and Human readable data processed - amount of Image data read/processed
Remove resetting counts to zero at restart.
Remove some logging

0.3.9
Further image verification
Change to using hdiutil to dismount - otherwise leaving diskimages-helper processes hanging
Using deattach to hopefully avoid
Oops

0.3.8
Verify image data before sending to DeepState (having some issues with invalid image data crashing deepstate)
Few unicode exception further fixes
Change to skip every 2nd supercharge image if 1/2 of set time delayed.

0.3.2
Stop adding to que if DeepStateService not responding/Down/Not on
Delete superCharge Images first if que speed becoming issue
[starts doing this 1/2 of the set time, eg. >30 seconds will skip Supercharge Images]
First Fix for orphan Temp files... every hour check for orphaned files and delete


0.3.1
Add Main Server Device - created with pluginConfig
Allows monitoring of DeepState service, images, delay etc. Found was constantly looking for this info
Force ejects RAM disk

0.3.0
Add check for Temp Files in directory, before delete
Use RAMdisk for temp files add setting:
    Creates a 256MB Ram disk to use for all Temporary Files - downloading from BI
    If drive full just skips and typically means > 200 files behind so not great
    Ejects/Closes/Creates if and when needed
    If PluginConfig changes will force restart of Plugin to create RamDisk
    Further checks/balances for RAMdisk creation
    
With BI Plugin 1.1.15: Sends BlueIris Trigger Type
Ignores AUDIO triggers (yah!) as this was causing a lot of activity for me particularly when windy
[Add selection of particular triggers perhaps later]

0.2.6
Remove Unselected Cameras from being an option with Events (confusing), Can set up multiple events for objects, from one many or different cameras.
Just can't select a Camera which isn't enabled in Main Plugin Config

0.2.5
Add support for every every object available with DeepState - eg. cats, dogs etc.
Extend this support to Html Image Server (now every objectType is possible)
Extend this support to Devices and Events and Actions
Important:
Plugin will not save any images for any object, unless there is a corresponding device with that Object type within Indigo
eg. if want to save every Car image - need to create a Indigo Car device, etc for every object

TODO
- Add multiple similiar objects together as a list - eg.cat,dog, bear!
(decide how to do that with Indigo config currently)
- Return Car back to all vehicles (currently just car)
- Add time of photo taken to image, not time processed


Example Captures and Reports:

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570248411.68.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570248411.68.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570248998.48.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570249337.26.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570249554.39.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Crop_ExternalActionURL_1570249423.16.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Crop_ExternalActionURL_1570249505.94.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Full_ExternalActionURL_1570249423.16.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Full_ExternalActionURL_1570249505.94.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Full_ExternalActionURL_1570249554.23.jpg)





