set -x
#!/bin/bash
if ifconfig wlan0 | grep -q "inet :" ; then
   echo "Network connection Up"
else
   echo "Network connection down! Attempting reconnection."
   ifup --force wlan0
fi
