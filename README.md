# PiHeating converted to work with Docker
To complete:
    Variables not applying therefore all IPs need to be manually entered.

Python code for Raspberry Pi to control a wireless boiler via Vera home automation with heat information from MAX! Cube.

RPi Python Software to switch on a wireless controled boiler depending on what states the valves are in on the MAX Radiator Thermostats.

The message gets to the Boiler via a Vera home automation unit and Mysensor 433Mhz transmitter node.

Basic, and I do mean that, Instructions can be found in /PiHeating/src/heating/installation.txt and crontab instructions.txt

made changes to the basic folder layout to make it easier to install on Raspberry. cd into your home directory on Pi then
git clone the files in from the link provided by Git. This will create a PiHeating folder with the required files inside.

i.e. "$ git clone https://github.com/stephenmhall/PiHeating.git" you can then use "$ git pull" to get latest files after any changes.
Be carefull as this might include the variables.txt file which would overwrite your settings. Best to make a backup before updating.

Edit the variables.txt file before running to match your Pi IP address and your MAX Cube IP address. The database should be created and populated with the MAX valves and thermostats on first run.

Before setting up auto starting using the crontab instructions it is a good idea to run the software manually on a command line to check for any problems. just "$ sudo python main.py" to start from inside the PiHeating directory. I left some print statements in so you should see lists of your rooms at some point.


Autostart using systemd
- Added file into /config to use with systemd
  sudo cp /home/pi/PiHeating/piheating.service /lib/systemd/system/myscript.service
  To start use
  sudo systemctl start piheating.service 
  To stop use 
  sudo systemctl stop piheating.service 
  To enable start at boot  use 
  sudo systemctl enable piheating.service 
  
