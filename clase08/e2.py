# Avanzar hasta x = 3 m y luego girar 90° a la derecha con PID
import time
from robot_interface import robot_connect

rov = robot_connect.start()
print("ROV conectado")

# =====================================================
# PARTE 1: AVANZAR HASTA X = 3 METROS
# =====================================================
objetivo_x = 3.0      # metros
margen_x = 0.2        # tolerancia ±0.2 m
tiempo_maximo_x = 40  # segundos

kp_x = 0.5   # P: reacción al error
error_prev_x = 0.0
inicio = time.time()

while True:
    # 1. LEER
    pos = rov.get_position()
    error_x = objetivo_x - pos["x"]

    # 2. ¿LLEGAMOS?
    if abs(error_x) < margen_x:
        print("Objetivo en x alcanzado")
        break

    # 3. ¿SE ACABÓ EL TIEMPO? (va en un if aparte para que siempre se revise)
    if time.time() - inicio >= tiempo_maximo_x:
        print("Tiempo máximo alcanzado (avance)")
        break

   # Corregir el avance
    correccion = error_x * kp_x

    # Limitar el comando al rango -1 a 1
    correccion = max(-1.0, min(1.0, correccion))

    rov.set_surge(correccion)
    time.sleep(0.1)

rov.stop()
pos = rov.get_position()
print(f"Posición en x: {pos['x']:.2f}")
time.sleep(1)   # esperar que el ROV se quede quieto antes de girar

# =====================================================
# PARTE 2: GIRAR 90° A LA DERECHA
# =====================================================
# Ojo: get_heading() BAJA cuando giramos a la derecha (set_yaw positivo).
# Por eso el objetivo es el rumbo inicial MENOS 90.
rumbo_inicial = rov.get_heading()
objetivo_yaw = rumbo_inicial - 90.0

margen_yaw = 3.0       # tolerancia ±3°
tiempo_maximo_yaw = 30 # segundos

kp_yaw = 0.5  # el error está en grados, por eso kp es chico

error_prev_yaw = 0.0
inicio = time.time()   # reiniciar el cronómetro para el giro

while True:
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
    if time.time() - inicio >= tiempo_maximo_yaw:
        print("Tiempo máximo alcanzado (giro)")
        break
    
    # 4. CORREGIR con Kp
    correccion = kp_yaw * error_yaw
    correccion = max(-30, min(30, correccion))   # limitar entre -30 y 30

    # 5. ACTUAR
    # El signo menos es porque set_yaw positivo hace BAJAR el rumbo
    rov.set_yaw(-correccion)
    time.sleep(0.1)

rov.stop()
print(f"Rumbo final: {rov.get_heading():.2f}")
print(f"Grados girados: {rumbo_inicial - rov.get_heading():.1f}")

# Detener y desconectar
robot_connect.stop()
