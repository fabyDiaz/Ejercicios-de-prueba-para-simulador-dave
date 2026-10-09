# Detección de boya roja:  dave_client + OpenCV
import cv2
import numpy as np
from robot_interface import robot_connect

rov = robot_connect.start()  # conecta con el simulador
frame = rov.get_image()           # ← numpy BGR de DAVE
hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # ← convierte espacio

# Rojo bajo
lower_rojo1 = np.array([0, 50, 30])
upper_rojo1 = np.array([10, 255, 180])

# Rojo alto
lower_rojo2 = np.array([170, 50, 30])
upper_rojo2 = np.array([179, 255, 180])

mask1 = cv2.inRange(hsv, lower_rojo1, upper_rojo1)
mask2 = cv2.inRange(hsv, lower_rojo2, upper_rojo2)

mascara_roja = mask1 | mask2

# ← 1 donde hay rojo, 0 donde no  así de simple
cv2.imshow('Mascara', mascara_roja)     # ← mostrar en pantalla
cv2.waitKey(10)

# Contornos y centroide - continuación
contornos, _ = cv2.findContours(mascara_roja, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contornos:
    c = max(contornos, key=cv2.contourArea)  # ← objeto más grande
    M = cv2.moments(c)
    if M['m00'] > 0:
        cx = int(M['m10'] / M['m00'])  # ← x del centroide
        cy = int(M['m01'] / M['m00'])  # ← y del centroide
        area = cv2.contourArea(c)
        # Area grande = objeto cerca. Area pequeña = objeto lejos.
        print(f'Boya en ({cx}, {cy}) — área: {area:.0f} px²')