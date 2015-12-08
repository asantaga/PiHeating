#!/usr/bin/env python
import sqlite3
dataBase =  'heating.db'

class DbUtils():
    def __init__(self):
        """
        Database utilities
        """

    def initialiseDB(self):
        print "initialising database"
        
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor() #Cursor object to execute sql commands
        cursor.execute("""CREATE TABLE IF NOT EXISTS MaxCubes
                        (ID TEXT PRIMARY KEY,
                        SerialNo TEXT,
                        rfChannel TEXT,
                        dutyCycle INTEGER)
                        """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS rooms
                        (ID INT PRIMARY KEY,
                        Name TEXT,
                        GroupID TEXT)
                        """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS devices
                        (RFAddress TEXT NOT NULL PRIMARY KEY,
                        Type INT,
                        SerialNo TEXT,
                        Name TEXT,
                        RoomID INT,
                        UpdateTime TEXT)
                        """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS valves
                        (RFAddress TEXT NOT NULL PRIMARY KEY,
                         ValvePos INT,
                         SetTemp TEXT,
                         ActTemp TEXT)
                        """)
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS boiler
                        (ID INTEGER PRIMARY KEY ASC,
                         Time TEXT,
                         State INTEGER)
                        """)
        
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS temps
                        (ID INTEGER PRIMARY KEY ASC,
                         RoomName TEXT,
                         time TEXT,
                         SetTemp TEXT,
                         ActTemp TEXT,
                         ValvePos INTEGER,
                         OutsideTemp TEXT)
                        """)
        
        
            
    def insertTemps(self, msg):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.executemany("INSERT or REPLACE into temps(ID,RoomName,time,SetTemp,ActTemp,ValvePos,OutsideTemp)\
                                VALUES(NULL, ?, ?, ?, ?, ?, ?)", msg)
            
            
    def updateCube(self, msg):
        
        try:
            conn = sqlite3.connect(dataBase)
            cursor = conn.cursor()
            cursor.execute("INSERT or REPLACE into MaxCubes(ID,SerialNo,rfChannel,dutyCycle)\
                                 VALUES(?, ?, ?, ?)", msg)
            #print "Committing Database"
            conn.commit()
            
        except Exception as e:
            #print "Database Rollback"
            conn.rollback()
            raise e
        finally:
            #print "Closing Database"
            conn.close()
            
    def updateRooms(self, msg):
        
        try:
            conn = sqlite3.connect(dataBase)
            cursor = conn.cursor()
            cursor.executemany("INSERT or REPLACE into rooms(ID,Name,GroupID)\
                                 VALUES(?, ?, ?)", msg)
            #print "Committing Database"
            conn.commit()
            
        except Exception as e:
            #print "Database Rollback"
            conn.rollback()
            raise e
        finally:
            #print "Closing Database"
            conn.close()
            
    def updateDevices(self, msg):
        
        try:
            conn = sqlite3.connect(dataBase)
            cursor = conn.cursor()
            cursor.executemany("INSERT or REPLACE into devices(RFAddress,Type,SerialNo,Name,RoomID,UpdateTime)\
                                 VALUES(?, ?, ?, ?, ?, ?)", msg)
            #print "Committing Database"
            conn.commit()
            
        except Exception as e:
            #print "Database Rollback"
            conn.rollback()
            raise e
        finally:
            #print "Closing Database"
            conn.close()
            
    def updateValves(self, msg):
        
        try:
            conn = sqlite3.connect(dataBase)
            cursor = conn.cursor()
            cursor.executemany("INSERT or REPLACE into valves(RFAddress,ValvePos,SetTemp,ActTemp)\
                                 VALUES(?, ?, ?, ?)", msg)
            #print "Committing Database"
            conn.commit()
            
        except Exception as e:
            #print "Database Rollback"
            conn.rollback()
            raise e
        finally:
            #print "Closing Database"
            conn.close()
            
    def updateBoiler(self, msg):
        
        try:
            conn = sqlite3.connect(dataBase)
            cursor = conn.cursor()
            cursor.execute("INSERT or REPLACE into boiler(ID,Time,State)\
                                 VALUES(NULL, ?, ?)", msg)
            #print "Committing Database"
            conn.commit()
            
        except Exception as e:
            #print "Database Rollback"
            conn.rollback()
            raise e
        finally:
            #print "Closing Database"
            conn.close()
            
    def getTemps(self, roomName, currentTime):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("""SELECT * FROM temps WHERE RoomName = '{}' AND time > {}""".format(roomName, currentTime))
            variables = cursor.fetchall()
            return variables
        
    def getCubes(self):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM MaxCubes")
            variables = cursor.fetchall()
            return variables[0]
        
    def getRooms(self):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM rooms ORDER by Name ASC")
            variables = cursor.fetchall()
            return variables
        
    def getDevices(self):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM devices")
            variables = cursor.fetchall()
            return variables
        
    def getValves(self):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM valves")
            variables = cursor.fetchall()
            return variables
        
    def getBoiler(self):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM boiler WHERE ID = (SELECT MAX(ID) FROM boiler)")
            variables = cursor.fetchall()
            return variables[0]
        
    def getAllBoiler(self):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM boiler")
            variables = cursor.fetchall()
            return variables
        
    def getTimedBoiler(self, timeLimit):
        conn = sqlite3.connect(dataBase)
        cursor = conn.cursor()
        with conn:
            cursor.execute("SELECT * FROM boiler WHERE Time > {}".format(timeLimit))
            variables = cursor.fetchall()
            return variables
        
    