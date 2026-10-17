# Avanzar hasta x = 3 m y girar 90° a la derecha, mirando por la cámara
import time
import cv2
from robot_interface import robot_connect

rov = robot_connect.start()
print("ROV conectado")

# =====================================================
# PARTE 1: AVANZAR HASTA X = 3 METROS
# =====================================================
objetivo_x = 3.0      # metros
margen_x = 0.2        # tolerancia ±0.2 m
kp_x = 0.5            # factor de corrección
tiempo_maximo = 40    # segundos
inicio = time.time()

while True:
    # Mostrar la cámara
    frame = rov.get_image()
    if frame is not None:
        cv2.imshow("Camara", frame)
        cv2.waitKey(1)

    # 1. LEER
    pos = rov.get_position()
    error_x = objetivo_x - pos["x"]

    # 2. ¿LLEGAMOS?
    if abs(error_x) < margen_x:
        print("Objetivo en x alcanzado")
        break

    # 3. ¿SE ACABÓ EL TIEMPO?
    if time.time() - inicio >= tiempo_maximo:
        print("Tiempo máximo alcanzado (avance)")
        break

    # 4. CORREGIR con Kp
    correccion = kp_x * error_x
    correccion = max(-1.0, min(1.0, correccion))   # limitar entre -1 y 1
    rov.set_surge(correccion)

    time.sleep(0.1)

rov.stop()
pos = rov.get_position()
print(f"Posición en x: {pos['x']:.2f}")

# =====================================================
# PARTE 2: GIRAR 90° A LA DERECHA
# =====================================================
# Ojo: get_heading() BAJA cuando giramos a la derecha (set_yaw positivo).
# Por eso el objetivo es el rumbo inicial MENOS 90.
rumbo_inicial = rov.get_heading()
objetivo_yaw = rumbo_inicial - 90.0

margen_yaw = 5.0      # tolerancia ±5°
kp_yaw = 0.5        # el error está en grados, por eso kp es chico
tiempo_maximo = 30    # segundos
inicio = time.time()  # reiniciar el cronómetro para el giro

while True:
    # Mostrar la cámara
    frame = rov.get_image()
    if frame is not None:
        cv2.imshow("Camara", frame)
        cv2.waitKey(1)

    # 1. LEER
    rumbo = rov.get_heading()
    error_yaw = objetivo_yaw - rumbo

    # Tomar siempre el camino más corto (ej: -350° es lo mismo que +10°)
    if error_yaw > 180:
        error_yaw = error_yaw - 360
    if error_yaw < -180:
        error_yaw = error_yaw + 360

    # 2. ¿LLEGAMOS?
    if abs(error_yaw) < margen_yaw:
        print("Rumbo objetivo alcanzado")
        break

    # 3. ¿SE ACABÓ EL TIEMPO?
    if time.time() - inicio >= tiempo_maximo:
        print("Tiempo máximo alcanzado (giro)")
        break

    # 4. CORREGIR con Kp
    correccion = kp_yaw * error_yaw
    correccion = max(-30, min(30, correccion))
    # El signo menos es porque set_yaw positivo hace BAJAR el rumbo
    rov.set_yaw(-correccion)

    time.sleep(0.1)

rov.stop()
print(f"Grados girados: {rumbo_inicial - rov.get_heading():.1f}")

# Cerrar todo
cv2.destroyAllWindows()
robot_connect.stop()