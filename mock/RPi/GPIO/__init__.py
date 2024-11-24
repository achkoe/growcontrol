import pathlib

BCM = None
OUT = None
HIGH = 1
LOW = 0
IN = None


def setmode(arg):
    pass

def setup(*args):
    pass

def output(*args):
    with pathlib.Path(__file__).parent.parent.parent.joinpath("_output.txt").open("w") as fh:
        print(args, file=fh)    

def input(*args):
    return 1