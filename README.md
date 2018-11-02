# Deprecated
---
```
Alas this code is now deprecated for me. Im suffering from a known problem with the max!cube which is if you poll it too often it eventually hard resets itself and everything stops working.. You need to go around "RESET"each TRV and then manually add them to the cube again.. For a heating system is isnt ideal.. 

Eq3 havent responded to my plees of assistance and this screams of Internet of Abandonment...

Until I have a solution for the cube resetting itself I wont be developing this any further
```
---


# PiHeating 
This code is based on Stephen Halls original code ([stephenmhall/PiHeating](https://github.com/stephenmhall/PiHeating)) however now heavily modified. Specifically Ive simplified the code and removed the vera device control stuff. If you want the vera control then I suggest you look at the original code (Stephenmhall) or let me know and I'll look to adding it back in.



This repository contains Python code solution for Raspberry Pi to control a wireless boiler with heat information from MAX! Cube. Boiler control done using relay attached to Pi.

RPi Python Software to switch on a wireless controled boiler depending on what states the valves are in on the MAX Radiator Thermostats. The PI will request heat depending on parameters set in the variables.txt file

Basic Install Instructions can be found in docs/installation.txt and you can can run the PIHeating via crontab or systemd service



Before setting up auto starting using the systemd, or crontab, it is a good idea to run the software manually on a command line to check for any problems. just "$ sudo python main.py" to start from inside the PiHeating/bin directory. I left some print statements in so you should see lists of your rooms at some point.

## Website

PIHeating provides a website for you to view, and potentially change, heating status. This can be accessed using http://IPAddress:portNumber

## REST API (Of Sorts)

| URL       | Method | What                                                         | Example              |
| --------- | ------ | ------------------------------------------------------------ | -------------------- |
| /status   | GET    | Gives JSON string indicating boiler status (Active/Inactive) | {'boilerStatus':'1'} |
| /ecomode  | GET    | Sets the MAX Radiators into ECO mode. This is done by setting a fixed temperature (e.g, 15c) and setting the mode to manual.  This call will take 1second for each radiator you have. This is so it doesnt overload the MaxCube | 200 response         |
| /automode | GET    | Sets the MAX Radiators into AUTO mode. This is done by setting a fixed temperature (e.g, 15c) and setting the mode to manual.  This call will take 1second for each radiator you have. This is so it doesnt overload the MaxCube | 200 response         |
|           |        |                                                              |                      |
|           |        |                                                              |                      |
|           |        |                                                              |                      |
|           |        |                                                              |                      |
|           |        |                                                              |                      |
|           |        |                                                              |                      |



## Integration with Home Assistant

You can display the Max Radiator valves/temperature within HomeAssistant using the Max! component. You can add the boiler as a sensor using the following YAML in HomeAssistant configuration.yaml

```
sensor max_boiler_status:
   - platform: rest
     name: MAX Boiler Status
     resource: http://<raspberryPIIP>:<port>/status
     method: GET
     value_template: '{{value_json.boilerStatus}}'
```

You can also get HomeAssistant to change the mode of the house from ECO to AUTO based on the presence of devices. 

e.g. 

1. Setup  [GPSLogger](https://www.home-assistant.io/components/device_tracker.gpslogger/) in home assistant so that it knows about your mobile phones. If this is working correctly you will have a number of "device_tracker" devices in HomeAssistant. For me I have device_tracker.josphone and device_tracker.angelosphone

2. Configure a zone around your home , say 500m, 
   configuration.yaml

   ```
   zone:
     - name: Home
       latitude: 51.4946549
       longitude: -0.3169144
       radius: 500
       icon: mdi:home

   ```

3. Configure Automation so that when you arrive within the zone it calls the boiler to Auto Mode, when you leave set the boiler to ECO mode, e.g. 

*configuration.yaml*
This entry adds a REST call to the RaspberryPI, telling it to either go to ECO mode or to Auto mode. Change the IP address of your raspberry pi
```
rest_command:
  heating_ecomode:
     url: 'http://192.168.0.28/ecomode'
     method: GET
     timeout: 60
  heating_automode:
     url: 'http://192.168.0.28/automode'
     method: GET
     timeout: 60
```
*automations.yaml*
These two automations (written backwards sorry), listen to the locations of the two device trackers (two in my case, you can have one), if both are not at home then set the boiler to ECO mode, else set to auto

   ```
- action:
  - alias: ''
    data:
      message: Neither Angelo or Jo Home, turn boiler off
    service: notify.mypushbullet
  - service: rest_command.heating_ecomode
  alias: NeitherAngeloOrJoHome
  condition: []
  id: '1521329285927'
  trigger:
  - platform: template
    value_template: "{% if is_state(\"device_tracker.angelosphone\", \"home\") or\n\
      \     is_state(\"device_tracker.josphone\", \"home\") %}\nfalse\n{% else %}\n\
      true\n{% endif %}"


- action:
  - service: rest_command.heating_automode
  alias: AngeloOrJoHome
  condition: []
  id: '1521331821816'
  trigger:
  - platform: template
    value_template: "{% if is_state(\"device_tracker.angelosphone\", \"home\") or\n\
      \     is_state(\"device_tracker.josphone\", \"home\") %}\ntrue\n{% endif %}"
   ```
   
