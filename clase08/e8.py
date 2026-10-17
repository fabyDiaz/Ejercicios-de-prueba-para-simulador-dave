# Recorrer un camino de boyas: pasar cada boya dejándola a la DERECHA
import time
import cv2
import numpy as np
from robot_interface import robot_connect

# Rango de color ROJO en HSV (dos rangos porque el rojo "da la vuelta")
rojo_bajo_min = np.array([0, 50, 30])
rojo_bajo_max = np.array([10, 255, 180])
rojo_alto_min = np.array([170, 50, 30])
rojo_alto_max = np.array([179, 255, 180])

NUM_BOYAS = 3          # cuántas boyas tiene el camino
AREA_MINIMA = 15       # manchas más chicas se ignoran (ruido)
SEPARACION = 2.5       # qué tan a la izquierda de la boya apuntamos
ALTO_PASADA = 50       # px: boya así de alta = ya está cerca
KP_YAW = 0.1           # error de 300 px → giro 30
VELOCIDAD = 0.35       # velocidad de avance
TIEMPO_PASAR = 2.5     # segundos de avanzar recto cuando la boya queda atrás

rov = robot_connect.start()
print("Comenzando el camino...")

boyas_pasadas = 0
pasando = False        # True mientras tenemos una boya a nuestro lado derecho

for vuelta in range(3000):        # 3000 vueltas × 0.1 s = 5 minutos máximo
    # 1. TOMAR LA FOTO
    frame = rov.get_image()
    if frame is None:
        time.sleep(0.1)
        continue
    ancho_img = frame.shape[1]

    # 2. MÁSCARA DE COLOR ROJO
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara1 = cv2.inRange(hsv, rojo_bajo_min, rojo_bajo_max)
    mascara2 = cv2.inRange(hsv, rojo_alto_min, rojo_alto_max)
    mascara = mascara1 + mascara2
    # unir las partes de la boya (el cono y su base) en una sola mancha
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((15, 5), np.uint8))

    # 3. BUSCAR LA MANCHA MÁS GRANDE (la boya más cercana)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    area = 0
    if contornos:
        c = max(contornos, key=cv2.contourArea)
        area = cv2.contourArea(c)

    veo_boya = area >= AREA_MINIMA
    boya_al_lado = False
    if veo_boya:
        x, y, w, h = cv2.boundingRect(c)
        cx = x + w / 2
        # ¿La boya está cerca y a la derecha? Entonces la tenemos al lado
        if h > ALTO_PASADA and cx > 0.7 * ancho_img:
            boya_al_lado = True

    # 4. DECIDIR QUÉ HACER
    if boya_al_lado:
        # Boya cerca y a la derecha: avanzar recto para pasarla
        rov.set_yaw(0)
        rov.set_surge(VELOCIDAD)
        pasando = True
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        print("Boya a la derecha, pasándola...")

    elif pasando:
        # La boya que teníamos al lado ya no está: quedó atrás.
        # Avanzar un poco más para alejarnos de ella y contarla.
        rov.set_yaw(0)
        rov.set_surge(VELOCIDAD)
        time.sleep(TIEMPO_PASAR)
        pasando = False

        boyas_pasadas = boyas_pasadas + 1
        print(f"Boyas pasadas: {boyas_pasadas} de {NUM_BOYAS}")
        if boyas_pasadas == NUM_BOYAS:
            break
        continue

    elif not veo_boya:
        # No veo ninguna boya: girar a la derecha para buscar la siguiente
        rov.set_surge(0.0)
        rov.set_yaw(20)
        print("Buscando boya...")

    else:
        # Veo una boya adelante: apuntar a un punto a su IZQUIERDA,
        # así la boya nos queda a la derecha al pasar.
        x_meta = x - SEPARACION * h
        error_x = x_meta - ancho_img / 2     # + derecha, - izquierda

        # Girar hacia ese punto con Kp
        giro = KP_YAW * error_x
        giro = max(-30, min(30, giro))       # limitar entre -30 y 30
        rov.set_yaw(giro)

        # Avanzar solo si estamos apuntando más o menos bien
        if abs(error_x) < 100:
            rov.set_surge(VELOCIDAD)
        else:
            rov.set_surge(0.0)

        # Dibujar: caja verde en la boya y línea azul donde apuntamos
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.line(frame, (int(x_meta), 0), (int(x_meta), frame.shape[0]), (255, 0, 0), 2)
        print(f"boya alto = {h} px | error_x = {error_x:.0f} px")

    # 5. MOSTRAR LA CÁMARA
    cv2.imshow("Camara", frame)
    cv2.waitKey(1)

    time.sleep(0.1)

print("¡Camino completado!")
rov.stop()
cv2.destroyAllWindows()
robot_connect.stop()