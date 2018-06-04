#!/bin/sh
#Sleep 5mins on initial boot, this is to prevent bootloops where we constantly reboot , test, reboot etc etc 
cat stat.log | mail -s "PiHeating Rebooted- logfile" you@youremail.com
sleep 300
#
while :
do
   if nc -z 192.168.0.1 80 2>/dev/null; then
       echo "server is ok ✓ `date`" >> stat.log
   else
       echo "server is down ✗ `date`" >> stat.log
       echo "REBOOTING Server" >> stat.log
       /sbin/shutdown -r now
   fi
   echo "Sleeping for 10mins" >> stat.log
   # Sleep for 5mins before testing again
   sleep 300
done

