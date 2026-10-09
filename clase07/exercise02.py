# Seguir una ruta de boyas: pasar cada boya dejándola a la derecha
# ros2 launch cirta_demos dave_bluerov_buoys.launch.py world_name:=dave_ocean_waves_buoy_course_1
import math
import os
import time

import cv2
import numpy as np
from robot_interface import robot_connect

MOSTRAR = "DISPLAY" in os.environ
SEPARACION = 2.5    # apuntar 2.5 altos de boya a la izquierda de su borde
ALTO_CERCA = 70     # px: boya cercana para empezar la ruta
ALTO_PASADA = 50    # px: boya cercana y a la derecha = la estamos pasando
VEL_AVANCE = 0.35
TIEMPO_PASAR = 2.5  # s: seguir recto al pasar una boya (la cámara ya no la ve)
RADIO_LLEGADA = 1.5  # m del punto de partida = vuelta completa
TIEMPO_MAX = 300     # s: por seguridad, terminar igual
KP_YAW = 120.0


def detectar_boyas(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, (0, 50, 30), (10, 255, 180)) | \
        cv2.inRange(hsv, (170, 50, 30), (179, 255, 180))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((15, 5), np.uint8))
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boyas = []
    for c in contornos:
        if cv2.contourArea(c) > 15:
            x, y, w, h = cv2.boundingRect(c)
            boyas.append({"cx": x + w / 2, "cy": y + h / 2, "x": x, "w": w, "h": h})
    return boyas


def mostrar(frame, boya=None, x_meta=None):
    if not MOSTRAR:
        return
    if boya is not None:
        cv2.rectangle(frame, (boya["x"], int(boya["cy"] - boya["h"] / 2)),
                      (boya["x"] + boya["w"], int(boya["cy"] + boya["h"] / 2)), (0, 255, 0), 2)
        cv2.line(frame, (int(x_meta), 0), (int(x_meta), frame.shape[0]), (255, 0, 0), 1)
    cv2.imshow("camara", frame)
    cv2.waitKey(1)


rov = robot_connect.start()
inicio = None
while inicio is None:
    inicio = rov.get_position()

# 1) Desplazarse a la izquierda hasta dejar la primera boya a la derecha
while True:
    frame = rov.get_image()
    if frame is None:
        continue
    cercanas = [b for b in detectar_boyas(frame) if b["h"] > ALTO_CERCA]
    if cercanas and max(cercanas, key=lambda b: b["h"])["cx"] > 0.7 * frame.shape[1]:
        break
    rov.set_sway(-0.3)  # negativo = izquierda
    mostrar(frame)
    time.sleep(0.05)
rov.set_sway(0.0)
print("Primera boya a la derecha, comenzando la ruta")

# 2) Pasar boya por boya
anterior = None
nos_alejamos = False
t_inicio = time.time()
while True:
    pos = rov.get_position()
    if pos is None:
        continue
    distancia = math.hypot(pos["x"] - inicio["x"], pos["y"] - inicio["y"])
    if distancia > 5.0:
        nos_alejamos = True
    if nos_alejamos and distancia < RADIO_LLEGADA:
        break
    if time.time() - t_inicio > TIEMPO_MAX:
        print("Tiempo máximo alcanzado")
        break

    frame = rov.get_image()
    if frame is None:
        continue
    ancho_img = frame.shape[1]
    boyas = detectar_boyas(frame)
    candidatas = [b for b in boyas
                  if not (b["h"] > ALTO_PASADA and b["cx"] > 0.65 * ancho_img)
                  and b["x"] + b["w"] < 0.9 * ancho_img]

    # la boya que seguíamos salió por la derecha: seguir recto hasta pasarla
    if anterior is not None and anterior["h"] > 0.6 * ALTO_PASADA and anterior["cx"] > 0.55 * ancho_img and \
            not any(abs(b["cx"] - anterior["cx"]) < 25 for b in candidatas):
        print("Pasando boya")
        rov.set_yaw(0)
        rov.set_surge(VEL_AVANCE)
        time.sleep(TIEMPO_PASAR)
        anterior = None
        continue

    if candidatas:
        boya = max(candidatas, key=lambda b: b["h"])  # la más alta = la más cercana
        x_meta = boya["x"] - SEPARACION * boya["h"]   # punto a la izquierda de la boya
        error_x = (x_meta - ancho_img / 2) / (ancho_img / 2)
        rov.set_yaw(KP_YAW * error_x)
        rov.set_surge(VEL_AVANCE * max(0.0, 1 - 2 * abs(error_x)))  # si hay que girar mucho, gira en el lugar
        anterior = boya
        print(f"boya x={boya['cx']:.0f}px alto={boya['h']}px meta={x_meta:.0f}px ({len(boyas)} vistas)")
        mostrar(frame, boya, x_meta)
    else:
        # sin boyas a la vista: girar a la derecha buscando la siguiente
        rov.set_yaw(30)
        rov.set_surge(0.15)
        anterior = None
        mostrar(frame)
    time.sleep(0.05)

print("¡Ruta completada!")
rov.stop()
robot_connect.stop()