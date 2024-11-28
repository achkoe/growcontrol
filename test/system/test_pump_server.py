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
    return xmlrpc.client.ServerProxy(f"http://localhost:{tst_configuration.mock_server_port}")


def test_pump_auto_manual(mock_proxy):
    pass    
