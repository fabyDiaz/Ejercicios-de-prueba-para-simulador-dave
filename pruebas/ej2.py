
#PRUEBA CON YAW 
import time

from robot_interface import robot_connect

rov = robot_connect.start()

print(f"Rumbo inicial: {rov.get_yaw()}°")


rov.set_yaw(30) #LOS APUTNTES DICE QUE DEBE ESTAR NORMALIZADO ENTER -1 Y 1, PERO NO FUNCIONA. CREO QUE FUNCIONA CON SISTEMA SEXADECIMAL, POR ESO LE PUSE 30
time.sleep(5) 
rov.stop() 
rumbo = rov.get_yaw()
print(f"rumbo: {rumbo:.0f}°")
robot_connect.stop()