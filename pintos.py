import cv2
import numpy as np

def detectar_piedritas_color_frijoles_pintos(image_path):
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
        # Rango de área ajustado para alta resolución
        if area < 1900:
            continue

        # Calcular circularidad
        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)

        # Filtro de forma combinado
        if circularity > 0.65 or circularity < 0.15:
            continue

        # Aproximación de polígono mejorada
        approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)
        vertices = len(approx)

        # Las piedras suelen tener formas más irregulares
        if vertices < 6 or vertices > 15:
            continue

        # Dibujar detecciones
        cv2.drawContours(result, [approx], -1, (0, 255, 0), 2)
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
        total_piedras += 1

    # Mostrar resultados
    print(f"Piedras detectadas: {total_piedras}")
    cv2.imshow("Piedritas - Frijoles Pintos (Filtrado Relajado)", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    detectar_piedritas_color_frijoles_pintos("/home/richy/Documents/frijoles/pintos/frijol1.jpg")
