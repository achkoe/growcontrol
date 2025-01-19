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
from colorama import Fore, Back, Style, init
import test.tst_configuration as tst_configuration
import configuration
from servers.base import load_settings
from servers.fan_server import Bridge, START_AT_MINUTE


LOGGER = logging.getLogger()
init(autoreset=True)
COLOR = Back.MAGENTA + Fore.WHITE
    
    
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
    print(COLOR + "Verify that 'Temperature' is red", end=" ")
    input("Press key to continue")
    LOGGER.info("set temperature to 22")
    mock_proxy.set_temperature(22)
    print(COLOR + "Verify that 'Temperature' is green", end=" ")
    input("Press key to continue")


def test_humidity(mock_proxy):
    LOGGER.info("set humidity to 32")
    mock_proxy.set_humidity(32)
    print(COLOR + "Verify that 'Humidity' is red", end=" ")
    input("Press key to continue")
    LOGGER.info("set humidity to 22")
    mock_proxy.set_humidity(65)
    print(COLOR + "Verify that 'Humidity' is green", end=" ")
    input("Press key to continue")
        

def test_pump_manual_auto(pump_proxy):
    LOGGER.info(f"set pump Manual On")
    pump_proxy.set("Manual", "On")
    print(COLOR + "Verify that pump is in state 'Manual' and 'On", end=" ")
    input("Press key to continue")
    LOGGER.info(f"set pump Manual Off")
    pump_proxy.set("Manual", "Off")
    print(COLOR + "Verify that pump is in state 'Manual' and 'Off", end=" ")
    input("Press key to continue")
    LOGGER.info(f"set pump Auto Off")
    pump_proxy.set("Auto", "Off")
    print(COLOR + "Verify that pump is in state 'Auto' and 'Off' and 'WAIT'", end=" ")
    input("Press key to continue")
    LOGGER.info(f"set pump Auto On")
    pump_proxy.set("Auto", "On")
    print(COLOR + "Verify that pump is in state 'Auto' and 'On' and 'WAIT'", end=" ")
    input("Press key to continue")
    
    
def test_pump_auto(mock_proxy):
    LOGGER.info("set moisture to min  (16000)")
    mock_proxy.set_value(16000)
    print(COLOR + "Verify that pump is 'RUN'", end=" ")
    input("Press key to continue")
    LOGGER.info("set moisture to max (7600)")
    mock_proxy.set_value(7600)
    print(COLOR + "Verify that pump is 'Off'", end=" ")
    input("Press key to continue")
    

def test_fan(fan_proxy, caplog):
    print(COLOR + "Press button Fan/Auto to put the fan in mode 'Manual'", end=" ")
    input("Press key to continue")
    r = fan_proxy.get_fan()
    e = "OFF"
    show(e, r)
    r = fan_proxy.get_fan_mode()
    e = "Manual"
    show(e, r)
    print(COLOR + "Press button Fan/Auto/Off to put the fan in state 'On'", end=" ")
    input("Press key to continue")
    r = fan_proxy.get_fan()
    e = "ON"
    show(e, r)
    print(COLOR + "Press button Fan/Auto/On to put the fan in state 'Off", end=" ")
    input("Press key to continue")
    r = fan_proxy.get_fan()
    e = "OFF"
    show(e, r)
    print(COLOR + "Press button Fan/Auto to put the fan in mode 'Auto'", end=" ")
    input("Press key to continue")
    r = fan_proxy.get_fan_mode()
    e = "Auto"
    show(e, r)
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
        
        
def test_light(light_proxy, caplog):
    ee = light_proxy.get()
    print(COLOR + "Press button Light/Auto to put the light in mode 'Manual'", end=" ")
    input("Press key to continue")
    r = light_proxy.get()
    show(ee, r)
    print(COLOR + "Press button Light/On/Off to toggle the light", end=" ")
    input("Press key to continue")
    e = {"light": "OFF" if r["light"] == "ON" else "OFF"}
    r = light_proxy.get()
    show(e, r)
    
    pin, state = read_last_output()
    LOGGER.info(f"pin={pin}, state={state}")
    e = 1 if r["light"] == "ON" else 0
    assert pin == configuration.port_light
    assert state == e
    
    print(COLOR + "Press button Light/On/Off to toggle the light", end=" ")
    input("Press key to continue")
    e = {"light": "ON" if r["light"] == "OFF" else "ON"}
    r = light_proxy.get()
    show(e, r)
    
    pin, state = read_last_output()
    LOGGER.info(f"pin={pin}, state={state}")
    e = 1 if r["light"] == "ON" else 0
    assert pin == configuration.port_light
    assert state == e
    
    print(COLOR + "Press button Light/Auto to put the light in mode 'Auto'", end=" ")
    input("Press key to continue")
    r = light_proxy.get()
    show(ee, r)
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
    
    
    
    
    
    
    
    
    
    
    
    