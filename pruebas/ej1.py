#CLASE 1

import time

from robot_interface import robot_connect

rov = robot_connect.start()

nombre_rov = "BlueRov2"

rov.stop()

print(f"ROV {nombre_rov} conectado")
robot_connect.stop()