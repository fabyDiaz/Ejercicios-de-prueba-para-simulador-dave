# Buscar un objeto rojo girando, y detenerse cuando lo encuentra
import time
import cv2
import numpy as np
from robot_interface import robot_connect

# Rango de color ROJO en HSV (el rojo necesita dos rangos porque "da la vuelta")
rojo_bajo_min = np.array([0, 50, 30])
rojo_bajo_max = np.array([10, 255, 255])
rojo_alto_min = np.array([170, 50, 30])
rojo_alto_max = np.array([179, 255, 255])

AREA_MINIMA = 200     # manchas más chicas se ignoran (ruido)

rov = robot_connect.start()
print("Buscando objeto...")

encontrado = False

for _ in range(300):              # 300 vueltas × 0.1 s = 30 segundos
    # 1. TOMAR LA FOTO
    frame = rov.get_image()
    if frame is None:
        time.sleep(0.1)
        continue

    # 2. PASAR A HSV Y HACER LA MÁSCARA
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara1 = cv2.inRange(hsv, rojo_bajo_min, rojo_bajo_max)
    mascara2 = cv2.inRange(hsv, rojo_alto_min, rojo_alto_max)
    mascara = mascara1 + mascara2          # juntar las dos máscaras

    # 3. BUSCAR CONTORNOS
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

    # 4. ¿HAY ALGO ROJO SUFICIENTEMENTE GRANDE?
    if contornos:
        c = max(contornos, key=cv2.contourArea)   # la mancha más grande
        area = cv2.contourArea(c)

        if area > AREA_MINIMA:
            # ¡Lo encontramos! Dibujar una caja verde alrededor
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            encontrado = True

    # 5. MOSTRAR LA CÁMARA Y LA MÁSCARA
    cv2.imshow("Camara", frame)
    cv2.imshow("Mascara", mascara)
    cv2.waitKey(1)

    # 6. DECIDIR
    if encontrado:
        rov.stop()
        print(f"¡Objeto encontrado! Área: {area:.0f} px²")
        break
    else:
        rov.set_yaw(0.2)          # no lo veo: seguir girando para buscar

    time.sleep(0.1)

if not encontrado:
    print("No se encontró ningún objeto")

rov.stop()
cv2.waitKey(3000)                 # dejar la imagen 3 segundos para verla
cv2.destroyAllWindows()
robot_connect.stop()