import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QTabWidget,
    QPushButton, QFileDialog, QMessageBox, QSlider, QDialog, QHBoxLayout,
    QFormLayout, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from analizador_epidemiologico import AnalizadorEpidemiologico

class VentanaAnalisisAvanzado(QDialog):
    """Ventana para análisis epidemiológico avanzado"""
    def __init__(self, df, parent=None):
        super(VentanaAnalisisAvanzado, self).__init__(parent)
        self.df = df
        self.analizador = AnalizadorEpidemiologico(dataframe=df)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario para análisis avanzados"""
        self.setWindowTitle("Análisis Epidemiológico Avanzado")
        self.setMinimumSize(900, 700)  # Aumentamos el tamaño mínimo para mejor visualización
        
        # Layout principal
        layout_principal = QVBoxLayout(self)
        
        # Crear tabwidget para diferentes análisis
        self.tabs = QTabWidget()
        self.tab_incidencia = QtWidgets.QWidget()
        self.tab_distribucion = QtWidgets.QWidget()
        self.tab_mortalidad = QtWidgets.QWidget()
        
        self.tabs.addTab(self.tab_incidencia, "Incidencia")
        self.tabs.addTab(self.tab_distribucion, "Distribución")
        self.tabs.addTab(self.tab_mortalidad, "Mortalidad")
        
        # Nueva pestaña para análisis de fallecidos
        self.tab_fallecidos = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_fallecidos, "Análisis Fallecidos")
        self.setup_tab_fallecidos()
        
        # Configurar pestaña de incidencia
        self.setup_tab_incidencia()
        
        # Configurar pestaña de distribución
        self.setup_tab_distribucion()
        
        # Configurar pestaña de mortalidad
        self.setup_tab_mortalidad()
        
        # Agregar tabs al layout principal
        layout_principal.addWidget(self.tabs)
        
        # Botón para cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        layout_principal.addWidget(btn_cerrar)
        
        self.setLayout(layout_principal)
        
    def setup_tab_fallecidos(self):
        """Configura la pestaña de análisis de fallecidos"""
        layout = QVBoxLayout(self.tab_fallecidos)
        
        # Selector de tipo de gráfico
        self.cmb_tipo_fallecidos = QComboBox()
        self.cmb_tipo_fallecidos.addItems([
            "Resumen general",
            "Por departamento",
            "Distribución por edad",
            "Por tipo de contagio"
        ])
        
        # Botón de generación
        btn_generar = QPushButton("Generar Gráfico")
        btn_generar.clicked.connect(self.generar_grafico_fallecidos)
        
        # Área del gráfico
        self.figure_fallecidos = plt.figure(figsize=(10, 6))
        self.canvas_fallecidos = FigureCanvas(self.figure_fallecidos)
        self.canvas_fallecidos.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        
        # Organizar elementos
        layout.addWidget(QLabel("Seleccione el tipo de análisis:"))
        layout.addWidget(self.cmb_tipo_fallecidos)
        layout.addWidget(btn_generar)
        layout.addWidget(self.canvas_fallecidos)
        
        self.tab_fallecidos.setLayout(layout)
    
    def generar_grafico_fallecidos(self):
        """Genera los diferentes gráficos de fallecidos"""
        try:
            self.figure_fallecidos.clear()
            ax = self.figure_fallecidos.add_subplot(111)
            
            tipo = self.cmb_tipo_fallecidos.currentText()
            
            if tipo == "Resumen general":
                self.analizador.graficar_fallecidos(ax=ax)
            elif tipo == "Por departamento":
                self.analizador.graficar_fallecidos_por_departamento(ax=ax)
            elif tipo == "Distribución por edad":
                # Corrección: Llamar al método con el nombre correcto
                self.analizador.graficar_distribucion_Edad_fallecidos(ax=ax)
            elif tipo == "Por tipo de contagio":
                self.analizador.graficar_fallecidos_por_contagio(ax=ax)
            
            self.figure_fallecidos.tight_layout()  # Ajuste automático del layout
            self.canvas_fallecidos.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al generar gráfico: {str(e)}")
        
    def setup_tab_incidencia(self):
        """Configura la pestaña de análisis de incidencia"""
        layout = QVBoxLayout(self.tab_incidencia)
        
        # Opciones
        group_opciones = QGroupBox("Opciones de Incidencia")
        layout_opciones = QFormLayout()
        
        # ComboBox para seleccionar período
        self.cmb_periodo = QComboBox()
        self.cmb_periodo.addItems(["Diario (D)", "Semanal (W)", "Mensual (M)", "Anual (Y)"])
        self.cmb_periodo.setCurrentText("Mensual (M)")
        layout_opciones.addRow("Período:", self.cmb_periodo)
        
        # ComboBox para seleccionar columna de fecha
        self.cmb_columna_fecha = QComboBox()
        columnas_fecha = [col for col in self.df.columns if 'fecha' in col.lower()]
        self.cmb_columna_fecha.addItems(columnas_fecha)
        if 'fecha de diagnóstico' in columnas_fecha:
            self.cmb_columna_fecha.setCurrentText('fecha de diagnóstico')
        layout_opciones.addRow("Columna de fecha:", self.cmb_columna_fecha)
        
        # Botón para generar gráfico
        self.btn_generar_incidencia = QPushButton("Generar Gráfico de Incidencia")
        self.btn_generar_incidencia.clicked.connect(self.generar_grafico_incidencia)
        layout_opciones.addRow(self.btn_generar_incidencia)
        
        group_opciones.setLayout(layout_opciones)
        layout.addWidget(group_opciones)
        
        # Área para el gráfico
        self.figure_incidencia = plt.figure(figsize=(10, 6))
        self.canvas_incidencia = FigureCanvas(self.figure_incidencia)
        self.canvas_incidencia.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.canvas_incidencia)
        
        self.tab_incidencia.setLayout(layout)
        
    def setup_tab_distribucion(self):
        """Configura la pestaña de análisis de distribución"""
        layout = QVBoxLayout(self.tab_distribucion)
        
        # Opciones
        group_opciones = QGroupBox("Opciones de Distribución")
        layout_opciones = QFormLayout()
        
        # ComboBox para seleccionar columna de agrupación
        self.cmb_columna_grupo = QComboBox()
        columnas_grupo = ['Edad', 'Sexo', 'Estado', 'Nombre departamento', 'Nombre municipio']
        columnas_grupo = [col for col in columnas_grupo if col in self.df.columns]
        self.cmb_columna_grupo.addItems(columnas_grupo)
        layout_opciones.addRow("Agrupar por:", self.cmb_columna_grupo)
        
        # ComboBox para tipo de gráfico
        self.cmb_tipo_grafico = QComboBox()
        self.cmb_tipo_grafico.addItems(["Barras", "Pastel"])
        layout_opciones.addRow("Tipo de gráfico:", self.cmb_tipo_grafico)
        
        # Checkbox para usar bins (solo para edad)
        self.check_usar_bins = QtWidgets.QCheckBox("Usar rangos para edad")
        self.check_usar_bins.setChecked(True)
        layout_opciones.addRow(self.check_usar_bins)
        
        # Botón para generar gráfico
        self.btn_generar_distribucion = QPushButton("Generar Gráfico de Distribución")
        self.btn_generar_distribucion.clicked.connect(self.generar_grafico_distribucion)
        layout_opciones.addRow(self.btn_generar_distribucion)
        
        group_opciones.setLayout(layout_opciones)
        layout.addWidget(group_opciones)
        
        # Área para el gráfico
        self.figure_distribucion = plt.figure(figsize=(10, 6))
        self.canvas_distribucion = FigureCanvas(self.figure_distribucion)
        self.canvas_distribucion.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.canvas_distribucion)
        
        self.tab_distribucion.setLayout(layout)
        
    def setup_tab_mortalidad(self):
        """Configura la pestaña de análisis de mortalidad"""
        layout = QVBoxLayout(self.tab_mortalidad)
        
        # Opciones
        group_opciones = QGroupBox("Opciones de Mortalidad")
        layout_opciones = QFormLayout()
        
        # ComboBox para seleccionar columna de agrupación
        self.cmb_columna_mort = QComboBox()
        columnas_grupo = ['General', 'Edad', 'sexo', 'Nombre departamento']
        self.cmb_columna_mort.addItems(columnas_grupo)
        layout_opciones.addRow("Agrupar por:", self.cmb_columna_mort)
        
        # Checkbox para usar bins (solo para edad)
        self.check_usar_bins_mort = QtWidgets.QCheckBox("Usar rangos para edad")
        self.check_usar_bins_mort.setChecked(True)
        layout_opciones.addRow(self.check_usar_bins_mort)
        
        # Botón para generar gráfico
        self.btn_generar_mortalidad = QPushButton("Generar Gráfico de Mortalidad")
        self.btn_generar_mortalidad.clicked.connect(self.generar_grafico_mortalidad)
        layout_opciones.addRow(self.btn_generar_mortalidad)
        
        group_opciones.setLayout(layout_opciones)
        layout.addWidget(group_opciones)
        
        # Área para el gráfico
        self.figure_mortalidad = plt.figure(figsize=(10, 6))
        self.canvas_mortalidad = FigureCanvas(self.figure_mortalidad)
        self.canvas_mortalidad.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.canvas_mortalidad)
        
        self.tab_mortalidad.setLayout(layout)
    
    def generar_grafico_incidencia(self):
        """Genera el gráfico de incidencia según las opciones seleccionadas"""
        try:
            # Obtener opciones seleccionadas
            periodo_texto = self.cmb_periodo.currentText()
            periodo = periodo_texto.split("(")[1].split(")")[0]  # Extraer D, W, M o Y
            columna_fecha = self.cmb_columna_fecha.currentText()
            
            # Limpiar figura actual
            self.figure_incidencia.clear()
            ax = self.figure_incidencia.add_subplot(111)
            
            # Generar gráfico
            self.analizador.graficar_incidencia(periodo=periodo, columna_fecha=columna_fecha, ax=ax)
            
            # Ajustar automáticamente el layout
            self.figure_incidencia.tight_layout()
            
            # Actualizar canvas
            self.canvas_incidencia.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al generar gráfico: {str(e)}")
    
    def generar_grafico_distribucion(self):
        """Genera el gráfico de distribución según las opciones seleccionadas"""
        try:
            # Obtener opciones seleccionadas
            columna_grupo = self.cmb_columna_grupo.currentText()
            tipo_grafico = 'pie' if self.cmb_tipo_grafico.currentText() == "Pastel" else 'bar'
            usar_bins = self.check_usar_bins.isChecked() and columna_grupo == 'Edad'
            
            # Configurar bins si es necesario
            bins = None
            if usar_bins:
                bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 120]
            
            # Limpiar figura actual
            self.figure_distribucion.clear()
            ax = self.figure_distribucion.add_subplot(111)
            
            # Generar gráfico
            self.analizador.graficar_distribucion_por_grupo(
                columna_grupo=columna_grupo, 
                bins=bins,
                tipo_grafico=tipo_grafico,
                ax=ax
            )
            
            # Ajustar automáticamente el layout
            self.figure_distribucion.tight_layout()
            
            # Actualizar canvas
            self.canvas_distribucion.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al generar gráfico: {str(e)}")
    
    def generar_grafico_mortalidad(self):
        """Genera el gráfico de mortalidad según las opciones seleccionadas"""
        try:
            # Obtener opciones seleccionadas
            columna_mort = self.cmb_columna_mort.currentText()
            columna_mort = None if columna_mort == 'General' else columna_mort
            usar_bins = self.check_usar_bins_mort.isChecked() and columna_mort == 'edad'
            
            # Configurar bins si es necesario
            bins = None
            if usar_bins:
                bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 120]
            
            # Limpiar figura actual
            self.figure_mortalidad.clear()
            ax = self.figure_mortalidad.add_subplot(111)
            
            # Generar gráfico
            self.analizador.graficar_tasa_mortalidad(
                por_grupo=columna_mort, 
                bins=bins,
                ax=ax
            )
            
            # Ajustar automáticamente el layout
            self.figure_mortalidad.tight_layout()
            
            # Actualizar canvas
            self.canvas_mortalidad.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al generar gráfico: {str(e)}")

# Esta clase se puede usar en main_app.py añadiendo un botón para abrir el análisis avanzado
def abrir_analisis_avanzado(df):
    """Función para abrir la ventana de análisis avanzado desde la aplicación principal"""
    ventana = VentanaAnalisisAvanzado(df)
    ventana.exec()