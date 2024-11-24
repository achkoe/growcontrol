import logging
import xmlrpc.client
import test.tst_configuration as configuration


mock_proxy = xmlrpc.client.ServerProxy(
    f"http://localhost:{configuration.mock_server_port}")


TEMPERATURE = 33.3
HUMIDITY = 55.5


class BME280():
    def __init__(self, *args, **kwargs):
        pass    
    
    def get_temperature(self):
        try:
            return mock_proxy.get_temperature()
        except Exception as e:
            return TEMPERATURE

    def get_humidity(self):
        try:
            return mock_proxy.get_humidity()
        except Exception as e:
            return HUMIDITY

    
