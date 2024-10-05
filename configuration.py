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
# GPIO for pump 2 (not yet available)
port_pump2 = 10
# GPIO for pump 3 (not yet available)
port_pump3 = 9
# GPIO for heater (not yet implemented)
port_heater = 25
# GPIO for fan
port_fan = 17
# GPIO for light1 and light 2
port_light1 = 22
port_light2 = 27

pump_moisture_dict = {
    1: dict(channel=0, pump=4004, gpio=port_pump1)
}

log_format = "%(module)s:%(levelname)s:%(asctime)s:%(message)s"
