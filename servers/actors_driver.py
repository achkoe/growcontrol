import logging
from dotenv import dotenv_values
import configuration
from base import get_loglevel
#import RPi.GPIO as GPIO

logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(get_loglevel("ACTOR_DRIVER_LOGLEVEL"))

_STATE_MAP = dict()


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(list(configuration.actors_dict.values()), GPIO.OUT)


def set(name, state):
    _STATE_MAP.setdefault(name, None)
    if _STATE_MAP[name] is not state:
        _STATE_MAP[name] = state
    LOGGER.info(f"{name} -> {state}")
    GPIO.output(configuration.actors_dict[name], GPIO.HIGH if state is True else GPIO.LOW)
    

if __name__ == "__main__":
    import argparse
    omap = dict((index, key) for index, key in enumerate(configuration.actors_dict))
    parser = argparse.ArgumentParser()
    parser.add_argument("key", choices=list(omap.keys()), type=int, help=f"set output {omap}")
    parser.add_argument("value", choices=["on", "off"], help="set/reset output")
    args = parser.parse_args()
    print(args)
    
    init()
    set(args.kay, True if args.value == "on" else False)