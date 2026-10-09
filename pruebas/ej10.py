import time, cv2
import numpy as np
from robot_interface import robot_connect

rov = robot_connect.start()

lower_naranja = np.array([10, 100, 100])
upper_naranja = np.array([25, 255, 255])

while True:
    frame = rov.get_image()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, lower_naranja, upper_naranja)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contornos:
        c = max(contornos, key=cv2.contourArea)
        area = cv2.contourArea(c)

        if area > UMBRAL_AREA:
            M = cv2.moments(c)
            cx = int(M["m10"] / M["m00"])
            dist = estimar_distancia(area)
            error_x = cx - frame.shape[1] // 2

            if dist <= UMBRAL_DIST:
                rov.stop()
                print("Boya alcanzada!")
                break
            elif abs(error_x) > UMBRAL_X:
                yaw = 0.2 if error_x > 0 else -0.2
                rov.set_velocity(yaw=yaw)
            else:
                rov.set_velocity(surge=0.3)
        else:
            rov.stop()
            print("Objeto no visible.")
    else:
        rov.stop()
        print("Objeto no visible.")

    time.sleep(0.1)

robot_connect.stop()