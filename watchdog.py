import os
import pathlib
import time
import datetime
from collections import deque
import subprocess


processes = {
    0: dict(name="http_server", folder="http", args=['flask', 'run', "--host", "0.0.0.0"], t=0),
    1: dict(name="sensor_server", folder=".", args=['python', 'servers/sensors_server.py'], t=0), 
    2: dict(name="light_server", folder=".", args=['python', 'servers/light_server.py'], t=0), 
    3: dict(name="fan_server", folder=".", args=['python', 'servers/fan_server.py'], t=2), 
    4: dict(name="pump_server_1", folder=".", args=['python', 'servers/pump_server.py', '1'], t=0), 
    5: dict(name="pump_server_2", folder=".", args=['python', 'servers/pump_server.py', '2'], t=0), 
    6: dict(name="logdata_server", folder=".", args=['python', 'servers/logdata_server.py'], t=2), 
}

logfilename = "watchdog.log"
logqueue = deque(maxlen=16)

def start():
    for key in [1, 2, 3, 4, 5, 6]:
        process = processes[key]
        print(" ".join(process["args"]))
        processes[key]["p"] = subprocess.Popen(process["args"], cwd=pathlib.Path(__file__).parent.joinpath(process["folder"]))
        time.sleep(process["t"])
    
    os.environ["FLASK_APP"] = "http_server.py"
    os.environ['FLASK_ENV'] = 'development'
    process = subprocess.Popen(
        processes[0]["args"],
        cwd=str(pathlib.Path.cwd().joinpath(processes[0]["folder"])),
    )
    processes[0]["p"] = process
    
    print(", ".join(str(processes[key]["p"].pid) for key in processes))
        
        
def watch():
    flag = False
    while True:
        print("{}".format(["-", "+"][flag]), end=" ")
        flag = not flag
        for key in processes:
            status = processes[key]["p"].poll()
            print("{}: {}".format(key, status), end=" ")
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
    with pathlib.Path.cwd().joinpath(logfilename).open("w") as fh:
        # create log file
        print("Everything okay", file=fh)
    start()
    watch()
    