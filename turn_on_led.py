import RPi.GPIO as GPIO
import sys

BLUE_LED = 18
RED_LED = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BLUE_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)


if int(sys.argv[1]):
    GPIO.output(BLUE_LED, True)
    GPIO.output(RED_LED, False)
else:
    GPIO.output(RED_LED, True)
    GPIO.output(BLUE_LED, False)
