import logging
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import test.tst_configuration as configuration


logging.basicConfig(format=configuration.log_format, level=logging.DEBUG)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.CRITICAL)

TEMPERATURE = 22.2
HUMIDITY = 55.5
VALUE = 22

    
def set_temperature(value):
    global TEMPERATURE
    LOGGER.info(f"set_temperature <- {value}")
    TEMPERATURE = value   
    return TEMPERATURE 


def get_temperature():
    global TEMPERATURE
    return TEMPERATURE


def set_humidity(value):
    global HUMIDITY
    HUMIDITY = value  
    return HUMIDITY  


def get_humidity():
    global HUMIDITY
    return HUMIDITY


def set_value(value):
    global VALUE
    VALUE = value  
    return VALUE  


def get_value():
    global VALUE
    return VALUE


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


LOGGER.critical("MOCK SERVER STARTED")
port = configuration.mock_server_port
with SimpleXMLRPCServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
    server.register_introspection_functions()
    server.register_function(set_temperature)
    server.register_function(get_temperature)
    server.register_function(set_humidity)
    server.register_function(get_humidity)
    server.register_function(set_value)
    server.register_function(get_value)
    server.serve_forever()
