import cv2
import numpy as np

def detectar_piedras_negros(imagen_path):
    # cargar la imagen
    imagen = cv2.imread(imagen_path)
    imagen = cv2.resize(imagen, (0, 0), fx=0.5, fy=0.5)  # Reduce size by half
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # definir rangos de colores en HSV
    colores_hex = ["#FCFFEE", "#FFF1E5", "#AB8683"]
    colores_hsv = [
        (25, 5, 235), (15, 20, 255),  # Aproximación de #FCFFEE y #FFF1E5 en HSV
        (5, 50, 170)  # Aproximación de #AB8683 en HSV
    ]

    # Máscaras para cada color
    mask_total = np.zeros(imagen.shape[:2], dtype=np.uint8)
    for hsv_color in colores_hsv:
        lower_bound = np.array([hsv_color[0] - 10, max(hsv_color[1] - 40, 0), max(hsv_color[2] - 40, 0)])
        upper_bound = np.array([hsv_color[0] + 10, min(hsv_color[1] + 40, 255), min(hsv_color[2] + 40, 255)])

        mask = cv2.inRange(imagen_hsv, lower_bound, upper_bound)
        mask_total = cv2.bitwise_or(mask_total, mask)

    kernel = np.ones((5, 5), np.uint8)
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, kernel)  # Remove small spots
    mask_total = cv2.morphologyEx(mask_total, cv2.MORPH_CLOSE, kernel)  # Close gaps in background

    # Encontrar contornos de las piedras detectadas
    contornos, _ = cv2.findContours(mask_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar contornos sobre la imagen original
    resultado = imagen.copy()

    filtered_contours = []
    for c in contornos:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        if 1350 < area < 8000:  # Discard tiny contours and very large background
            filtered_contours.append(c)

    cv2.drawContours(resultado, filtered_contours, -1, (0, 0, 255), 2)

    # Eliminar la apertura de ventana para mostrar la imagen
    # cv2.imshow('Piedras Detectadas', resultado)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return resultado

def detectar_piedras_pintos(image_path):
    # Cargar la imagen
    image = cv2.imread(image_path)
    if image is None:
        print("No se pudo cargar la imagen:", image_path)
        return

    # Convertir a LAB (mejor para diferenciar colores similares)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Rangos de color ajustados para piedras (incluyendo #404038)
    lower_piedra = np.array([15, 115, 115])   # L mínimo reducido
    upper_piedra = np.array([75, 145, 145])   # L máximo aumentado

    # Crear máscara
    mask = cv2.inRange(lab, lower_piedra, upper_piedra)

    # Operaciones morfológicas mejoradas
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)

    # Encontrar contornos
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

        approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)
        vertices = len(approx)

        if vertices < 6 or vertices > 15:
            continue

        # Usar mismo formato que en detectar_piedras_negros: contorno y rectángulo en rojo
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

    # reducir tamaño para procesamiento más rápido
    h, w = img.shape[:2]
    img = cv2.resize(img, (w//reduce_factor, h//reduce_factor))

    # cuantizar colores (reducir paleta)
    quantized = (img // 32) * 32  # Reduce a 8 niveles por canal (256/32=8)

    # calcular histograma 3D
    hist = np.zeros((8, 8, 8), dtype=int)
    for r in range(quantized.shape[0]):
        for c in range(quantized.shape[1]):
            b, g, r_col = quantized[r, c] // 32
            hist[b, g, r_col] += 1

    # encontrar el bin con mayor frecuencia
    max_bin = np.unravel_index(np.argmax(hist), hist.shape)

    # calcular color promedio del bin (punto medio del rango)
    color_rgb = [(i * 32 + 16) for i in max_bin[::-1]]  # Invertir orden (R, G, B)

    return tuple(color_rgb)

def detectar_piedras(imagen_path):
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

if __name__ == '__main__':
    detectar_piedras("/home/richy/Documents/frijoles/pintos/frijol1.jpg")
