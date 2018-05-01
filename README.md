# Crypto-Guru-Pending-Burst-Notifier-for-Raspberry-Pi-Printer
This is a variant of Thothloki's CryptoGuruPendingNotifier found here: https://github.com/thothloki/CryptoGuruPendingNotifier<br>
It also leverages a few of other projects, namely Spebern's API that allowed Thothloki to build his notifier: https://github.com/spebern/goburstpool-api-example Afafruit's IOT Printer project found here: https://learn.adafruit.com/pi-thermal-printer/overview Alex Eames' LED dimming http://RasPi.tv/2013/how-to-use-soft-pwm-in-rpi-gpio-pt-2-led-dimming-and-motor-speed-control   and the python-escpos project here: https://github.com/python-escpos/python-escpos If I've missed anyone out or I've used some of your code and I've not credited you, let me know and I'll add you in here.

This version runs on a Raspberry Pi and prints daily and on-demand summaries of your burst mining activities, particularly to see what your pending balance is for the CryptoGuru burst pools.

Please note, this is only here to share the code. I'm not going to provide any support or bug fixes unless it's something that's bothering me personally.

If you find value in this code/app, please consider donating to me (address below)

This was written in Python 3.

If you want to replicate this project without hacking around with the code, you will need the following:<br>
1x Raspberry Pi with GPIO headers<br>
An LED push button for an arcade machine - See here for how to connect it. https://learn.adafruit.com/pi-thermal-printer/soldering<br>
An Epson TM88-III POS printer with USB interface

You can probably use a different Epson POS printer or interface fairly easily but that's entirely up to you to figure out.

For the script to run you will need to install the following prerequisites:<br>
sudo apt-get update<br>
sudo apt-get install git cups wiringpi build-essential libcups2-dev libcupsimage2-dev python-serial python-pil python-unidecode rpi.gpio<br>
sudo pip3 install python-escpos grpcio-tools chardet2 urllib3 requests

Edit the script and change these variables to your details:<br>
burstAddress = "BURST-XYKV-9LAA-KQ4Z-FWGT3" # Your BURST wallet in quotes.<br>
poolAddress  = "0-100-pool.burst.cryptoguru.org:8008" # The address of your pool.

Don't change anything else unless you're confident with what you're doing.

Finally run the script as root/sudo. You need this for access to the GPIO pins.<br>
sudo python3 CGPN-Printable-RPi.py

A daily print out will run at 6:30am If you want to change this time, stop the script, change the following variables and restart the script.<br>
dFHours      = 6     # Hour to run daily (24 hours)<br>
dFMins       = 30    # Mins past the hour to run daily

A single tap of the button will print out a summary. Hold it down for 2+ seconds and the Raspberry Pi will shutdown.

If you like this, please donate some BURST to me!<br>
BURST: BURST-XYKV-9LAA-KQ4Z-FWGT3
