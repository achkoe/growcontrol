sensors_server_port = 4000
fan_server_port = 4001
light_server_port = 4002
logdata_server_port = 4003

# GPIO for water low sensor, 1: water is low, 0: water is available
port_waterlow = 18
port_watermedium = 23
port_waterhigh = 24

# GPIO for pump 1
port_pump1 = 17
# Milliliter per seconds for pump 1
pump1_milliliter_per_second = 25
# GPIO for pump 2 (not yet available)
port_pump2 = 9
# Milliliter per seconds for pump 2
pump2_milliliter_per_second = 50
# GPIO for pump 3 (not yet available)
port_pump3 = 9
# Milliliter per seconds for pump 3
pump3_milliliter_per_second = 50
# GPIO for exhaust air fan
port_fan_exhaust_air = 25
# GPIO for fan
port_fan = 10
# GPIO for light
port_light = 15 
# GPIO for heater
port_heater = 22
# GPIO humidifier
port_humidifier = 27

pump_moisture_dict = {
    1: dict(channel=0, pump=4004, gpio=port_pump1, milliliter_per_second=pump1_milliliter_per_second),
    2: dict(channel=1, pump=4005, gpio=port_pump2, milliliter_per_second=pump2_milliliter_per_second),
}

log_format = "%(module)s:%(levelname)s:%(asctime)s:%(message)s"


# FAN is ON if port 10 is LOW
# FAN EXHAUST AIR is ON if port 25 is LOW
# PUMP 1 is ON if port 17 is HIGH
# PUMP 2 is ON if port 9 is HIGH
# LIGHT is ON if port 15 is HIGH
# HEATER is ON if port 22 is HIGH
# RESERVED is ON if port 27 is HIGH