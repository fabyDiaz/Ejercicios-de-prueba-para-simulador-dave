# Buscar la boya roja, centrarla y avanzar hasta llegar a ella
import time
import cv2
import numpy as np
from robot_interface import robot_connect

# Rango de color ROJO en HSV (dos rangos porque el rojo "da la vuelta")
rojo_bajo_min = np.array([0, 50, 30])
rojo_bajo_max = np.array([10, 255, 180])
rojo_alto_min = np.array([170, 50, 30])
rojo_alto_max = np.array([179, 255, 180])

AREA_MINIMA = 15        # manchas más chicas se ignoran (ruido)
ANCHO_LLEGADA = 150     # px: si la boya se ve así de ancha, llegamos
MARGEN_X = 50           # px: si está a menos de esto del centro, está centrada
KP_YAW = 0.1            # error de 300 px → giro 30
VELOCIDAD = 0.3         # velocidad de avance

rov = robot_connect.start()
print("Buscando boya...")

for vuelta in range(600):         # 600 vueltas × 0.1 s = 60 segundos
    # 1. TOMAR LA FOTO
    frame = rov.get_image()
    if frame is None:
        time.sleep(0.1)
        continue

    # 2. MÁSCARA DE COLOR ROJO
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara1 = cv2.inRange(hsv, rojo_bajo_min, rojo_bajo_max)
    mascara2 = cv2.inRange(hsv, rojo_alto_min, rojo_alto_max)
    mascara = mascara1 + mascara2
    # unir las partes de la boya (el cono y su base) en una sola mancha
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((15, 5), np.uint8))

    # 3. BUSCAR LA MANCHA MÁS GRANDE
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    area = 0
    if contornos:
        c = max(contornos, key=cv2.contourArea)
        area = cv2.contourArea(c)

    # 4. DECIDIR QUÉ HACER
    if area < AREA_MINIMA:
        # No veo la boya: girar para buscar
        rov.set_surge(0.0)
        rov.set_yaw(20)
        print("Buscando...")

    else:
        # Veo la boya: ¿dónde está y qué tan ancha se ve?
        x, y, w, h = cv2.boundingRect(c)
        cx = x + w / 2                       # centro de la boya
        centro_imagen = frame.shape[1] / 2   # mitad del ancho de la imagen
        error_x = cx - centro_imagen         # + derecha, - izquierda

        # ¿Llegamos?
        if w >= ANCHO_LLEGADA:
            rov.stop()
            print(f"¡Llegamos a la boya! Ancho: {w} px")
            break

        # Girar hacia la boya con Kp
        giro = KP_YAW * error_x
        giro = max(-30, min(30, giro))       # limitar entre -30 y 30
        rov.set_yaw(giro)

        # Avanzar solo si la boya está centrada
        if abs(error_x) < MARGEN_X:
            rov.set_surge(VELOCIDAD)
        else:
            rov.set_surge(0.0)

        # Dibujar caja verde alrededor de la boya
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        print(f"error_x = {error_x:.0f} px | ancho = {w} px")

    # 5. MOSTRAR LA CÁMARA
    cv2.imshow("Camara", frame)
    cv2.waitKey(1)

    time.sleep(0.1)

rov.stop()
cv2.waitKey(3000)                 # dejar la imagen 3 segundos para verla
cv2.destroyAllWindows()
robot_connect.stop()