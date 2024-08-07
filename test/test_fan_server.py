import sys
import time
import logging
import pathlib
import types

sys.path.append(str(pathlib.Path(__file__).parent.parent.joinpath("servers")))
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from servers.fan_server import Bridge

LOGGER = logging.getLogger()
WAIT, RUN = 0, 1
START_AT_MINUTE = 5

class Time():
    def __init__(self) -> None:
        self.time_struct = types.SimpleNamespace()
        self.time_struct.tm_min = 0
        
    def localtime(self):
        return self.time_struct
      
time = Time()      

class SensorProxy():
    def __init__(self):
        self._humidity = 40
        self._temperature = 40
        
    def temperature(self):
        return self._temperature
    
    def humidity(self):
        return self._humidity
    
    
class Dut(Bridge):
    def __init__(self):
        super().__init__()
        self.sensors_proxy = SensorProxy()
        
    def _execute(self):
        LOGGER.info(f"state={self.state}")
        temperature = float(self.sensors_proxy.temperature())
        humidity = float(self.sensors_proxy.humidity())
      
        if self.fan_mode_manual is False:
            if temperature > float(self.settings["temperature_high_level"]) or humidity > float(self.settings["humidity_high_level"]):
                # start fan to reduce temperature or humidity
                self.fan_status = True
                self.state = WAIT
            else:
                time_struct = time.localtime()
                if self.state == WAIT:
                    if time_struct.tm_min == START_AT_MINUTE:   
                        # start fan every hour + START_AT_MINUTE minutes
                        LOGGER.info(f"state 0 -> 1")
                        self.fan_status = True
                        self.state = RUN
                    else:
                        self.fan_status = False
                else:
                    if time_struct.tm_min == START_AT_MINUTE + int(self.settings["fan_minutes_in_hour"]):
                        # stop fan every hour + START_AT_MINUTE minutes + fan_minutes_in_hour
                        self.fan_status = False
                        self.state = WAIT
                        LOGGER.info(f"state 1 -> 0")
        else:
            self.fan_status = self.fan_on
        

class Test():
    def setup_class(self):
        self.dut = Dut()
        
    def test_1(self):
        self.dut.settings["temperature_high_level"] = 100
        self.dut.settings["humidity_high_level"] = 100
        self.dut.settings["fan_minutes_in_hour"] = 5
        self.dut.fan_mode_manual = False
        
        for _ in range(2):
            time.time_struct.tm_min = 0
            self.dut._execute()
            assert self.dut.state == WAIT
            assert self.dut.fan_status is False

            time.time_struct.tm_min = START_AT_MINUTE
            self.dut._execute()
            assert self.dut.state == RUN
            assert self.dut.fan_status is True

            time.time_struct.tm_min = START_AT_MINUTE + 1
            self.dut._execute()
            assert self.dut.state == RUN
            assert self.dut.fan_status is True

            time.time_struct.tm_min = START_AT_MINUTE + 5
            self.dut._execute()
            assert self.dut.state == WAIT
            assert self.dut.fan_status is False
            
            