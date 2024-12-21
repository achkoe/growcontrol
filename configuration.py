sensors_server_port = 4000
fan_server_port = 4001
light_server_port = 4002
logdata_server_port = 4003

# GPIO for water low sensor, 1: water is low, 0: water is available
port_waterlow = 18
port_watermedium = 23
port_waterhigh = 24

# GPIO for pump 1
port_pump1 = 15
# Milliliter per seconds for pump 1
pump1_milliliter_per_second = 25
# GPIO for pump 2 (not yet available)
port_pump2 = 10
# Milliliter per seconds for pump 2
pump2_milliliter_per_second = 50
# GPIO for pump 3 (not yet available)
port_pump3 = 9
# Milliliter per seconds for pump 3
pump3_milliliter_per_second = 50
# GPIO for exhaust air fan
port_fan_exhaust_air = 25
# GPIO for fan
port_fan = 17
# GPIO for light
port_light = 22
# GPIO for heater
port_heater = 27

pump_moisture_dict = {
    1: dict(channel=0, pump=4004, gpio=port_pump1, milliliter_per_second=pump1_milliliter_per_second),
 #   2: dict(channel=1, pump=4005, gpio=port_pump2, milliliter_per_second=pump2_milliliter_per_second),
}

log_format = "%(module)s:%(levelname)s:%(asctime)s:%(message)s"
