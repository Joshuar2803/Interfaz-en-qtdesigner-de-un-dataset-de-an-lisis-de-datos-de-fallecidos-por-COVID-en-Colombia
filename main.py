import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Importar módulos de PyQt6
from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QMessageBox, 
                            QFileDialog, QWidget, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

# Para resolver el problema de incompatibilidad entre matplotlib y PyQt6
# Usamos directamente el backend compatible con PyQt6
import matplotlib
matplotlib.use('QtAgg')  # Importante: establecer el backend antes de importar pyplot

# Importaciones condicionales para manejar los módulos externos
try:
    from ventana_analisis_avanzado import abrir_analisis_avanzado
    from analizador_epidemiologico import AnalizadorEpidemiologico

except ImportError:
    # Define funciones de reemplazo si no encuentras los módulos
    def abrir_analisis_avanzado(df):
        QMessageBox.warning(None, "Módulo no disponible", "El módulo de análisis avanzado no está disponible.")
    
    class AnalizadorEpidemiologico:
        def __init__(self, dataframe=None):
            self.df = dataframe

print("Directorio de trabajo actual:", os.getcwd())

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Cargar la interfaz UI
        uic.loadUi('appMain1.ui', self)
        
        # Conexión a los widgets
        self.cmb_sexo = self.findChild(QtWidgets.QComboBox, 'cmb_sexo')
        self.cmb_estado = self.findChild(QtWidgets.QComboBox, 'cmb_estado')
        self.sldEdad = self.findChild(QtWidgets.QSlider, 'sldEdad')
        self.lcdNumber = self.findChild(QtWidgets.QLCDNumber, 'lcdNumber')
        self.pushButton = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.tableView = self.findChild(QtWidgets.QTableView, 'tableView')
        
        # Crear un QWidget para reemplazar el graphicsView
        self.plot_container = QWidget(self)
        self.graphicsView = self.findChild(QtWidgets.QGraphicsView, 'graphicsView')
        geo = self.graphicsView.geometry()
        self.plot_container.setGeometry(geo)
        self.plot_layout = QVBoxLayout(self.plot_container)
        
        # Ocultar el graphicsView original
        self.graphicsView.hide()
        
        # Inicializar el gráfico
        self.initialize_plot()
        
        # Configurar menú
        self.setup_menu()
        
        # Conectar señales
        self.sldEdad.valueChanged.connect(self.actualizar_lcd)
        self.pushButton.clicked.connect(self.graficar)
        
        # Cargar datos y configurar controles
        self.cargar_datos()
        self.configurar_combos()
        self.configurar_slider()
        self.actualizar_tabla()
        
        # Crear analizador si hay datos
        if hasattr(self, 'df'):
            self.analizador = AnalizadorEpidemiologico(dataframe=self.df)
    
    def initialize_plot(self):
        """Crear y configurar el área de gráfico"""
        try:
            # Limpiar cualquier widget existente en el layout
            while self.plot_layout.count():
                item = self.plot_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Crear figura de matplotlib
            self.figure = plt.figure(figsize=(5, 4))
            
            # Usar el widget de matplotlib para Qt
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            self.canvas = FigureCanvasQTAgg(self.figure)
            
            # Añadir el canvas al layout
            self.plot_layout.addWidget(self.canvas)
            
            # Inicializar con un gráfico vacío
            self.ax = self.figure.add_subplot(111)
            self.ax.set_title('No hay datos para mostrar')
            self.ax.text(0.5, 0.5, 'Seleccione filtros y presione "Graficar"',
                       horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error al inicializar el gráfico: {e}")
            # En caso de error, crear un widget simple con un mensaje
            error_widget = QFrame(self.plot_container)
            error_layout = QVBoxLayout(error_widget)
            error_label = QtWidgets.QLabel(f"Error al crear gráfico: {str(e)}")
            error_layout.addWidget(error_label)
            self.plot_layout.addWidget(error_widget)
    
    def setup_menu(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        menu_archivo = menubar.addMenu('Archivo')
        
        # Acción: Abrir CSV
        accion_abrir = QtGui.QAction('Abrir CSV', self)
        accion_abrir.triggered.connect(self.abrir_csv)
        menu_archivo.addAction(accion_abrir)
        # Acción: Exportar datos filtrados
        accion_exportar = QtGui.QAction('Exportar datos filtrados', self)
        accion_exportar.triggered.connect(self.exportar_filtrados)
        menu_archivo.addAction(accion_exportar)

        # Acción: Salir
        accion_salir = QtGui.QAction('Salir', self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)
        
        # Menú Análisis
        menu_analisis = menubar.addMenu('Análisis')
        
        # Acción: Análisis Avanzado
        accion_avanzado = QtGui.QAction('Análisis Epidemiológico Avanzado', self)
        accion_avanzado.triggered.connect(self.abrir_analisis_avanzado)
        menu_analisis.addAction(accion_avanzado)
    
    def cargar_datos(self, dataset_csv=None):
        """Carga los datos desde el archivo CSV"""
        try:
            # Cargar el CSV, usar ruta proporcionada o valor predeterminado
            if dataset_csv:
                self.df = pd.read_csv(dataset_csv)
            else:
                self.df = pd.read_csv('dataset.csv')
            
            # Convertir columnas de fechas a formato datetime
            columnas_fecha = [col for col in self.df.columns if 'fecha' in col.lower()]
            for col in columnas_fecha:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                except:
                    pass  # Manejar columnas que no son de fecha
                    
            # Verificar si la columna 'edad' existe, si no, intenta crear una
            if 'Edad' not in self.df.columns:
                if 'medida de edad' in self.df.columns:
                    self.df['Edad'] = pd.to_numeric(self.df['medida de edad'], errors='coerce')
            
            print(f"Datos cargados correctamente. {len(self.df)} registros.")
            
            # Crear analizador una vez que tengamos los datos
            self.analizador = AnalizadorEpidemiologico(dataframe=self.df)
            
            # Actualizar componentes con los nuevos datos
            self.configurar_combos()
            self.configurar_slider()
            self.actualizar_tabla()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar los datos: {str(e)}")
            print(f"Error al cargar los datos: {e}")
            # Crear un DataFrame vacío con las columnas esperadas si hay un error
            self.df = pd.DataFrame(columns=['Fecha reporte web', 'Id de caso', 'Fecha de notificación',
                                           'Código divipola departamento', 'Nombre departamento',
                                           'Código divipola municipio', 'Nombre municipio', 'Edad',
                                           'Medida de edad', 'Sexo', 'Tipo de contagio',
                                           'Ubicación del caso', 'Estado', 'Código iso del país',
                                           'Nombre del país', 'Recuperado', 'Fecha de inicio de síntomas',
                                           'Fecha de muerte', 'fecha de diagnóstico', 'Fecha de recuperación',
                                           'Tipo de recuperación', 'Pertenencia étnica',
                                           'Nombre del grupo étnico'])
    
    def abrir_csv(self):
        """Abre un diálogo para seleccionar un archivo CSV"""
        # Corrección: No llamar a options(), usar directamente QFileDialog
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo CSV", "", "Archivos CSV (*.csv)"
        )
        
        if ruta_archivo:
            self.cargar_datos(ruta_archivo)
    
    def exportar_filtrados(self):
        """Exporta los datos filtrados a un nuevo archivo CSV"""
        if not hasattr(self, 'df') or self.df.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return
            
        # Aplicar filtros actuales
        df_filtrado = self.aplicar_filtros()
        
        # Diálogo para seleccionar ubicación de guardado
        # Corrección: No llamar a options(), usar directamente QFileDialog
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self, "Guardar datos filtrados",
            "", "Archivos CSV (*.csv)"
        )
        
        if ruta_archivo:
            try:
                # Asegurar que tenga extensión .csv
                if not ruta_archivo.lower().endswith('.csv'):
                    ruta_archivo += '.csv'
                    
                df_filtrado.to_csv(ruta_archivo, index=False)
                QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a {ruta_archivo}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar datos: {str(e)}")
    
    def configurar_combos(self):
        """Configura los ComboBoxes con los valores únicos de las columnas correspondientes"""
        if not hasattr(self, 'df'):
            return
            
        # Limpiar ComboBoxes antes de agregar nuevos elementos
        self.cmb_sexo.clear()
        self.cmb_estado.clear()
        
        # Configurar ComboBox de sexo
        if 'Sexo' in self.df.columns:
            valores_sexo = ['Todos'] + sorted(self.df['Sexo'].dropna().unique().tolist())
            self.cmb_sexo.addItems(valores_sexo)
        else:
            self.cmb_sexo.addItems(['N/A'])
        
        # Configurar ComboBox de estado
        if 'Nombre departamento' in self.df.columns:
            valores_estado = ['Todos'] + sorted(self.df['Nombre departamento'].dropna().unique().tolist())
            self.cmb_estado.addItems(valores_estado)
        else:
            self.cmb_estado.addItems(['N/A'])
    
    def configurar_slider(self):
        """Configura el slider de edad según los valores en el dataset"""
        if not hasattr(self, 'df'):
            return
            
        if 'Edad' in self.df.columns:
            edad_min = int(self.df['Edad'].min()) if not pd.isna(self.df['Edad'].min()) else 0 
            edad_max = int(self.df['Edad'].max()) if not pd.isna(self.df['Edad'].max()) else 100
            
            # Configurar el rango del slider
            self.sldEdad.setMinimum(edad_min)
            self.sldEdad.setMaximum(edad_max)
            self.sldEdad.setValue(edad_min)  # Valor inicial
            
            # Actualizar el LCD con el valor inicial
            self.lcdNumber.display(edad_min)
        else:
            # Si no hay columna de edad, deshabilitar el slider
            self.sldEdad.setEnabled(False)
    
    def actualizar_lcd(self, valor):
        """Actualiza el display LCD con el valor del slider"""
        self.lcdNumber.display(valor)
    
    def actualizar_tabla(self):
        """Actualiza la tabla con los datos filtrados"""
        if not hasattr(self, 'df'):
            return
            
        # Aplicar filtros
        df_filtrado = self.aplicar_filtros()
        
        # Crear modelo para la tabla
        model = QStandardItemModel()
        
        # Establecer encabezados de columnas
        model.setHorizontalHeaderLabels(df_filtrado.columns)
        
        # Llenar el modelo con datos
        for row in range(min(100, len(df_filtrado))):  # Limitar a 100 filas para mejor rendimiento
            for col in range(len(df_filtrado.columns)):
                value = str(df_filtrado.iloc[row, col])
                item = QStandardItem(value)
                model.setItem(row, col, item)
        
        # Asignar el modelo a la tabla
        self.tableView.setModel(model)
        self.tableView.resizeColumnsToContents()
    
    def aplicar_filtros(self):
        """Aplica los filtros seleccionados al DataFrame"""
        if not hasattr(self, 'df'):
            return pd.DataFrame()
            
        df_filtrado = self.df.copy()
        
        # Filtrar por sexo
        if self.cmb_sexo.currentText() != 'Todos' and 'Sexo' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Sexo'] == self.cmb_sexo.currentText()]
        
        # Filtrar por estado
        if self.cmb_estado.currentText() != 'Todos' and 'Nombre departamento' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Nombre departamento'] == self.cmb_estado.currentText()]
        
        # Filtrar por edad
        if 'Edad' in df_filtrado.columns and self.sldEdad.isEnabled():
            edad_seleccionada = self.sldEdad.value()
            df_filtrado = df_filtrado[df_filtrado['Edad'] >= edad_seleccionada]
        
        return df_filtrado
    
    def graficar(self):
        """Genera un gráfico basado en los datos filtrados"""
        if not hasattr(self, 'df'):
            QMessageBox.warning(self, "Advertencia", "No hay datos para graficar.")
            return
            
        try:
            df_filtrado = self.aplicar_filtros()
            
            # Limpiar la figura anterior
            self.figure.clear()
            
            # Crear un nuevo subplot
            ax = self.figure.add_subplot(111)
            
            # Intentar graficar por sexo
            if 'Sexo' in df_filtrado.columns and not df_filtrado['Sexo'].isna().all():
                conteo_sexo = df_filtrado['Sexo'].value_counts()
                conteo_sexo.plot(kind='bar', ax=ax)
                ax.set_title('Distribución por Sexo')
                ax.set_xlabel('Sexo')
                ax.set_ylabel('Cantidad')
            
            # Si no hay datos por sexo, intentar por estado
            elif 'Nombre departamento' in df_filtrado.columns and not df_filtrado['Nombre departamento'].isna().all():
                conteo_estado = df_filtrado['Nombre departamento'].value_counts()
                conteo_estado.plot(kind='bar', ax=ax)
                ax.set_title('Distribución por Estado')
                ax.set_xlabel('Nombre departamento')
                ax.set_ylabel('Cantidad')
            
            # Si ninguno de los anteriores está disponible
            else:
                ax.text(0.5, 0.5, 'No hay datos suficientes para graficar',
                       horizontalalignment='center', verticalalignment='center')
            
            # Ajustar el tamaño del gráfico y refrescar el canvas
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error al graficar: {e}")
            QMessageBox.warning(self, "Error", f"Error al generar el gráfico: {str(e)}")
    
    def abrir_analisis_avanzado(self):
        """Abre la ventana de análisis epidemiológico avanzado"""
        if not hasattr(self, 'df') or self.df.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos para analizar.")
            return
            
        # Abre la ventana de análisis avanzado
        abrir_analisis_avanzado(self.df)

# Punto de entrada de la aplicación
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())