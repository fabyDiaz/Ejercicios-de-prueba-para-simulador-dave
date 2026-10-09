# ESTE EJERCICIO ESTABA EN EL REPOSITORIO, PROBLEMAS CON YAW.
# Una secuencia de movimientos
# Clase 03 · surge y yaw
# Qué observar: avanza, gira a la izquierda y retrocede; mira el rumbo cambiar.

import time
from robot_interface import robot_connect

rov = robot_connect.start()

# Avanzar ~2 m
rov.set_surge(0.5)
time.sleep(3.0)          # surge positivo = adelante
rov.stop()

# Girar ~90° a la izquierda
rov.set_yaw(0.3)
time.sleep(3.0)          # yaw positivo = izquierda
rov.stop()

# Retroceder ~1 m
rov.set_surge(-0.4)
time.sleep(2.0)          # surge negativo = atrás
rov.stop()

print("Secuencia completada.")
robot_connect.stop()
