Indigoplugin for DeepQuestAI

This is now the beginning of a plugin for DeepQuestAI or DeepStackAI 

DeepQuestAI is an interesting local AI detection API AI engine.

https://deepquestai.com/

This plugin deeply ties in with BlueIris plugin (where new updated version is needed), it then uses indigo 7+ Broadcast ability to communicate between plugins.

You need to install and setup DeepStackAI.
Windows, Mac versons available - with local usage for current plugin requirements
An API number is needed.

Setup

1. Install DeepStack, run and activate with your API code

2. Install Plugin and setup with PluginConfig

Enter the ipaddress of your DeepStateAI API
Enter the port that you are using.

3.  Make sure running BlueIris Plugin version 1.1.12 and above
Enable within BlueIris plugin, the Broadcast setting

# DeepStateAI Plugin

## Plugin Config Settings:

DeepQuest API:  Not needed as yet
Use local DeepQuestAI - will use 'localhost' for IP address if running locally
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

Warning:
Currently there are no checks on how far behind it might be getting...

## Plugin:
Has One Device

DeepState Object Device:
Choose between Vehicle and Person
Enter the desired confidence for this Object.
When found the Device will be updated with details, including Image link

##Has One Trigger:

This is likely the main usage:
Edit Event Settings:
- Select the object Type that trigger is looking for Person versus Car
- Select the confidence interval to use eg. 0.6
- Select the Cameras you are using for this trigger, one or many
- Select the don't retrigger within this time period eg. 10 seconds or 120 seconds etc

Then usual indigo conditions, action groups apply.
eg.
person found, do this etc.





