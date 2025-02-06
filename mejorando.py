import cv2
import numpy as np

def procesar_imagen_mejorado(ruta_imagen):
    # Cargar y redimensionar
    img = cv2.imread(ruta_imagen)
    img = cv2.resize(img, (756, 1008))  # Mantenemos el tamaño para procesamiento
    
    # 1. Preprocesamiento en HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Ecualización en canal V (mejor que CLAHE para texturas)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    v_eq = clahe.apply(v)
    
    # Fusionar canales actualizados
    hsv_eq = cv2.merge([h, s, v_eq])
    
    # 2. Segmentación mejorada
    # Usamos canal S para detectar suciedad/Textura
    _, thresh_s = cv2.threshold(s, 40, 255, cv2.THRESH_BINARY_INV)
    
    # Umbral adaptativo en V ecualizado
    thresh_v = cv2.adaptiveThreshold(v_eq, 255, 
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 31, 7)
    
    # Combinar máscaras
    combinado = cv2.bitwise_or(thresh_s, thresh_v)
    
    # Operaciones morfológicas avanzadas
    kernel_eliptico = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    kernel_rect = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    
    # Secuencia: abrir -> cerrar -> dilatar
    morfo = cv2.morphologyEx(combinado, cv2.MORPH_OPEN, kernel_eliptico, iterations=2)
    morfo = cv2.morphologyEx(morfo, cv2.MORPH_CLOSE, kernel_rect, iterations=3)
    morfo = cv2.dilate(morfo, kernel_rect, iterations=1)
    
    # 3. Análisis de contornos
    contornos, _ = cv2.findContours(morfo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrado inicial por área y relación de aspecto
    contornos_filtrados = []
    for cnt in contornos:
        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        relacion_aspecto = max(w/h, h/w)
        
        if area > 150 and relacion_aspecto < 3.5:
            contornos_filtrados.append(cnt)
    
    # 4. Análisis multivariable
    for cnt in contornos_filtrados:
        # Geometría
        area = cv2.contourArea(cnt)
        perimetro = cv2.arcLength(cnt, True)
        x,y,w,h = cv2.boundingRect(cnt)
        
        # Máscara ROI
        mascara = np.zeros_like(v_eq)
        cv2.drawContours(mascara, [cnt], -1, 255, -1)
        
        # Análisis de forma
        circularidad = (4 * np.pi * area) / (perimetro**2 + 1e-6)
        casco = cv2.convexHull(cnt)
        convexidad = area / cv2.contourArea(casco)
        relacion_aspecto = max(w/h, h/w)
        
        # Análisis de textura (HSV + V ecualizado)
        # 1. Variación en canal S (suciedad)
        _, std_s = cv2.meanStdDev(s, mask=mascara)
        
        # 2. Energía de textura en V
        sobel_v = cv2.Sobel(v_eq, cv2.CV_64F, 1, 1, ksize=5)
        textura_sobel = np.var(sobel_v[mascara == 255])
        
        # 3. Entropía de histograma en ROI
        hist = cv2.calcHist([v_eq], [0], mascara, [256], [0,256])
        hist = hist / hist.sum() + 1e-6
        entropia = -np.sum(hist * np.log2(hist))
        
        # Clasificación con umbrales ajustados
        es_piedra = False
        criterios = [
            circularidad < 0.65,          # Piedras menos circulares
            convexidad < 0.82,            # Menos convexas
            textura_sobel > 300,          # Textura más rugosa
            std_s > 25,                   # Mayor variación en saturación (tierra)
            entropia > 6.5                # Mayor complejidad textural
        ]
        
        # Sistema de votación ponderado
        peso_criterios = [1.5, 1.2, 2.0, 1.7, 1.5]  # Priorizamos textura
        score = sum([c * p for c, p in zip(criterios, peso_criterios)])
        
        if score >= 4.0:
            es_piedra = True
        
        # Visualización
        color = (0, 0, 255) if es_piedra else (0, 255, 0)
        cv2.drawContours(img, [cnt], -1, color, 2)
        cv2.putText(img, f"S:{std_s[0][0]:.1f}", (x, y-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,0), 1)
    
    # Nuevo: Calcular y mostrar la variación en la saturación
    ksize = 5
    s_float = s.astype(np.float32)
    mean_s = cv2.boxFilter(s_float, ddepth=-1, ksize=(ksize, ksize), borderType=cv2.BORDER_REFLECT)
    mean_sq = cv2.boxFilter(s_float * s_float, ddepth=-1, ksize=(ksize, ksize), borderType=cv2.BORDER_REFLECT)
    std = cv2.sqrt(mean_sq - mean_s * mean_s)
    std_norm = cv2.normalize(std, None, 0, 255, cv2.NORM_MINMAX)
    std_norm = np.uint8(std_norm)
    cv2.imshow("Saturation Variation", std_norm)
    
    return img

# Uso
resultado = procesar_imagen_mejorado('/home/richy/Documents/frijoles/pintos/frijol1.jpg')
cv2.imshow('Deteccion Mejorada', resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()