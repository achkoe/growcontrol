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


def test_light_server(mock_proxy):
    
    now = datetime.datetime.now()
    on_time = now + datetime.timedelta(seconds=60)
    on_time_str = on_time.strftime("%H:%M")
    off_time = now + datetime.timedelta(seconds=120)
    off_time_str = off_time.strftime("%H:%M")
    
    data = dict(
        light_on_time=on_time_str, 
        light_off_time=off_time_str, 
    )
    ic(data)
    r = requests.post(f"{BASEURL}/settings", data=data)
    expected = 200
    assert r.status_code == expected

    passed = False
    tstart = time.time()
    while time.time() - tstart <= 65:
        r = requests.get(f"{BASEURL}/update")
        assert r.status_code == expected
        obtained = r.json()["light_state"]
        if int(time.time() - tstart) % 5 == 0:
            ic(obtained)
        if obtained == "ON":
            ic(obtained)
            passed = True
            break
        time.sleep(1)
    assert passed

    passed = False
    tstart = time.time()
    while time.time() - tstart <= 65:
        r = requests.get(f"{BASEURL}/update")
        assert r.status_code == expected
        obtained = r.json()["light_state"]
        if int(time.time() - tstart) % 5 == 0:
            ic(obtained)
        if obtained == "OFF":
            ic(obtained)
            passed = True
            break
        time.sleep(1)
    assert passed
        
        
        
    
    return
    
    value = 111
    mock_proxy.set_temperature(value)
    r = requests.get(f"{BASEURL}/update")
    assert r.status_code == expected
    print(r.json())
    