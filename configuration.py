sensors_server_port = 4000
fan_server_port = 4001
light_server_port = 4002
logdata_server_port = 4003

pump_moisture_dict = {
    1: dict(channel=0, pump=4004, gpio=15)
}

# GPIO for water low sensor, 1: water is low, 0: water is available
port_waterlow = 18
port_watermedium = 23
port_waterhigh = 24

log_format = "%(module)s:%(levelname)s:%(asctime)s:%(message)s"
