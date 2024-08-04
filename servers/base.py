import pathlib
import json
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def create_server(theclass, port):
    # Create server
    with SimpleXMLRPCServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(theclass())
        server.serve_forever()


def load_settings():
   with pathlib.Path(__file__).parent.parent.joinpath("settings.json").open("r") as fh:
      settings = json.load(fh)
   for key in ("light_1_on_time", "light_1_off_time", "light_2_on_time", "light_2_off_time"):
      (hour, minute, second) = (int(item) for item in settings[key].split(":"))
      settings[key] = hour * 60 * 60 + minute * 60 + second
   return settings
