import logging
from dotenv import dotenv_values
import configuration
from base import get_loglevel
import RPi.GPIO as GPIO

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