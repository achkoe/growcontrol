import pathlib
import json
import logging
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from dotenv import dotenv_values

# Restrict to a particular path.


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def create_server(theclass, port):
    # Create server
    with SimpleXMLRPCServer(('localhost', port), requestHandler=RequestHandler, logRequests=False) as server:
        server.register_introspection_functions()
        server.register_instance(theclass())
        server.serve_forever()


def _make_integer_time(timestr: str) -> int:
    hms = (int(item) for item in timestr.split(":"))
    rval = 0
    for item, factor in zip(hms, (60 * 60, 60, 1)):
        rval += item * factor
    return rval


def load_settings(raw=False):
    with pathlib.Path(__file__).parent.parent.joinpath("settings.json").open("r") as fh:
        raw_settings = json.load(fh)
    if raw:
        return raw_settings
    settings = dict((k, raw_settings[k]["value"]) for k in raw_settings)
    for key in ("light_on_time", "light_off_time"):
        settings[f"{key}_i"] = _make_integer_time(settings[key])
    return settings


def save_settings(settings):
    with pathlib.Path(__file__).parent.parent.joinpath("settings.json").open("r") as fh:
        raw_settings = json.load(fh)
    for key in ("light_on_time", "light_off_time"):
        settings[f"{key}_i"] = _make_integer_time(settings[key])
    for key in settings:
        raw_settings[key]["value"] = settings[key]
    with pathlib.Path(__file__).parent.parent.joinpath("settings.json").open("w") as fh:
        json.dump(raw_settings, fh, indent=4)
    return settings


def get_loglevel(key):
    return int(dotenv_values(pathlib.Path(__file__).parent.joinpath(".env")).get(
        key, logging.CRITICAL))
