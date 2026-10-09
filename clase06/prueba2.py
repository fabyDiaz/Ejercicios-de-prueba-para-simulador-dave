import cv2
import time
from robot_interface import robot_connect


# Conectar con el ROV
rov = robot_connect.start()

print("ROV conectado")

objetivo_x = 3.0
margen = 0.2


# Mantener la cámara activa mientras avanza
for i in range(100):

    frame = rov.get_image()

    actual_x = rov.get_position()
    error_x = objetivo_x - actual_x["x"]

    if frame is not None:
        cv2.imshow("Camara del ROV", frame)

    if abs(error_x) > margen:
        rov.set_surge(error_x * 0.2)
    else:
        rov.set_surge(0.0)
        print("¡Llegamos al objetivo!")
        break

    print(f"X actual: {actual_x['x']:.2f} m | Error: {error_x:.2f} m")

    cv2.waitKey(1)
    time.sleep(0.1)


# Detener el avance
rov.stop()

print("Movimiento terminado")

# Cerrar la ventana de la cámara
cv2.destroyAllWindows()

# Desconectar el ROV
robot_connect.stop()