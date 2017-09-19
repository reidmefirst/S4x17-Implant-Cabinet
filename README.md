This project accompanies the S4x17 Flag writeup available at a to-be-determined URL.

This particular flag requires players to break into a control cabinet and 'place an implant.' Players have to open the cabinet door without triggering a door alarm contact. If the player succeeds, a success ticket prints out from the cabinet printer, and the player can prove that they won.

# Hardware prep

The cabinet build requires the following parts:

* Raspberry Pi2 or Pi3. We recommend the 3, so that you can set up a hostapd on it for troubleshooting.
* USB thermal receipt printer (we used this one: https://www.amazon.com/gp/product/B015W1VG18/ref=oh_aui_search_detailpage?ie=UTF8&psc=1 )
* PiFace shield
* Raspberry Pi camera
* Magnetic reed relay switch
* Pushbutton with built-in LED
* A 12V piezo speaker
* A cabinet that can accept a padlock

Use an input on the PiFace shield to read the status of the reed relay switch (tell if it is open or closed). We used input 0.

Use another input on the PiFace shield to read the button press from the pushbutton switch. We used input 7.

Use an output on the PiFace shield, coupled with a current-limiting resistor, to connect to the pushbutton switch LED. This lets us flash the LED when conditions are correct. We used output 2. Note that outputs 0 and 1 on the PiFace are connected to relays, this is the first of the 3.3V outputs.

Use a relay output on the PiFace shield to operate the speaker. We used output 0. You will need to supply the relay with +12V power via a separate power supply so that the speaker operates.

# Software Setup

## Modify the code, if needed

Modify the code to reflect the pins that you chose to connect your system. 

The pin definitions are set by global variables:
* alarmPin - This output ontrols the piezo speaker
* implantPin - This input reads the 'place implant' button
* cabinetState - This input reads the magnetic reed relay latch
* ledPin - This output controls which pin flashes the 'ready for implant' light. Remember to use a resistor so your LED doesn't try to draw too much current.

## Install opencv, set up the Pi

You will need to install opencv (use apt-get on your raspbian distro), as well as python opencv libraries (use pip). You will also need to install the imutils (apt-get).

You will also need to enable the camera using raspberry pi configuration tool (use raspi-config to do this, may require a reboot).

## Copy files to your pi

Copy the files in this project to your raspberry pi:

* cabinetmanager.py to /home/pi/
* cabinetmanager-init to /etc/init.d/
* CabinetOpen/ and sub-files to /home/pi/

Then register the cabinetmanager init script:

`sudo update-rc.d cabinetmanager-init defaults`

## Reboot check

You should now reboot your raspberry pi. When the cabinetmanager script
starts, it will beep the piezo speaker twice. This signals the start of
calibration. Once the cabinetmanager has taken its initial baseline camera image, it will beep the piezo speaker twice to signify that it is ready for play.

# Troubleshooting

Some earlier raspbian distros fail to load the bcm2835-v4l2 driver (use modprobe to load it manually, if it is not loaded). This seems to be fixed these days, but if the application crashes processing the 'frame' variable right away, this is a sign that the driver was not loaded at startup.
