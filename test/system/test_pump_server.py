"""
For this tests several servers needs to be started before test starts. 
See file 'setup' how to start them.

source ~/venv/vg311/bin/activate
export PYTHONPATH=/home/achimk/work/growcontrol:/home/achimk/work/growcontrol/mock

"""
import xmlrpc.client
import json
import datetime
import logging
import time
from icecream import ic
import pytest
import requests
import  configuration 
from servers.base import load_settings, save_settings
import test.tst_configuration as tst_configuration


LOGGER = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)

THE_TIME = time.time()


ADDRESS = "127.0.0.1"
PORT = 5000
BASEURL = f"http://{ADDRESS}:{PORT}"
    
    
@pytest.fixture
def mock_proxy():
    proxy = xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.mock_server_port}")
    yield proxy
    proxy.set_value(0)


def test_pump(mock_proxy):
    settings = load_settings()
    pump_on_time = settings["pump_amount"] / configuration.pump_moisture_dict[1]["milliliter_per_second"]
    LOGGER.info(f"pump_on_time={pump_on_time}")
    
    pump_proxies = dict((key, xmlrpc.client.ServerProxy(
        f"http://localhost:{configuration.pump_moisture_dict[key]['pump']}")) for key in configuration.pump_moisture_dict)
    
    LOGGER.info("setting moisture low")
    mock_proxy.set_value(17000)
    
    pump_check_interval = settings["pump_check_interval"]
    LOGGER.info(f'pump_check_interval={pump_check_interval}')
    value = pump_check_interval / (60 * 60)
    settings["pump_check_interval"] = value
    save_settings(settings)
    LOGGER.info(f"reload -> {pump_proxies[1].reload()}")
    settings["pump_check_interval"] = pump_check_interval
    save_settings(settings)
    
    tstart = time.time()
    success = False
    while time.time() - tstart <= pump_on_time + 2:
        state = pump_proxies[1].get()
        LOGGER.info(f"t={(time.time() - tstart):5.2f}, state={state}")
        if state == "OFF":
            success = True
            break
        time.sleep(0.1)
    
    tstart = time.time()
    success = False
    while time.time() - tstart <= pump_check_interval:
        state = pump_proxies[1].get()
        LOGGER.info(f"t={(time.time() - tstart):5.2f}, state={state}")
        if state == "ON":
            success = True
            break
        time.sleep(0.1)
    assert success is True

    tstart = time.time()
    success = False
    while time.time() - tstart <= pump_on_time + 2:
        state = pump_proxies[1].get()
        LOGGER.info(f"t={(time.time() - tstart):5.2f}, state={state}")
        if state == "OFF":
            success = True
            break
        time.sleep(0.1)
    telapsed = time.time() - tstart
    LOGGER.info(f"on time={telapsed}, pump_on_time={pump_on_time}")
    assert telapsed == pytest.approx(pump_on_time, 0.1)

    tstart = time.time()
    success = False
    while time.time() - tstart <= pump_check_interval + 2:
        state = pump_proxies[1].get()
        LOGGER.info(f"t={(time.time() - tstart):5.2f}, state={state}")
        if state == "ON":
            success = True
            break
        time.sleep(0.1)
    telapsed = time.time() - tstart
    LOGGER.info(f"check time={telapsed}, pump_check_interval={pump_check_interval}")
    assert telapsed == pytest.approx(pump_check_interval, 0.1)
