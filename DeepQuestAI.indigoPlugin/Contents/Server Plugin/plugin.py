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
from shutil import copyfile

from PIL import Image,ImageDraw,ImageFont
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#from SocketServer import ThreadingMixIn
#from os import curdir, sep
import subprocess
import plistlib

import glob

from contextlib import contextmanager

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
    def __init__(self, path, indigodeviceid, cameraname, utctime, external, superchargeImage, alertimage):
        self.path = path
        self.indigodeviceid = indigodeviceid
        self.cameraname = cameraname
        self.utctime = utctime
        self.external = external
        self.superchargeImage = superchargeImage
        self.alertimage = alertimage

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):

        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
        self.startingUp = True
        self.pluginIsInitializing = True
        self.pluginIsShuttingDown = False

        self.pluginneedsrestart = False

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

        # Change to logging
        pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t[%(levelname)8s] %(name)20s.%(funcName)-25s%(msg)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
        self.plugin_file_handler.setFormatter(pfmt)

        self.previoustimeDelay = 0

        self.pathtoPlugin = os.getcwd()

        self.deepstatetimeouts =0

        self.pathtoNotFound = self.pathtoPlugin + '/Images/notfoundimage.jpg'

        self.logger.info(u"{0:<30} {1}".format("Install Path :", self.pathtoPlugin.replace('\n', '')))

        self.logger.info(u"{0:=^130}".format(""))
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
        self.deepstateIssue = False
        self.triggersTriggered = {}

        self.API = self.pluginPrefs.get('API', False)
        self.useLocal = self.pluginPrefs.get('useLocal', False)
        self.ipaddress = self.pluginPrefs.get('ipaddress', '')
        self.superCharge = self.pluginPrefs.get('superCharge', False)

        self.useRAMdisk = self.pluginPrefs.get('useRAMdisk',False)

        self.confidenceMain = self.pluginPrefs.get('confidenceMain', 0.7)
        self.imageScale = self.pluginPrefs.get('imageScale', 100)
        self.superChargedelay = self.pluginPrefs.get('superChargedelay', 2)
        self.superChargeimageno = self.pluginPrefs.get('superChargeimageno', 5)  ## actually means number of images
        self.timeLimit = self.pluginPrefs.get('timeLimit', 60)

        self.httpserver = self.pluginPrefs.get('httpserver', True)
        self.httpport = self.pluginPrefs.get('httpport',4142)


        self.port = self.pluginPrefs.get('port', '7188')
        self.deviceCamerastouse = self.pluginPrefs.get('deviceCamera','')

        # below for http server
        self.HTMLimageNo = 0
        self.HTMLlastObject = 'unknown'
        self.HTMLarchivelastObject = 'unknown'
        self.HTMLlistFiles = []
        #self.imageNoCar = 0
        #self.imageNoCarCrop = 0
        #self.imageNoPerson = 0
        #self.imageNoPersonCrop = 0

        self.copyfilescurrently = False
        self.RAMdevice =''
        self.RAMpath = ''

        self.imageTimeout = 10
        self.serverTimeout = 7
        self.debug1 = self.pluginPrefs.get('debug1', False)
        self.debug2 = self.pluginPrefs.get('debug2', False)
        self.debug3 = self.pluginPrefs.get('debug3', False)
        self.debug4 = self.pluginPrefs.get('debug4',False)
        self.debug5 = self.pluginPrefs.get('debug5', False)

        self.mainSkippedImages = 0
        self.mainProcessedImages = 0
        self.mainTimeLastRun = ''
        self.mainBytesProcessed = float(0)
        self.mainDataProcessed = 'Unknown'

        self.next_update_check = t.time()
        MAChome = os.path.expanduser("~") + "/"

        self.saveDirectory = self.pluginPrefs.get('directory', '')
        self.archiveDirectory = self.pluginPrefs.get('archivedirectory', '')
        self.tempDirectory = self.pluginPrefs.get('tempdirectory','')
        # default below
        self.folderLocation = MAChome + "Documents/Indigo-DeepQuestAI/"
        #self.folderLocationFaces = MAChome + "Documents/Indigo-DeepQuestAI/Faces/"
        #self.folderLocationCars = MAChome + "Documents/Indigo-DeepQuestAI/Cars/"
        #self.folderLocationTemp = MAChome + "Documents/Indigo-DeepQuestAI/Temp/"

        self.archiveMounted = False

        if self.saveDirectory == '':
            self.saveDirectory = self.folderLocation
            self.logger.debug(u'Self.SaveDirectory changed:'+self.saveDirectory)
            self.pluginPrefs['directory'] = self.saveDirectory
        try:
            if not os.path.exists(self.saveDirectory):
                os.makedirs(self.saveDirectory)
        except:
            self.logger.error(u'Error Accessing Save Directory.  Using Default:'+unicode(self.folderLocation))
            self.saveDirectory = self.folderLocation
            self.pluginPrefs['directory'] = self.saveDirectory
            pass

        if self.tempDirectory == '':
            self.tempDirectory = self.folderLocation +'Temp/'
            self.logger.debug(u'Self.tempDirectory changed:'+self.tempDirectory)
            self.pluginPrefs['tempdirectory'] = self.tempDirectory
        try:
            if self.useRAMdisk == False:
                if not os.path.exists(self.tempDirectory):
                    os.makedirs(self.tempDirectory)
        except:
            self.logger.error(u'Error Accessing Temp Directory.  Using Default:'+unicode(self.folderLocation))
            self.tempDirectory = self.folderLocation + 'Temp/'
            self.pluginPrefs['tempdirectory'] = self.tempDirectory
            pass

        self.folderLocationTemp = self.tempDirectory

        if self.debug3:
            self.logger.debug(u'Path to Image Not Found equals:'+self.pathtoNotFound)

        self.deviceNeedsUpdated = ''

        self.que = Queue()
        self.quesize = 0

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

            pluginneedsrestart = False

            self.debugLevel = valuesDict.get('showDebugLevel', "10")
            self.debugLog(u"User prefs saved.")
            self.API = valuesDict.get('API','')
            #self.logger.error(unicode(valuesDict))
            self.useLocal = valuesDict.get('useLocal', False)
            self.ipaddress = valuesDict.get('ipaddress', '')
            self.superCharge = valuesDict.get('superCharge', False)

            if valuesDict.get('useRAMdisk',False) == False and self.useRAMdisk:
                self.pluginneedsrestart = True
                ## if enabling Ramdisk need to restart
            if valuesDict.get('useRAMdisk', False) == True and self.useRAMdisk == False:
                self.pluginneedsrestart = True

            self.useRAMdisk = valuesDict.get('useRAMdisk',False)

            self.confidenceMain = valuesDict.get('confidenceMain', 0.7)
            self.imageScale = valuesDict.get('imageScale', 100)
            self.superChargeimageno = valuesDict.get('superChargeimageno', 3)
            self.timeLimit = valuesDict.get('timeLimit', 60)

            self.superChargedelay = valuesDict.get('superChargedelay', 3)
            self.port = valuesDict.get('port', '7188')
            self.logLevel = int(valuesDict.get("showDebugLevel",'5'))
            self.deviceCamerastouse = valuesDict.get('deviceCamera','')

            self.httpport = valuesDict.get('httpport',4142)
            self.httpserver = valuesDict.get('httpserver',True)

            self.debug1 = valuesDict.get('debug1', False)
            self.debug2 = valuesDict.get('debug2', False)
            self.debug3 = valuesDict.get('debug3', False)
            self.debug4 = valuesDict.get('debug4', False)
            self.debug5 = valuesDict.get('debug5', False)

            self.saveDirectory = valuesDict.get('directory', '')
            self.archiveDirectory = valuesDict.get('archivedirectory', '')
            self.tempDirectory = valuesDict.get('tempdirectory','')

            self.indigo_log_handler.setLevel(self.logLevel)
            self.logger.debug(u"logLevel = " + str(self.logLevel))
            self.logger.debug(u"User prefs saved.")
            self.logger.debug(u"Debugging on (Level: {0})".format(self.debugLevel))

            #if pluginneedsrestart:
                #self.restartPlugin()

        self.logger.debug(unicode(valuesDict))
        return True
    def generateMain(self,valuesDict):

        self.logger.debug(u'generateMain Devices Called.')
        deviceName = 'DeepState Main Service'
        FoundDevice = False
        for dev in indigo.devices.itervalues('self.DeepStateService'):
            FoundDevice = True

        if FoundDevice == False:
            self.logger.info(u'No matching Main Device Found - creating one:')
            self.logger.info(unicode(deviceName) + '  created Device')
            device = indigo.device.create(address=deviceName, deviceTypeId='DeepStateService', name=deviceName,
                                      protocol=indigo.kProtocol.Plugin, folder='DeepState AI')
            self.sleep(1)
            stateList = [
                {'key': 'deviceIsOnline', 'value': True, 'uiValue': 'Online'},
                {'key': 'imagesSkipped', 'value': self.mainSkippedImages},
                {'key': 'imagesProcessed', 'value': self.mainProcessedImages},
                {'key': 'ipaddress', 'value': self.ipaddress},
                {'key': 'timeLastrun', 'value': self.mainTimeLastRun},
                {'key': 'currentQue', 'value': self.quesize},
                {'key': 'currentDelay', 'value': self.previoustimeDelay}
            ]
            device.updateStatesOnServer(stateList)
            #device.updateStateOnServer('deviceIsOnline', value=True, uiValue="Online")


    # Start 'em up.
    def deviceStartComm(self, dev):

        self.debugLog(u"deviceStartComm() method called.")
        dev.stateListOrDisplayStateIdChanged()

        if dev.deviceTypeId == 'DeepStateObject':
            if dev.enabled:
                objectName = dev.pluginProps['objectType']
                if objectName =='other':
                    objectName = dev.pluginProps['objectOther']
                self.logger.debug('Checking directory for ObjectType:' + unicode(objectName))
                self.createFolder(objectName)

        if dev.deviceTypeId== "DeepStateService":
            #self.logger.error(unicode(dev))
            if dev.enabled:
                stateList = [
                    {'key': 'deviceIsOnline', 'value': True},
                    {'key': 'ipaddress', 'value': self.ipaddress},
                    {'key': 'timeLastrun', 'value': self.mainTimeLastRun},
                    {'key': 'currentQue', 'value': self.quesize},
                    {'key': 'currentDelay', 'value': self.previoustimeDelay}
                ]
                dev.updateStatesOnServer(stateList)
                try:
                    self.mainProcessedImages = int(dev.states['imagesProcessed'])
                    self.mainSkippedImages = int(dev.states['imagesSkipped'])
                    self.mainBytesProcessed = float(dev.states['bytesProcessed'])
                    self.mainDataProcessed = str(dev.states['dataProcessed'])
                except:
                    self.logger.debug(u'Error reading images Processed/Skipped states, setting to zero')
                    self.mainProcessedImages = 0
                    self.mainSkippedImages = 0
                    self.mainBytesProcessed = float(0)
                    self.mainDataProcessed = 'Unknown'

    # Shut 'em down.
    def deviceStopComm(self, dev):

        self.debugLog(u"deviceStopComm() method called.")
        indigo.server.log(u"Stopping device: " + dev.name)



    def runConcurrentThread(self):


        try:
            resetImages = t.time()+360
            restartPluginCheck = t.time() +10
            mainDeviceupdate = t.time() +10
            checkTempfiles = t.time() + 60 *60
            archiveImages = t.time() + 60*60 * 24

            while True:

                self.sleep(1)
                # below for http server
                if t.time()>resetImages:
                    self.HTMLlistFiles = []
                    self.HTMLimageNo = 0
                    resetImages = t.time()+ 360

                if t.time()>restartPluginCheck and self.pluginneedsrestart:
                    self.ejectRAMdisk()
                    self.unmountArchive()
                    self.sleep(5)
                    self.restartPlugin()

                if t.time()>mainDeviceupdate:
                    self.refreshMainDevice()
                    mainDeviceupdate = t.time()+10

                if t.time()>checkTempfiles:
                    self.checkqueandDelete()
                    checkTempfiles = t.time()+ 60*60

                if t.time()>archiveImages:
                    self.copytoArchive()
                    archiveImages = archiveImages + 60*60*24

        except self.StopThread:
            self.debugLog(u'Restarting/or error. Stopping Main thread.')
            self.ejectRAMdisk()
            self.unmountArchive()
            pass

    def shutdown(self):

        self.debugLog(u"shutdown() method called.")


    def createFolder(self,objectType):
        if self.debug2:
            self.logger.debug('Checking Directory for ObjectType')
        if not os.path.exists(self.saveDirectory+'/'+objectType):
            os.makedirs(self.saveDirectory+'/'+objectType)
            if self.debug2:
                self.logger.debug('Created directory for new Object Type:'+unicode(objectType))
        return

    def ejectRAMdisk(self):

        try:
            self.logger.debug(u'Plugin closing & Ejecting RAMdisk')
            if os.path.exists('/Volumes/DeepStateTemp'):
                #subprocess.check_output(['/usr/bin/hdiutil', 'eject', '/Volumes/DeepStateTemp'])
                #self.sleep(1)
                subprocess.check_output(['/usr/bin/hdiutil', 'detach', '/Volumes/DeepStateTemp'] )

        except Exception as ex:
            self.logger.debug(u'Caught exception Ramdisk:'+unicode(ex))
            pass

    def unmountArchive(self):
        self.logger.debug(u'Unmounting Archive')
        local_dir = self.saveDirectory + 'ARCHIVE'
        retcode = subprocess.call(["/sbin/umount", local_dir])
        if retcode != 0:
            self.logger.debug("Unmount operation failed.  retcode:" + unicode(retcode))
        else:
            self.logger.info(u'Archive successfully dismounted.')
            self.archiveMounted = False
        return


    def useArchive(self):
        self.logger.debug(u'Mounting Archive for use whilst plugin running')
        remote_dir = self.archiveDirectory
        local_dir= self.saveDirectory+'ARCHIVE'
        self.logger.debug('Mounting SMB path for archive use: remote_Dir:' + unicode(remote_dir) + '  local_Dir:' + unicode(local_dir))
        local_dir = os.path.abspath(local_dir)
        self.logger.debug('Mounting: Localdir:' + unicode(local_dir))
        retcode = subprocess.call(["/sbin/mount", "-t", "smbfs", remote_dir, local_dir])

        if retcode != 0:
            self.logger.info("Mount operation failed. retcode:" + unicode(retcode))
            return False
        else:
            self.archiveMounted = True
            self.logger.info(u'Archive SMB drive successfully mounted: '+unicode(remote_dir))
            return True

    def copytoArchive(self):
        self.logger.debug(u'Running copy thread..')

        if self.copyfilescurrently==False:
            CopyArchive = threading.Thread(target=self.ThreadcopytoArchive() )
            CopyArchive.setDaemon(True  )
            CopyArchive.start()

    def ThreadcopytoArchive(self):
        self.logger.debug(u'Thread: Copying Files to Archive.')

        if self.archiveMounted:
            try:
                self.copyfilescurrently = True
                src = self.saveDirectory
                dst = self.saveDirectory + 'ARCHIVE'
                two_days = datetime.datetime.now() - datetime.timedelta(days=2)

                # copy existing directory structure of image directories to archive
                for dirpath, dirnames, filenames in os.walk(src):
                    if 'ARCHIVE' in dirpath or 'Temp' in dirpath:
                        #self.logger.debug(u'Skip Archive/Temp directory for obvious reasons: DirPath:'+unicode(dirpath))
                        continue
                    self.logger.debug(u'Two days equals:' + unicode(two_days))
                    structure = os.path.join(dst, dirpath[len(src):])
                    if not os.path.isdir(structure):
                        os.mkdir(structure)
                        self.logger.info(u'Archive: Creating directory: Structure: '+unicode(structure)+ u'  DirectoryName:'+unicode(dirnames))
                    # create directories
                    if dirpath != src:
                    # usefilenames to copy
                        self.logger.debug(u'dirpath:' + unicode(dirpath) + u' dirnames:' + unicode( dirnames) + u' and filenames:' + unicode(filenames))
                        for f in filenames:
                            if str(f).startswith('.')==False:
                                filetime = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dirpath, f)))
                                #self.logger.debug(u'FileName:'+unicode(os.path.join(dirpath, f))+ u' and filetime:'+unicode(filetime))
                                if filetime >= two_days:
                                    #self.logger.debug(u'Two days equals:' + unicode(two_days))
                                    self.logger.debug(u'Skipping file...' + unicode( os.path.join(dirpath, f)) + u' and filetime:' + unicode(filetime))
                                    # new file skip moving
                                else:
                                    try:

                                        self.logger.debug(u'Moving file...'+unicode(os.path.join(dirpath, f)) + u' and filetime:'+unicode(filetime))
                                        shutil.copy2(os.path.join(dirpath, f), structure)
                                        # use copy2 to copy datetime info and overwrite files if they already exists
                                        os.remove(os.path.join(dirpath, f))
                                    except Exception as ex:
                                        self.logger.debug(u'Exception moving file:'+ex)
                                        pass


                self.copyfilescurrently = False
            except:
                self.logger.exception(u'copytoArchive Exception:')
                self.copyfilescurrently = False

        else:
            self.logger.info(u'Archive drive is not mounted.  Please correct and setup from Plugin Config.')
            self.logger.info(u'Check network location exists and Directory writable by selected user')



    def createRAMdisk(self):

        self.logger.debug(u'Okay doing best to create a RAMDISK for Temporary file usage: 256MB used')
        self.logger.debug(u'First ejecting disk incase still exists')
        self.ejectRAMdisk()
        self.sleep(2)

        if os.path.exists('/Volumes/DeepStateTemp'):
            self.logger.info(u'Difficult ejecting RamDISK.  Please eject manually and restart plugin')

        if self.debug3:
            self.logger.debug(u'Current Temp File location:'+self.folderLocationTemp)
        name = 'DeepStateTemp'
        size =524288   # 256 MB RAM drive

        self.RAMdevice = subprocess.check_output(
            ['/usr/bin/hdiutil', 'attach', '-nomount', 'ram://%i' % (size )]
        ).strip()
        subprocess.check_output(
            ['/usr/sbin/diskutil', 'erasevolume', 'hfsx', name, self.RAMdevice]
        )

        self.logger.debug(u'createRAMdisk  :  self.RAMdevice:'+unicode(self.RAMdevice))


        self.RAMpath = plistlib.readPlistFromString(
            subprocess.check_output(
                ['/usr/sbin/diskutil', 'info', '-plist', self.RAMdevice]
            )
        )['MountPoint']

        self.logger.debug(u'createRAMdisk  : self.RAMpath:' + unicode(self.RAMpath))

        self.logger.info(u'Please Wait 10 seconds before opening config Dialogs...')
        self.sleep(10)  # give time to finish creation of RAMDisk
        self.logger.info(u'Please continue.')
        self.tempDirectory = self.RAMpath + '/Temp/'
        self.folderLocationTemp = self.tempDirectory
        self.pluginPrefs['tempdirectory'] = self.tempDirectory
        if self.debug3:
            self.logger.debug(u'Current Temp File Now location:'+self.folderLocationTemp)

    def restartPlugin(self):

        self.logger.debug(u'Restarting Plugin')
        plugin = indigo.server.getPlugin("com.GlennNZ.indigoplugin.DeepQuestAI")
        if plugin.isEnabled():
            plugin.restart()

    def startup(self):

        self.debugLog(u"Starting Plugin. startup() method called.")

        if not os.path.exists(self.saveDirectory):
            os.makedirs(self.saveDirectory)

       # if not os.path.exists(self.folderLocationFaces):
        #    os.makedirs(self.folderLocationFaces)

      #  if not os.path.exists(self.folderLocationCars):
      #      os.makedirs(self.folderLocationCars)
        if self.useRAMdisk:
            self.createRAMdisk()

        if self.archiveDirectory != '':
            self.createFolder('ARCHIVE')
            self.useArchive()

        if not os.path.exists(self.folderLocationTemp):
            os.makedirs(self.folderLocationTemp)

        self.deleteTempfiles()

        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"broadcasterStarted", u"broadcasterStarted")
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"broadcasterShutdown", u"broadcasterShutdown")
        indigo.server.subscribeToBroadcast(kBroadcasterPluginId, u"motionTrue", u"motionTrue")

        self.logger.debug(u'Starting DeepState send Thread:')
        ImageThread = threading.Thread(target=self.threadSendtodeepstate )
        ImageThread.setDaemon(True  )
        ImageThread.start()

        serverthread = threading.Thread(target=self.listenHTTP)
        serverthread.setDaemon(True)
        serverthread.start()
        #self.listenHTTP()



    def validatePrefsConfigUi(self, valuesDict):

        self.debugLog(u"validatePrefsConfigUi() method called.")

        errorDict = indigo.Dict()

        if valuesDict.get('directory', '') != '':
            # check read/write access to directory
            if os.access(valuesDict['directory'],os.W_OK) == False:
                errorDict['directory']='No write Access to this location.'
                errorDict['showAlertText']='Error.  Cannot write to this location'
                self.logger.debug(u'DiskAccessError:  Cannot Read/Write to this location')
                return (False, valuesDict, errorDict)
            else:
                self.logger.debug(u'DiskAcces:  All Good.  Can Read/Write to this location')

        if valuesDict.get('archivedirectory', '') != '' and self.archiveMounted==False:
            # check read/write access to directory
            try:
                self.createFolder('ARCHIVE')
                self.saveDirectory = valuesDict['directory']
                self.archiveDirectory = valuesDict['archivedirectory']
                self.sleep(1)

                if self.useArchive():
                    # mounted successully
                    pass
                else:
                    self.archiveMounted = False
                    self.archiveDirectory = ''
                    errorDict['archivedirectory'] = 'Unable to access this directory.  Make sure Username password in correct format'
                    errorDict['showAlertText'] = 'Unable to setup access to SMB archive.  Please ensure network location and directory exisits'
                    return (False, valuesDict, errorDict)

            except:
                self.logger.error(u'Issue Creating Archive Access')
                errorDict['archivedirectory']='Unable to access this directory.  Make sure Username password in correct format'
                errorDict['showAlertText']= 'Unable to setup access to SMB archive'
                self.archiveDirectory =''
                self.archiveMounted = False # shouldnt be needed, easier to read
                return (False,valuesDict, errorDict)

        if valuesDict.get('archivedirectory', '') == '':
            # remove archive, dismount etc.
            if self.archiveMounted:
                self.unmountArchive()
            self.archiveDirectory = ''



        if valuesDict.get('directory','') == '':
            MAChome = os.path.expanduser("~") + "/"
            folderLocation = MAChome + "Documents/Indigo-DeepQuestAI/"
            valuesDict['directory'] = folderLocation
            self.pluginPrefs['directory'] = folderLocation
        # self.errorLog(u"Plugin configuration error: ")

        return True, valuesDict

    def validateDeviceConfigUi(self, valuesDict, typeID, devId):
        self.logger.debug(u'validateDeviceConfigUi Called')
        errorDict = indigo.Dict()

        try:
            if typeID=='DeepStateObject':
                if valuesDict['objectType']=='other':
                    if valuesDict['objectOther'] not in self.alldeepstateclasses:
                        errorDict['objectOther'] ='Objectname you have entered not within above examples'
                        return (False, valuesDict, errorDict)

                    self.logger.debug(u'Creating Save Folder for this Object Type:'+unicode(valuesDict['objectOther']) )
                    self.createFolder(valuesDict['objectOther'])

            return (True, valuesDict, errorDict)


        except ValueError:
            self.logger.debug(u'Error in Validate')
            return (False, valuesDict, errorDict)
        except:
            self.logger.exception(u'Caught Error in Device Validate')
            return (False, valuesDict, errorDict)

    def validateEventConfigUi(self, valuesDict, typeID, devId):
        self.logger.debug(u'validateEventConfigUi Called')
        errorDict = indigo.Dict()

        try:
            if typeID=='objectFound':
                if valuesDict['objectType']=='other':
                    if valuesDict['objectOther'] not in self.alldeepstateclasses:
                        errorDict['objectOther'] ='Objectname you have entered not within above examples'
                        return (False, valuesDict, errorDict)
            if self.debug5:
                self.logger.debug(u'Event Dict:'+unicode(valuesDict))
            return (True, valuesDict, errorDict)

        except ValueError:
            self.logger.debug(u'Error in Validate')
            return (False, valuesDict, errorDict)
        except:
            self.logger.exception(u'Caught Error in Event Validate')
            return (False, valuesDict, errorDict)


    def checkqueandDelete(self):
        self.logger.debug(u'Checking for left over Temp files..')
        if self.quesize == 0:
            self.logger.debug(u'Que is empty, so deleting all Temp files...')
            self.deleteTempfiles()



    def refreshMainDevice(self):
        """
        The refreshData() method controls the updating of all plugin
        devices.
        """

        #self.debugLog(u"refreshMainDevice() method called.")

        try:
            # Check to see if there have been any devices created.
            for dev in indigo.devices.itervalues(filter="self"):
                if dev.deviceTypeId == 'DeepStateService':
                    self.refreshDataForDev(dev)

            return True

        except Exception as error:
            self.errorLog(u"Error refreshing devices. Please check settings.")
            self.errorLog(unicode(error.message))
            return False

    def refreshDataForDev(self, dev):

        #if dev.configured:
            #if self.debug3:
                #self.debugLog(u"Found configured device: {0}".format(dev.name))
        if dev.enabled:
            #currentque = int(self.que.qsize())
            #timeDifference = int(t.time() - t.mktime(dev.lastChanged.timetuple()))
            online = not self.deepstateIssue
            self.mainDataProcessed= self.humansize(self.mainBytesProcessed)

            stateList = [
                    {'key': 'deviceIsOnline', 'value': online},
                    {'key': 'imagesSkipped', 'value': self.mainSkippedImages},
                    {'key': 'imagesProcessed', 'value': self.mainProcessedImages},
                    {'key': 'dataProcessed', 'value': self.mainDataProcessed},
                    {'key': 'bytesProcessed', 'value': self.mainBytesProcessed},
                    {'key': 'ipaddress', 'value': self.ipaddress},
                    {'key': 'timeLastrun', 'value': self.mainTimeLastRun},
                    {'key': 'currentQue', 'value': self.quesize},
                    {'key': 'currentDelay', 'value': self.previoustimeDelay}
                ]
            dev.updateStatesOnServer(stateList)



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
            if the_file.startswith('TempFile_'):
                file_path = os.path.join(self.folderLocationTemp, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.exception(e)

    def EventreturnCameras(self,filter='', valuesDict=None, typeId='', targetId=0):
        self.logger.debug(u'Generate Cameras Lists for Event')
        myArray = []
        if self.debug5:
            self.logger.debug(u'self.deviceCamerstouse:' + unicode(self.deviceCamerastouse))
        for dev in indigo.devices.itervalues("com.GlennNZ.indigoplugin.BlueIris.BlueIrisCamera"):

            if dev.enabled:
                if self.debug5:
                    self.logger.debug(u'Checking dev.id:'+unicode(dev.id)+' and device name:'+unicode(dev.name))
                if str(dev.id) in self.deviceCamerastouse:
                    if self.debug5:
                        self.logger.debug(u'Update Camera: Add to List:'+unicode(dev.id))
                    myArray.append((dev.id,dev.name))
        if self.debug5:
            self.logger.debug(unicode(myArray))
        return myArray



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

        self.debug1 = True
        self.debug2 = True
        self.debug3 = True
        self.debug4 = True
        self.debug5 = True
        self.pluginPrefs['debug1']= self.debug1
        self.pluginPrefs['debug2'] = self.debug2
        self.pluginPrefs['debug3'] = self.debug3
        self.pluginPrefs['debug4'] = self.debug4
        self.pluginPrefs['debug5'] = self.debug5


############ Broadcast Subscribe stuff

    def broadcasterStarted(self):
        self.logger.debug("received broadcasterStarted message")
        return

    def broadcasterShutdown(self):
        self.logger.debug("received broadcasterShutdown message")
        return

    def checkcars(self, liveurlphoto, ipaddress, cameraname, image, imagefresh, indigodeviceid, confidence, x_min,x_max,y_min,y_max, external):
        self.logger.debug('Now checking for Cars....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:
            cropped = imagefresh.crop((x_min, y_min, x_max, y_max))
            filename = self.folderLocationCars + "DeepStateCars_{}_{}.jpg".format(cameraname, str(t.time()))
            cropped.save(filename)
            ## Save Full image here as well
            image.save(self.folderLocationCars + "DeepStateCarsFull_{}_{}.jpg".format(cameraname, str(t.time())))

            self.checkDevices('car', cameraname, filename, confidence)
            self.triggerCheck('car', cameraname, indigodeviceid, 'objectTrigger', confidence, external)
        except Exception as ex:
            self.logger.debug('Error Saving to Vehicles: ' + unicode(ex))

    def checkfaces2(self,  liveurlphoto, ipaddress, cameraname, image, indigodeviceid, confidence, x_min,x_max,y_min,y_max, external):
        self.logger.debug('Now checking for Faces 2/Cropping only....')
        urltosend = 'http://' + ipaddress + ":7188/v1/vision/face"
        try:
            cropped = image.crop((x_min, y_min, x_max, y_max))
            filename= self.folderLocationFaces + "DeepStateFaces_{}_{}.jpg".format(cameraname, str(t.time()))
            cropped.save(filename)
            self.checkDevices('person', cameraname, filename, confidence)
            self.triggerCheck('person', cameraname, indigodeviceid, 'objectTrigger', confidence, external)

        except Exception as ex:
            self.logger.debug('Error Saving to Vehicles: ' + unicode(ex))

    def checkallobjects(self, deepStateObject, liveurlphoto, ipaddress, cameraname, image, imagefresh, indigodeviceid, confidence, x_min,x_max,y_min,y_max, external):

        self.logger.debug('Now checking for All Objects only: Checking against:'+unicode(deepStateObject))

        try:
            filenameCrop = self.saveDirectory+deepStateObject+'/' + 'DeepState_'+deepStateObject+'_Crop_{}_{}.jpg'.format(cameraname, str(t.time()))
            filenameFull = self.saveDirectory+deepStateObject+'/' + 'DeepState_'+deepStateObject+'_Full_{}_{}.jpg'.format(cameraname, str(t.time()))
            if self.checkDevices(deepStateObject, cameraname, filenameFull, confidence):
                # only save images if a Device exists - still trigger though regardless
                cropped = imagefresh.crop((x_min, y_min, x_max, y_max))
                cropped.save(filenameCrop)
                image.save(filenameFull)

            self.triggerCheck(deepStateObject, cameraname, indigodeviceid, 'objectTrigger', confidence, external)

        except Exception as ex:
            self.logger.exception('Error Saving All Objects: ' + unicode(ex))

    def checkDevices(self, objectname, cameraname, filename, confidence):

        self.logger.debug('CheckDevices run')
        for dev in indigo.devices.itervalues("self.DeepStateObject"):
            if dev.enabled:
                objectName = dev.pluginProps['objectType']
                if objectName =='other':
                    objectName = dev.pluginProps['objectOther']
                #self.logger.debug('Checking for ObjectType:' + unicode(objectName))
                if objectName == objectname:
                    dev.updateStateOnServer('objectType', value=objectname)
                    dev.updateStateOnServer('cameraFound', value=cameraname)
                    dev.updateStateOnServer('imageLink', value=filename)
                    time = t.time()
                    update_time = t.strftime('%c')
                    dev.updateStateOnServer('timeLastFound', value=time)
                    dev.updateStateOnServer('confidence', value=confidence)
                    dev.updateStateOnServer('date', value=update_time)
                    return True
        return False

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


    def triggerCheck(self, objectname, cameraname, indigodeviceid, event, confidence, external):

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
                    objectName = trigger.pluginProps['objectType']
                    if objectName == 'other':
                        objectName = trigger.pluginProps['objectOther']
                    if str(objectName)== str(objectname):
                        triggerconfidence = trigger.pluginProps.get('confidence',0.6)

                        if str(indigodeviceid) in trigger.pluginProps['deviceCamera'] and float(confidence) >= float(triggerconfidence) or (external == True and float(confidence>=float(triggerconfidence))):
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
                                        self.logger.debug(u'Trigger :'+ unicode(trigger.name) + u' not run again, as current time='+unicode(t.time())+u' and time past run='+unicode(self.triggersTriggered[trigger.id]))
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
                 self.logger.debug(u'Requests: status code:'+unicode(r.status_code)+ u' try one more time..')
                 self.sleep(1)
                 start = t.time()
                 r2 = requests.get(url, stream=True, timeout=self.serverTimeout)
                 if r2.status_code == 200:
                     # self.logger.debug(u'Yah Code 200....')
                     with open(path, 'wb') as f:
                        for chunk in r2.iter_content(1024):
                            f.write(chunk)
                            if t.time()>(start +self.imageTimeout):
                                self.logger.error(u'Download Image Taking too long.  Aborted.  ?Network issue')
                                break
                        if self.debug2:
                            self.logger.debug(u'2nd Saved Image attempt for:'+unicode(path)+u' in [seconds]:'+unicode(t.time()-start))
                 else:
                     self.logger.debug(u'2nd attempt failed.')


        except requests.exceptions.Timeout:
            self.logger.debug(u'threadDownloadImage has timed out and cannot connect to BI Server.')
            pass

        except requests.exceptions.ConnectionError:
            self.logger.debug(u'connectServer has a Connection Error and cannot connect to BI Server.')
            self.sleep(5)
            pass
        except IOError as ex:
            self.logger.debug(u'threadDownloadImage has an IO Error:'+unicode(ex))
            pass

        except:
            self.logger.exception(u'Caught Exception in threadDownloadImage')

    def humansize(self, nbytes):
        i = 0
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        while nbytes >= 1024 and i < len(suffixes) - 1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])


    def threadSendtodeepstate(self):

        alreadysuperchargeSkip = False

        while True:

            item = self.que.get()   # blocks here until another que items
            ## blocks here until next item
            cameraname= item.cameraname
            indigodeviceid = item.indigodeviceid
            path = item.path
            utctime = item.utctime
            external = item.external
            superchargeImage =item.superchargeImage
            timedelay = float(t.time())-float(utctime)
            pasttimedelay = self.previoustimeDelay

            try:
                ## add velocity setting as well
                velocity = timedelay - pasttimedelay
                if self.debug2:
                    self.logger.debug(u'Thread:SendtoDeepState: Processing: Velocity here:'+unicode(velocity))
                self.previoustimeDelay = timedelay ## update to new timedelay value
                #self.quesizeold = int(self.que.qsize())

                #quesizedelta = self.quesize - int(self.que.qsize())
                #self.logger.error(u'Thread:SendtoDeepState: Processing: Que Size: '+unicode(self.quesize)+u' and delta:'+unicode(quesizedelta))


                if self.debug2:
                    self.logger.debug(u'Thread:SendtoDeepstate: Processing next item in que: Cameraname:'+unicode(cameraname)+', image file:'+unicode(path)+', from IndigoID:'+unicode(indigodeviceid))
                    self.logger.debug(u'Thread:SendtoDeepState: Processing items now '+unicode(timedelay)+u' seconds later than image captured.')

                if timedelay > int(self.timeLimit)/2:
                    if alreadysuperchargeSkip:
                        alreadysuperchargeSkip = False
                    # if already halfway to limit start deleting the supercharged files
                    else:
                        self.logger.info(u'Deepstate Processing slowing down, skipping ever 2nd SuperCharged Image')
                        self.mainSkippedImages = self.mainSkippedImages + 1

                        alreadysuperchargeSkip = True
                        try:
                            os.remove(path)
                        except Exception as ex:
                            self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                        self.que.task_done()
                        self.quesize = int(self.que.qsize())
                        continue

                if timedelay> int(self.timeLimit) and velocity > -5:  ## if more than 60 seconds delayed in processing images, skip current item and delete temp image
                    self.logger.info(u'Thread:SendtoDeepstate:  Processing items now '+unicode(self.timeLimit)+u' seconds behind image capture, and velocity >-5 positive.  Aborting this image until resolved.')
                    self.mainSkippedImages = self.mainSkippedImages +1
                    try:
                        os.remove(path)
                    except Exception as ex:
                        self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                    self.que.task_done()
                    self.quesize = int(self.que.qsize())
                    continue

                if self.useLocal:
                    ipaddress = 'localhost'
                else:
                    ipaddress = self.ipaddress

                urltosend = 'http://' + ipaddress + ":" + self.port + "/v1/vision/detection"
                if self.debug3:
                    self.logger.debug(u'Now Validing Image Data before sending..')

                if not self.imageVerify(path):
                    self.logger.debug(u'Image Failed Verification.  Skipped.')
                    self.mainSkippedImages = self.mainSkippedImages + 1
                    try:
                        os.remove(path)
                    except Exception as ex:
                        self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                    self.que.task_done()
                    self.quesize = int(self.que.qsize())
                    continue

                if self.debug3:
                    self.logger.debug(u'Sending to :'+unicode(urltosend))


                liveurlphoto = open(path, 'rb').read()
                image = Image.open(path)
                imagefresh = Image.open(path)

                bytesImage = os.path.getsize(path)

                if self.debug3:
                    self.logger.debug(u'Size of Current Image:'+unicode(bytesImage))

                self.reply = True
                response = requests.post(urltosend, files={"image": liveurlphoto}, timeout=15).json()
                if self.debug1:
                    self.logger.debug(unicode(response))
                #self.listCameras[cameraname] = False  # set to false as already run.

                vehicles = ['bicycle', 'car', 'motorcycle', 'bus', 'train']
                anyobjectfound = False
                if response['success'] == True:
                    self.mainProcessedImages = self.mainProcessedImages +1
                    self.mainBytesProcessed = self.mainBytesProcessed + bytesImage

                    self.mainTimeLastRun = t.strftime('%c')
                    self.deepstateIssue = False
                    self.deepstatetimeouts = 0
                    for object in response["predictions"]:
                        carfound = False
                        label = object["label"]
                        #if self.debug4:
                            #self.logger.error(u'Checking Found item:'+unicode(label))
                        y_max = int(object["y_max"])
                        y_min = int(object["y_min"])
                        x_max = int(object["x_max"])
                        x_min = int(object["x_min"])
                        confidence = float(object['confidence'])

                        ## if mainconfidence less than completely skip this object
                        if confidence < float(self.confidenceMain):
                            if self.debug4:
                                self.logger.debug(u'Low Confidence for Object:'+unicode(label)+' so skipping.  Checking next.')
                            continue

                        objectfound = True
                        if label in vehicles:
                            carfound = True
                        draw = ImageDraw.Draw(image)
                        draw.rectangle(((x_min, y_min), (x_max, y_max)), fill=None, outline='red', width=3)
                        labelonbox = str(label) + ' ' + str(confidence)
                        draw.text((x_min + 5, y_min + 5), labelonbox, font=ImageFont.truetype(font='Arial.ttf', size=18),
                                  fill='red')
                        cropped = imagefresh.crop((x_min, y_min, x_max, y_max))
                        #if label == 'person':
                            ## check for faces - disabled not really helpful
                            ## change to check for every object possible.
                            #self.checkfaces2(cropped, ipaddress, cameraname, imagefresh, indigodeviceid, confidence, x_min, x_max, y_min, y_max, external)
                            #image.save(self.folderLocationFaces + "DeepStateFacesFull_{}_{}.jpg".format(cameraname, str(t.time())))
                        #if carfound:
                        self.checkallobjects(label, cropped,ipaddress,cameraname, image,imagefresh, indigodeviceid, confidence,x_min, x_max,  y_min, y_max, external)
                            #self.checkcars(cropped, ipaddress, cameraname, image, imagefresh, indigodeviceid, confidence,x_min, x_max,  y_min, y_max, external)
                            #image.save(self.folderLocationCars + "DeepStateCarsFull_{}_{}.jpg".format(cameraname, str(t.time())))
                            #carfound = False

                else:
                    self.logger.debug(u'Thread:SendtoDeepstate: DeepState Request failed:')
                    self.deepstateIssue = True

                self.que.task_done()
                self.quesize = int(self.que.qsize())
                try:
                    os.remove(path)
                except Exception as ex:
                    self.logger.debug(u'Error deleting file'+unicode(ex))

            except self.StopThread:
                self.logger.debug(u'Self.Stop Thread called')
                self.deepstateIssue = True
                pass

            except requests.exceptions.Timeout as ex:
                self.logger.debug(u'threadaddtoQue has timed out and cannot connect to DeepStateAI:'+unicode(ex))

                self.deepstatetimeouts = self.deepstatetimeouts + 1
                if self.deepstatetimeouts >= 5:
                    self.logger.debug(u'Timeouts greater than 5. setting Issue')
                    self.deepstateIssue = True
                try:
                    os.remove(path)
                except Exception as ex:
                    self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                self.que.task_done()
                self.quesize = int(self.que.qsize())
                pass

            except requests.exceptions.ConnectionError:
                self.logger.debug(u'Threadaddtoque has a Connection Error and cannot connect to DeepStateAI.')
                self.deepstateIssue = True
                try:
                    os.remove(path)
                except Exception as ex:
                    self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                self.que.task_done()
                self.quesize = int(self.que.qsize())
                self.sleep(1)
                pass

            except IOError as ex:
                self.logger.debug(u'Thread:SendtoDeepstate: IO Error: Probably file failed downloading...'+unicode(ex))
                self.deepstateIssue = True
                try:
                    os.remove(path)
                except Exception as ex:
                    self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                self.que.task_done()
                self.quesize = int(self.que.qsize())
                pass

            except Exception as ex:
                self.logger.exception(u'Thread:SendtoDeepstate:Error sending to Deepstate: ' + unicode(ex))
                self.deepstateIssue = True
                try:
                    os.remove(path)
                except Exception as ex:
                    self.logger.debug(u'Caught Issue Deleting File:' + unicode(ex))
                    pass
                self.que.task_done()
                self.quesize = int(self.que.qsize())
                self.reply = False

    def imageVerify(self, path):
        if self.debug4:
            self.logger.debug(u'imageVerify called for image Path:'+unicode(path))
        try:
            img = Image.open(path)
            img.verify()
            img.close()
            im = Image.open(path)
            im.transpose(Image.FLIP_LEFT_RIGHT)
            im.close()
            return True
        except Exception as ex:
            if self.debug3:
                self.logger.debug(u'Exception: Image Verification Failed:'+unicode(ex))
            return False




    ## Actions.xml
    def resetImageTimers(self, action):
        self.logger.debug(u"resetImageTimers Called as Action.")
        self.HTMLimageNo = 0
        self.HTMLlistFiles = []
        #self.imageNoCar = 0
        #self.imageNoCarCrop = 0
        #self.imageNoPerson = 0
        #self.imageNoPersonCrop = 0

        return

    def setMainConfidence(self, action):
        self.logger.debug(u"setMainConfidence Called as Action.")
        confidenceLevel = action.props.get('confidence',0.7)
        self.confidenceMain = confidenceLevel
        self.pluginPrefs['confidenceMain']= self.confidenceMain
        self.logger.debug(u'Main Confidence level now set to :'+unicode(self.confidenceMain))
        return

    def setCameras(self, action):
        self.logger.debug(u"setCameras Called as Action.")
        deviceCameras = action.props.get('deviceCamera',0.7)
        self.deviceCamerastouse = deviceCameras
        self.pluginPrefs['deviceCamera']= self.deviceCamerastouse
        self.logger.debug(u'Cameras Enabled now now set to :'+unicode(self.deviceCamerastouse))
        return

    def setSupercharge(self, action):
        self.logger.debug(u"set SuperCharge Called as Action.")
        self.superCharge = action.props.get('superCharge', False)
        self.superChargedelay = action.props.get('superChargedelay', 2)
        self.superChargeimageno = action.props.get('superChargeimageno', 5)

        self.pluginPrefs['superCharge']= self.superCharge
        self.pluginPrefs['superChargedelay'] = self.superChargedelay
        self.pluginPrefs['superChargeimageno'] = self.superChargeimageno
        self.logger.debug(u'SuperCharge :'+unicode(self.superCharge)+'  Delay:'+unicode(self.superChargedelay) +u' and Image Number:'+unicode(self.superChargeimageno) )
        return

    def sendtoDeepState(self, action):
        self.logger.debug(u"Send to DeepState Called as Action.")

        imageType = action.props.get('imageType','')
        imageLocation = action.props.get('ImageLocation','')

        if imageType=='' or imageLocation =='':
            self.logger.debug(u'Please enter values for Action.  Aborted')
            return
        try:
            if imageType == 'URL':
                Externaladd = threading.Thread(target=self.threadaddtoQue, args=[imageLocation, 'ExternalActionURL', 1, True, ''])
                Externaladd.setDaemon(True)
                Externaladd.start()
                return
            if imageType == 'FILE':
                path = self.folderLocationTemp + 'TempFile_{}'.format(uuid.uuid4())
                copyfile(imageLocation,path)
                ## create a temporary file from the one given - otherwise will be deleted
                item = deepstateitem(path, 1, 'ExternalActionFile', t.time(), True, False ,'')
                if self.debug1:
                    self.logger.debug(u'Putting item into DeepState Que: Item:' + unicode(item))
                self.que.put(item)
        except Exception as ex:
            self.logger.exception(u'Caught Exception:  Some thing wrong with File Path or URL'+unicode(ex))
            return
        return

    ##

    def motionTrue(self, arg):

        try:
            urlphoto = arg[0]+'?s='+str(self.imageScale)
            cameraname = arg[1]
            pathimage = arg[2]
            updatetime = arg[3]
            newimagedownloaded = arg[4]
            indigodeviceid = arg[5]
            typetrigger = arg[6]
            alertimage = arg[7]

            if str(indigodeviceid) not in self.deviceCamerastouse:
                #if self.debug1:
                    #self.logger.debug('Camera not enabled within DeepState Config Settings/Ignored.')
                #self.logger.debug(unicode(self.deviceCamerastouse))
                return

            if typetrigger == 'AUDIO':
                if self.debug1:
                    self.logger.debug('AUDIO Trigger Settings/Ignored.')
                #self.logger.debug(unicode(self.deviceCamerastouse))
                return
            if self.debug3:
                self.logger.debug(u"received Camera motionTrue message: %s" % (arg))

            motionTrue = threading.Thread(target=self.threadaddtoQue, args=[urlphoto, cameraname,indigodeviceid, False, alertimage])
            motionTrue.setDaemon(True)
            motionTrue.start()
            # given delayed images over 10 seconds or even longer need to thread below
            return

        except Exception as ex:
            self.logger.exception(u'Exception caught in motion true:'+unicode(ex))


    def threadDownloadandaddtoque(self, path, url, cameraname,indigodeviceid, external, alertimage):
        if self.debug2:
            self.logger.debug(u'threadDownloadandaddtoque called.'+u' & Number of Active Threads:' + unicode(
                threading.activeCount()))
        try:
             # add timer and move to chunk download...
             start = t.time()
             r = requests.get(url, stream=True, timeout=self.serverTimeout)
             if r.status_code == 200:
                 with open(path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                        if t.time()>(start +self.imageTimeout):
                            self.logger.error(u'downloadandaddtoque Download Image Taking too long.  Aborted.  ?Network issue')
                            break
                    if self.debug2:
                        self.logger.debug(u'downloadandaddtoque Saved Image attempt for:'+unicode(path)+u' in [seconds]:'+unicode(t.time()-start))
             else:
                 self.logger.debug(u'downloadandaddtoque Issue Downloading Image. Failed.')
                 self.logger.debug(u'downloadandaddtoque Requests: status code:'+unicode(r.status_code)+ u' try one more time..')
                 self.sleep(1)
                 start = t.time()
                 r2 = requests.get(url, stream=True, timeout=self.serverTimeout)
                 if r2.status_code == 200:
                     # self.logger.debug(u'Yah Code 200....')
                     with open(path, 'wb') as f:
                        for chunk in r2.iter_content(1024):
                            f.write(chunk)
                            if t.time()>(start +self.imageTimeout):
                                self.logger.error(u'downloadandaddtoque Download Image Taking too long.  Aborted.  ?Network issue')
                                break
                        if self.debug2:
                            self.logger.debug(u'downloadandaddtoque 2nd Saved Image attempt for:'+unicode(path)+u' in [seconds]:'+unicode(t.time()-start))
                 else:
                     self.logger.debug(u'downloadandaddtoque 2nd attempt failed.')
                     return
             # Image downloaded
             # Now add to Que
             item = deepstateitem(path, indigodeviceid, cameraname, t.time(), external, False, alertimage)
             if self.debug1:
                 self.logger.debug(u'downloadandaddtoque Putting item into DeepState Que: Item:' + unicode(item))
             self.que.put(item)
             return

        except requests.exceptions.Timeout:
            self.logger.debug(u'downloadandaddtoque  has timed out and cannot connect to BI Server.')

        except requests.exceptions.ConnectionError:
            self.logger.debug(u'downloadandaddtoque connectServer has a Connection Error and cannot connect to BI Server.')
            self.sleep(5)

        except IOError as ex:
            self.logger.debug(u'downloadandaddtoque has an IO Error:'+unicode(ex))

        except:
            self.logger.exception(u'downloadandaddtoque Caught Exception in threadDownloadImage')

    def threadaddtoQue(self, urlphoto,cameraname,indigodeviceid, external, alertimage):
        if self.debug3:
            self.logger.debug(u'Thread:AdddtoQue called.' + u' & Number of Active Threads:' + unicode(
                threading.activeCount())+ u' and current que:'+unicode(self.quesize))
        if int(self.quesize)==0:
            self.deepstateIssue = False
            ## if nothing in que set to False

        if self.deepstateIssue:
            self.logger.error(u'Issue with DeepState Service:  Not adding anything to que. Aborted.')
            return
#threadDownloadandaddtoque(self, path, url, cameraname,indigodeviceid, external, alertimage):
        try:

            if alertimage != '':
                self.logger.debug(u'threadAddtoque:  Checking Alert image as exists..')
                alertpath = self.folderLocationTemp + 'TempFile_AlertIMAGE_{}'.format(uuid.uuid4())
                alertimagecheck = threading.Thread(target=self.threadDownloadandaddtoque, args=[alertpath, alertimage, cameraname, indigodeviceid, True, alertimage])
                alertimagecheck.setDaemon(True)
                alertimagecheck.start()


            if self.superCharge == False or external==True:  ##eg. one image
                path = self.folderLocationTemp + 'TempFile_{}'.format(uuid.uuid4())
                ImageThread = threading.Thread(target=self.threadDownloadandaddtoque, args=[path, urlphoto, cameraname, indigodeviceid, True, alertimage] )
                ImageThread.setDaemon(True)
                ImageThread.start()

                # above combines single thread to download, when finished successfully add to que.
                #self.threadDownloadImage(path, urlphoto)  # if single image, don't thread... already in a addtoque thread
                #self.sleep(0.5)
                #item = deepstateitem(path, indigodeviceid, cameraname, t.time(),external , False, alertimage)
                #if self.debug1:
                    #self.logger.debug(u'Putting item into DeepState Que: Item:'+unicode(item))
                #self.que.put(item)

            else:
                ## Add first image, as not supercharge, add rest
                numberofseconds = range( int(self.superChargeimageno) )  #seconds here changed usage to number of images
                path = self.folderLocationTemp + 'TempFile_{}'.format(uuid.uuid4())
                #ImageThread = threading.Thread(target=self.threadDownloadImage, args=[path, urlphoto])
                #ImageThread.start()
                #self.sleep(0.3)
                self.threadDownloadImage(path, urlphoto)   ## here first one don't thread as well...
                item = deepstateitem(path, indigodeviceid, cameraname, t.time(), external, False, alertimage)
                self.que.put(item)
                if self.debug1:
                    self.logger.debug(u'Putting SuperCharge.1 item into DeepState Que: Item:' + unicode(item))
                for n in numberofseconds:
                    self.logger.debug(u'************** Downloading Images:  Image:'+unicode(n) +u' for Camera:'+unicode(cameraname) )
                    path = self.folderLocationTemp + 'TempFile_{}'.format(uuid.uuid4())
                    ImageThread2 = threading.Thread(target=self.threadDownloadandaddtoque, args=[path, urlphoto, cameraname, indigodeviceid, True, alertimage])
                    ImageThread2.setDaemon(True)
                    ImageThread2.start()
                    self.sleep(float(self.superChargedelay))

                    #self.sleep(0.5)#sleep for the delay
                    #item = deepstateitem(path, indigodeviceid, cameraname, t.time(),external, True, alertimage)
                    #if self.debug1:
                        #self.logger.debug(u'Putting item into DeepState Que: Item.Path:'+unicode(item.path))
                    #self.que.put(item)

            self.quesize = int(self.que.qsize())
            if self.debug2:
                self.logger.debug(u'Thread:AddtoQue:  Number in que:' + unicode(self.quesize))

            if self.quesize> 50:
                self.logger.info(u'Currently Size of DeepStateAI processing Que is '+unicode(self.quesize)+u'. Consider your settings if this continues.')
            return

        except self.StopThread:
            self.logger.debug(u'Self.Stop Thread called')
            pass

        except Exception as e:
            self.logger.exception(u'Exception caught in Thread Add to Que')

    def listenHTTP(self):
        try:
            self.debugLog(u"Starting HTTP Image Server  thread")
            if self.httpserver:
                indigo.server.log(u"Http Server Image Server on TCP port " + str(self.httpport))
                self.server = HTTPServer(('', int(self.httpport)), lambda *args: httpHandler(self, *args))
                self.server.serve_forever()

        except self.StopThread:
            self.logger.debug(u'Self.Stop Thread called')
            pass
        except:
            self.logger.exception(u'Caught Exception in ListenHttp')

#class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
 #   """Handle requests in a separate thread."""

class httpHandler(BaseHTTPRequestHandler):
    def __init__(self,plugin, *args):
        try:
            self.plugin=plugin
            if self.plugin.debug4:
                self.plugin.debugLog(u'New Http Handler thread:'+threading.currentThread().getName()+", total threads: "+str(threading.activeCount()))
            BaseHTTPRequestHandler.__init__(self, *args)
        except Exception as ex:
            self.plugin.logger.debug(u'httpHandler init caught Exception'+unicode(ex))
            pass

    def date_sortfiles(self,path):
        try:
            self.plugin.logger.debug(u'Date_Sort Files called...')
            files = list(filter(os.path.isfile,glob.glob(path)))
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            # return newish first
            return files
        except Exception as ex:
            self.plugin.logger.debug(u'Error in Data_SortFiles'+unicode(ex))
            return ''

    def do_GET(self):

        try:

            if self.plugin.debug4:
                self.plugin.logger.debug(u'Html Server: do_get: self.path = '+unicode(self.path) )
                #self.plugin.logger.debug(u'Html Server: do_get:self.path[1:-5]:'+unicode(self.path[1:-5]) )
                #self.plugin.logger.debug(u'Html Server: do_get:self.path[1:8]:' + unicode(self.path[1:8]))
                #self.plugin.logger.debug(u'Html Server: do_get:self.path[9:-5]:' + unicode(self.path[9:-5]))

            if self.path[1:8]=='archive' and self.plugin.archiveMounted:
                if self.plugin.debug4:
                    self.plugin.logger.debug(u'Seems like a Archive directory is being requested.')
                if self.path[9:-5] in self.plugin.alldeepstateclasses:
                    objectName = self.path[9:-5]  # get the named object/is checked above
                    if self.plugin.HTMLarchivelastObject != objectName:
                        # serving new image - reset the count
                        # and re-read the image Directories!
                        self.plugin.HTMLarchivelastObject = objectName
                        self.plugin.HTMLimageNo = 0
                        if self.plugin.debug4:
                            self.plugin.logger.debug('HTML: do_Get: New image Serving reset count, and re-reading directory')
                        self.plugin.HTMLlistFiles = self.date_sortfiles(self.plugin.saveDirectory + 'ARCHIVE/'+ objectName + '/' + 'DeepState_' + objectName + '_Full*.jpg')
                    else:
                        if not self.plugin.HTMLlistFiles:
                            # empty
                            self.plugin.HTMLlistFiles = self.date_sortfiles(self.plugin.saveDirectory + 'ARCHIVE/' + objectName + '/' + 'DeepState_' + objectName + '_Full*.jpg')
                    if self.plugin.debug4:
                        self.plugin.logger.debug(u'd_Get: Html ObjectName:' + unicode(objectName))
                    # ignore the full/crop bit
                    # just serve the full one
                    self.send_response(200)
                    mimetype = 'image/jpg'
                    self.send_header('Content-type', mimetype)
                    self.end_headers()

                    if self.plugin.HTMLimageNo >= len(self.plugin.HTMLlistFiles):
                        self.plugin.HTMLimageNo = 0
                    # self.plugin.logger.debug(u'listFiles:'+unicode(listFiles))
                    if self.plugin.debug4:
                        self.plugin.logger.debug(u'self.plugin.imageNo =' + unicode(self.plugin.HTMLimageNo))

                    if self.plugin.HTMLlistFiles:
                        file = open(self.plugin.HTMLlistFiles[self.plugin.HTMLimageNo], 'rb')
                        self.wfile.write(file.read())
                        file.close()
                        self.plugin.HTMLimageNo = self.plugin.HTMLimageNo + 1
                    else:
                        file = open(self.plugin.pathtoNotFound, 'rb')
                        self.wfile.write(file.read())
                        file.close()
                    return

            if self.path[1:-5] in self.plugin.alldeepstateclasses:
            ## Okay so requested html path contains a DeepStateObject
            ## Could either be full or Crop - although not sure much role of cropped files...
            ## Just serve the Full File
                objectName = self.path[1:-5] # get the named object/is checked above
                if self.plugin.HTMLlastObject != objectName:
                    # serving new image - reset the count
                    # and re-read the image Directories!

                    self.plugin.HTMLlastObject = objectName
                    self.plugin.HTMLimageNo = 0
                    if self.plugin.debug4:
                        self.plugin.logger.debug('HTML: do_Get: New image Serving reset count, and re-reading directory')
                    self.plugin.HTMLlistFiles = self.date_sortfiles(self.plugin.saveDirectory + objectName + '/' + 'DeepState_' + objectName + '_Full*.jpg')
                else:
                    if not self.plugin.HTMLlistFiles:
                        # empty
                        self.plugin.HTMLlistFiles = self.date_sortfiles(self.plugin.saveDirectory + objectName + '/' + 'DeepState_' + objectName + '_Full*.jpg')
                if self.plugin.debug4:
                    self.plugin.logger.debug(u'd_Get: Html ObjectName:'+unicode(objectName))
                # ignore the full/crop bit
                # just serve the full one
                self.send_response(200)
                mimetype = 'image/jpg'
                self.send_header('Content-type', mimetype)
                self.end_headers()


                if self.plugin.HTMLimageNo >= len(self.plugin.HTMLlistFiles):
                    self.plugin.HTMLimageNo = 0
                #self.plugin.logger.debug(u'listFiles:'+unicode(listFiles))
                if self.plugin.debug4:
                    self.plugin.logger.debug(u'self.plugin.imageNo =' + unicode(self.plugin.HTMLimageNo))

                if self.plugin.HTMLlistFiles:
                    file = open(self.plugin.HTMLlistFiles[self.plugin.HTMLimageNo], 'rb')
                    self.wfile.write(file.read())
                    file.close()
                    self.plugin.HTMLimageNo = self.plugin.HTMLimageNo + 1
                else:
                    file = open(self.plugin.pathtoNotFound, 'rb')
                    self.wfile.write(file.read())
                    file.close()

            return

        except self.plugin.StopThread:
            self.logger.debug(u'Self.Stop Thread called')
            pass
        except IOError:
            self.plugin.logger.debug(u'IOError: Exception:')
        except Exception as ex:
            self.plugin.logger.debug(u'HTML Server: do_Get: Caught Exception'+unicode(ex))