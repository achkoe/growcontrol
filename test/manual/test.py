"""
. ~/venv/vg311/bin/activate
export PYTHONPATH=/home/achimk/work/growcontrol:/home/achimk/work/growcontrol/mock
python mock_server.py &

pytest -s ./test/manual/test.py 
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
    return xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.mock_server_port}")


@pytest.fixture
def pump_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.pump_moisture_dict[1]['pump']}")


@pytest.fixture
def fan_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{configuration.fan_server_port}")
    
def show(e, r):
    LOGGER.log(logging.INFO if e == r else logging.CRITICAL, f"expected {e!r}, received {r!r}")
    
def test_temperature(mock_proxy):
    LOGGER.info("set temperature to 32")
    mock_proxy.set_temperature(32)
    input("Verify that 'Temperature' is red")
    LOGGER.info("set temperature to 22")
    mock_proxy.set_temperature(22)
    input("Verify that 'Temperature' is green")
        

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