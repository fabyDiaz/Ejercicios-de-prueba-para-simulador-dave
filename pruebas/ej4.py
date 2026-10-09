#LO MISMO QUE EJ3.PY SOLO QUE DEJÉ SOLO EL YAW PARA HACER PRUEBAS
# Una secuencia de movimientos
# Clase 03 · surge y yaw
# Qué observar: avanza, gira a la izquierda y retrocede; mira el rumbo cambiar.

import time
from robot_interface import robot_connect

rov = robot_connect.start()

# Girar ~90° a la izquierda
rov.set_yaw(0.3)
time.sleep(3.0)          # yaw positivo = izquierda
rov.stop()

print("Secuencia completada.")
print(f"{rov.get_yaw()}")
robot_connect.stop()
