import cv2
from robot_interface import robot_connect

rov = robot_connect.start() # conectar con el BlueROV2 en DAVE
frame = rov.get_image() # imagen BGR lista para OpenCV — forma (alto, ancho,
print(f"Resolución: {frame.shape[1]} × {frame.shape[0]}")
cv2.imshow("Camara del ROV", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
robot_connect.stop()