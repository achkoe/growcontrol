"""Watchdog for growcontrol"""
import os
import logging
import pathlib
import time
import datetime
import json
import argparse
from collections import deque
import subprocess
import psutil
from dotenv import dotenv_values
import configuration


loglevel = int(dotenv_values(pathlib.Path(__file__).parent.joinpath("servers", ".env")).get("WATCHDOG_LOGLEVEL", logging.CRITICAL))
logging.basicConfig(format=configuration.log_format, level=loglevel)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(loglevel)


# flask --app http_server run --debug --host 0.0.0.0
processes = {
    0: dict(name="sensor_server", folder=".", args=['python', 'servers/sensors_server.py'], t=2), 
    1: dict(name="actors_server", folder=".", args=['python', 'servers/actors_server.py'], t=2), 
    2: dict(name="logdata_server", folder=".", args=['python', 'servers/logdata_server.py'], t=2), 
    3: dict(name="http_server", folder="http", args=['flask', '--app', 'http_server', 'run', "--host", "0.0.0.0"], t=0),
}

logfilename = "watchdog.log"
pidfilename = "pid.json"
logqueue = deque(maxlen=16)

def start():
    for key in processes:
        process = processes[key]
        LOGGER.warning("start {}".format(" ".join(process["args"])))
        processes[key]["p"] = subprocess.Popen(process["args"], cwd=pathlib.Path(__file__).parent.joinpath(process["folder"]))
        time.sleep(process["t"])
        
    LOGGER.warning("PIDS:{}".format(", ".join(str(processes[key]["p"].pid) for key in processes)))
    with pathlib.Path.cwd().joinpath(pidfilename).open("w") as fh:
        pid_map = {"watchdog": os.getpid()}
        pid_map.update(dict((processes[key]["name"], processes[key]["p"].pid) for key in processes))
        json.dump(pid_map, fh, indent=4)
        
        
def watch():
    while True:
        for key in processes:
            status = processes[key]["p"].poll()
            LOGGER.info("pid {0} {1!r}: {2}".format(processes[key]["p"].pid, processes[key]["name"], status))
            if status is not None:
                logqueue.append("{0}: {1} has return code {2}".format(
                    datetime.datetime.now().isoformat(),
                    processes[key]["name"], 
                    status))
                # one process has terminated, so kill all started processes and call start again
                with pathlib.Path.cwd().joinpath(logfilename).open("w") as fh:
                    for line in logqueue:
                        print(line, file=fh)
                        LOGGER.warning(line)
                for killkey in processes:
                    if killkey == key:
                        continue
                    processes[killkey]["p"].terminate()
                start()
        time.sleep(1)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kill", action="store_true", help="kill all previously started processes")
    args = parser.parse_args()
    if args.kill is True:
        with pathlib.Path.cwd().joinpath(pidfilename).open("r") as fh:
            pid_map = json.load(fh)
        for key, pid in pid_map.items():
            try:
                p = psutil.Process(pid)
                p.terminate()
                print(f"{key} process terminated")
            except Exception as e:
                print(e)
    else:
        with pathlib.Path.cwd().joinpath(logfilename).open("w") as fh:
            # create log file
            print("Everything okay", file=fh)
        start()
        watch()
    
