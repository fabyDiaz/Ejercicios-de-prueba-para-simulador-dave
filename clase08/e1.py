#Avanzar-> girar -> bajar
import time
from robot_interface import robot_connect

# Conectar con el ROV
rov = robot_connect.start()

print("ROV conectado")

rov.set_surge(0.5)
time.sleep(3)
rov.stop()
pos = rov.get_position();
print(f"Posición en x: {pos["x"]:.2f}")
time.sleep(3)

# Girar un poco
rov.set_yaw(30)
time.sleep(3)
rov.stop()
rumbo = rov.get_heading()
print(f"Rumbo: {rumbo:.2f}")
time.sleep(3)

#bajar
rov.set_heave(0.5)
time.sleep(5)
rov.stop()
profundidad = rov.get_depth()
print(f"profundidad:{profundidad:.2f}")

# Detener y desconectar el ROV
robot_connect.stop()
