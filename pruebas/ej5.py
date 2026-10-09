#EJERCICIO SOLO PARA ABRIR LA CÁMARA. ES LA SOLUCIÓN DEL EJERCICIO 1 DE LA CLASE 6

import cv2
from robot_interface import robot_connect

rov = robot_connect.start()

frame = rov.get_image()  #CAMBIÉ get_camera por get_image

print("Tipo:", type(frame))
print("Resolución:", frame.shape)

cv2.imshow("Camara del ROV", frame)

cv2.waitKey(0)

cv2.destroyAllWindows()

robot_connect.stop()