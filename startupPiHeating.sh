echo "Copying PiHeating to /run/shm"
mkdir -p /run/shm/PiHeating/bin
cp -r /home/pi/PiHeating/bin/* /run/shm/PiHeating/bin
echo "Starting PiHeating"
cd /run/shm/PiHeating/bin
python main.py
