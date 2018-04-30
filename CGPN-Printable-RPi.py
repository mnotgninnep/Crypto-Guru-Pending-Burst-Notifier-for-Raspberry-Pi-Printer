
# This particular script was written by mikeyp.
#
# MUST BE RUN AS ROOT for GPIO access.
# Some code borrowed from Adafruit's IOT thermal printer project
# https://github.com/adafruit/Python-Thermal-Printer
# Also based on code from Thothloki's CryptoGuruPendingNotifier
# https://github.com/thothloki/CryptoGuruPendingNotifier
# Donate BURST Coin to him here: BURST-QCL8-NXGJ-L5WD-35KXA
# Donate BURST Coin to me here:  BURST-XYKV-9LAA-KQ4Z-FWGT3

# Script Revisions:
# V1.0 - Initial version.
# V1.1 - Fixed typo in a string.
# V1.2 - Re-ordered and tidied up the code into a sensible order. Also added
#        code to set daily flag at the beginning to prevent printout if the
#        script is started after the daily flag time.

# You need to install the following:
# sudo apt-get install git cups wiringpi build-essential libcups2-dev libcupsimage2-dev python-serial python-pil python-unidecode
# sudo apt-get install rpi.gpio
# sudo pip3 install python-escpos
# sudo pip3 install grpcio-tools
# sudo pip3 install chardet2 urllib3
# sudo pip3 install requests

###########################################################
# THE SCRIPT NEEDS TO BE RUN AS SUDO/ROOT FOR GPIO ACCESS #
###########################################################

# Load required resources
import RPi.GPIO as GPIO
import subprocess, time, threading
from escpos import *
import grpc
import api_pb2
import api_pb2_grpc
from decimal import Decimal
import requests

# Set some variables
burstAddress = "BURST-XYKV-9LAA-KQ4Z-FWGT3"
poolAddress  = "0-100-pool.burst.cryptoguru.org:8008"
ledPin       = 18    # LED is powered from this pin
buttonPin    = 23    # RPi listens to this pin for the button press
holdTime     = 2     # Duration for button hold (shutdown)
tapTime      = 0.01  # Debounce time for button taps
printer      = printer.Usb(0x04b8,0x0202) # Device ID for Epson TM-T88III
printerchars = 42    # Char limit for Epson TM-T88III
dFHours      = 6     # Hour to run daily (24 hours)
dFMins       = 30    # Mins past the hour to run daily
dailyFlag    = False # Set after daily trigger occurs

# Now set dailyFlag correctly for the time of day...
l = time.localtime()
if (60 * l.tm_hour + l.tm_min) > (60 * dFHours + dFMins):
    if dailyFlag == False:
        dailyFlag = True
    else:
        dailyFlag = False  # Reset daily trigger

# Collect variables from t'internet.
# Converts the burst address to its numeric form. Invoked from getBurstData().
def convert(addy):
    burst = addy
    try:
        URL = ("https://wallet1.burstnation.com:8125/burst?requestType=rsConvert&account=" + burst)
        r = requests.get(url = URL)
        data = r.json()
        numeric = data['account']
        return numeric
    except:
        numeric = ''
        return numeric

# Gets the wallet balance. Invoked from getBurstData().
def getBal(addy):
    burst = addy
    try:
        URL = ("https://explore.burst.cryptoguru.org/api/v1/account/" + burst)
        r = requests.get(url = URL)
        data = r.json()
        bar = ((data['data'])['balance'])
        bal = (int(bar)/100000000)
        return bal
    except:
        bal = ''
        return bal

# Gets various data from the burst pool. Invoked from tap().
def getBurstData():
    addy = burstAddress
    poolSelect = poolAddress
    if addy == "":
        pendingAmount = "0"
        effectiveCapacity = "0"
    else:
        channel = grpc.insecure_channel(str(poolSelect))
        stub = api_pb2_grpc.ApiStub(channel)
        addy = convert(addy)
        addy2 = int(addy)
        miner1 = (stub.GetMinerInfo(api_pb2.MinerRequest(ID=addy2)))
        pend = (int(miner1.pending)/float(100000000))
        cap = Decimal(miner1.effectiveCapacity)
        cap = round(cap, 4)
        historic = (miner1.historicalShare)
        historic = round((historic * 100),3)
        blocks = (miner1.nConf)
        balance = getBal(addy)
        pendingAmount = (str(pend) + " Burst")
        effectiveCapacity = (str(cap) + " TB")
        historicalShare = (str(historic) + "%")
        validDl = (str(blocks))
        bal = (str(balance) + " BURST")
        return(pendingAmount, effectiveCapacity, historicalShare, validDl, bal)

# Called when button is held down.  Prints image, invokes shutdown process.
def hold():
    e.set()
    # I turned off the goodbye print to not waste paper.
    # Uncomment the next 5 lines to turn it on.
    #greetingmessage = "\nShutting Down.\n\n"
    #printer.set(align='center', width=1)
    #printer.image("goodbye.png")
    #printer.text(greetingmessage)
    #printer.cut()
    subprocess.call("sync")
    subprocess.call(["shutdown", "-h", "now"])
    e.clear()

# Generates pulsating LED for the button. Threaded process called from the LED fade start below.
def ledfading(e, th):
    led.start(0)              # start led on 0 percent duty cycle (off)
    pause_time = 0.015           # you can change this to slow down/speed up
    while True:
        # now the fun starts, we'll vary the duty cycle to 
        # dim/brighten the led
        for i in range(0,101):      # 101 because it stops when it finishes 100
            if e.isSet():
                i = 100
            led.ChangeDutyCycle(i)
            time.sleep(pause_time)
        for i in range(100,-1,-1):      # from 100 to zero in steps of -1
            if e.isSet():
                i = 100
            led.ChangeDutyCycle(i)
            time.sleep(pause_time)

# Formats the print job and sends it to the printer
def sendprint(pendingAmount, effectiveCapacity, historicalShare, validDl, bal):
    header = "CryptoGuru Pending Notifier\n\n"
    printjob = burstAddress
    printjob = printjob + "\nPending: " + pendingAmount
    printjob = printjob + "\nEffective Capacity: " + effectiveCapacity
    printjob = printjob + "\nHistorical Share: " + historicalShare
    printjob = printjob + "\nValid Deadlines Last 360 Blocks: " + validDl
    printjob = printjob + "\nPool: " + poolAddress
    printjob = printjob + "\nWallet Balance: " + bal
    footer = "\n\nPlease donate! Scripts by\nThothloki BURST-QCL8-NXGJ-L5WD-35KXA and\nmikeyp BURST-XYKV-9LAA-KQ4Z-FWGT3"
    printer.set(align='center', width=1)
    print(header) # To terminal
    printer.text(header)
    printer.set(align='left', width=1)
    print(printjob) # To terminal
    printer.text(printjob)
    printer.set(align='left', width=1)
    print(footer) # To terminal
    printer.text(footer)
    printer.cut()

# Called when button is briefly tapped. Invokes getBurstData and prints the result.
def tap():
    e.set()  # LED on while working
    pendingAmount, effectiveCapacity, historicalShare, validDl, bal = getBurstData()
    # Output variables to screen/printer
    sendprint(pendingAmount, effectiveCapacity, historicalShare, validDl, bal) # Send activity to printer.
    e.clear() # Revert LED to usual state

####################
## Initialization ##
####################

# Use Broadcom pin numbers (not Raspberry Pi pin numbers) for GPIO
GPIO.setmode(GPIO.BCM) # choose BCM or BOARD numbering schemes. I use BCM

# Enable LED and button (w/pull-up on latter)
GPIO.setup(ledPin, GPIO.OUT) # set GPIO pin 18 as output for led
led = GPIO.PWM(18, 100)      # create object led for PWM on pin 18 at 100 Hertz
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # set GPIO 18 as output for led

# Set led fade start
e = threading.Event()
th = threading.Thread(name="non-block", target=ledfading, args=(e, 2))
th.start()

# LED on while working
e.set()

# Processor load is heavy at startup; wait a moment to avoid
# stalling during greeting.
time.sleep(10)

# Print greeting message
# I turned off the hello print to not waste paper.
# Uncomment the next 5 lines to turn it on.
#greetingmessage = "\nHello, this printer is online and ready!\n\n"
#printer.set(align='center', width=1)
#printer.image("hello.png")
#printer.text(greetingmessage)
#printer.cut()
# Revert LED to usual state
e.clear()

# Poll initial button state and time
prevButtonState = GPIO.input(buttonPin)
prevTime        = time.time()
tapEnable       = False
holdEnable      = False

# Main loop
try:
    while(True):
        # Poll current button state and time
        buttonState = GPIO.input(buttonPin)
        t           = time.time()

        # Has button state changed?
        if buttonState != prevButtonState:
            prevButtonState = buttonState   # Yes, save new state/time
            prevTime        = t
        else:                             # Button state unchanged
            if (t - prevTime) >= holdTime:  # Button held more than 'holdTime'?
                # Yes it has.  Is the hold action as-yet untriggered?
                if holdEnable == True:        # Yep!
                    print("Button held down, shutting down.") # Let console user know what's happened
                    hold()                      # Perform hold action (usu. shutdown)
                    holdEnable = False          # 1 shot...don't repeat hold action
                    tapEnable  = False          # Don't do tap action on release
            elif (t - prevTime) >= tapTime: # Not holdTime.  tapTime elapsed?
                # Yes.  Debounced press or release...
                if buttonState == True:       # Button released?
                    if tapEnable == True:       # Ignore if prior hold()
                        print("Button tapped.")
                        tap()                     # Tap triggered (button released)
                        tapEnable  = False        # Disable tap and hold
                        holdEnable = False
                else:                         # Button pressed
                    tapEnable  = True           # Enable tap and hold actions
                    holdEnable = True

        # Once per day (currently set for 6:30am local time, or when script
        # is first run, if after 6:30am), run forecast and sudoku scripts.
        # Set dFHour and dFMins above.
        l = time.localtime()
        if (60 * l.tm_hour + l.tm_min) > (60 * dFHours + dFMins):
            if dailyFlag == False:
                print("Daily printout at 6:30am.")
                tap()
                dailyFlag = True
        else:
            dailyFlag = False  # Reset daily trigger

except KeyboardInterrupt:
    led.stop()            # stop the led PWM output
    GPIO.cleanup()          # clean up GPIO on CTRL+C exit
