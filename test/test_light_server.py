import logging
import time
import xmlrpc.client
import pytest
import test.tst_configuration as tst_configuration
import configuration
from servers.base import load_settings, _make_integer_time
import servers.light_server 
from servers.light_server import Bridge


LOGGER = logging.getLogger()
servers.light_server.LOGGER.setLevel(logging.NOTSET)


the_time = "2024-11-10T12:00:00"


def test(monkeypatch):
    
    def mock_localtime():
        global the_time
        r = time.strptime(the_time, "%Y-%m-%dT%H:%M:%S") 
        return r
    
    global the_time
    
    light_on_time_hour, light_on_time_minute = 14, 10
    light_off_time_hour, light_off_time_minute = 14, 20
    
    monkeypatch.setattr(time, "localtime", mock_localtime)
        
    bridge = Bridge()
    bridge.settings["light_on_time_i"] = _make_integer_time(f"{light_on_time_hour:02}:{light_on_time_minute:02}")
    bridge.settings["light_off_time_i"] = _make_integer_time(f"{light_off_time_hour:02}:{light_off_time_minute:02}")
    
    for offset, expected in [(-1, "OFF"), (0, "ON"), (1, "ON"), (9, "ON"), (10, "ON"), (11, "OFF")]:
        minute = light_on_time_minute + offset
        the_time = f"2024-11-10T{light_on_time_hour:02}:{minute:02}:00"
        bridge._execute()
        obtained = bridge.get()
        LOGGER.info(f"{the_time} -> {obtained}")
        assert list(obtained.keys()) == ["light_state"]
        assert obtained["light_state"] == expected, f"{the_time}: expected {expected!r}, obtained {obtained!r}"

        
        