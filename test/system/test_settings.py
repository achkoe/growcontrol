"""
For this tests several servers needs to be started before test starts. 
See file 'run' how to start them.

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
import test.tst_configuration as tst_configuration


LOGGER = logging.getLogger()
logging.getLogger("urllib3").setLevel(logging.WARNING)


ADDRESS = "127.0.0.1"
PORT = 5000
BASEURL = f"http://{ADDRESS}:{PORT}"
    
    
@pytest.fixture
def mock_proxy():
    return xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.bme280_server_port}")

@pytest.mark.parametrize(
    ("ondelta", "offdelta", "expected_response_list"), [
        pytest.param(60, 120, ["ON", "OFF"], id="on_smaller_off"), 
        pytest.param(120, 60, ["OFF", "ON"], id="off_smaller_on")])
def test_light_server(ondelta, offdelta, expected_response_list, mock_proxy):
    
    now = datetime.datetime.now()
    on_time = now + datetime.timedelta(seconds=ondelta)
    on_time_str = on_time.strftime("%H:%M")
    off_time = now + datetime.timedelta(seconds=offdelta)
    off_time_str = off_time.strftime("%H:%M")
    
    data = dict(
        light_on_time=on_time_str, 
        light_off_time=off_time_str, 
    )
    LOGGER.info(f"settings -> {data}")
    r = requests.post(f"{BASEURL}/settings", data=data, timeout=5)
    expected_code = 200
    assert r.status_code == expected_code
    
    passed = False
    expected_response = expected_response_list[0]
    tstart = time.time()
    while True:
        telapsed = time.time() - tstart
        if telapsed > 65:
            break
        r = requests.get(f"{BASEURL}/update", timeout=5)
        assert r.status_code == expected_code
        obtained = r.json()["light_state"]
        if int(telapsed) % 5 == 0:
            LOGGER.info(f"t={telapsed:.2f} -> {obtained!r}")
        if obtained == expected_response:
            LOGGER.info(f"PASS: t={telapsed:.2f} -> {obtained!r}")
            passed = True
            break
        time.sleep(1)
    assert passed, f"expected {expected_response!r}, but obtained {obtained!r}"

    passed = False
    expected_response = expected_response_list[1]
    tstart = time.time()
    while True:
        telapsed = time.time() - tstart
        if telapsed > 65:
            break
        r = requests.get(f"{BASEURL}/update", timeout=5)
        assert r.status_code == expected_code
        obtained = r.json()["light_state"]
        if int(time.time() - tstart) % 5 == 0:
            LOGGER.info(f"t={telapsed:.2f} -> {obtained!r}")
        if obtained == expected_response:
            LOGGER.info(f"PASS: t={telapsed:.2f} -> {obtained!r}")
            passed = True
            break
        time.sleep(1)
    assert passed, f"expected {expected_response!r}, but obtained {obtained!r}"
        
        
        
    
    return
    
    value = 111
    mock_proxy.set_temperature(value)
    r = requests.get(f"{BASEURL}/update")
    assert r.status_code == expected
    print(r.json())
    