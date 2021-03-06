from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    import RPi.GPIO as GPIO
import logging
from variables import Variables
from database import DbUtils
from os import system
import time

module_logger = logging.getLogger("main.heatinggpio")

B_OFF = 04      # Boiler off LED    ANGELOUNUSED
H_ON  = 17      # Heat On LED
H_OFF = 18      # Heat Off LED      ANGELOUNUSED
C_OK  = 22      # Cube OK LED       ANGELOUNUSED
C_ERR = 23      # Cube Error LED    ANGELOUNUSED
HBEAT = 27      # HEARTBEAT LED
ON_OFF = 05     # Boiler ON/Off button  ANGELOUNUSED
CHECKH = 06     # Manual Valve check button ANGELOUNUSED
SHUTDOWN = 12   # Shutdown RPi button   ANGELOUNUSED
REBOOT   = 11   # Reboot RPi button
BOILER_SW= 07   # Boiler relay switch output


def hBeat(beat_time):
    module_logger.info("starting heart beat for %s" % beat_time)
    GPIO.setup(HBEAT,GPIO.OUT)
    GPIO.output(HBEAT,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(HBEAT,GPIO.LOW)
    module_logger.debug("heartbeat ended")


def setupGPIO(input_queue):
    '''
    Constructor
    '''
    module_logger.info("Setting up GPIO Pins")
    if _platform == "linux" or _platform == "linux2":
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(B_OFF,GPIO.OUT) # Boiler Disabled
        GPIO.setup(H_ON,GPIO.OUT) # Heat ON
        GPIO.setup(H_OFF,GPIO.OUT) # Heat Off
        GPIO.setup(C_OK,GPIO.OUT) # Cube OK
        GPIO.setup(C_ERR,GPIO.OUT) # Cube Error
        GPIO.setup(HBEAT,GPIO.OUT) # Heart beat
        GPIO.setup(BOILER_SW,GPIO.OUT) # Boiler Switch
        GPIO.setup(ON_OFF,GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Disable Heat Button
        GPIO.setup(CHECKH,GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Check Heat
        #GPIO.setup(SHUTDOWN,GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 
        GPIO.setup(REBOOT,GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Reboot Raspberry Pi
          
        GPIO.add_event_detect(ON_OFF,GPIO.FALLING, callback=buttonDisableBoiler, bouncetime=500)# 05
#        GPIO.add_event_detect(CHECKH,GPIO.FALLING, callback=buttonCheckHeat, bouncetime=500)    # 06
        #GPIO.add_event_detect(SHUTDOWN,GPIO.FALLING, callback=buttonShutdown, bouncetime=500)     # 12
        GPIO.add_event_detect(REBOOT,GPIO.FALLING, callback=buttonReboot, bouncetime=500)       # 13


def buttonDisableBoiler(channel):
    module_logger.info('Button Disable Boiler pressed, channel %s' % channel)
    boilerState = Variables().readVariables(['BoilerEnabled'])
    if boilerState == 1:
        boilerState = 0
    else:
        boilerState = 1
    Variables().writeVariable([['BoilerEnabled', boilerState]])

    # Set Boiler State
    if boilerState:
        module_logger.debug('GPIO boiler on')
        GPIO.output(B_OFF,GPIO.HIGH)
    else:
        module_logger.debug('GPIO boiler off')
        GPIO.output(B_OFF,GPIO.LOW)

#
# This function appears to flash the LEDs and then check if heat is needed
# alas it cant call the MaxInterface function as it would be a circular reference
# commenting out for now
#def buttonCheckHeat(channel):
#    module_logger.info('Button check heat pressed, channel %s' % channel)
#    GPIO.output(B_OFF,GPIO.LOW)
#    GPIO.output(H_ON,GPIO.LOW)
#    GPIO.output(H_OFF,GPIO.LOW)
#    GPIO.output(C_OK,GPIO.LOW)
#    GPIO.output(C_ERR,GPIO.LOW)
#
#    for _ in range(4):
#        sleepTime = 0.1
#        GPIO.output(H_ON,GPIO.HIGH)
#        time.sleep(sleepTime)
#        GPIO.output(H_ON,GPIO.LOW)
#        GPIO.output(H_OFF,GPIO.HIGH)
#        time.sleep(sleepTime)
#        GPIO.output(H_OFF,GPIO.LOW)
#        GPIO.output(C_ERR,GPIO.HIGH)
#        time.sleep(sleepTime)
#        GPIO.output(C_ERR,GPIO.LOW)
#        GPIO.output(C_OK,GPIO.HIGH)
#        time.sleep(sleepTime)
#        GPIO.output(C_OK,GPIO.LOW)
#
#    MaxInterface().checkHeat(0)
#    setStatusLights()

def buttonReboot(channel):
    module_logger.info('Button Reboot pressed, channel %s' % channel)
    buttonPressTimer = 0
    while True:
        if (GPIO.input(channel) == False):
            buttonPressTimer += 1
            if buttonPressTimer > 4:
                ledFlash = GPIO.PWM(C_ERR, 30)
                ledFlash.start(50)
            elif buttonPressTimer == 2:
                ledFlash = GPIO.PWM(C_ERR, 5)
                ledFlash.start(50)
            elif buttonPressTimer == 3:
                ledFlash = GPIO.PWM(C_ERR, 10)
                ledFlash.start(50)
            elif buttonPressTimer < 3:
                ledFlash = GPIO.PWM(C_ERR, 2)
                ledFlash.start(50)
        else:
            if buttonPressTimer > 4:
                module_logger.warning("Rebooting now")
                system("sudo reboot")
            elif buttonPressTimer <= 4:
                module_logger.info('not long enough press for reboot')
            buttonPressTimer = 0
            ledFlash.stop()
            setStatusLights()
            break
        time.sleep(1)

def relayHeating(status):
    module_logger.info('Manual Heating switch, status %s' % status)
    if status == 0:
        GPIO.output(BOILER_SW,GPIO.LOW) # Pull down Relay to switch off
    elif status == 1:
        GPIO.output(BOILER_SW,GPIO.HIGH)
    
def setStatusLights():
    module_logger.info("setting status lights")
    cube_state, boiler_enabled, local_relay = Variables().readVariables(['CubeOK',  'BoilerEnabled', 'ManualHeatingSwitch'])
    heating_state = DbUtils().getBoiler()[2]
    if cube_state:
        GPIO.output(C_OK,GPIO.HIGH)
        GPIO.output(C_ERR,GPIO.LOW)
    else:
        GPIO.output(C_OK,GPIO.LOW)
        GPIO.output(C_ERR,GPIO.HIGH)
    
    # Set Heating State
    if heating_state:
        # Heat required
        module_logger.info("Setting Lights to Heat Required H_ON and Relay to high")
        GPIO.output(H_ON,GPIO.HIGH)
        GPIO.output(H_OFF,GPIO.LOW)
        if local_relay:
            module_logger.info("Switching local relay to high")
            GPIO.output(BOILER_SW,GPIO.HIGH) # Pull down Relay to switch on.
    else:
        # No heat required
        module_logger.info("Setting Lights to Heat Required H_OF and Relay to Low")
        GPIO.output(H_ON,GPIO.LOW)
        GPIO.output(H_OFF,GPIO.HIGH)
        if local_relay:
            module_logger.info("Switching local relay to low")
            GPIO.output(BOILER_SW,GPIO.LOW)
    
    # Set Boiler State
    if boiler_enabled:
        module_logger.info("Boiler Enabled Light On")
        GPIO.output(B_OFF,GPIO.HIGH)
    else:
        module_logger.info("Boiler Enabled Light Off ")
        GPIO.output(B_OFF,GPIO.LOW)

