"""
. ~/venv/vg311/bin/activate
export PYTHONPATH=/home/achimk/work/growcontrol:/home/achimk/work/growcontrol/mock
python mock_server.py &

pytest -s ./test/manual/test.py 
"""
import logging
import pathlib
import xmlrpc.client
import re
import pytest
import test.tst_configuration as tst_configuration
import configuration
from servers.base import load_settings
from servers.fan_server import Bridge, START_AT_MINUTE


LOGGER = logging.getLogger()
    
    
@pytest.fixture
def mock_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.mock_server_port}")


@pytest.fixture
def pump_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.pump_moisture_dict[1]['pump']}")


@pytest.fixture
def fan_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.fan_server_port}")


@pytest.fixture
def light_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.light_server_port}")
    
    
def show(e, r):
    LOGGER.log(logging.INFO if e == r else logging.CRITICAL, f"expected {e!r}, received {r!r}")
    
    
def read_last_output():
    with pathlib.Path(__file__).parent.parent.parent.joinpath("mock", "_output.txt").open("r") as fh:
        s = fh.readline()
    mo = re.match(r"^\((?P<pin>\d+)\s*,\s*(?P<state>\d+)\)", s)
    assert mo is not None, mo
    pin = int(mo.group("pin"))
    state = int(mo.group("state"))
    return pin, state
    
def test_temperature(mock_proxy):
    LOGGER.info("set temperature to 32")
    mock_proxy.set_temperature(32)
    input("Verify that 'Temperature' is red")
    LOGGER.info("set temperature to 22")
    mock_proxy.set_temperature(22)
    input("Verify that 'Temperature' is green")


def test_humidity(mock_proxy):
    LOGGER.info("set humidity to 32")
    mock_proxy.set_humidity(32)
    input("Verify that 'Humidity' is red")
    LOGGER.info("set humidity to 22")
    mock_proxy.set_humidity(65)
    input("Verify that 'Humidity' is green")
        

def test_pump_manual_auto(pump_proxy):
    LOGGER.info(f"set pump Manual On")
    pump_proxy.set("Manual", "On")
    input("Verify that pump is in state 'Manual' and 'On")
    LOGGER.info(f"set pump Manual Off")
    pump_proxy.set("Manual", "Off")
    input("Verify that pump is in state 'Manual' and 'Off")
    LOGGER.info(f"set pump Auto Off")
    pump_proxy.set("Auto", "Off")
    input("Verify that pump is in state 'Auto' and 'Off' and 'WAIT'")
    LOGGER.info(f"set pump Auto On")
    pump_proxy.set("Auto", "On")
    input("Verify that pump is in state 'Auto' and 'On' and 'WAIT'")
    
    
def test_pump_auto(mock_proxy):
    LOGGER.info("set moisture to min  (16000)")
    mock_proxy.set_value(16000)
    input("Verify that pump is 'RUN'")
    LOGGER.info("set moisture to max (7600)")
    mock_proxy.set_value(7600)
    input("Verify that pump is 'Off'")
    

def test_fan(fan_proxy, caplog):
    input("Press button Fan/Auto to put the fan in mode 'Manual'")
    r = fan_proxy.get_fan()
    e = "OFF"
    show(e, r)
    r = fan_proxy.get_fan_mode()
    e = "Manual"
    show(e, r)
    input("Press button Fan/Auto/Off to put the fan in state 'On'")
    r = fan_proxy.get_fan()
    e = "ON"
    show(e, r)
    input("Press button Fan/Auto/On to put the fan in state 'Off")
    r = fan_proxy.get_fan()
    e = "OFF"
    show(e, r)
    input("Press button Fan/Auto to put the fan in mode 'Auto'")
    r = fan_proxy.get_fan_mode()
    e = "Auto"
    show(e, r)
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
        
        
def test_light(light_proxy, caplog):
    ee = light_proxy.get()
    input("Press button Light/Auto to put the light in mode 'Manual'")
    r = light_proxy.get()
    show(ee, r)
    input("Press button Light/On/Off to toggle the light")
    e = {"light": "OFF" if r["light"] == "ON" else "OFF"}
    r = light_proxy.get()
    show(e, r)
    
    pin, state = read_last_output()
    LOGGER.info(f"pin={pin}, state={state}")
    e = 1 if r["light"] == "ON" else 0
    assert pin == configuration.port_light
    assert state == e
    
    input("Press button Light/On/Off to toggle the light")
    e = {"light": "ON" if r["light"] == "OFF" else "ON"}
    r = light_proxy.get()
    show(e, r)
    
    pin, state = read_last_output()
    LOGGER.info(f"pin={pin}, state={state}")
    e = 1 if r["light"] == "ON" else 0
    assert pin == configuration.port_light
    assert state == e
    
    input("Press button Light/Auto to put the light in mode 'Auto'")
    r = light_proxy.get()
    show(ee, r)
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
    
    
    
    
    
    
    
    
    
    
    
    