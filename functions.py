'''
Aqui podras encontrar las funciones fundamentales que se usan tanto para la 
deteccion de las piedras en los frijoles como para la deteccion de que tipo
de frijol es el que vamos a procesar.

Para la deteccion de las piedras en los frijoles se usan las funciones:
    - detectar_piedras_negros()
    - detectar_piedras_pintos()
    - color_dominante()

Dependencias:
    cv2
    numpy

Instalacion de dependencias:
    pip install opencv-python-headless numpy
    
'''

import cv2
import numpy as np
 
def detectar_piedras_negros(imagen_path, colores_hsv=None):
    # cargar la imagen
    imagen = cv2.imread(imagen_path)
    imagen = cv2.resize(imagen, (0, 0), fx=0.5, fy=0.5)  # reducir el tamano a la mitad
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV) # 

    # colores en HSV
    colores_hsv = [
        (25, 5, 235), # aproximación de #FFF1E5 en HSV
        (15, 20, 255),  # aproximación de #FCFFEE en HSV
        (5, 50, 170)  # aproximación de #AB8683 en HSV
    ]

    # mascara para cada color
    mask_total = np.zeros(imagen.shape[:2], dtype=np.uint8)
    for hsv_color in colores_hsv:
        lower_bound = np.array([hsv_color[0] - 10, max(hsv_color[1] - 40, 0), max(hsv_color[2] - 40, 0)])
        upper_bound = np.array([hsv_color[0] + 10, min(hsv_color[1] + 40, 255), min(hsv_color[2] + 40, 255)])

        mask = cv2.inRange(imagen_hsv, lower_bound, upper_bound)
        mask_total = cv2.bitwise_or(mask_total, mask)

    kernel = np.ones((5, 5), np.uint8)
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, kernel)  # Remove small spots
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, kernel)  # Close gaps in background

    # para mostrar la imagen post mascara
    # cv2.imshow("Post-mask", mask_total)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Encontrar contornos de las piedras detectadas
    contornos, _ = cv2.findContours(mask_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar contornos sobre la imagen original
    resultado = imagen.copy()

    filtered_contours = []
    for c in contornos:
        area = cv2.contourArea(c)
        if not (1350 < area < 8000):
            continue
        # Calcular la convexidad
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            continue
        convexity_ratio = area / hull_area
        if convexity_ratio < 0.5:
            continue
        # Aproximar contorno y filtrar por número de vértices
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        vertices = len(approx)
        if vertices < 5:
            continue
        filtered_contours.append(c)

    cv2.drawContours(resultado, filtered_contours, -1, (0, 0, 255), 2)

    # Eliminar la apertura de ventana para mostrar la imagen
    # cv2.imshow('Piedras Detectadas', resultado)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return resultado

# aquí estoy tratando de ajustar los parámetros de como se detecta los 
# frijoles negros para detectar los frijoles pintos, pero no funciona bien como
# el que tengo ahora de 1
# def detectar_piedras_pintos2(imagen_path):
#     # Definir los colores HSV para los pintos (valores ajustados)
#     # #3C3B35, #2D281E, #020106, #302E28, #0F0703, #30281D
#     colores_hsv_pintos =[(25, 30, 60),
#         (20, 85, 45),
#         # (126, 213, 6),
#         (23, 42, 48),
#         (15, 50, 15),
#         (20, 85, 45)
#     ]
    
#     return detectar_piedras_negros(imagen_path, colores_hsv=colores_hsv_pintos)

def detectar_piedras_pintos(image_path):
    # cargar imagen
    image = cv2.imread(image_path)
    if image is None:
        print("No se pudo cargar la imagen:", image_path)
        return

    # convertir a LAB
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # rangos de color para piedras
    lower_piedra = np.array([15, 115, 115])
    upper_piedra = np.array([75, 145, 145])

    # crear mascara
    mask = cv2.inRange(lab, lower_piedra, upper_piedra)

    # operaciones morfologicas
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # mostrar imagen post-máscara
    # cv2.imshow("Post-mask", mask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # encontrar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = image.copy()
    total_piedras = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 1900:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)
        if circularity > 0.65 or circularity < 0.15:
            continue

        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            continue
        convexity_ratio = area / hull_area
        if convexity_ratio < 0.4:
            continue

        approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)
        vertices = len(approx)
        if vertices < 6 or vertices > 15:
            continue

        cv2.drawContours(result, [approx], -1, (0, 0, 255), 2)
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
        total_piedras += 1

    return result

# funcion para obtener el color predominante de una imagen (esto es para detectar si son frijoles pintos o negros)
def color_dominante(ruta_imagen, reduce_factor=8):
    # leer imagen y convertir a RGB
    img = cv2.imread(ruta_imagen)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # reducir tamano para procesamiento mas rapido
    h, w = img.shape[:2]
    img = cv2.resize(img, (w//reduce_factor, h//reduce_factor))

    # cuantizar colores (reducir paleta)
    quantized = (img // 32) * 32  # reduce a 8 niveles por canal (256/32=8)

    # calcular histograma 3D
    hist = np.zeros((8, 8, 8), dtype=int)
    for r in range(quantized.shape[0]):
        for c in range(quantized.shape[1]):
            b, g, r_col = quantized[r, c] // 32
            hist[b, g, r_col] += 1

    # encontrar el bin con mayor frecuencia
    max_bin = np.unravel_index(np.argmax(hist), hist.shape)

    # calcular color promedio del bin (punto medio del rango)
    color_rgb = [(i * 32 + 16) for i in max_bin[::-1]]  # invertir orden (R, G, B)

    return tuple(color_rgb)

def detectar_tipo(imagen_path):
    image = cv2.imread(imagen_path)
    if image is None:
        print("No se pudo cargar la imagen:", imagen_path)
        return
    
    # checar si la imagen es de frijoles pintos o negros usando el color predominante
    predominante = color_dominante(imagen_path)

    # si el predominante es menor a 200, entonces son negros, sino son pintos
    if sum(predominante) < 200:
        tipo = "Frijoles Negros"
    else:
        tipo = "Frijoles Pintos"

    print(tipo)

# para probar de manera rapida
# if __name__ == '__main__':
#     # detectar_piedras_pintos("/home/richy/Documents/frijoles/pintos/frijol2.jpg")
#     # imagen = detectar_piedras_pintos("/home/richy/Documents/frijoles/pintos/frijol2.jpg")
#     # imagen = detectar_piedras_pintos2("/home/richy/Documents/frijoles/pintos/frijol5.jpg")
#     imagen = detectar_piedras_negros("/home/richy/Documents/frijoles/negros/frijol2.jpg")
#     cv2.imshow('Detected Stones', imagen)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
