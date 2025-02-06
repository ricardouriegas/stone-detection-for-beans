import cv2
import numpy as np

def detectar_piedras_negros(imagen_path):
    # Cargar la imagen
    imagen = cv2.imread(imagen_path)
    imagen = cv2.resize(imagen, (0, 0), fx=0.5, fy=0.5)  # Reduce size by half
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definir rangos de colores en HSV
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

    # Mostrar la imagen resultante
    cv2.imshow('Piedras Detectadas', resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return resultado

# Ejecutar detección
if __name__ == '__main__':
    detectar_piedras_negros("/home/richy/Documents/frijoles/negros/frijol2.jpg")
