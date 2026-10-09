import cv2
import time
from robot_interface import robot_connect


# Conectar con el ROV
rov = robot_connect.start()

print("ROV conectado")

# Girar un poco
rov.set_yaw(30)
time.sleep(5)
rov.stop()

# Avanzar
rov.set_surge(0.5)

# Mantener la cámara activa mientras avanza
for i in range(100):
    frame = rov.get_image()

    if frame is not None:
        cv2.imshow("Camara del ROV", frame)

    cv2.waitKey(1)
    time.sleep(0.1)

# Detener el avance
rov.stop()

print("Movimiento terminado")

# Cerrar la ventana de la cámara
cv2.destroyAllWindows()

# Detener y desconectar el ROV
rov.stop()
robot_connect.stop()
