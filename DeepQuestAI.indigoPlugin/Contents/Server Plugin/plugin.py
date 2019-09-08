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
from Queue import *
import threading
import uuid

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

class deepstateitem:
    def __init__(self, path, indigodeviceid, cameraname):
        self.path = path
        self.indigodeviceid = indigodeviceid
        self.cameraname = cameraname


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

        #self.listCameras = {}  # use a dictionary of CameraNames False/True as to request already sent

        self.reply = False
        self.triggers = {}

        self.triggersTriggered = {}

        self.API = self.pluginPrefs.get('API', False)
        self.useLocal = self.pluginPrefs.get('useLocal', False)
        self.ipaddress = self.pluginPrefs.get('ipaddress', False)
        self.superCharge = self.pluginPrefs.get('superCharge', False)
        self.superChargedelay = self.pluginPrefs.get('superChargedelay', 2)
        self.superChargeimageno = self.pluginPrefs.get('superChargeimageno', 5)  ## actually means number of images

        self.port = self.pluginPrefs.get('port', '7188')
        self.deviceCamerastouse = self.pluginPrefs.get('deviceCamera','')

        self.imageTimeout = 10
        self.serverTimeout = 5
        self.debug1 = self.pluginPrefs.get('debug1', False)
        self.debug2 = self.pluginPrefs.get('debug2', False)
        self.debug3 = self.pluginPrefs.get('debug3', False)
        self.debug4 = self.pluginPrefs.get('debug4',False)
        self.debug5 = self.pluginPrefs.get('debug5', False)


        self.next_update_check = t.time()
        MAChome = os.path.expanduser("~") + "/"
        self.folderLocation = MAChome + "Documents/Indigo-DeepQuestAI/"
        self.folderLocationFaces = MAChome + "Documents/Indigo-DeepQuestAI/Faces/"
        self.folderLocationCars = MAChome + "Documents/Indigo-DeepQuestAI/Cars/"
        self.folderLocationTemp = MAChome + "Documents/Indigo-DeepQuestAI/Temp/"

        self.deviceNeedsUpdated = ''

        self.que = Queue()

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
            self.superCharge = valuesDict.get('superCharge', False)
            self.superChargeimageno = valuesDict.get('superChargeimageno', 3)
            self.superChargedelay = valuesDict.get('superChargedelay', 3)
            self.port = valuesDict.get('port', '7188')
            self.logLevel = int(valuesDict.get("showDebugLevel",'5'))
            self.deviceCamerastouse = valuesDict.get('deviceCamera','')
            self.debug1 = valuesDict.get('debug1', False)
            self.debug2 = valuesDict.get('debug2', False)
            self.debug3 = valuesDict.get('debug3', False)
            self.debug4 = valuesDict.get('debug4', False)
            self.debug5 = valuesDict.get('debug5', False)


            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(u"logLevel = " + str(self.logLevel))
            self.logger.debug(u"User prefs saved.")
            self.logger.debug(u"Debugging on (Level: {0})".format(self.debugLevel))

        self.logger.debug(unicode(valuesDict))
        return True

    # Start 'em up.
    def deviceStartComm(self, dev):

         self.debugLog(u"deviceStartComm() method called.")

         dev.stateListOrDisplayStateIdChanged()

    # Shut 'em down.
    def deviceStopComm(self, dev):

        self.debugLog(u"deviceStopComm() method called.")
        indigo.server.log(u"Stopping device: " + dev.name)

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
        if not os.path.exists(self.folderLocationTemp):
            os.makedirs(self.folderLocationTemp)

        self.deleteTempfiles()

        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"broadcasterStarted", u"broadcasterStarted")
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"broadcasterShutdown", u"broadcasterShutdown")
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"motionTrue", u"motionTrue")

        self.logger.debug(u'Starting DeepState send Thread:')
        ImageThread = threading.Thread(target=self.threadSendtodeepstate )
        ImageThread.start()



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

    def deleteTempfiles(self):
        self.logger.debug(u'Deleting temp files if any.')
        for the_file in os.listdir(self.folderLocationTemp):
            file_path = os.path.join(self.folderLocationTemp, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                self.logger.exception(e)

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

    def checkcars(self, liveurlphoto, ipaddress, cameraname, image, indigodeviceid, confidence, x_min,x_max,y_min,y_max):
        self.logger.debug('Now checking for Cars....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:
            cropped = image.crop((x_min, y_min, x_max, y_max))
            filename = self.folderLocationCars + "DeepStateCars_{}_{}.jpg".format(cameraname, str(t.time()))
            cropped.save(filename)

            self.checkDevices(cropped, 'car', ipaddress, cameraname, image, filename, confidence)
            self.triggerCheck('car', cameraname, indigodeviceid, 'objectTrigger', confidence)
        except Exception as ex:
            self.logger.debug('Error Saving to Vehicles: ' + unicode(ex))

    def checkfaces2(self, liveurlphoto, ipaddress, cameraname, image, indigodeviceid, confidence, x_min,x_max,y_min,y_max):
        self.logger.debug('Now checking for Faces 2/Cropping only....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:
            cropped = image.crop((x_min, y_min, x_max, y_max))
            filename= self.folderLocationFaces + "DeepStateFaces_{}_{}.jpg".format(cameraname, str(t.time()))
            cropped.save(filename)

            self.checkDevices(cropped, 'person', ipaddress, cameraname, image, filename, confidence)
            self.triggerCheck('person', cameraname, indigodeviceid, 'objectTrigger', confidence)

        except Exception as ex:
            self.logger.debug('Error Saving to Vehicles: ' + unicode(ex))

    def checkDevices(self, cropped, objectname, ipaddress, cameraname, image, filename, confidence):
        self.logger.debug('CheckDevices run')

        for dev in indigo.devices.itervalues("self.DeepStateObject"):
            if dev.enabled:
                objectName = dev.pluginProps['objectType']
                self.logger.debug('ObjectType:'+unicode(objectName))
                if objectName == objectname:
                    dev.updateStateOnServer('objectType', value=objectname)
                    dev.updateStateOnServer('cameraFound', value=cameraname)
                    dev.updateStateOnServer('imageLink', value=filename)
                    time = t.time()
                    update_time = t.strftime('%c')
                    dev.updateStateOnServer('timeLastFound', value=time)
                    dev.updateStateOnServer('confidence', value=confidence)
                    dev.updateStateOnServer('date', value=update_time)

    def checkfaces(self, cropped, ipaddress, cameraname, image):
        self.logger.error('Now checking for Faces....')

        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:

            image_file = StringIO.StringIO()
            cropped.save(image_file,'JPEG')
            image_file.seek(0)

            response = requests.post(urltosend, files={"image": image_file}, timeout=30).json()
            self.logger.error(unicode(response))
            #self.listCameras[cameraname] = False  # set to false as already run.

            if response['success'] == True:
                for object in response["predictions"]:
                    filename = self.folderLocationFaces + "DeepStateFaces_{}_{}.jpg".format(cameraname, str(t.time() )  )
                    cropped.save(filename)

            else:
                self.logger.debug('DeepState Faces Request failed:')

            # update devices
            self.checkDevices(cropped, 'person',ipaddress, cameraname, image, filename)
            self.triggerCheck('person', cameraname, 'objectTrigger')

        except Exception as ex:
            self.logger.debug('Error sending to Deepstate: ' + unicode(ex))
            self.reply = False

    ##################  Triggers

    def triggerStartProcessing(self, trigger):
        self.logger.debug("Adding Trigger %s (%d) - %s" % (trigger.name, trigger.id, trigger.pluginTypeId))
        assert trigger.id not in self.triggers
        self.triggers[trigger.id] = trigger

    def triggerStopProcessing(self, trigger):
        self.logger.debug("Removing Trigger %s (%d)" % (trigger.name, trigger.id))
        assert trigger.id in self.triggers
        del self.triggers[trigger.id]


    def triggerCheck(self, objectname, cameraname, indigodeviceid, event, confidence):

        if self.debug2:
            self.logger.debug('triggerCheck run. Object:'+unicode(objectname)+' Camera:' + unicode(cameraname) + ' Event:' + unicode(event))
        try:
            if self.pluginIsInitializing:
                self.logger.info(u'Trigger: Ignore as Plugin Just started.')
                return

            for triggerId, trigger in sorted(self.triggers.iteritems()):
                if self.debug5:
                    self.logger.debug("Checking Trigger %s (%s), Type: %s, CameraName: %s, Event: %s, Confidence:%s" % (
                    trigger.name, trigger.id, trigger.pluginTypeId, cameraname, event, confidence))

                # Change to List for all Cameras
                if (trigger.pluginTypeId == 'objectFound'):
                    if str(trigger.pluginProps['objectType'])== str(objectname):
                        triggerconfidence = trigger.pluginProps.get('confidence',0.6)

                        if str(indigodeviceid) in trigger.pluginProps['deviceCamera'] and float(confidence) >= float(triggerconfidence):
                            # check if cameraname within list - although might be device ID
                            if self.debug5:
                                self.logger.debug("===== Executing objectFound Trigger %s (%d) and confidence is %s" % (
                                    trigger.name, trigger.id, confidence))
                                #if self.debug4:
                                    #self.logger.debug(u'deviceCamera' + unicode(trigger.pluginProps['deviceCamera']))
                                    #self.logger.debug(u'indigodeviceid:' + unicode(indigodeviceid))
                            if trigger.id not in self.triggersTriggered:
                                # no previous triggers
                                # add to self.triggersTriggered
                                self.triggersTriggered[trigger.id] = t.time()  ## add utc timestamp
                                ## run trigger as no previous times of running
                                if self.debug5:
                                    self.logger.debug(u'self.triggersTriggered:'+unicode(self.triggersTriggered))
                                    self.logger.debug(u'Running Trigger as just added.')
                                indigo.trigger.execute(trigger)
                            else:
                                if self.debug5:
                                    self.logger.debug(u'Trigger.ID found and self.triggersTriggered:' + unicode(self.triggersTriggered))
                                if float(t.time()) >=  float(self.triggersTriggered[trigger.id]) +int( trigger.pluginProps.get('dontretrigger',10) ):  ## request already running
                                    # okay more than 10 seconds ago, re-run trigger and update time
                                    self.triggersTriggered[trigger.id] = t.time()  ## add utc timestamp
                                    if self.debug5:
                                        self.logger.debug(u'self.triggersTriggered:' + unicode(self.triggersTriggered))
                                    indigo.trigger.execute(trigger)
                                else:
                                    if self.debug5:
                                        self.logger.error(u'Trigger :'+ unicode(trigger.name) + u' not run again, as current time='+unicode(t.time())+u' and time past run='+unicode(self.triggersTriggered[trigger.id]))
                                    # add requesting running and continue



                elif self.debug2:
                    self.logger.debug(
                        "Not Run Trigger Type %s (%d), %s" % (trigger.name, trigger.id, trigger.pluginTypeId))

        except:
            self.logger.exception(u'Caught Exception within Trigger Check')
            return

    def threadDownloadImage(self, path, url):
        if self.debug2:
            self.logger.debug(u'threadDownloadImages called.'+u' & Number of Active Threads:' + unicode(
                    threading.activeCount()))
        try:
             # add timer and move to chunk download...
             start = t.time()
             r = requests.get(url, stream=True, timeout=self.serverTimeout)
             if r.status_code == 200:
                 # self.logger.debug(u'Yah Code 200....')
                 with open(path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                        if t.time()>(start +self.imageTimeout):
                            self.logger.error(u'Download Image Taking too long.  Aborted.  ?Network issue')
                            break
                    if self.debug2:
                        self.logger.debug(u'Saved Image attempt for:'+unicode(path)+u' in [seconds]:'+unicode(t.time()-start))
             else:
                 self.logger.debug(u'Issue Downloading Image. Failed.')

        except requests.exceptions.Timeout:
            self.logger.debug(u'threadDownloadImage has timed out and cannot connect to BI Server.')
            pass

        except requests.exceptions.ConnectionError:
            self.logger.debug(u'connectServer has a Connection Error and cannot connect to BI Server.')
            self.sleep(5)
            pass

        except:
            self.logger.exception(u'Caught Exception in threadDownloadImage')

    def threadSendtodeepstate(self):
        if self.debug2:
            self.logger.debug(u'threadSendtodeepState called.'+u' & Number of Active Threads:' + unicode(
                    threading.activeCount()))
        while True:
            try:
                item = self.que.get()
                cameraname= item.cameraname
                indigodeviceid = item.indigodeviceid
                path = item.path
                if self.debug2:
                    self.logger.debug(u'Thread:SendtoDeepstate: Processing next item in que: Cameraname:'+unicode(cameraname)+', image file:'+unicode(path)+', from IndigoID:'+unicode(indigodeviceid))

                if self.useLocal:
                    ipaddress = 'localhost'
                else:
                    ipaddress = self.ipaddress

                urltosend = 'http://' + ipaddress + ":" + self.port + "/v1/vision/detection"
                if self.debug1:
                    self.logger.debug(urltosend)

                liveurlphoto = open(path, 'rb').read()
                image = Image.open(path)
                imagefresh = Image.open(path)

                self.reply = True
                response = requests.post(urltosend, files={"image": liveurlphoto}, timeout=30).json()
                self.logger.debug(unicode(response))
                #self.listCameras[cameraname] = False  # set to false as already run.

                vehicles = ['bicycle', 'car', 'motorcycle', 'bus', 'train']
                anyobjectfound = False
                if response['success'] == True:
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
                        draw.rectangle(((x_min, y_min), (x_max, y_max)), fill=None, outline='red', width=3)
                        labelonbox = str(label) + ' ' + str(confidence)
                        draw.text((x_min + 5, y_min + 5), labelonbox, font=ImageFont.truetype(font='Arial.ttf', size=18),
                                  fill='red')
                        cropped = imagefresh.crop((x_min, y_min, x_max, y_max))
                        if label == 'person':
                            ## check for faces
                            self.checkfaces2(cropped, ipaddress, cameraname, imagefresh, indigodeviceid, confidence, x_min, x_max, y_min, y_max)
                            image.save(
                                self.folderLocationFaces + "DeepStateFacesFull_{}_{}.jpg".format(cameraname, str(t.time())))
                        if carfound:
                            self.checkcars(liveurlphoto, ipaddress, cameraname, imagefresh, indigodeviceid, confidence,x_min, x_max,
                                           y_min, y_max)
                            image.save(
                                self.folderLocationCars + "DeepStateCarsFull_{}_{}.jpg".format(cameraname, str(t.time())))
                            carfound = False

                    if anyobjectfound:
                        # image.save(self.folderLocation+"/DeepState_{}_{}.jpg".format(cameraname, label))
                        anyobjectfound = False

                else:
                    self.logger.debug(u'Thread:SendtoDeepstate: DeepState Request failed:')

                self.que.task_done()
                if os.path.exists(path):
                    os.remove(path)
                else:
                    self.logger.error(u"Thread:SendtoDeepstate: Error: deleting temporary file: it appears the file does not exist.  Path:"+unicode(path))

            except Exception as ex:
                self.logger.exception(u'Thread:SendtoDeepstate:Error sending to Deepstate: ' + unicode(ex))
                self.reply = False

    def motionTrue(self, arg):
        if self.debug3:
            self.logger.debug(u"received Camera motionTrue message: %s" % (arg) )
        try:
            urlphoto = arg[0]
            cameraname = arg[1]
            pathimage = arg[2]
            updatetime = arg[3]
            newimagedownloaded = arg[4]
            indigodeviceid = arg[5]

            if str(indigodeviceid) not in self.deviceCamerastouse:
                if self.debug1:
                    self.logger.debug('Camera not enabled within DeepState Config Settings/Ignored.')
                #self.logger.debug(unicode(self.deviceCamerastouse))
                return

            motionTrue = threading.Thread(target=self.threadaddtoQue, args=[urlphoto, cameraname,indigodeviceid])
            motionTrue.start()
            # given delayed images over 10 seconds or even longer need to thread below
            return

        except Exception as ex:
            self.logger.exception(u'Exception caught in motion true:'+unicode(ex))

    def threadaddtoQue(self, urlphoto,cameraname,indigodeviceid):
        if self.debug3:
            self.logger.debug(u'Thread:AdddtoQue called.' + u' & Number of Active Threads:' + unicode(
                threading.activeCount()))
        try:
            if self.superCharge == False:
                path = self.folderLocationTemp + 'TempFile_{}'.format(uuid.uuid4())
                ImageThread = threading.Thread(target=self.threadDownloadImage, args=[path, urlphoto])
                ImageThread.start()
                self.sleep(0.5)
                item = deepstateitem(path, indigodeviceid, cameraname)
                if self.debug1:
                    self.logger.debug(u'Putting item into DeepState Que: Item:'+unicode(item))
                self.que.put(item)
            else:
                numberofseconds = range( int(self.superChargeimageno) )  #seconds here changed usage to number of images
                for n in numberofseconds:
                    self.logger.error(u'Downloading Images:  Image:'+unicode(n) +u' for Camera:'+unicode(cameraname) )
                    path = self.folderLocationTemp + 'TempFile_{}'.format(uuid.uuid4())
                    ImageThread = threading.Thread(target=self.threadDownloadImage,
                                               args=[path, urlphoto])
                    ImageThread.start()
                    self.sleep(int(self.superChargedelay))
                    self.sleep(0.5)#sleep for the delay
                    item = deepstateitem(path, indigodeviceid, cameraname)
                    if self.debug1:
                        self.logger.debug(u'Putting item into DeepState Que: Item.Path:'+unicode(item.path))
                    self.que.put(item)

            return

        except Exception as e:
            self.logger.exception(u'Exception caught in Thread Add to Que')

