import logging
from database import DbUtils
from variables import Variables
from webui import CreateUIPage
from heatinggpio import relayHeating

import base64
import socket
import datetime
import time
import sys
import urllib2
import json
import requests

import multiprocessing

maxDetails = {}
rooms = {}
devices = {}
devices_eco_temps = {}
valves = {}
valveList = []
message = ""
boilerOn = 0
weekDays = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday']
outsideTempCheck = 0

module_logger = logging.getLogger("main.max")


class MaxInterface():

    def checkHeat(self, input_queue):
        MAXData, validData = self.getData()
        if validData:
            self.parseData(MAXData)
            self.switchHeat()


    def createSocket(self):
        logger = logging.getLogger("main.max.createSocket")
        logger.setLevel(logging.DEBUG)
        # Create Socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            logger.info('Socket Created')
            return s
        except socket.error:
            logger.exception("unable to create socket")
            s.close()
            sys.exit()

    def getData(self):
        logger = logging.getLogger("main.max.getData")
        validData = False
        message = ""
        Max_IP, Max_IP2, Max_Port = Variables().readVariables(
            ['MaxIP', 'MaxIP2', 'MaxPort'])
        logger.info('Max Connection Starting on : IP1-%s or IP2-%s on port %s ' %
                    (Max_IP, Max_IP2, Max_Port))
        cube1 = 0
        cube2 = 0
        success = False

        try:
            # Connect to Max Cube1
            while cube1 < 3 and not success:
                try:
                    logger.info(
                        'tyring to connect to Max1 on ip %s on try %s' % (Max_IP, cube1))
                    s = self.createSocket()
                    s.connect((Max_IP, int(Max_Port)))
                    logger.info(
                        'Socket Connected to Max1 on ip %s on try %s' % (Max_IP, cube1))
                    Variables().writeVariable([['ActiveCube', 1]])
                    Variables().writeVariable([['CubeOK', 1]])
                    success = True

                except Exception, err:
                    s.close()
                    Variables().writeVariable([['CubeOK', 0]])
                    logger.exception(
                        "unable to make connection, trying later %s" % err)
                    time.sleep(2)

                cube1 += 1

            if not success:
                raise Exception("Cube 1 fail")

        except Exception, err:
            logger.exception(
                "unable to make connection to Cube 1, trying Cube2 %s" % err)
            # Connect to Max Cube2
            while cube2 < 3 and not success:
                try:
                    logger.info(
                        'tyring to connect to Max2 on ip %s on try %s' % (Max_IP2, cube2))
                    s = self.createSocket()
                    s.connect((Max_IP2, int(Max_Port)))
                    logger.info('Socket Connected to Max2 on ip %s' % Max_IP2)
                    Variables().writeVariable([['ActiveCube', 2]])
                    Variables().writeVariable([['CubeOK', 1]])
                    success = True

                except Exception, err:
                    s.close()
                    Variables().writeVariable([['CubeOK', 0]])
                    logger.exception(
                        "unable to make connection, trying later %s" % err)
                    time.sleep(2)

                cube2 += 1

        try:
            while 1:
                reply = s.recv(1024)
                message += reply
        except:
            logger.info("Message ended")

        if message != "":
            Variables().writeVariable([['CubeOK', 1]])
            validData = True

        s.close()
        logger.debug(message)
        return (message, validData)

    def parseData(self, message):
        print_on = int(Variables().readVariables(['PrintData']))
        message = message.split('\r\n')

        for lines in message:
            # print lines
            try:
                if lines[0] == 'H':
                    self.maxCmd_H(lines)
                elif lines[0] == 'M':
                    self.maxCmd_M(lines, 0)
                elif lines[0] == 'C':
                    self.maxCmd_C(lines)
                elif lines[0] == 'L':
                    self.maxCmd_L(lines)
                else:
                    break
            except:
                pass

        if print_on:
            for keys in maxDetails:
                print keys, maxDetails[keys]
            print "Rooms"
            for keys in rooms:
                print keys, rooms[keys]
            print "devices"
            for keys in devices:
                print keys, devices[keys]
            print "Eco Temperatures" 
            for keys in devices_eco_temps:
                print keys,devices_eco_temps[keys]
            print "valves"
            for keys in valves:
                print keys, valves[keys]

    def hexify(self, tmpadr):
        """ returns hexified address """
        return "".join("%02x" % ord(c) for c in tmpadr).upper()

    def maxCmd_H(self, line):
        """ process H response """
        print "Data from Max_Cmd_H"
        line = line.split(',')
        serialNumber = line[0][2:]
        rfChannel = line[1]
        maxId = line[2]
        dutyCycle = int(line[5], 16)
        maxDetails['serialNumber'] = serialNumber
        maxDetails['rfChannel'] = rfChannel
        maxDetails['maxId'] = maxId

        msg = (maxId, serialNumber, rfChannel, dutyCycle)
        DbUtils().updateCube(msg)

    def maxCmd_C(self, line):
        """ process C response """
        print "Data from Max_Cmd_C"
        line = line.split(",")
        es = base64.b64decode(line[1])
        if ord(es[0x04]) == 1:
            print "adding device"
            dev_adr = self.hexify(es[0x01:0x04])
            devices[dev_adr][8] = es[0x16]
            # Store the Eco Temp in the devices_eco_temp array
            devices_eco_temps[dev_adr]=ord(es[0x13])/2

    def maxCmd_M(self, line, refresh):
        """ process M response Rooms and Devices"""
        print "Data from Max_Cmd_M"
        logger = logging.getLogger("main.max.maxCmd_M")
        expectedRoomNo = int(Variables().readVariables(['ExpectedNoOfRooms']))
        line = line.split(",")
        es = base64.b64decode(line[2])
        room_num = ord(es[2])
        logger.info("Number of rooms found : {}".format(room_num))

        # Check number of rooms
        if room_num != expectedRoomNo:
            Variables().writeVariable([['RoomsCorrect', 0]])
            logger.info("RoomsCorrect set to  : {}".format(0))
        else:
            Variables().writeVariable([['RoomsCorrect', 1]])
            logger.info("RoomsCorrect set to  : {}".format(1))

        es_pos = 3
        this_now = datetime.datetime.now()
        for _ in range(0, room_num):
            room_id = str(ord(es[es_pos]))
            room_len = ord(es[es_pos + 1])
            es_pos += 2
            room_name = es[es_pos:es_pos + room_len]
            es_pos += room_len
            room_adr = es[es_pos:es_pos + 3]
            es_pos += 3
            if room_id not in rooms or refresh:
                # id   :0room_name, 1room_address,   2is_win_open
                rooms.update(
                    {room_id: [room_name, self.hexify(room_adr), False]})
        dev_num = ord(es[es_pos])
        es_pos += 1
        for _ in range(0, dev_num):
            dev_type = ord(es[es_pos])
            es_pos += 1
            dev_adr = self.hexify(es[es_pos:es_pos + 3])
            es_pos += 3
            dev_sn = es[es_pos:es_pos + 10]
            es_pos += 10
            dev_len = ord(es[es_pos])
            es_pos += 1
            dev_name = es[es_pos:es_pos + dev_len]
            es_pos += dev_len
            dev_room = ord(es[es_pos])
            es_pos += 1
            if dev_adr not in devices or refresh:
                # 0type     1serial 2name     3room    4OW,5OW_time, 6status,
                # 7info, 8temp offset
                devices.update(
                    {dev_adr: [dev_type, dev_sn, dev_name, dev_room, 0, this_now, 0, 0, 7]})
        dbMessage = []
        for keys in rooms:
            roomText = str(rooms[keys][0])

            # For testing ' in names
#             if roomText == "Bathroom":
#                 roomText = "Bathroom's"

            dbList = keys, roomText, rooms[keys][1]
            dbMessage.append(dbList)
        print dbMessage
        DbUtils().updateRooms(dbMessage)
        dbMessage = []
        for keys in devices:
            dbList = keys, devices[keys][0], devices[keys][1], devices[
                keys][2], devices[keys][3], devices[keys][5]
            dbMessage.append(dbList)
        DbUtils().updateDevices(dbMessage)

    def maxCmd_L(self, line):
        """ process L response """
        print "Data from Max_Cmd_L"
        line = line.split(":")
        # print line
        es = base64.b64decode(line[1])
        es_pos = 0
        # print "hex ", self.hexify(es)

        while (es_pos < len(es)):
            dev_len = ord(es[es_pos]) + 1
            # print "Dev Len ", dev_len
            valve_adr = self.hexify(es[es_pos + 1:es_pos + 4])
            # print valve_adr
            valve_status = ord(es[es_pos + 0x05])
            # print valve_status
            valve_info = ord(es[es_pos + 0x06])
            valve_temp = 0xFF
            valve_curtemp = 0xFF

            valve_info_string = '{0}{{:{1}>{2}}}'.format(
                'ob', 0, 8).format(bin(valve_info)[2:])
            valve_mode = str(valve_info_string[8:])

            if valve_mode == '00':
                valve_MODE = 'AUTO'
            elif valve_mode == '01':
                valve_MODE = 'MANUAL'
            elif valve_mode == '11':
                valve_MODE = 'BOOST'
            elif valve_mode == '10':
                valve_MODE = 'VACATION'

            link_status = int(valve_info_string[3:4])
            battery_status = int(valve_info_string[2:3])

            # WallMountedThermostat (dev_type 3)
            if dev_len == 13:
                # print "WALL THERMOSTAT"
                valve_pos = 999
                if valve_info & 3 != 2:

                    # valve_temp = float(int(self.hexify(es[es_pos + 0x08]),
                    # 16)) / 2  # set temp

                    # Get Binary at offset 8
                    valve_binary = "{0:08b}".format(
                        int(self.hexify(es[es_pos + 0x08]), 16))
                    # print "Valve Binary ", valve_binary

                    # Use msb of offset 8 for msb or actual temperature
                    if valve_binary[0:1] == "1":
                        temp_headder = "01"
                    else:
                        temp_headder = "00"

                    # Just use last 6 bits for set temp
                    valve_binary = valve_binary[-6:]
                    # print "Valve Binary after trim", valve_binary

                    valve_temp = float(int(valve_binary, 2)) / 2  # set temp
                    # print "Valve Set temp ", valve_temp

                    # print "Offset 12 Binary :
                    # {0:08b}".format(int(self.hexify(es[es_pos + 0x0C]), 16))

                    curr_binary = "{0}{1:08b}".format(
                        temp_headder,
                        int(self.hexify(es[es_pos + 0x0C]), 16))

                    # print "Current Temp Binary ", curr_binary

                    valve_curtemp = float(
                        int(curr_binary, 2)) / 10  # measured temp
                    # print "Valve Current Temp ", valve_curtemp

            # HeatingThermostat (dev_type 1 or 2)
            elif dev_len == 12:
                valve_pos = ord(es[es_pos + 0x07])
                if valve_info & 3 != 2:
                    valve_temp = float(
                        int(self.hexify(es[es_pos + 0x08]), 16)) / 2
                    valve_curtemp = float(ord(es[es_pos + 0x0A])) / 10

            # WindowContact
            elif dev_len == 7:
                pass

            valves.update({valve_adr: [
                          valve_pos, valve_temp, valve_curtemp, valve_MODE, link_status, battery_status]})
            # save status and info
            #devices[valve_adr][6] = valve_status
            #devices[valve_adr][7] = valve_info
            es_pos += dev_len

        dbMessage = []
        for keys in valves:
            dbList = keys, valves[keys][0], valves[keys][1], valves[keys][
                2], valves[keys][3], valves[keys][4], valves[keys][5]
            dbMessage.append(dbList)
            # print dbList
        DbUtils().updateValves(dbMessage)

    def getCurrentOutsidetemp(self):
        """
        Get Current outside temperature from OpenWeatherMap using the API

        """
        logger = logging.getLogger("main.max.getCurrentOutsidetemp")
        try:
            cityID, userKey = Variables().readVariables(
                ['WeatherCityID', 'WeatherKey'])
            f = urllib2.urlopen(
                'http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}'.format(cityID, userKey))
            json_string = f.read()
            parsed_json = json.loads(json_string)
            temp_k = parsed_json['main']['temp']  # kelvin -273.15
            temp_c = temp_k - 273.15
            f.close()
            logger.info("Outside temp is %sK %sC" % (temp_k, temp_c))
            return temp_c
        except Exception, err:
            logger.exception("No temp data %s" % err)

    def switchHeat(self):
        module_logger.info("main.max.switchHeat running")
        logTime = time.time()
        boilerEnabled, singleRadThreshold, multiRadThreshold,  multiRadCount, AllValveTotal, ManualHeatingSwitch, boilerOverride = Variables().readVariables(['BoilerEnabled', 'SingleRadThreshold', 'MultiRadThreshold', 'MultiRadCount', 'AllValveTotal', 'ManualHeatingSwitch', 'BoilerOverride'])

        roomTemps = CreateUIPage().createRooms()
        outsideTemp = self.getCurrentOutsidetemp()

        # Add outside temp to each rooms information
        for i in range(len(roomTemps)):
            roomTemps[i] = roomTemps[i] + (str(outsideTemp),)

        # Calculate if heat is required
        valveList = []
        for room in roomTemps:
            valveList.append(room[4])

        singleRadOn = sum(i >= singleRadThreshold for i in valveList)
        multiRadOn = sum(i >=  multiRadThreshold for i in valveList)
        totalRadOn = sum(i >=  10 for i in valveList)

        if singleRadOn >= 1 or multiRadOn >= multiRadCount or totalRadOn >= AllValveTotal:
            boilerState = 1
        else:
            boilerState = 0

        # Print out Summary Information
        module_logger.info("Number of Single Radiators over threashold %s " % singleRadOn)
        module_logger.info("Number of Multiple Radiators over threashold %s" % multiRadOn)
        module_logger.info("Total Radiators on %s" % totalRadOn)
        module_logger.info("Setting Boiler state to %s" % boilerState)

        # Boiler Override
        if boilerOverride == 1:
            module_logger.info('Boiler override ON')
            boilerState = 1
        if boilerOverride == 0:
            boilerState = 0
            module_logger.info('Boiler overrideOFF')

        module_logger.info("main.max.switchHeat Boiler is %s, Heating is %s" % (
            boilerEnabled, boilerState))

        # Update Temps database
        DbUtils().insertTemps(roomTemps)

        # Control Boiler
        if boilerEnabled:
            # Set Manual Boiler Switch if enabled
            if ManualHeatingSwitch:
                 module_logger.info("Switching local Relay %s" %boilerState)
                 relayHeating(boilerState)
        else:
            boilerState = 0

            # Set Manual Boiler Switch if enabled
            if ManualHeatingSwitch:
                module_logger.info("Switching local Relay %s" %boilerState)
                relayHeating(boilerState)
        try:
            boilerOn = DbUtils().getBoiler()[2]
        except:
            boilerOn = 9

        if boilerState != boilerOn:
            msg = (logTime, boilerState)
            DbUtils().updateBoiler(msg)
        boilerOn = boilerState

        # Create UI Pages
        CreateUIPage().saveUI(roomTemps)
        # CreateUIPage().saveAdminUI()
