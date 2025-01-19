import logging
import time
import xmlrpc.client
import pytest
import test.tst_configuration as tst_configuration
import configuration
from servers.base import load_settings, _make_integer_time
import servers.pump_server 
from servers.pump_server import Bridge


LOGGER = logging.getLogger()
servers.pump_server.LOGGER.setLevel(logging.NOTSET)


the_time = "2024-11-10T12:00:00"

class SensorProxy():
    def __init__(self):
        self.waterlevel_value = 0
        self.moisture_value = 15000
        
    def waterlevel(self):
        return self.waterlevel_value
    
    def moisture(self, channel):
        return self.moisture_value
        
        
    
def test_waterlevel():
    bridge = Bridge(moisture_channel=0, pump_gpio=configuration.port_pump1, milliliter_per_second=configuration.pump1_milliliter_per_second)
    bridge.sensor_proxy = SensorProxy()
    bridge.sensor_proxy.waterlevel_value = 0
    assert bridge.pump_state is False
    bridge._execute()
    assert bridge.pump_state is False
    LOGGER.info(f"waterlevel <- 1, moisture <- 15000")
    bridge.sensor_proxy.moisture_value = 15000
    bridge.sensor_proxy.waterlevel_value = 1
    bridge._execute()
    assert bridge.pump_state is False
    LOGGER.info(f"waterlevel <- 1, moisture <- 0")
    bridge.sensor_proxy.waterlevel_value = 1
    bridge.sensor_proxy.moisture_value = 0
    bridge.last_time = None
    bridge.pump_on_time = 3
    for e in (True, True, True, False):
        bridge._execute()
        LOGGER.info(f"time={time.time()}, start_time={bridge.start_time}, pump_state={bridge.pump_state}: sleep 1 second")
        assert bridge.pump_state is e
        time.sleep(1)
    
    
def _test(monkeypatch):
    
    def mock_localtime():
        global the_time
        r = time.strptime(the_time, "%Y-%m-%dT%H:%M:%S") 
        return r
    
    global the_time
    
    light_on_time_hour, light_on_time_minute = 14, 10
    light_off_time_hour, light_off_time_minute = 14, 20
    
    monkeypatch.setattr(time, "localtime", mock_localtime)
        
    bridge = Bridge()
    

if __name__ == "__main__":
    test_waterlevel()