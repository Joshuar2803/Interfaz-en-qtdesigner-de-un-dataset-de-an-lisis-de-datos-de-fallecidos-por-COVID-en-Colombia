import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

class AnalizadorEpidemiologico:
    """
    Clase para realizar análisis epidemiológicos especializados sobre el dataset.
    Esta clase complementa la aplicación principal añadiendo funcionalidades
    de análisis más avanzadas.
    """
    
    def __init__(self, dataframe=None, ruta_csv=None):
        """
        Inicializa el analizador con un DataFrame existente o cargándolo desde un CSV
        
        Args:
            dataframe (pandas.DataFrame, opcional): DataFrame existente
            ruta_csv (str, opcional): Ruta al archivo CSV para cargar
        """
        if dataframe is not None:
            self.df = dataframe
        elif ruta_csv is not None:
            self.df = pd.read_csv('dataset.csv')
            self._procesar_fechas()
        else:
            self.df = pd.DataFrame()
            
    # Añadir estos métodos dentro de la clase AnalizadorEpidemiologico

    def _procesar_fechas(self):
        """Convierte columnas de fechas a formato datetime"""
        columnas_fecha = [col for col in self.df.columns if 'fecha' in col.lower()]
        for col in columnas_fecha:
            try:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            except:
                pass
    
    def calcular_incidencia_por_periodo(self, periodo='M', columna_fecha='Fecha de diagnóstico'):
        """
        Calcula la incidencia de casos por período de tiempo
        
        Args:
            periodo (str): Período para agrupar ('D': diario, 'W': semanal, 'M': mensual)
            columna_fecha (str): Columna de fecha a utilizar
            
        Returns:
            pandas.Series: Serie con la incidencia por período
        """
        if columna_fecha not in self.df.columns:
            raise ValueError(f"La columna {columna_fecha} no existe en el DataFrame")
            
        # Agrupar por período y contar casos
        incidencia = self.df.groupby(pd.Grouper(key=columna_fecha, freq=periodo)).size()
        return incidencia
    
    def graficar_incidencia(self, periodo='M', columna_fecha='fecha de diagnóstico', ax=None):
        """
        Genera un gráfico de incidencia a lo largo del tiempo
        
        Args:
            periodo (str): Período para agrupar ('D': diario, 'W': semanal, 'M': mensual)
            columna_fecha (str): Columna de fecha a utilizar
            ax (matplotlib.axes, opcional): Axes donde graficar
            
        Returns:
            matplotlib.axes: Axes con el gráfico
        """
        incidencia = self.calcular_incidencia_por_periodo(periodo, columna_fecha)
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        incidencia.plot(kind='line', marker='o', ax=ax)
        
        # Configurar etiquetas y título
        titulo_periodo = {'D': 'Diaria', 'W': 'Semanal', 'M': 'Mensual', 'Y': 'Anual'}
        ax.set_title(f'Incidencia {titulo_periodo.get(periodo, "")} de Casos')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Número de Casos')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        return ax
    
    def calcular_distribucion_por_grupo(self, columna_grupo='Edad', bins=None):
        """
        Calcula la distribución de casos por grupos (ej. Edad, Sexo)
        
        Args:
            columna_grupo (str): Columna para agrupar
            bins (list, opcional): Bins para agrupar variables numéricas
            
        Returns:
            pandas.Series: Serie con la distribución por grupo
        """
        if columna_grupo not in self.df.columns:
            raise ValueError(f"La columna {columna_grupo} no existe en el DataFrame")
        
        # Para variables numéricas como Edad, podemos usar bins
        if bins is not None and pd.api.types.is_numeric_dtype(self.df[columna_grupo]):
            # Crear grupos de Edad
            etiquetas = [f'{bins[i]}-{bins[i+1]-1}' for i in range(len(bins)-1)]
            self.df['grupo_' + columna_grupo] = pd.cut(
                self.df[columna_grupo], 
                bins=bins,
                labels=etiquetas, 
                right=False
            )
            distribucion = self.df['grupo_' + columna_grupo].value_counts().sort_index()
        else:
            # Para variables categóricas
            distribucion = self.df[columna_grupo].value_counts()
        
        return distribucion
    
    def graficar_distribucion_por_grupo(self, columna_grupo='Edad', bins=None, tipo_grafico='bar', ax=None):
        """
        Genera un gráfico de distribución por grupos
        
        Args:
            columna_grupo (str): Columna para agrupar
            bins (list, opcional): Bins para agrupar variables numéricas
            tipo_grafico (str): Tipo de gráfico ('bar', 'pie')
            ax (matplotlib.axes, opcional): Axes donde graficar
            
        Returns:
            matplotlib.axes: Axes con el gráfico
        """
        distribucion = self.calcular_distribucion_por_grupo(columna_grupo, bins)
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        if tipo_grafico == 'pie':
            distribucion.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
        else:
            distribucion.plot(kind='bar', ax=ax)
            ax.set_xlabel(columna_grupo.capitalize())
            ax.set_ylabel('Número de Casos')
            
        ax.set_title(f'Distribución de Casos por {columna_grupo.capitalize()}')
        
        return ax
    
    def calcular_tasa_mortalidad(self, por_grupo=None, bins=None):
        """
        Calcula la tasa de mortalidad general o por grupos
        
        Args:
            por_grupo (str, opcional): Columna para agrupar la tasa de mortalidad
            bins (list, opcional): Bins para agrupar variables numéricas
            
        Returns:
            float o pandas.Series: Tasa de mortalidad
        """
        # Verificar si hay columnas para identificar muertes
        if 'Estado' not in self.df.columns:
            raise ValueError("No hay columna 'Estado' para identificar muertes")
            
        # Contar casos y muertes
        total_casos = len(self.df)
        muertes = self.df[self.df['Estado'].str.contains('Fallecido', case=False, na=False)].copy()
        total_muertes = len(muertes)
        
        # Calcular tasa general
        if por_grupo is None:
            return (total_muertes / total_casos) * 100
        
        # Calcular tasa por grupos
        if por_grupo not in self.df.columns:
            raise ValueError(f"La columna {por_grupo} no existe en el DataFrame")
            
        # Para variables numéricas como Edad, podemos usar bins
        if bins is not None and pd.api.types.is_numeric_dtype(self.df[por_grupo]):
            # Crear grupos
            etiquetas = [f'{bins[i]}-{bins[i+1]-1}' for i in range(len(bins)-1)]
            self.df['grupo_' + por_grupo] = pd.cut(
                self.df[por_grupo], 
                bins=bins,
                labels=etiquetas, 
                right=False
            )
            muertes['grupo_' + por_grupo] = pd.cut(
                muertes[por_grupo], 
                bins=bins,
                labels=etiquetas, 
                right=False
            )
            
            # Contar casos por grupo
            casos_por_grupo = self.df['grupo_' + por_grupo].value_counts().sort_index()
            muertes_por_grupo = muertes['grupo_' + por_grupo].value_counts().sort_index()
            
            # Asegurar que todos los grupos estén presentes
            for grupo in casos_por_grupo.index:
                if grupo not in muertes_por_grupo:
                    muertes_por_grupo[grupo] = 0
            
            muertes_por_grupo = muertes_por_grupo.sort_index()
            
            # Calcular tasa
            tasa_mortalidad = (muertes_por_grupo / casos_por_grupo) * 100
            
        else:
            # Para variables categóricas
            casos_por_grupo = self.df[por_grupo].value_counts()
            muertes_por_grupo = muertes[por_grupo].value_counts()
            
            # Asegurar que todos los grupos estén presentes
            for grupo in casos_por_grupo.index:
                if grupo not in muertes_por_grupo:
                    muertes_por_grupo[grupo] = 0
            
            # Calcular tasa
            tasa_mortalidad = (muertes_por_grupo / casos_por_grupo) * 100
            
        return tasa_mortalidad
    
    def graficar_tasa_mortalidad(self, por_grupo=None, bins=None, ax=None):
        """
        Genera un gráfico de tasa de mortalidad
        
        Args:
            por_grupo (str, opcional): Columna para agrupar la tasa de mortalidad
            bins (list, opcional): Bins para agrupar variables numéricas
            ax (matplotlib.axes, opcional): Axes donde graficar
            
        Returns:
            matplotlib.axes: Axes con el gráfico
        """
        tasa_mortalidad = self.calcular_tasa_mortalidad(por_grupo, bins)
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        if isinstance(tasa_mortalidad, pd.Series):
            tasa_mortalidad.plot(kind='bar', ax=ax)
            ax.set_xlabel(por_grupo.capitalize())
            ax.set_title(f'Tasa de Mortalidad por {por_grupo.capitalize()}')
        else:
            ax.bar(['Total'], [tasa_mortalidad])
            ax.set_title('Tasa de Mortalidad General')
            
        ax.set_ylabel('Tasa de Mortalidad (%)')
        
        # Añadir etiquetas de valores sobre las barras
        for i, v in enumerate(tasa_mortalidad):
            if isinstance(tasa_mortalidad, pd.Series):
                ax.text(i, v + 0.5, f'{v:.2f}%', ha='center')
            else:
                ax.text(0, v + 0.5, f'{v:.2f}%', ha='center')
                
        return ax
    
    def calcular_tiempo_hospitalizacion(self, columna_inicio='fecha de diagnóstico', 
                                      columna_fin='fecha de recuperación'):
        """
        Calcula el tiempo promedio de hospitalización o recuperación
        
        Args:
            columna_inicio (str): Columna con la fecha de inicio
            columna_fin (str): Columna con la fecha de fin
            
        Returns:
            float: Tiempo promedio en días
        """
        if columna_inicio not in self.df.columns or columna_fin not in self.df.columns:
            raise ValueError(f"Columnas {columna_inicio} o {columna_fin} no existen en el DataFrame")
            
        # Filtrar registros con ambas fechas válidas
        df_tiempo = self.df.dropna(subset=[columna_inicio, columna_fin])
        
        # Calcular diferencia en días
        df_tiempo['tiempo_dias'] = (df_tiempo[columna_fin] - df_tiempo[columna_inicio]).dt.days
        
        # Filtrar valores negativos o extremadamente grandes (posibles errores)
        df_tiempo = df_tiempo[(df_tiempo['tiempo_dias'] >= 0) & (df_tiempo['tiempo_dias'] <= 365)]
        
        return df_tiempo['tiempo_dias'].mean()
    
    def calcular_fallecidos(self):
        """Calcula la cantidad total de fallecidos"""
        if 'Estado' not in self.df.columns:
            raise ValueError("No existe la columna 'Estado'")
        return len(self.df[self.df['Estado'].str.contains('Fallecido', case=False, na=False)])

    def graficar_fallecidos(self, ax=None):
        """Genera el gráfico de cantidad total de fallecidos"""
        cantidad = self.calcular_fallecidos()
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(6, 3))
            
        ax.text(0.5, 0.5, f'{cantidad:,}\nFallecidos',
                fontsize=32, ha='center', va='center', 
                weight='bold', color='darkred')
        ax.axis('off')
        ax.set_title('Cantidad de personas fallecidas', 
                    fontsize=16, weight='bold', pad=20)
        return ax

    def graficar_fallecidos_por_departamento(self, ax=None):
        """Genera gráfico de barras de fallecidos por departamento"""
        if 'Nombre departamento' not in self.df.columns:
            raise ValueError("Columna 'Nombre departamento' no encontrada")
            
        data = self.df[self.df['Estado'].str.contains('Fallecido', case=False, na=False)]
        fallecidos_depto = data.groupby('Nombre departamento').size()
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
            
        fallecidos_depto.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Fallecidos por departamento', fontsize=18, weight='bold')
        ax.set_xlabel('Departamento', fontsize=14)
        ax.set_ylabel('Cantidad', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        return ax
    
    def graficar_distribucion_Edad_fallecidos(self, ax=None):
        """
            Genera un histograma de distribución por Edad de fallecidos.
             """
        if 'Edad' not in self.df.columns:
            raise ValueError("Columna 'Edad' no encontrada")
        
        # Filtrar sólo los casos de fallecidos
        data = self.df[self.df['Estado'].str.contains('Fallecido', case=False, na=False)].copy()
        # Asegurarnos de que Edad sea numérico y sin NaNs
        data['Edad'] = pd.to_numeric(data['Edad'], errors='coerce')
        data = data.dropna(subset=['Edad'])
        
        # Crear figura/axes si no se proporcionó uno
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        
        # Dibujar histograma
        sns.histplot(data['Edad'], bins=30, kde=True, ax=ax, color='skyblue')
        
        # Ajustar etiquetas y título
        ax.set_title('Distribución de fallecidos por Edad', fontsize=18, weight='bold')
        ax.set_xlabel('Edad', fontsize=14)
        ax.set_ylabel('Cantidad', fontsize=14)
        
        return ax


    def graficar_fallecidos_por_contagio(self, ax=None):
        """Genera gráfico de fallecidos por Tipo de contagio"""
        if 'Tipo de contagio' not in self.df.columns:
            raise ValueError("Columna 'Tipo de contagio' no encontrada")
            
        data = self.df[self.df['Estado'].str.contains('Fallecido', case=False, na=False)]
        contagios = data['Tipo de contagio'].value_counts()
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
            
        contagios.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title('Fallecidos por Tipo de contagio', fontsize=18, weight='bold')
        ax.set_xlabel('Tipo de contagio', fontsize=14)
        ax.set_ylabel('Cantidad', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        return ax
    

    def exportar_datos_filtrados(self, filtros, ruta_salida):
        """
        Exporta los datos filtrados a un nuevo CSV
        
        Args:
            filtros (dict): Diccionario con filtros {columna: valor}
            ruta_salida (str): Ruta del archivo de salida
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        df_filtrado = self.df.copy()
        
        # Aplicar filtros
        for columna, valor in filtros.items():
            if columna in df_filtrado.columns:
                if isinstance(valor, (list, tuple)):
                    df_filtrado = df_filtrado[df_filtrado[columna].isin(valor)]
                else:
                    df_filtrado = df_filtrado[df_filtrado[columna] == valor]
        
        # Exportar a CSV
        try:
            df_filtrado.to_csv(ruta_salida, index=False)
            return True
        except Exception as e:
            print(f"Error al exportar: {e}")
            return False

# Ejemplo de uso:
if __name__ == "__main__":
    # Este código se ejecuta solo si se ejecuta directamente este script
    try:
        # Cargar datos
        analizador = AnalizadorEpidemiologico(ruta_csv="dataset.csv")
        
        # Ejemplo 1: Graficar incidencia mensual
        plt.figure(figsize=(12, 6))
        analizador.graficar_incidencia(periodo='M')
        plt.savefig('incidencia_mensual.png')
        
        # Ejemplo 2: Graficar distribución por grupo de Edad
        plt.figure(figsize=(10, 6))
        bins_Edad = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 120]
        analizador.graficar_distribucion_por_grupo('Edad', bins=bins_Edad)
        plt.savefig('distribucion_Edad.png')
        
        # Ejemplo 3: Graficar tasa de mortalidad por Sexo
        plt.figure(figsize=(8, 6))
        analizador.graficar_tasa_mortalidad(por_grupo='Sexo')
        plt.savefig('mortalidad_s.png')
        
        print("Análisis completado y gráficos guardados.")
        
    except Exception as e:
        print(f"Error en la ejecución del ejemplo: {e}")
