# Avanzar mirando la cámara
import time
import cv2
from robot_interface import robot_connect

rov = robot_connect.start()
print("ROV conectado")

for _ in range(100):            # 100 vueltas × 0.1 s = 10 segundos
    frame = rov.get_image()     # 1. tomar la foto de la cámara
    if frame is None:           # la cámara todavía no manda imagen
        time.sleep(0.1)
        continue

    cv2.imshow("Camara", frame) # 2. mostrar la foto en una ventana
    cv2.waitKey(1)              # necesario para que la ventana se actualice

    rov.set_surge(0.3)          # 3. avanzar despacio
    time.sleep(0.1)

rov.stop()
cv2.destroyAllWindows()         # cerrar la ventana
robot_connect.stop()