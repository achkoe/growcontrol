import logging
import xmlrpc.client
import test.tst_configuration as configuration


mock_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.mock_server_port}")


VALUE = 22.0

class AnalogIn():
    def __init__(self, *args, **kwargs):
        try:
            self.value = mock_proxy.get_value()
        except:
            self.value = 22