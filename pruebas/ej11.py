import time
from robot_interface import robot_connect

rov = robot_connect.start()

print("Yaw inicial:", rov.get_yaw())

rov.set_yaw(0.5)

for i in range(10):
    time.sleep(1)
    print(f"Segundo {i+1}: yaw = {rov.get_yaw()}")

rov.set_yaw(0)

print("Yaw después de detener:", rov.get_yaw())

rov.stop()
robot_connect.stop()