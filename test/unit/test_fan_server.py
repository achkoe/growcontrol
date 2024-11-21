"""
For this tests several servers needs to be started before test starts. 
Here is how to start them:

source ~/venv/vg311/bin/activate
export PYTHONPATH=/home/achimk/work/growcontrol:/home/achimk/work/growcontrol/mock
python ../servers/sensors_server.py &
python ../servers/fan_server.py &
python mock_server.py &
"""
import logging
import time
import xmlrpc.client
import pytest
import test.tst_configuration as tst_configuration
import configuration
from servers.base import load_settings
from servers.fan_server import Bridge, START_AT_MINUTE


LOGGER = logging.getLogger()
    
    
@pytest.fixture
def mock_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.bme280_server_port}")

@pytest.fixture
def sensors_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.sensors_server_port}")

@pytest.fixture
def fan_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.fan_server_port}")
    

def test_heater_auto(mock_proxy, sensors_proxy, fan_proxy):
    settings = load_settings()
    LOGGER.info(settings)
    min_value = float(settings["temperature_low_level"])
    max_value = float(settings["temperature_high_level"])
    parameters = [
        (min_value - 1, "ON"),
        (min_value + 0, "ON"),
        (min_value + 1, "ON"),
        (max_value - 1, "ON"),
        (max_value + 0, "OFF"),
        (max_value + 1, "OFF")
    ]
    LOGGER.info('fan_proxy.set_heater("Auto", "OFF")')
    fan_proxy.set_heater("Auto", "OFF")
    for (value, expected) in parameters:
        LOGGER.info(f"set temperature {value}")
        mock_proxy.set_temperature(value)
        time.sleep(2)
        obtained = sensors_proxy.temperature()
        LOGGER.info(f"sensors_proxy.temperature() -> {obtained}")
        obtained = fan_proxy.get_heater()
        LOGGER.info(f"fan_proxy.get_heater() -> {obtained}")
        assert obtained == expected

def test_heater_manual(mock_proxy, sensors_proxy, fan_proxy):
    settings = load_settings()
    LOGGER.info(settings)
    min_value = float(settings["temperature_low_level"])
    for expected in ["OFF", "ON"]:
        LOGGER.info(f'fan_proxy.set_heater("Manual", {expected!r})')
        fan_proxy.set_heater("Manual", expected)
        value = min_value - 1
        LOGGER.info(f"set temperature {value}")
        mock_proxy.set_temperature(value)
        time.sleep(2)
        obtained = sensors_proxy.temperature()
        LOGGER.info(f"sensors_proxy.temperature() -> {obtained}")
        obtained = fan_proxy.get_heater()
        LOGGER.info(f"fan_proxy.get_heater() -> {obtained}")
        assert obtained == expected


the_time = "2024-11-10T12:00:00"


def test_fan(monkeypatch, mock_proxy):
    def mock_localtime():
        global the_time
        r = time.strptime(the_time, "%Y-%m-%dT%H:%M:%S") 
        return r
    
    global the_time

    monkeypatch.setattr(time, "localtime", mock_localtime)

    settings = load_settings()
    mock_proxy.set_temperature(float(settings["temperature_high_level"]) - 1.0)
    mock_proxy.set_humidity(float(settings["humidity_high_level"]) - 1.0)
    fan_minutes_in_hour = int(settings["fan_minutes_in_hour"])
    
    bridge = Bridge()
    bridge.fan_mode_manual = False
    for offset, expected in [(-1, "OFF"), (0, "ON"), (1, "ON"), (fan_minutes_in_hour - 1, "ON"), (fan_minutes_in_hour - 0, "OFF"), (fan_minutes_in_hour + 1, "OFF"), ]:
        minute = START_AT_MINUTE + offset
        the_time = f"2024-11-10T15:{minute:02}:00" 
        bridge._execute()
        obtained = bridge.get_fan()
        LOGGER.info(f"minute {minute} -> {obtained!r}")
        assert obtained == expected, f"minute {minute} -> obtained {obtained!r}, expected {expected!r}"