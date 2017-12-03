FROM python:3
MAINTAINER twistedsanity

# Evironment variables to be changed in variables.txt
# ENV DEBIAN_FRONTEND=noninteractive 
# $WebIP,192.168.0.41
# $WebPort,4102
# $MaxIP,192.168.0.36
# $MaxIP2,192.168.0.37
# $VeraIP,192.168.0.13
# $VeraPort,3480
# $VeraDevice,92
# $VeraOutsideTempID,112
# $SingleRadThreshold,78
# $MultiRadThreshold,60
# $MultiRadCount,2
# $AllValveTotal,120
# $WeatherKey,713951e4ce665b2d2d5d1b7a10b88f63
# $WeatherCityID,6640068
# $WeatherWidget,http://forecast.io/embed/#lat=57.155689&lon=-2.295520&name=Kier Circle Westhill&units=uk


# Use baseimage-docker's init system.
# CMD ["/sbin/my_init"]

# Update packages and install software
RUN \
	apt-get update && \
	apt-get install -y \
	apt-utils \
 	# python-dev \
	wget \
	unzip \
  
# Needed for testing
	nano \
	iputils-ping \
	dnsutils && \
# End testing apps

	apt-get clean && rm -rf /tmp/* /var/tmp/* && \
	pip install psutil && \


# Get and install PiHeating files
	wget https://github.com/twistedsanity/PiHeating/archive/master.zip && \
	unzip master.zip && \
	cp -rp PiHeating-master/* /home/pi/heating/ && \
	chmod +x /home/pi/heating/main.py && \ 

	sed -i \
         's/WebIP,192.168.0.41/WebIP,$WebIP/' \
         's/WebPort,4102/WebPort,$WebPort/' \
			   's/MaxIP,192.168.0.36/MaxIP,$MaxIP/' \
         's/MaxIP2,192.168.0.37/MaxIP2,$MaxIP2/' \
         's/VeraIP,192.168.0.13/VeraIP,$VeraIP/' \
         's/VeraDevice,92/VeraDevice,$VeraDevice/' \
         's/VeraOutsideTempID,112/VeraOutsideTempID,$VeraOutsideTempID/' \
         's/SingleRadThreshold,78/SingleRadThreshold,$SingleRadThreshold/' \
         's/MultiRadThreshold,60/MultiRadThreshold,$MultiRadThreshold/' \
         's/MultiRadCount,2/MultiRadCount,$MultiRadCount/' \
         's/AllValveTotal,120/AllValveTotal,$AllValveTotal/' \
			   's/WebIP,192.168.0.41/$WeatherKey/' \
         's/WebIP,192.168.0.41/$WeatherCityID/' \
         's/WebIP,192.168.0.41/$WeatherWidget/' \
		/home/pi/heating/variables.txt && \	
	
# Volumes
VOLUME /home/pi

# Running scripts during container startup
CMD [ "python", "./main.py" ]
