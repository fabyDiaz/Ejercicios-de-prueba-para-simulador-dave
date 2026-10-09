import cv2
import numpy as np

from robot_interface import robot_connect

rov = robot_connect.start()

img = rov.get_image()  # Imagen BGR directa de la cámara de DAVE

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

lower_naranja = np.array([10, 100, 100])  # Rango naranja en HSV
upper_naranja = np.array([25, 255, 255])

mascara = cv2.inRange(hsv, lower_naranja, upper_naranja)

area = cv2.countNonZero(mascara)

print(f"Área total detectada: {area} píxeles blancos")

cv2.imshow("Original", img)
cv2.imshow("Máscara naranja", mascara)

cv2.waitKey(0)
cv2.destroyAllWindows()

robot_connect.stop()