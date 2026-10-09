import cv2
import time
from robot_interface import robot_connect

# CONECTAR AL ROV
rov = robot_connect.start()

print("ROV conectado")

# POSICIÓN INICIAL

posicion_inicial = rov.get_position()

objetivo_y = posicion_inicial["y"]
objetivo_z = posicion_inicial["z"]

print(
    f"Posición inicial: "
    f"X={posicion_inicial['x']:.2f}, "
    f"Y={objetivo_y:.2f}, "
    f"Z={objetivo_z:.2f}"
)


# OBJETIVO DE AVANCE
objetivo_x = 3.0
margen_x = 0.2

# Ganancias de posición
KP_X = 0.2
KP_Y = 0.1
KP_Z = 0.1

print("Avanzando hasta X = 3 metros...")

while True:

    # Cámara
    frame = rov.get_image()

    if frame is not None:
        cv2.imshow("Camara del ROV", frame)

    cv2.waitKey(1)

    # Posición actual
    posicion = rov.get_position()
    actual_x = posicion["x"]
    actual_y = posicion["y"]
    actual_z = posicion["z"]

    # Errores de posición
    error_x = objetivo_x - actual_x
    error_y = objetivo_y - actual_y
    error_z = objetivo_z - actual_z

    # Control de posición
    surge = error_x * KP_X
    sway = error_y * KP_Y
    heave = error_z * KP_Z

    # Limitar valores entre -1 y 1
    surge = max(-1.0, min(1.0, surge))
    sway = max(-1.0, min(1.0, sway))
    heave = max(-1.0, min(1.0, heave))

    # Enviar los tres movimientos
    rov.set_velocity(
        surge=surge,
        sway=sway,
        heave=heave
    )

    print(
        f"X={actual_x:.2f} | "
        f"Y={actual_y:.2f} | "
        f"Z={actual_z:.2f}"
    )

    # ¿Llegamos a X = 3?

    if abs(error_x) <= margen_x:

        print("¡Llegamos a los 3 metros!")
        break
    time.sleep(0.1)

# PREPARAR GIRO

print("Manteniendo posición mientras gira...")

# OBJETIVO DE YAW
objetivo_yaw = 90.0
margen_yaw = 10.0

KP_YAW = 0.2

while True:

    # Cámara
    frame = rov.get_image()

    if frame is not None:
        cv2.imshow("Camara del ROV", frame)

    cv2.waitKey(1)

    # Posición actual

    posicion = rov.get_position()

    actual_x = posicion["x"]
    actual_y = posicion["y"]
    actual_z = posicion["z"]


    # Errores de posición
    error_x = objetivo_x - actual_x
    error_y = objetivo_y - actual_y
    error_z = objetivo_z - actual_z

    # Mantener posición
    surge = error_x * KP_X
    sway = error_y * KP_Y
    heave = error_z * KP_Z

    # Limitar entre -1 y 1
    surge = max(-1.0, min(1.0, surge))
    sway = max(-1.0, min(1.0, sway))
    heave = max(-1.0, min(1.0, heave))

    # Mantener X, Y y Z
    rov.set_velocity(
        surge=surge,
        sway=sway,
        heave=heave
    )

    # Control del YAW
    actual_yaw = rov.get_yaw()
    error_yaw = objetivo_yaw - actual_yaw

    if abs(error_yaw) > margen_yaw:
        rov.set_yaw(error_yaw * KP_YAW)
    else:
        rov.set_yaw(0.0)
        print("¡Llegamos a 90 grados!")
        break
    print(
        f"X={actual_x:.2f} | "
        f"Y={actual_y:.2f} | "
        f"Z={actual_z:.2f} | "
        f"Yaw={actual_yaw:.1f}°"
    )
    time.sleep(0.1)


# DETENER MOVIMIENTOS

rov.set_velocity(
    surge=0.0,
    sway=0.0,
    heave=0.0
)

rov.set_yaw(0.0)


print("Movimiento terminado")


# CERRAR CÁMARA
cv2.destroyAllWindows()


# DETENER Y DESCONECTAR
rov.stop()
robot_connect.stop()

