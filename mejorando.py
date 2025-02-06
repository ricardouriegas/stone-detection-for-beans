import cv2
import numpy as np

def procesar_imagen(ruta_imagen):
    # Cargar imagen y redimensionar
    img = cv2.imread(ruta_imagen)
    img = cv2.resize(img, (756, 1008))  # Reducción para mejor procesamiento
    
    # 1. Preprocesamiento
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (7, 7), 2)
    
    # Ecualización adaptativa
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gris_eq = clahe.apply(gris)
    
    # 2. Segmentación
    thresh = cv2.adaptiveThreshold(gris_eq, 255, 
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 21, 5)
    
    # Operaciones morfológicas
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    morfo = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Detección de bordes
    bordes = cv2.Canny(gris_eq, 30, 150)
    combinado = cv2.bitwise_or(morfo, bordes)
    # imprimir bordes detectados
    cv2.imshow('Bordes', combinado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Encontrar contornos
    contornos, _ = cv2.findContours(combinado, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtro por tamaño mínimo
    contornos = [c for c in contornos if cv2.contourArea(c) > 100]
    
    # 3. Análisis de forma y textura
    for cnt in contornos:
        # Geometría básica
        area = cv2.contourArea(cnt)
        perimetro = cv2.arcLength(cnt, True)
        bbox = cv2.boundingRect(cnt)
        
        # Relación de aspecto
        relacion_aspecto = max(bbox[2]/bbox[3], bbox[3]/bbox[2])
        
        # Circularidad
        circularidad = (4 * np.pi * area) / (perimetro**2 + 1e-6)
        
        # Convexidad
        casco = cv2.convexHull(cnt)
        area_casco = cv2.contourArea(casco)
        convexidad = area / (area_casco + 1e-6)
        
        # ROI para textura
        mascara = np.zeros_like(gris)
        cv2.drawContours(mascara, [cnt], -1, 255, -1)
        
        # Análisis de textura (Laplaciano)
        laplaciano = cv2.Laplacian(gris_eq, cv2.CV_64F, ksize=3)
        textura_var = np.var(laplaciano[mascara == 255])
        
        # Análisis de intensidad
        _, std_dev = cv2.meanStdDev(gris_eq, mask=mascara)
        std_dev = std_dev[0,0]
        
        # Clasificación
        es_piedra = False
        criterios = [
            circularidad < 0.6,          # Piedras menos circulares
            convexidad < 0.85,           # Piedras menos convexas
            textura_var > 150,           # Mayor variación textural
            std_dev > 25                 # Mayor dispersión de intensidad
        ]
        
        if sum(criterios) >= 3:
            es_piedra = True
        
        # Dibujar resultados
        color = (0, 0, 255) if es_piedra else (0, 255, 0)
        grosor = 2 if es_piedra else 1
        cv2.drawContours(img, [cnt], -1, color, grosor)
        cv2.putText(img, f"C:{circularidad:.2f}", (bbox[0], bbox[1]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,0), 1)
    
    return img

# Ejemplo de uso
resultado = procesar_imagen('/home/richy/Documents/frijoles/pintos/frijol1.jpg')
cv2.imshow('Resultado', resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()