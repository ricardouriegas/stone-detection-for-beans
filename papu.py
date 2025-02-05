import cv2
import numpy as np

def hex_to_hsv(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    bgr = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return hsv[0][0]

# Colores proporcionados
colores_piedras = {
    "clara": ['#FCE2CD', '#B9A298', '#BB9D90'],
    "oscura": ['#292823', '#2E261B']
}

# Calcular rangos HSV para cada tipo de piedra
def calcular_rangos(colores_hex):
    h_values = []
    s_values = []
    v_values = []

    for hex in colores_hex:
        h, s, v = hex_to_hsv(hex)
        h_values.append(h)
        s_values.append(s)
        v_values.append(v)

    # Expandir rangos para tolerar variaciones
    h_min = max(0, min(h_values) - 10)
    h_max = min(179, max(h_values) + 10)
    s_min = max(0, min(s_values) - 40)
    s_max = min(255, max(s_values) + 40)
    v_min = max(0, min(v_values) - 40)
    v_max = min(255, max(v_values) + 40)

    return (np.array([h_min, s_min, v_min], np.uint8),
            np.array([h_max, s_max, v_max], np.uint8))

# Rangos calculados
rango_clara = calcular_rangos(colores_piedras["clara"])
rango_oscura = calcular_rangos(colores_piedras["oscura"])

print("Rango piedra clara:", rango_clara)
print("Rango piedra oscura:", rango_oscura)

def detectar_piedras(imagen_path):
    img = cv2.imread(imagen_path)
    img_resized = cv2.resize(img, (1024, 768))
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)

    # Máscaras con los rangos calculados
    mascara_clara = cv2.inRange(hsv, *rango_clara)
    mascara_oscura = cv2.inRange(hsv, *rango_oscura)

    # Mejorar máscaras
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25,25))
    mascara_clara = cv2.morphologyEx(mascara_clara, cv2.MORPH_CLOSE, kernel)
    mascara_oscura = cv2.morphologyEx(mascara_oscura, cv2.MORPH_CLOSE, kernel)

    # Función de detección mejorada
    def encontrar_piedra(mascara, color):
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contornos:
            area = cv2.contourArea(cnt)
            if area < 5000: continue

            # Aproximación de forma convexa
            hull = cv2.convexHull(cnt)
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            box = np.intp(box)

            # Filtrar por relación de aspecto y solidez
            x,y,w,h = cv2.boundingRect(hull)
            relacion = max(w,h)/min(w,h)
            if relacion < 1.8:
                # Escalar a coordenadas originales
                box = box * np.array([img.shape[1]/1024, img.shape[0]/768])
                cv2.drawContours(img, [box.astype(int)], 0, color, 20)

    # Detectar y dibujar
    encontrar_piedra(mascara_clara, (0,255,255))  # Amarillo para piedra clara
    encontrar_piedra(mascara_oscura, (128,0,255))  # Naranja para piedra oscura

    # Guardar y mostrar
    cv2.imwrite('resultado.jpg', img)
    cv2.namedWindow('Resultado', cv2.WINDOW_NORMAL)
    cv2.imshow('Resultado', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

detectar_piedras('/home/richy/Documents/frijoles/pintos/frijol1.jpg')
