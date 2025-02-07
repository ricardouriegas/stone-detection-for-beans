"""
Template: Marco Aurelio Nuño Maganda
Author: Ricardo Emmanuel Uriegas Ibarra - 2230122

Requirements:
pip3 install pyqt6
pip3 install opencv-python
pip3 install opencv-python-headless numpy

Version verification:
pip3 show pyqt6
pip3 show opencv-python

Run:
python3 main.py

"""


import functions # archivo functions.py con las funciones para el procesamiento de la imagen

from ast import literal_eval as make_tuple
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
)
from PyQt6.QtGui import QFont
import cv2

class MiEtiqueta(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()      
        self.Lista=[]
        self.setStyleSheet("border: 1px solid black;")

    clicked = pyqtSignal()

    def mousePressEvent(self, e):
        self.x = e.position().x()
        self.y = e.position().y()
        #self.center = e.pos()
        #self.Lista.append(e.pos())
        #print (type(e.pos()), str(self.x)+","+str(self.y))
        #self.Lista.append([self.x,self.y])
        self.Lista.append((self.x,self.y) )
        
        print (self.Lista)
        self.clicked.emit()


class Window(QtWidgets.QWidget):

    def undoCircle(self):
        # Check if there is a circle to remove
        if not self.viewer.Lista:
            QtWidgets.QMessageBox.information(self, 'Info', "No more circles to remove.")
            return
        # Remove the last point added
        self.viewer.Lista.pop()
        # Reload the original image
        self.OpenCV_image = cv2.imread(self._path)
        if self.OpenCV_image is None:
            QtWidgets.QMessageBox.warning(self, 'Error', f"Could not load image file: {self._path}")
            return
        tamano = (self.viewer.size().width(), self.viewer.size().height())
        self.OpenCV_image = cv2.resize(self.OpenCV_image, tamano, interpolation=cv2.INTER_LINEAR)
        # Redraw circles for remaining points
        for point in self.viewer.Lista:
            ii = tuple(int(x) for x in point)
            self.OpenCV_image = cv2.circle(self.OpenCV_image, ii, 10, (255,255,0), 4)
        self.ActualizarPixMap()

    def Metodo (self):
        # Validación: confirmar que la imagen esté cargada
        if not hasattr(self, "OpenCV_image") or self.OpenCV_image is None:
            QtWidgets.QMessageBox.warning(self, 'Error', "Image not loaded.")
            return
        r=1
        for i in self.viewer.Lista:
            ii = tuple(int(x) for x in i)
            self.OpenCV_image = cv2.circle(self.OpenCV_image,ii,10,(255,255,0),4 ) 
        self.ActualizarPixMap()

    def center(self):
        """
        Centra la Ventada SI o SI
        """
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()

        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def __init__(self):
        super().__init__()
        self.setGeometry(10, 10, 900,600)
        self.center()
    
        self._path = None
        self.LastPoint = None

        self.viewer =MiEtiqueta ()
        self.viewer2 =MiEtiqueta ()
        self.viewer.clicked.connect(self.Metodo)
        
        self.buttonOpen = QtWidgets.QPushButton("Abrir Imagen")
        BUTTON_SIZE = QSize(200, 50)
        self.buttonOpen.setMinimumSize(BUTTON_SIZE)
        self.buttonOpen.clicked.connect(self.handleOpen)

        self.elements = []
        
        self.procesarImagenEntrada =  QtWidgets.QPushButton("Procesar")
        self.procesarImagenEntrada.setMinimumSize(BUTTON_SIZE)
        self.procesarImagenEntrada.clicked.connect(self.ProcesarImage)

        self.guardarImagen =  QtWidgets.QPushButton("Guardar")
        self.guardarImagen.setMinimumSize(BUTTON_SIZE)
        self.guardarImagen.clicked.connect(self.handleSaveFile)


        layout = QtWidgets.QGridLayout(self)
        self.botonProcesaReservado = QtWidgets.QPushButton("Reservado")
        #self.botonProcesaReservado.setText("Marker Ratio")
        #self.botonProcesaReservado.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.botonProcesaReservado.setMinimumSize(BUTTON_SIZE)
        # Connect the "Reservado" button to undoCircle (ctrl+z behavior)
        self.botonProcesaReservado.clicked.connect(self.undoCircle)

        layout.addWidget(self.buttonOpen, 0, 0, 1, 1)
        layout.addWidget(self.guardarImagen, 0, 3, 1, 1)
        layout.addWidget(self.botonProcesaReservado, 0, 2, 1, 1)
        layout.addWidget(self.procesarImagenEntrada, 0, 1, 1, 1)

        layout.addWidget(self.viewer, 1, 0, 1, 2)
        layout.addWidget(self.viewer2, 1, 2, 1, 2)

        #layout.addWidget(QPushButton("X"), 3, 0, 1, 4)
        #layout.addWidget(QLabel("X"), 3, 0, 1, 4)
                
        #layout.setColumnStretch(0, 4)
        #layout.setColumnStretch(1, 4)
        #layout.setColumnStretch(2, 4)

        Tamano=(self.viewer.size().width(),self.viewer.size().height())
        
        print (self.viewer.size(),type(self.viewer.size()),Tamano)

    def ActualizarPixMap (self):
        QImageTemp = QtGui.QImage(cv2.cvtColor(self.OpenCV_image, cv2.COLOR_BGR2RGB), self.OpenCV_image.shape[1],self.OpenCV_image.shape[0], self.OpenCV_image.shape[1] * 3,QtGui.QImage.Format.Format_RGB888)

        pixmap = QtGui.QPixmap(QImageTemp)
        self.viewer.setPixmap(pixmap)

    def MyMouseClickedOnListViewXX (self,e):
        IndiceCliqueado=self.ListView.currentIndex().row()
        if (self.elements[IndiceCliqueado].filed):
            self.elements[IndiceCliqueado].filed=False
        else:
            self.elements[IndiceCliqueado].filed=True

        # Actualizar la vista
       #self.ActualizarImagen()

    def ProcesarImage(self):
        # Validación: confirmar que se haya abierto una imagen
        if not self._path:
            QtWidgets.QMessageBox.warning(self, 'Error', "No image file opened.")
            return
        predominante = functions.color_dominante(self._path)
        if sum(predominante) < 200:
            self.procesedImage = functions.detectar_piedras_negros(self._path)
        else:
            self.procesedImage = functions.detectar_piedras_pintos(self._path)

        # mostrar la imagen procesada en el recuadro derecho y adaptando su tamano
        self.ActualizarPixMap2(self.procesedImage)
        
    def ActualizarPixMap2(self, image):
        # Validación: confirmar que la imagen procesada no esté vacía
        if image is None:
            QtWidgets.QMessageBox.warning(self, 'Error', "Processed image is empty.")
            return
        # Redimensiona la imagen procesada para que tenga el mismo tamano que viewer2
        tamano = (self.viewer2.size().width(), self.viewer2.size().height())
        image_resized = cv2.resize(image, tamano, interpolation=cv2.INTER_LINEAR)
        QImageTemp = QtGui.QImage(cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB),
                                  image_resized.shape[1],
                                  image_resized.shape[0],
                                  image_resized.shape[1] * 3,
                                  QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap(QImageTemp)
        self.viewer2.setPixmap(pixmap)
    
    def handleSaveFile(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "Images(*.jpg *.png)")
        # Validación: confirmar que se haya especificado un nombre de archivo y que exista imagen procesada
        if not fileName:
            QtWidgets.QMessageBox.warning(self, 'Error', "No file name specified.")
            return
        if not hasattr(self, 'procesedImage') or self.procesedImage is None:
            QtWidgets.QMessageBox.warning(self, 'Error', "No processed image to save.")
            return
        print (fileName)
        cv2.imwrite(fileName,self.procesedImage)


    def handleOpen(self):
        start="."

        path = QtWidgets.QFileDialog.getOpenFileName(self, "Choose File", start, "Images(*.jpg *.png)")[0]
        # Validación: confirmar que se haya seleccionado un archivo
        if not path:
            QtWidgets.QMessageBox.warning(self, 'Error', "No file selected.")
            return
        self.FilePath = path+".txt"
        self._path = path

        self.ActualizarImagen()

    def ActualizarImagen (self):

        self.OpenCV_image = cv2.imread(self._path)
        # Validación: confirmar que la imagen se haya cargado
        if self.OpenCV_image is None:
            QtWidgets.QMessageBox.warning(self, 'Error', f"Could not load image file: {self._path}")
            return
        Tamano=(self.viewer.size().width(),self.viewer.size().height())
        print (self.viewer.size(),type(self.viewer.size()),Tamano)           
        self.OpenCV_image = cv2.resize(self.OpenCV_image, Tamano, interpolation = cv2.INTER_LINEAR)

        #for i in self.viewer.Lista:
        #    print (i)


        QImageTemp = QtGui.QImage(cv2.cvtColor(self.OpenCV_image, cv2.COLOR_BGR2RGB), self.OpenCV_image.shape[1],self.OpenCV_image.shape[0], self.OpenCV_image.shape[1] * 3,QtGui.QImage.Format.Format_RGB888)

        pixmap = QtGui.QPixmap(QImageTemp)
        self.viewer.setPixmap(pixmap)
        self.viewer2.setPixmap(pixmap)
        


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("---")
    window.show()
    sys.exit(app.exec())