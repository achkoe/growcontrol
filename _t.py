import time
import argparse
import RPi.GPIO as GPIO
import configuration

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("time", type=int)
    args = parser.parse_args()

    port = configuration.port_fan
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(port, GPIO.OUT)
    GPIO.output(port, GPIO.LOW)
    time.sleep(args.time)
    GPIO.output(port, GPIO.HIGH)

# 400ml pro Pumpe in 30 Sekunden
