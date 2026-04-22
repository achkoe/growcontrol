sensors_server_port = 4000
fan_server_port = 4001
light_server_port = 4002
logdata_server_port = 4003
pump_server_port = 4004

# GPIO for water low sensor, 1: water is low, 0: water is available
port_waterlow = 18
port_watermedium = 23
port_waterhigh = 24

# GPIO for pump 
port_pump = 27
# pump on time
# pump off time
# GPIO for exhaust air fan
port_fan_exhaust_air = 25
# GPIO for fan
port_fan = 10
# GPIO for light
port_light = 15 
# GPIO for heater
port_heater = 22
# GPIO humidifier
port_humidifier = 9
# GPIO for reserved
port_reserved = 17

moisture_dict = {
    1: dict(channel=0),
    2: dict(channel=1),
}
pump_dict = {1: port_pump, 2: port_reserved}

log_format = "%(module)s:%(levelname)s:%(asctime)s:%(message)s"


# FAN is ON if port 10 is LOW
# FAN EXHAUST AIR is ON if port 25 is LOW
# RESERVED is ON if port 17 is HIGH
# HUMDIFIER is ON if port 9 is HIGH
# LIGHT is ON if port 15 is HIGH
# HEATER is ON if port 22 is HIGH
# PUMP is ON if port 27 is HIGH