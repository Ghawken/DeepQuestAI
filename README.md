# Indigoplugin for DeepQuestAI

This is a _Simple_ plugin for DeepQuestAI or DeepStackAI.

DeepQuestAI is an interesting local Artificial Intelligence Object ML detection API AI engine.
https://deepquestai.com/

It runs locally on your network - no internet, or cloud involvement needed, until some of BlueIris alternatives
DeepQuest has also been used as a base for local AI addon for Blue Iris (see ipcamtalk forums)

DeepQuest runs with a docker container on windows PC (Follow instructions), Docker on mac or within a rpi (ideallly with Neural NCS stick)
A new beta and open sourcing of it is expected at anytime..  (Sep 2020)

This plugin can tie deeply in with BlueIris plugin (where the latest BI Plugin version is needed), it then uses indigo 7+ Broadcast ability to communicate between plugins.

You need to install and setup DeepStack AI, as per its instructions.  
After this is completed you will end up with a IP address and port where Deepstack is running.

Within Deepstack we need the **Detection API Running**  or "VISION-DETECTION=True" in startup commands.

This will end up with a IP address and port where Deepstack is running.

On my now growing, now for over a year with a smattering of other users testing works very well.
Currently (have scanned 2021439 images so far - more than 700gigs!)

Is all local, which is both positive and negative:

Positive - have images to use and keep / Cars/ People saved forever 
         - Plugin can send images to archive Network directory keeping time stamped photos of all people detected etc.
         - No security issues; nothing going offsite
         - Options running on RPI with NCS2 (get about 1sec processing per image)
         - Seems faster than off site options (like Sentry on BI)
         - Run Action Groups based on URL or BI Camera when Object or no object 
         (add Machine Learning to lights off - e.g timer expired, check cameras for people, turn off if none)
         - Archive images forever; Gate Camera scans for Car, when detected saves images; no data issues given size of images
         - On setup enabled Blue Iris Cameras - flags back to BI that objecte detected eg. flags camera videos in BI interface
         
         
Negative - need CPU cycles to run the detection... 


#### **Potential Uses**

First:  (**with BlueIris setup and/or BI Indigo Plugin**)

Setup, enable broadcast in BI Indigo plugin
All BI Cameras will send motion alerts to this DeepState Plugin.
Camera Images will be processed by Deepstate as you request for objects.

What images? - well all Motion/Triggered images from the Camera itself.
eg. When motion detected at Gate Cam -> alerts Deepstate, sends image and processes this image for object detection
If object found:
    Can enable a Indigo Trigger - see DeepState Plugin Triggers 

Can create a DeepState Plugin Device for important objects eg. DeepState Device Person or Cars
If DeepState Device exists for this object Plugin will save all images of these objects, archiving to Network storage if enabled/setup
Device States also have time/last detected, image links etc.

eg. flow
![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateBISetup.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateBISetup.png)


#### or

No BlueIris, or BlueIris but only for occasional Action Group based use.
eg.
Check no person outside on BI Outside Cameras1,2,3,4 before turn lights off.

Action Group Only Usage:

With BlueIris have no enabled Cameras in PluginConfig (won't check any cameras regularly like about flow)
But you can trigger a actionGroup to run:

eg Check URL Image and Run Action Group if object Found or Not Found:
eg Check BlueIris Camera Feed and Run Action Group if Object Found or Not Found

Checks a URL Image from BI Camera for example, but can be any URL Image.
Checks for presence or absence of an object e.g car gone, person present.
Then runs an action group depending on presence or absence

eg.
Door closed trigger, run this AG, perhaps with delay,,,
Checks Camera for Person present - if no person run action group to turn lights off

eg.
Check Garage for Car - Car absent, run appropriate action groups

Flow:
![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateNotBISetup.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateNotBISetup.png)




### But wait there is more...

#### **HTTP Server:**

Creates a very basic image Web server -  for control page use, showing the last detected objects
Defaults to port 4142, set up in Plugin Config.

e.g 
`http://INDIGO-IP-ADDRESSS:4142/car.html`

Set the above as a refreshing URL in control page will show the last image of car found.

On refreshing the the same URL, the web server goes backwards in time through all saved non-archived images.
Cycling back to beginning again once reached end.

NB:  To save images need to create Indigo DeepState Device for that particularly Object Type!


## Setup

1. Install DeepStack, run.  
(API code now not needed free for all)
Start DeepStack Server - Detection recognition only API needed, pick port to run on DeepState on
Plugin Defaults to 7188

#### Plugin Needs Pillow installed/PIL for image control

`sudo pip install pillow`

2. Install this Plugin and setup with PluginConfig

Enter the ipaddress of your DeepStateAI API
Enter the port that you are using.

Follow the detailed instructions and information in the Plugin Config page

3.  Make sure running BlueIris Plugin version >1.1.12 and above
**Enable within BlueIris plugin, the Broadcast setting**


# DeepStateAI Plugin


## Plugin Config Settings:

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig1a.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig1a.png)

IP Address:  IP address of computer where deepStackAI running, or localhost
Port: Port of DeepStackAI service
Enabled Cameras:
BlueIris Cameras that are enabled for image checking.
Overriding Camera selection, can select all, and then within multiple triggers further define.

SuperCharge Detection:
This setting, pulls multiple images from BlueIris following camera triggering and chucks them all at the DeepStackAI API if enabled.
Images Number: Once camera triggered - the number of images to pull
Seconds Apart:  The numbers of seconds apart

eg.
SuperCharge Enabled:
Motion/Camera triggered.
DeepQuestAI will pull 5 images, 2 seconds apart one after another and send to DeepQuest API for image recognition.

Obviously the number of cameras enabled, and speed of DeepStack processing will be very important here

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig2.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig2.png)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig3.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStatePluginConfig3.png)


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
& etc

Will trigger however, without any devices existing - just won't save images.

Within Cars/Faces always saves a copy of the whole Image (with bounding red box and Confidence in top left)
Also saves a cropped Copy of the Person/Car

Will shortly add ability to date/move/keep images for as long as wanted.


## Plugin:
Has One User created Device:

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateDeviceOptions.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateDeviceOptions.png)


DeepState Object Device:
Choose between Vehicle and Person and Other - for everything else.
Enter the desired confidence for this Object.
When found the Device will be updated with details, including Image link

Has One Main Device:

Generated from within Plugin Config

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateMainDeviceStates.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateMainDeviceStates.png)

States as displayed above


## Has One Trigger:

Edit Event Settings:
- Select the object Type that trigger is looking for Person versus Car, versus other
- Select the confidence interval to use eg. 0.6
- Select the Cameras you are using for this trigger, one or many
- Select the don't retrigger within this time period eg. 10 seconds or 120 seconds etc

Then usual indigo conditions, action groups apply.
eg.
person found, do this etc.

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateTriggersObject.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateTriggersObject.png)

This trigger will fire ignoring the missing Cameras with the SendURL Action Group

## Actions

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateActions.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepStateActions.png)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/AGCheckURLAG.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/AGCheckURLAG.png)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/AGCheckBICamerasAG.png?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/AGCheckBICamerasAG.png)


ChangeLog:

Better late than Never!

0.6.8
Delete Action images from calls, rather than waiting for cleanup
Use &ALERT_PATH in BI trigger info, sometime in past this changed

0.6.7
Add some more information to Triggers/Actions regarding what happens
Add Possible Flow Charts to Readme.

0.6.6
Add BI Camera Checking Action Group - unfortunately needs BI server/port details entered in AG settings
Add option for 2nd DeepState service running - to be used for action groups if needed
Allows another instance of deepstate running on a localip eg. use RPI with deepstate/NCS somewhere to do some of the processing
If unchecked will use the main device for all calls (no change)
Shouldn't really be issue
Add new Action Group - for immediately sending back to DeepState the URL/or File, not que, send immediately
Change logic of new Action Groups to allow separate AG to be selected for object found/or not found and both...
Cosmetic changes

0.6.0
**** Report back to BlueIris and Flag video if object detected ****
Only will flag BI videos when Deep State Object device exists (same for saving images)
Use 'memo' = DeepState_ObjectType
Can't seem to access this memotext at moment within BI or iOS, but potentially with BI update.

0.5.9 Addition

Action Group 
Check URL Image and Run Action Group:

Checks a URL Image from BI Camera for example, but can be any URL Image.
Checks for presence or absence of an object e.g car gone, person present.
Then runs an action group depending on presence or absence
eg.
Door closed trigger, run this AG, perhaps with delay
Checks Camera for Person present - if no person run action group to turn lights off
eg.
Check Garage for Car - Car absent, run appropriate action groups

0.5.5
Add ability to set a archive smb network directory.
Needs to be a smb network location:  (if local directory just use SaveDirectory)
Format:
//USERNAME:PASSWORD@SERVER/Directory/Directory


Will copy files 2 days old, every 24 hours to this directory preserving datetime info of files for future reference
Add /archive/deepstateobject.html to HTML server - serving these archive images as well
Add menu item to copy to archive
Few text changes to config items

0.5.1
Trial of Daemon threads instead - to avoid hanging when closing RAMdisk
(only occured once, but needed restart as couldn't manually eject)

0.5.0
Better downloading, add to Que behaviour

Use BI ALertImages - changes to BI Plugin updates to version 1.1.16
If alertimage received/enabled in BI will always use Alert Image,plus whatever is setup
Uses hires AlertImages - Capture hi Res ALert images should be enabled in trigger tab of Camera

Changes to BI Trigger setup to format  **(NB Changed to ALERT_PATH)**
On:
192.168.1.6:4556/&CAM/&TYPE/&PROFILE/True/&ALERT_PATH
Off:
192.168.1.6:4556/&CAM/&TYPE/&PROFILE/False/&ALERT_PATH

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


![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570248411.68.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570248411.68.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570248998.48.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570249337.26.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg)


![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Full_ExternalActionURL_1570249554.39.jpg)



![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Full_ExternalActionURL_1570249423.16.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Crop_ExternalActionURL_1570249423.16.jpg)


![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Full_ExternalActionURL_1570249505.94.jpg)

![https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_car_Crop_ExternalActionURL_1570249337.26.jpg?raw=True](https://github.com/Ghawken/DeepQuestAI/blob/master/Images/DeepState_person_Crop_ExternalActionURL_1570249505.94.jpg)







