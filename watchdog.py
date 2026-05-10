"""Watchdog for growcontrol"""
import os
import pathlib
import time
import datetime
import json
import argparse
from collections import deque
import subprocess
import psutil

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
        print(" ".join(process["args"]))
        processes[key]["p"] = subprocess.Popen(process["args"], cwd=pathlib.Path(__file__).parent.joinpath(process["folder"]))
        time.sleep(process["t"])
        
    print(", ".join(str(processes[key]["p"].pid) for key in processes))
    with pathlib.Path.cwd().joinpath(pidfilename).open("w") as fh:
        pid_map = {"watchdog": os.getpid()}
        pid_map.update(dict((processes[key]["name"], processes[key]["p"].pid) for key in processes))
        json.dump(pid_map, fh, indent=4)
        
        
def watch():
    flag = False
    while True:
        print("{}".format(["-", "+"][flag]), end=" ")
        flag = not flag
        for key in processes:
            status = processes[key]["p"].poll()
            print("{}: {}".format(key, status), end=" ", flush=True)
            if status is not None:
                logqueue.append("{0}: {1} has return code {2}".format(
                    datetime.datetime.now().isoformat(),
                    processes[key]["name"], 
                    status))
                # one process has terminated, so kill all started processes and call start again
                with pathlib.Path.cwd().joinpath(logfilename).open("w") as fh:
                    for line in logqueue:
                        print(line, file=fh)
                        print(line)
                print()
                for killkey in processes:
                    if killkey == key:
                        continue
                    processes[killkey]["p"].terminate()
                start()
        print()
        time.sleep(1)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kill", action="store_true", help="kill all previously started processes")
    args = parser.parse_args()
    if args.kill is True:
        with pathlib.Path.cwd().joinpath(pidfilename).open("r") as fh:
            pid_map = json.load(fh)
        for key, pid in pid_map.items():
            p = psutil.Process(pid)
            p.terminate()
            print(f"{key} process terminated")
    else:
        with pathlib.Path.cwd().joinpath(logfilename).open("w") as fh:
            # create log file
            print("Everything okay", file=fh)
        start()
        watch()
    