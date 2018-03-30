# PiHeating 
Python code for Raspberry Pi to control a wireless boiler with heat information from MAX! Cube. Boiler control done using relay attached to Pi or Vera home automation

RPi Python Software to switch on a wireless controled boiler depending on what states the valves are in on the MAX Radiator Thermostats.

Basic, and I do mean that, Instructions can be found in /PiHeating/documentation/installation.txt 

Be carefull as this might include the variables.txt file which would overwrite your settings. Best to make a backup before updating.

Edit the variables.txt file before running to match your Pi IP address and your MAX Cube IP address. The database should be created and populated with the MAX valves and thermostats on first run. 

See variables_explanation.txt for a description for each variable.

You can run the PIHeating via crontab or systemd service

- Systemd file can be found in /config directory
- Starting using crontab can be achieved using the bootup.py file executed from a crontab

Before setting up auto starting using the systemd, or crontab, it is a good idea to run the software manually on a command line to check for any problems. just "$ sudo python main.py" to start from inside the PiHeating/bin directory. I left some print statements in so you should see lists of your rooms at some point.


## Autostart using systemd
- Using example file in /config to use with systemd

  `sudo cp /home/pi/PiHeating/config/piheating.service /lib/systemd/system/piheating.service`

  To start service use

  ```
  sudo systemctl start piheating.service 
  ```
  To stop use 
  ```
  sudo systemctl stop piheating.service 
  ```
  To enable start at boot  use 
  ```
  sudo systemctl enable piheating.service 
  ```

## Website

PIHeating provides a website for you to view, and potentially change, heating status. This can be accessed using http://IPAddress:4102

## REST API

The /status api allows you to see the status of the boiler (1=On , 0=Off)

GET http://<raspberryPiIP>:<port>/status
```json
{'boilerStatus':'1'}
```

Setting the house into ECO mode (based on the value in variables.txt)
GET http://raspberryPiIP>:<port>/ecomode

Setting the house into Auto mode (based on the value in variables.txt)
GET http://raspberryPiIP>:<port>/automode



## Integration with Home Assistant

You can display the Max Radiator valves/temperature within HomeAssistant using the Max! component. You can add the boiler as a sensor using the following YAML in HomeAssistant

```
sensor max_boiler_status:
   - platform: rest
     name: MAX Boiler Status
     resource: http://<raspberryPIIP>:4102/status
     method: GET
     value_template: '{{value_json.boilerStatus}}'
```
