#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
Author: GlennNZ
DeepQuestAI Plugin Take 1
"""
global MajorProblem

MajorProblem = 0
startingUp = False


import datetime
import time as t
import urllib2
import os
import sys
import shutil
import logging
import requests

from PIL import Image,ImageDraw,ImageFont

import StringIO

try:
    import indigo
except:
    pass
kBroadcasterPluginId = "com.GlennNZ.indigoplugin.BlueIris"
# Establish default plugin prefs; create them if they don't already exist.
kDefaultPluginPrefs = {
    u'configMenuPollInterval': "300",  # Frequency of refreshes.
    u'configMenuServerTimeout': "15",  # Server timeout limit.
    # u'refreshFreq': 300,  # Device-specific update frequency
    u'showDebugInfo': False,  # Verbose debug logging?
    u'configUpdaterForceUpdate': False,
    u'configUpdaterInterval': 24,
    u'updaterEmail': "",  # Email to notify of plugin updates.
    u'updaterEmailsEnabled': False  # Notification of plugin updates wanted.
}


class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):

        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.startingUp = True
        self.pluginIsInitializing = True
        self.pluginIsShuttingDown = False
        self.prefsUpdated = False
        self.logger.info(u"")
        self.logger.info(u"{0:=^130}".format(" Initializing New Plugin Session "))
        self.logger.info(u"{0:<30} {1}".format("Plugin name:", pluginDisplayName))
        self.logger.info(u"{0:<30} {1}".format("Plugin version:", pluginVersion))
        self.logger.info(u"{0:<30} {1}".format("Plugin ID:", pluginId))
        self.logger.info(u"{0:<30} {1}".format("Indigo version:", indigo.server.version))
        self.logger.info(u"{0:<30} {1}".format("Python version:", sys.version.replace('\n', '')))
        self.logger.info(u"{0:<30} {1}".format("Python Directory:", sys.prefix.replace('\n', '')))
        self.logger.info(u"{0:<30} {1}".format("Major Problem equals: ", MajorProblem))
        self.logger.info(u"{0:=^130}".format(""))

        # Change to logging
        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)


        self.logLevel = int(self.pluginPrefs.get(u"showDebugLevel",'5'))
        self.debugLevel = self.logLevel
        self.indigo_log_handler.setLevel(self.logLevel)
        self.logger.debug(u"logLevel = " + str(self.logLevel))
        self.logger.debug(u"User prefs saved.")
        self.logger.debug(u"Debugging on (Level: {0})".format(self.debugLevel))

        self.alldeepstateclasses = '''person,   bicycle,   car,   motorcycle,   airplane,
bus,   train,   truck,   boat,   traffic light,   fire hydrant,   stop_sign,
parking meter,   bench,   bird,   cat,   dog,   horse,   sheep,   cow,   elephant,
bear,   zebra, giraffe,   backpack,   umbrella,   handbag,   tie,   suitcase,
frisbee,   skis,   snowboard, sports ball,   kite,   baseball bat,   baseball glove,
skateboard,   surfboard,   tennis racket, bottle,   wine glass,   cup,   fork,
knife,   spoon,   bowl,   banana,   apple,   sandwich,   orange, broccoli,   carrot,
hot dog,   pizza,   donot,   cake,   chair,   couch,   potted plant,   bed, dining table,
toilet,   tv,   laptop,   mouse,   remote,   keyboard,   cell phone,   microwave,
oven,   toaster,   sink,   refrigerator,   book,   clock,   vase,   scissors,   teddy bear,
hair dryer, toothbrush'''


        ## Create new Log File

        self.listCameras = {}  # use a dictionary of CameraNames False/True as to request already sent

        self.reply = False
        self.triggers = {}
        self.API = self.pluginPrefs.get('API', False)
        self.useLocal = self.pluginPrefs.get('useLocal', False)
        self.ipaddress = self.pluginPrefs.get('ipaddress', False)

        self.deviceCamerastouse = self.pluginPrefs.get('deviceCamera','')

        self.debug1 = self.pluginPrefs.get('debug1', False)
        self.debug2 = self.pluginPrefs.get('debug2', False)
        self.debug3 = self.pluginPrefs.get('debug3', False)
        self.debug4 = self.pluginPrefs.get('debug4',False)

        self.next_update_check = t.time()
        MAChome = os.path.expanduser("~") + "/"
        self.folderLocation = MAChome + "Documents/Indigo-DeepQuestAI/"
        self.folderLocationFaces = MAChome + "Documents/Indigo-DeepQuestAI/Faces/"
        self.folderLocationCars = MAChome + "Documents/Indigo-DeepQuestAI/Cars/"

        self.deviceNeedsUpdated = ''

        if MajorProblem > 0:
            plugin = indigo.server.getPlugin('com.GlennNZ.indigoplugin.DeepQuestAI')

            if MajorProblem == 1:
                self.logger.error(u'Major Problem:  Restarting Plugin...')
                if plugin.isEnabled():
                    plugin.restart(waitUntilDone=False)
                self.sleep(1)
            if MajorProblem == 2:
                self.logger.error(u"{0:=^130}".format(""))
                self.logger.error(u"{0:=^130}".format(""))
                self.logger.error(u'Major Problem:   Please Disable Plugin.  Now Sleeping.  Please contact Developer.')
                self.logger.error(u"{0:=^130}".format(""))
                self.logger.error(u"{0:=^130}".format(""))
                if plugin.isEnabled():
                    # Can't disabled
                    # Can Sleep Forever Though
                    # plugin.disable()

                    self.sleep(86400)

        self.pluginIsInitializing = False


    def closedPrefsConfigUi(self, valuesDict, userCancelled):

        self.debugLog(u"closedPrefsConfigUi() method called.")

        if userCancelled:
            self.debugLog(u"User prefs dialog cancelled.")

        if not userCancelled:
            self.debugLevel = valuesDict.get('showDebugLevel', "10")
            self.debugLog(u"User prefs saved.")
            self.API = valuesDict.get('API','')
            #self.logger.error(unicode(valuesDict))
            self.useLocal = valuesDict.get('useLocal', False)
            self.ipaddress = valuesDict.get('ipaddress', False)
            self.logLevel = int(valuesDict.get("showDebugLevel",'5'))
            self.deviceCamerastouse = valuesDict.get('deviceCamera','')

            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(u"logLevel = " + str(self.logLevel))
            self.logger.debug(u"User prefs saved.")
            self.logger.debug(u"Debugging on (Level: {0})".format(self.debugLevel))

        self.logger.debug(unicode(valuesDict))
        return True

    # Start 'em up.
    def deviceStartComm(self, dev):

         self.debugLog(u"deviceStartComm() method called.")


    # Shut 'em down.
    def deviceStopComm(self, dev):

        self.debugLog(u"deviceStopComm() method called.")
        indigo.server.log(u"Stopping Enphase device: " + dev.name)

    def forceUpdate(self):
        self.updater.update(currentVersion='0.0.0')

    def checkForUpdates(self):
        if self.updater.checkForUpdate() == False:
            indigo.server.log(u"No Updates are Available")

    def updatePlugin(self):
        self.updater.update()

    def runConcurrentThread(self):

        try:


            while True:


                self.debugLog(u" ")

                for dev in indigo.devices.itervalues('self'):

                    self.debugLog(u"MainLoop:  {0}:".format(dev.name))


                self.sleep(60)

        except self.StopThread:
            self.debugLog(u'Restarting/or error. Stopping Main thread.')
            pass

    def shutdown(self):

         self.debugLog(u"shutdown() method called.")

    def startup(self):

        self.debugLog(u"Starting Plugin. startup() method called.")
        if not os.path.exists(self.folderLocation):
            os.makedirs(self.folderLocation)
        if not os.path.exists(self.folderLocationFaces):
            os.makedirs(self.folderLocationFaces)
        if not os.path.exists(self.folderLocationCars):
            os.makedirs(self.folderLocationCars)
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"broadcasterStarted", u"broadcasterStarted")
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"broadcasterShutdown", u"broadcasterShutdown")
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"motionTrue", u"motionTrue")



    def validatePrefsConfigUi(self, valuesDict):

        self.debugLog(u"validatePrefsConfigUi() method called.")

        error_msg_dict = indigo.Dict()

        # self.errorLog(u"Plugin configuration error: ")

        return True, valuesDict



    def setStatestonil(self, dev):

         self.debugLog(u'setStates to nil run')


    def refreshDataAction(self, valuesDict):
        """
        The refreshDataAction() method refreshes data for all devices based on
        a plugin menu call.
        """

        self.debugLog(u"refreshDataAction() method called.")
        self.refreshData()
        return True

    def refreshData(self):
        """
        The refreshData() method controls the updating of all plugin
        devices.
        """

        self.debugLog(u"refreshData() method called.")

        try:
            # Check to see if there have been any devices created.
            if indigo.devices.itervalues(filter="self"):

                self.debugLog(u"Updating data...")

                for dev in indigo.devices.itervalues(filter="self"):
                    self.refreshDataForDev(dev)

            else:
                indigo.server.log(u"No Client devices have been created.")

            return True

        except Exception as error:
            self.errorLog(u"Error refreshing devices. Please check settings.")
            self.errorLog(unicode(error.message))
            return False

    def refreshDataForDev(self, dev):

        if dev.configured:
            self.debugLog(u"Found configured device: {0}".format(dev.name))
        if dev.enabled:
            self.debugLog(u"   {0} is enabled.".format(dev.name))
            timeDifference = int(t.time() - t.mktime(dev.lastChanged.timetuple()))
        else:
            self.debugLog(u"    Disabled: {0}".format(dev.name))


    def refreshDataForDevAction(self, valuesDict):
        """
        The refreshDataForDevAction() method refreshes data for a selected device based on
        a plugin menu call.
        """

        self.debugLog(u"refreshDataForDevAction() method called.")

        dev = indigo.devices[valuesDict.deviceId]

        self.refreshDataForDev(dev)
        return True


    def toggleDebugEnabled(self):
        """ Toggle debug on/off. """

        self.logger.debug(u"toggleDebugEnabled() method called.")

        if self.debugLevel == int(logging.INFO):
            self.debug = True
            self.debugLevel = int(logging.DEBUG)
            self.pluginPrefs['showDebugInfo'] = True
            self.pluginPrefs['showDebugLevel'] = int(logging.DEBUG)
            self.logger.info(u"Debugging on.")
            self.logger.debug(u"Debug level: {0}".format(self.debugLevel))
            self.logLevel = int(logging.DEBUG)
            self.logger.debug(u"New logLevel = " + str(self.logLevel))
            self.indigo_log_handler.setLevel(self.logLevel)

        else:
            self.debug = False
            self.debugLevel = int(logging.INFO)
            self.pluginPrefs['showDebugInfo'] = False
            self.pluginPrefs['showDebugLevel'] = int(logging.INFO)
            self.logger.info(u"Debugging off.  Debug level: {0}".format(self.debugLevel))
            self.logLevel = int(logging.INFO)
            self.logger.debug(u"New logLevel = " + str(self.logLevel))
            self.indigo_log_handler.setLevel(self.logLevel)

    def toggleDebugMax(self):
        """ Toggle debug on/off. """


        self.logger.debug(u"toggleDebugMax() method called.")

        self.debug = True
        self.debugLevel = int(logging.DEBUG)
        self.pluginPrefs['showDebugInfo'] = True
        self.pluginPrefs['showDebugLevel'] = int(logging.DEBUG)
        self.logger.info(u"Debugging on.")
        self.logger.debug(u"Debug level: {0}".format(self.debugLevel))
        self.logLevel = int(logging.DEBUG)
        self.logger.debug(u"New logLevel = " + str(self.logLevel))
        self.indigo_log_handler.setLevel(self.logLevel)

############ Broadcast Subscribe stuff

    def broadcasterStarted(self):
        self.logger.debug("received broadcasterStarted message")
        return

    def broadcasterShutdown(self):
        self.logger.debug("received broadcasterShutdown message")
        return

    def checkcars(self, liveurlphoto, ipaddress, cameraname, image, x_min,x_max,y_min,y_max):
        self.logger.debug('Now checking for Cars....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:
            cropped = image.crop((x_min, y_min, x_max, y_max))
            cropped.save(self.folderLocationCars + "DeepStateCars_{}_{}.jpg".format(cameraname, str(t.time())))

        except Exception as ex:
            self.logger.debug('Error Saving to Vehicles: ' + unicode(ex))

    def checkfaces2(self, liveurlphoto, ipaddress, cameraname, image, x_min,x_max,y_min,y_max):
        self.logger.debug('Now checking for Faces 2/Cropping only....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:
            cropped = image.crop((x_min, y_min, x_max, y_max))
            cropped.save(self.folderLocationFaces + "DeepStateFaces_{}_{}.jpg".format(cameraname, str(t.time())))

        except Exception as ex:
            self.logger.debug('Error Saving to Vehicles: ' + unicode(ex))

    def checkfaces(self, cropped, ipaddress, cameraname, image):
        self.logger.error('Now checking for Faces....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:

            image_file = StringIO.StringIO()
            cropped.save(image_file,'JPEG')
            image_file.seek(0)

            response = requests.post(urltosend, files={"image": image_file}, timeout=30).json()
            self.logger.error(unicode(response))
            self.listCameras[cameraname] = False  # set to false as already run.

            if response['success'] == True:
                for object in response["predictions"]:
                    cropped.save(self.folderLocationFaces + "DeepStateFaces_{}_{}.jpg".format(cameraname, str(t.time()) ) )

            else:
                self.logger.debug('DeepState Faces Request failed:')

        except Exception as ex:
            self.logger.debug('Error sending to Deepstate: ' + unicode(ex))
            self.reply = False


    def motionTrue(self, arg):
        self.logger.debug("received Camera motionTrue message: %s" % (arg) )


        urlphoto = arg[0]
        cameraname = arg[1]
        pathimage = arg[2]
        updatetime = arg[3]
        newimagedownloaded = arg[4]
        indigodeviceid = arg[5]

        if str(indigodeviceid) not in self.deviceCamerastouse:
            self.logger.debug('Camera not enabled within DeepState Config Settings/Ignored.')
            #self.logger.debug(unicode(self.deviceCamerastouse))
            return


        basepath = os.path.dirname(pathimage)

        #self.logger.debug(basepath)

        ## self.listCameras - add request to current list
        self.logger.debug(unicode(self.listCameras))

        if cameraname not in self.listCameras:
            # no request running for this camera
            # add to self.listCameras
            self.listCameras[cameraname]=True
        else:
            if self.listCameras[cameraname]:  ## request already running
                self.logger.debug('Current request already running for this Camera: Aborted.')
                return
            else:
                self.listCameras[cameraname]=True
                # add requesting running and continue
        if self.useLocal:
            ipaddress = 'localhost'
        else:
            ipaddress = self.ipaddress

        urltosend = 'http://'+ipaddress+ ":7188/v1/vision/detection"
        self.logger.debug(urltosend)

        try:
            # pull image from url...
            liveurlphoto = requests.get(urlphoto)

            urlimage = Image.open(StringIO.StringIO(liveurlphoto.content))
#           image_data = urlimage
            #image_data = open(pathimage, "rb").read()
            image = urlimage
            imagefresh = Image.open(StringIO.StringIO(liveurlphoto.content))
             #   Image.open(pathimage).convert('RGB')

            self.reply = True
            response = requests.post(urltosend,files={"image":liveurlphoto.content},timeout=30).json()
            self.logger.debug(unicode(response))
            self.listCameras[cameraname]=False  # set to false as already run.

            vehicles = ['bicycle','car','motorcycle','bus','train']
            anyobjectfound =False
            if response['success']==True:
                for object in response["predictions"]:
                    carfound = False
                    label = object["label"]
                    y_max = int(object["y_max"])
                    y_min = int(object["y_min"])
                    x_max = int(object["x_max"])
                    x_min = int(object["x_min"])
                    confidence = float(object['confidence'])
                    if confidence > 0.6:
                        objectfound = True
                        if label in vehicles:
                            carfound = True
                    draw = ImageDraw.Draw(image)
                    draw.rectangle(((x_min,y_min),(x_max,y_max)),fill=None,outline='red', width=3)
                    labelonbox = str(label)+' '+str(confidence)
                    draw.text((x_min+5,y_min+5),labelonbox, font=ImageFont.truetype(font='Arial.ttf', size=18) ,fill='red')
                    cropped = imagefresh.crop((x_min, y_min, x_max, y_max))
                    if label == 'person':
                        ## check for faces
                        self.checkfaces2(cropped, ipaddress,cameraname, imagefresh, x_min,x_max,y_min,y_max)
                        image.save(self.folderLocationFaces+"DeepStateFacesFull_{}_{}.jpg".format(cameraname, str(t.time())))
                    if carfound:
                        self.checkcars(liveurlphoto, ipaddress,cameraname, imagefresh, x_min,x_max,y_min,y_max)
                        image.save(self.folderLocationCars + "DeepStateCarsFull_{}_{}.jpg".format(cameraname, str(t.time())))
                        carfound = False

                if anyobjectfound:
                    #image.save(self.folderLocation+"/DeepState_{}_{}.jpg".format(cameraname, label))
                    anyobjectfound = False

            else:
                self.logger.debug('DeepState Request failed:')

        except Exception as ex:
            self.logger.debug('Error sending to Deepstate: '+unicode(ex))
            self.reply = False