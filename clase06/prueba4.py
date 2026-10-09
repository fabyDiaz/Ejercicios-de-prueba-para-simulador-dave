import cv2
import time
from robot_interface import robot_connect


# Conectar con el ROV
rov = robot_connect.start()

print("ROV conectado")

# OBJETIVO DE AVANCE
objetivo_x = 3.0
margen_x = 0.2

print("Avanzando hasta X = 3 metros...")

while True:

    # Obtener imagen de la cámara
    frame = rov.get_image()

    # Obtener posición actual
    posicion = rov.get_position()
    actual_x = posicion["x"]

    # Calcular cuánto falta
    error_x = objetivo_x - actual_x

    # Mostrar cámara
    if frame is not None:
        cv2.imshow("Camara del ROV", frame)

    # Control del avance
    if abs(error_x) > margen_x:

        rov.set_surge(error_x * 0.2)

    else:

        rov.set_surge(0.0)

        print("¡Llegamos a los 3 metros!")
        break

    # Actualizar ventana de cámara
    cv2.waitKey(1)

    time.sleep(0.1)

# OBJETIVO DE GIRO

objetivo_yaw = 90.0
margen_yaw = 10.0

print("Girando hasta yaw = 90 grados...")

while True:

    # Obtener imagen de la cámara
    frame = rov.get_image()

    # Obtener yaw actual
    actual_yaw = rov.get_yaw()

    # Calcular cuánto falta
    error_yaw = objetivo_yaw - actual_yaw

    # Mostrar cámara
    if frame is not None:
        cv2.imshow("Camara del ROV", frame)

    # Control del giro
    if abs(error_yaw) > margen_yaw:
        rov.set_yaw(error_yaw * 0.2)
    else:
        rov.set_yaw(0.0)
        print("¡Llegamos a los 90 grados!")
        break

    # Actualizar ventana de cámara
    cv2.waitKey(1)

    time.sleep(0.1)

# FINAL
rov.set_surge(0.0)
rov.set_yaw(0.0)

print(f"Posición final X: {rov.get_position()['x']:.2f} m")
print(f"Rumbo final: {rov.get_yaw():.1f}°")

# Cerrar cámara
cv2.destroyAllWindows()

# Detener ROV
rov.stop()

# Desconectar
robot_connect.stop()
