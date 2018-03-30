#!/usr/bin/python
'''
Created on 1 Nov 2015

@author: stephen H

test change

'''
from __future__ import division

__updated__ = "2018-02-17"

import logging
from logging.handlers import RotatingFileHandler
from database import DbUtils
import threading
import multiprocessing
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from requesthandler import MyRequestHandler
from heatinggpio import setupGPIO, buttonCheckHeat, hBeat, setStatusLights
from variables import Variables
from sys import platform as _platform
from os import system
import hardware
import time
from max import MaxInterface

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()

reboot_Timer = 0.0
offTime = 0.0
shutdown_Timer = 0.0
shutOff_Timer = 0.0



def mainCheckHeat(self):
    MaxInterface().checkHeat(input_queue)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests is separate thread"""
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, queue=None):
        self.queue = queue
        print "ThreadingServerStarted"
        HTTPServer.__init__(self, server_address, RequestHandlerClass,
                           bind_and_activate=bind_and_activate)
        
class Main():
    
    def __init__(self):
        #Initialise the Logger
        logLevel = Variables().readVariables(['LoggingLevel']).rstrip('\r')
        #useNeoPixel = Variables().readVariables(['UseNeoPixel'])
        self.logger = logging.getLogger("main")
        logging.basicConfig()
        self.logger.setLevel(logLevel)
        
        fh = RotatingFileHandler("heating.log",
                                 maxBytes=1000000, # 1Mb I think
                                 backupCount=5)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.info("Main has started __init__ has run logger level is %s" % logLevel)
        
        try:
            cube = DbUtils().getCubes()
            self.logger.info("Database OK cube %s found" % (cube[1]))
        except Exception, err:
            DbUtils().initialiseDB()
            self.logger.exception("Database Initialised %s" % err)
        self.logger.info("Free Memory at Boot %s MB" % hardware.getRAM())
        self.logger.info("CPU Usage at Boot %s" % hardware.getCPUUse())
        
        
        
        setupGPIO(input_queue)
        
        # Start Web UI
        self.startKioskServer()
        
        # Start Main Loop
        self.doLoop()
        
    def doLoop(self):
        nextLoopCheck = time.time()
        while True:
            loopStartTime = time.time()
            if loopStartTime >= nextLoopCheck:
                print "running loop"
                checkInterval, boiler_enabled, useNeoPixel = Variables().readVariables(['Interval', 'BoilerEnabled', 'UseNeoPixel'])
                
                if boiler_enabled != 1:
                    checkInterval = checkInterval * 2
                if _platform == "linux" or _platform == "linux2":
                    self.logger.info("checking heat levels")
                    MaxInterface().checkHeat(input_queue)
                    self.logger.info("Memory free this loop %s MB" % hardware.getRAM())
                    self.logger.info("CPU Usage this loop %s" % hardware.getCPUUse())
                    self.logger.debug( "loop interval : %s" %(checkInterval))
                else:
                    MaxInterface().checkHeat(input_queue)
                    self.logger.info('Running Windows timer')
                setStatusLights() 
                nextLoopCheck = loopStartTime + checkInterval
                
            hBeat(2)
            time.sleep(.2)
            
            
    def startKioskServer(self):
        webIP, webPort = Variables().readVariables(['WebIP', 'WebPort'])
        self.logger.info("Web UI Starting on : %s %s" %( webIP, webPort))
        try:
            server = ThreadingHTTPServer((webIP, webPort), MyRequestHandler, queue=input_queue)
            uithread = threading.Thread(target=server.serve_forever)
            uithread.setDaemon(True)
            uithread.start()
        except Exception, err:
            self.logger.error("Unable to start Web Server on %s %s %s" %(webIP, webPort, err))
            self.logger.critical("Killing all Python processes so cron can restart")
            system("sudo pkill python")
        

if __name__=='__main__':
    Main()
