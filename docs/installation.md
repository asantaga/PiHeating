#Installation Instructions



## Configure the Pi

Install a Basic raspberry pi image

From command line or putty session

sudo raspi-config
	expand file system
	change user password
	advanced
		enable I2C
		disable serial boot console

finish
reboot

sudo apt-get update

sudo apt-get upgrade

sudo rpi-update

## disable bluetooth
sudo systemctl disable hciuart

add dtoverlay=pi3-miniuart-bt to /boot/config.txt file

start WinSCP
connect to RPi
	in /home/pi create folder heating
	in /home/pi create folder logs
	from source folder copy all files into heating folder
	edit variables.txt file
		change WebIP to be same as RPi IP
		change MaxIP to be same as Max cube
		change WeatherKey to own key from openweathermap site
		change WeatherCityID to own city
		change WeatherWidget to your location
		If using local relay change ManualHeatingSwitch to 1
		change HouseEcoTemp to the temperature you would like all your radiators to go to 			when the eco button is pressed
	If heating.db file exists please delete. It should be created on first run, do not delete again.

From command line or putty session	

sudo apt-get install python-dev
pip install psutil

## Install the software

	cd $HOME
	mkdir PiHeating
	cd PiHeating
	git clone https://github.com/asantaga/PiHeating
        pip install requests
        pip install setuptools
	pip install psutils

​	

Edit Variables.txt in the bin directory with your maxcube parameters. Use variables_Explanation.txt in the docs folder to understand what all the parameters mean. Many parameters are set dynamically by the system.

##Test the software

```
cd $HOME/PiHeating/bin
sudo python main.py
```

Hopefully it runs ok usually there are a few errors first run stop it and start again
CTRL +C to stop, there should now be a new database file and some log files

sudo python main.py 

on your PC you should be able to load web UI at http://RPi-IP

​	

## Make it run automatically 

Using example file in /config to use with systemd

`sudo cp /home/pi/PiHeating/config/piheating.service /lib/systemd/system/piheating.service`

To start service use

```
sudo systemctl start piheating.service 
```

To stop use

```
sudo systemctl stop piheating.service 
```

To enable start at boot use

```
sudo systemctl enable piheating.service 
```

## Making it reliable

The PiHeating software provides some graphs and charts for viewing, this is great however it does mean the PI is constantly writing to the SD , which is never good. The software by default copys itself to /run/shm (Ramdisk) so that it doesnt touch the SD card. This works great BUT when the raspberry PI is rebooted it will loose the history. If you want long term history then I recommend 
* Modifying startPiHeating.sh so that doesnt copy the code to /run/shm
* (Recommended) Use HomeAssistant somewhere else, and use that with influxDB & grafana. This is my preferred approach as I use homeAssistant to add geolocation to the solutioon (ie if your not at home then turn heating off)


##Sort out the hardware

For this software to work properly you need the following hardware

- Raspberry PI (Any model works fine)
- 5A 240V Relay to control the boiler thermostat line
- 3 x LEDs  (Red, Orange, Green)
- 3 x 330Ohm Resister



| Pin     | Suggested Colour | Use                                                          |      |
| ------- | ---------------- | ------------------------------------------------------------ | ------- |
| GPIO 27 | Green            | This LED is the heart beat led, it flashes every second or so to indicate that the PI is working and everything is fine ||
| GPIO 17 | Orange           | The LED is lit when the PI asks the boiler to turn on. Heat Required if you must ||
| GPIO 7 |  | This line is connected to the 240V 5A Relay to open/close the circuit ||
| +3v     | RED              | This LED simply shows there is power to the LED ||

Wiring diagram TBD
