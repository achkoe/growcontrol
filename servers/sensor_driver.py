import pathlib
import json
from configuration import port_waterlow, port_watermedium, port_waterhigh


def get():
    with pathlib.Path(__file__).parent.parent.joinpath("_data.json").open("r") as fh:
        data = json.load(fh)["sensor"]
    return data