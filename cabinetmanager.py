import cv2
import pifacedigitalio
import time
import imutils
from subprocess import call
# global?
pfd = pifacedigitalio.PiFaceDigital()

latchState = 0 # default closed
cabinetState = pfd.input_pins[0].value # default to what the latch thinks
implantPin = pfd.input_pins[7] # implant Pin
firstFrame = None

camera = cv2.VideoCapture(0)
time.sleep(0.25)

# initialize these so cabinetOpenedTime < alarmSquelchTime
cabinetOpenedTime = time.time()
alarmSquelchTime = time.time()

lastPrintTime = None

alarmPin = pfd.output_pins[0]
ledPin = pfd.output_pins[2]

def initializeFirstFrame(timeDelay):
	global firstFrame
	global camera
	alarmChirp() # chirp once when initializing
	print "initializing cabinet. please close!"
        # first, sleep for timeDelay seconds
        time.sleep(timeDelay)
	print "taking picture"
        (grabbed, frame) = camera.read()
	print grabbed
	print frame
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        # gray now has a greyscale version of our image
        firstFrame = gray
	alarmChirp() # chirp again to let us know we're done init()

def updateAlarm():
    global alarmSquelchTime
    global alarmPin
    if latchState == 0:
       pfd.leds[0].turn_off()
       alarmSquelchTime = time.time()
    else:
       pfd.leds[0].turn_on()
    return

def cabinet_opened(event):
    print "Cabinet was opened!"
    pfd.leds[0].turn_on()
    return

def cabinet_closed(event):
    print "Cabinet switch was closed. Will inspect the light sensor to make sure they're not lying."
    pfd.leds[0].turn_off()
    return

def implant_pressed(event):
    print "Implant button pressed"
    return

def implant_released(event):
    global alarmTime, cabinetOpenedTime, lastPrintTime
    if cabinetState == 1 and latchState == 0 and cabinetOpenedTime > alarmSquelchTime:
       if lastPrintTime:
          if (lastPrintTime - time.time()) < 30: # less than 30 seconds between prints? Debounce!
             print "User printing too frequently for some reason..."
             return
       lastPrintTime = time.time()
       print "Success. printing receipt"
       call(["/home/pi/CabinetOpen/success.sh"])
    else:
       print "NOPE. printing failure" # or not, why waste paper?
    return

def alarmChirp():
	global alarmPin
	print "chirping Alarm"
	alarmPin.turn_on()
	time.sleep(0.25)
	alarmPin.turn_off()
	time.sleep(0.25)
	alarmPin.turn_on()
	time.sleep(0.25)
	alarmPin.turn_off()

# will have to implement this
# return 0 if closed, return 1 if open
def getCabinetStateFromCamera():
	global camera
	global firstFrame
	global alarmPin
	startTime = time.time()
        (grabbed, frame) = camera.read()
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        # gray now has a greyscale version of our image
        if firstFrame is None:
                firstFrame = gray
                # we should beep the cabinet piezo now for a quick chirp
                # this will let us know the system is initialized, when
                # we plug the cabinet in
		alarmChirp()	
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        # dilate the thresholded image and find contours
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
	print "image inspected in ", time.time() - startTime
        if len(cnts) > 0:
                # cabinet is not really closed!
                return 1
        else:
                return 0

if __name__ == "__main__":
#    pifacedigital = pifacedigitalio.PiFaceDigital()

    listener = pifacedigitalio.InputEventListener(chip=pfd)
    listener.register(0, pifacedigitalio.IODIR_ON, cabinet_opened, settle_time=0.1)
    listener.register(0, pifacedigitalio.IODIR_OFF, cabinet_closed, settle_time=0.1)
    listener.register(7, pifacedigitalio.IODIR_ON, implant_pressed, settle_time=1.0)
    listener.register(7, pifacedigitalio.IODIR_OFF, implant_released, settle_time=0.1)
    listener.activate()
    print "Listener threads active. Initializing camera"
    initializeFirstFrame(5)
    while True:
       # periodically inspect the state of the cabinet and update variables as appropriate
       # this deals with debouncing
       latchTest = pfd.input_pins[0].value
       if latchTest != latchState:
          print "Latch state mismatch, resetting"
          latchState = latchTest
          updateAlarm()
       cabinetTest = getCabinetStateFromCamera() # returns 0 if closed, 1 if open
       if cabinetTest != cabinetState:
          print "Cabinet was",
	  if cabinetTest == 1:
            print "opened"
	    cabinetOpenedTime = time.time()
            # fixup for alarmSquelchTime. Why? Because alarm squelch time will
            # will be in the past now, so we'll have a bug. Logic is broken, doh!
            #alarmSquelchTime = time.time()
          else:
            print "closed"
          cabinetState = cabinetTest
       if cabinetState == 1 and latchState == 0 and cabinetOpenedTime > alarmSquelchTime:
          # blink the button LED
          ledPin.toggle()
       else:
          ledPin.turn_off()
          
       time.sleep(0.2)
