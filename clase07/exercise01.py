# Acercarse a una boya: detección de color + control proporcional
# ros2 launch cirta_demos dave_bluerov_buoys.launch.py
import os
import time

import cv2
import numpy as np
from robot_interface import robot_connect

MOSTRAR = "DISPLAY" in os.environ  # ventana solo si hay pantalla
ANCHO_LLEGADA = 110  # px: boya así de ancha = estamos cerca
KP_YAW = 60.0        # giro por error de centrado
KP_SURGE = 0.6       # avance por error de tamaño


def detectar_boyas(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, (0, 50, 30), (10, 255, 180)) | \
        cv2.inRange(hsv, (170, 50, 30), (179, 255, 180))
    # une el cono de la boya con su base
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((15, 5), np.uint8))
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boyas = []
    for c in contornos:
        if cv2.contourArea(c) > 15:
            x, y, w, h = cv2.boundingRect(c)
            boyas.append({"cx": x + w / 2, "cy": y + h / 2, "x": x, "w": w, "h": h})
    return boyas


rov = robot_connect.start()
print("Buscando boya...")

while True:
    frame = rov.get_image()
    if frame is None:
        continue
    ancho_img = frame.shape[1]
    boyas = detectar_boyas(frame)

    if not boyas:
        rov.set_velocity(0.0, 0.0, 0.0)
        rov.set_yaw(30)  # buscar girando
    else:
        boya = max(boyas, key=lambda b: b["w"])  # la más grande = la más cerca
        error_x = (boya["cx"] - ancho_img / 2) / (ancho_img / 2)  # -1 izquierda, +1 derecha
        error_ancho = (ANCHO_LLEGADA - boya["w"]) / ANCHO_LLEGADA

        if error_ancho <= 0:
            print("¡Llegamos a la boya!")
            break

        rov.set_yaw(KP_YAW * error_x)
        # avanza solo si la boya está más o menos al centro
        rov.set_surge(KP_SURGE * error_ancho if abs(error_x) < 0.3 else 0.0)
        print(f"boya x={boya['cx']:.0f}px ancho={boya['w']}px")

        if MOSTRAR:
            cv2.rectangle(frame, (boya["x"], int(boya["cy"] - boya["h"] / 2)),
                          (boya["x"] + boya["w"], int(boya["cy"] + boya["h"] / 2)), (0, 255, 0), 2)
    if MOSTRAR:
        cv2.imshow("camara", frame)
        cv2.waitKey(1)
    time.sleep(0.05)

rov.stop()
robot_connect.stop()