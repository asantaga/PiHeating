#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler
import cgi
from os import curdir, sep, system, execl
from sys import platform as _platform, executable, argv
import time
from webui import CreateUIPage
from graphing import MakeGraph
from variables import Variables
from sendmessage import SendMessage
import json
import hardware

from max import MaxInterface
VAR = Variables()
CUI = CreateUIPage()
GRAPH = MakeGraph()

import logging

module_logger = logging.getLogger("main.requesthandler")


class MyRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.input_queue = server.queue
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        
        

    def do_GET(self):
        module_logger.debug("GET %s" % self.path)
        if self.path=="/":
            roomTemps = CUI.createRooms()
            self.path="/index.html"
            self.updateUIPages(roomTemps)
            
#
# REST call to retun status of boiler :
#
        if self.path[0:10] == '/checkheat':
            MaxInterface().checkHeat("web checkheat")
            self.path="/index.html"

        if self.path[0:7] == '/status':
            from database import DbUtils
            DB=DbUtils() 
            checkInterval,cubeStatus=Variables().readVariables(['Interval','CubeOK'])
            statusResponse = {}
            statusResponse['boilerStatus']=DB.getBoiler()[2]
            statusResponse['ram']=hardware.getRAM()
            statusResponse['cpu']=hardware.getCPUUse()
            statusResponse['loopInterval']=checkInterval
            statusResponse['cubeStatus']=cubeStatus

            self.send_response(200)
            self.send_header('Content-type',"application/json")
            self.end_headers()
            self.wfile.write(json.dumps(statusResponse))

        if self.path[0:8] == '/ecomode':
            #roomData = self.path
            #SendMessage().updateRoom(roomData)
            SendMessage().setHouseMode("eco")
            self.path="/index.html"
            time.sleep(1)
            MaxInterface().checkHeat("requesthandler.ecomode")
            
        if self.path[0:9] == '/automode':
            roomData = self.path
            SendMessage().setHouseMode("auto")
            self.path="/index.html"
            time.sleep(1)
            MaxInterface().checkHeat("requesthandler.automode")

        if self.path[0:11] == '/rangegraph':
            print 'going to create rangeGraph page'
            CUI.rangeGraphUI()
            time.sleep(1)


        if self.path[0:5] == '/mode':
            roomData = self.path
            SendMessage().updateRoom(roomData)
            self.path="/index.html"
            MaxInterface().checkHeat("requesthandler.mode")

        if self.path[0:6] == '/graph':
            roomName = self.path
            GRAPH.createGraph(roomName)
            self.path="/graph.html"

        if self.path =="/?confirm=1&boilerswitch=Boiler+Enabled":
            VAR.writeVariable([['BoilerEnabled', 0]])
            self.path = "/index.html"
            MaxInterface().checkHeat("requesthandler.Boiler-disable")

        if self.path == '/?confirm=1&boilerswitch=Boiler+Disabled':
            VAR.writeVariable([['BoilerEnabled', 1]])
            self.path = "/index.html"
            MaxInterface().checkHeat("requesthandler.boiler-enable")

        elif self.path =="/admin":
            roomTemps = CUI.createRooms()
            self.path = "/admin.html"
            self.updateUIPages(roomTemps)

#                
        elif self.path == "/reboot":
            if _platform == "linux" or _platform == "linux2":
                print 'In Linux so rebooting'
                self.path = "/shutdown.html"
                system("sudo reboot")
                

        try:
            #Check the file extension required and
            #set the right mime type

            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + self.path) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return
        
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

        
    def do_POST(self):
        roomTemps = CUI.createRooms()
        module_logger.info("POST %s" % self.path)
        if self.path == "/admin":
            self.path = "/admin.html"
            form = cgi.FieldStorage(
                fp=self.rfile, 
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
            })
            #print form.keys()
            module_logger.debug("form keys %s" % form.keys())
            output = []
            for key in form.keys():
                varList=[]
                varList.append(key)
                varList.append(form[key].value)
                output.append(varList)
            #print output
            VAR.writeVariable( output )
            self.updateUIPages(roomTemps)    
        
        try:

            sendReply = False
            if self.path.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + self.path) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return
        
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
            
        return
        
    def updateUIPages(self, roomTemps):
        CUI.saveUI(roomTemps)
        #time.sleep(0.5)
        #CUI.saveAdminUI()
        
    def restart_program(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = executable
        execl(python, python, * argv)
        
    def postPage(self, pagePath):
        try:

            sendReply = False
            if pagePath.endswith(".html"):
                mimetype='text/html'
                sendReply = True
            if pagePath.endswith(".jpg"):
                mimetype='image/jpg'
                sendReply = True
            if pagePath.endswith(".gif"):
                mimetype='image/gif'
                sendReply = True
            if pagePath.endswith(".js"):
                mimetype='application/javascript'
                sendReply = True
            if pagePath.endswith(".css"):
                mimetype='text/css'
                sendReply = True

            if sendReply == True:
                #Open the static file requested and send it
                f = open(curdir + sep + pagePath) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return
        
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
