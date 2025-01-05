import time
import argparse
import RPi.GPIO as GPIO
import configuration

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("time", type=int)
    args = parser.parse_args()
    
    GPIO.setup(configuration.port_pump1, GPIO.OUT)
    GPIO.output(configuration.port_pump1, GPIO.HIGH)
    time.sleep(args.time)
    GPIO.output(configuration.port_pump1, GPIO.LOW)
    