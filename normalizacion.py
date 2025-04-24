# # Estimador de precios de inmuebles en la ciudad de San Juan, Argentina.

# ## 1. Inicialización: librerías, configuraciones y variables globales

# ### Importación de Librerías

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import re
import unicodedata
import os
from datetime import datetime, timedelta

# ## 2. Importación de Base de datos

# ### Buscar la base de datos


conn = sqlite3.connect('inmuebles_full.db')
df_all = pd.read_sql_query("SELECT * FROM inmuebles", conn)
conn.close()

# ## 3. Normalización de datos

df_all.shape

# Eliminar duplicados conservando el registro con menos valores nulos
df_all = df_all.loc[df_all.isnull().sum(axis=1).groupby(df_all['anuncio_id']).idxmin()]
df_all.shape

# Alternativa
# df_all = df_all.drop_duplicates(subset='anuncio_id', keep='last')

def estandarizar_superficie_a_metros(texto_superficie):
    """
    Intenta convertir una cadena de texto de superficie (en m² o ha) a metros cuadrados.
    Prioriza hectáreas. Si no encuentra hectáreas, busca el primer número y asume metros.

    Args:
        texto_superficie (str): La cadena de texto que describe la superficie.

    Returns:
        float or None: La superficie en metros cuadrados si se pudo convertir,
                       None en caso contrario (ej: rangos, descripciones no numéricas).
    """
    if not isinstance(texto_superficie, str):
        # Si no es una cadena o es nulo, retornar None
        return None

    texto_limpio = texto_superficie.strip().lower()

    # Limpieza básica y normalización: comas a puntos, eliminar puntos extra (miles), paréntesis
    texto_limpio = texto_limpio.replace(',', '.')
    # Eliminar puntos que no son decimales (ej: 7.100 -> 7100) - CUIDADO: esto asume que los puntos son separadores de miles
    # Si 7.100 es 7.1 hectáreas, la lógica de decimales debe manejarlo.
    # Un enfoque más seguro es solo reemplazar comas por puntos y confiar en float()
    # texto_limpio = texto_limpio.replace('.', '', texto_limpio.count('.') - 1) # Riesgoso si hay puntos decimales múltiples mal formados
    texto_limpio = texto_limpio.replace('(', '').replace(')', '') # Eliminar paréntesis como en (63.000m

    # Eliminar texto irrelevante común
    texto_limpio = texto_limpio.replace('aprox', '').replace('casi', '').replace('son', '')
    texto_limpio = texto_limpio.replace('s/título', '').replace('en t', '')
    texto_limpio = texto_limpio.replace('hectarea y media', '1.5 hectareas') # Normalizar "una hectárea y media"

    # --- 1. Intentar extraer hectáreas (Prioridad Alta) ---
    # Busca un número (incluye decimales, fracciones, o número seguido de 'mil') seguido de una unidad de hectárea
    patron_hectareas = re.compile(r'(\d*\.?\d+|\d+\/\d+|\d+\s*mil)\s*(ha|has|hectarea|hectareas|hectares|hás|ht|hs|hec)', re.IGNORECASE)
    match_ha = patron_hectareas.search(texto_limpio)

    if match_ha:
        valor_str = match_ha.group(1).strip()
        try:
            if '/' in valor_str: # Manejar fracciones como 1/2
                 num, den = map(float, valor_str.split('/')) # Usar float para posible 0.5
                 hectareas = num / den
            elif 'mil' in valor_str: # Manejar "5 mil hectáreas"
                 hectareas = float(valor_str.replace('mil', '').strip()) * 1000
            else:
                hectareas = float(valor_str) # Convertir el número principal
            metros_totales = hectareas * 10000

            # Buscar si hay metros adicionales en la misma cadena (ej: 2 hectareas 5462 mts)
            # Eliminar la parte de hectáreas procesada para buscar metros en el resto
            texto_sin_ha = texto_limpio[:match_ha.start()] + texto_limpio[match_ha.end():]
            patron_metros_adicionales = re.compile(r'(\d*\.?\d+)\s*(mts|m2|m²|m)', re.IGNORECASE)
            match_metros = patron_metros_adicionales.search(texto_sin_ha)
            if match_metros:
                 try:
                     metros_adicionales = float(match_metros.group(1).strip())
                     metros_totales += metros_adicionales
                 except ValueError:
                     pass # Ignorar si no se pudo convertir los metros adicionales

            return float(metros_totales) # Retorna el total (ha convertidas + metros adicionales)

        except ValueError:
            # Si el número de hectáreas no se pudo convertir, esta cadena no es procesable como hectárea
            pass # No retornamos aún, pasamos a la lógica de fallback

    # --- 2. Lógica de Fallback (Si no se encontraron hectáreas) ---
    # Si llegamos aquí, no encontramos un patrón claro de hectáreas.
    # Ahora, verificamos si es una cadena que no deberíamos intentar convertir.
    palabras_clave_no_superficie = ['desde', 'hasta', 'dep', 'coch', 'no hay construccione', 'produccion']
    if any(palabra in texto_limpio for palabra in palabras_clave_no_superficie):
         return None # Es un texto que indica otra cosa o un rango

    # Si no es una cadena no convertible explícitamente, buscamos el primer número.
    # Esto cubre casos como '800' (asumiendo metros) o '63000m' que no fue capturado por ha.
    patron_cualquier_numero = re.compile(r'(\d*\.?\d+)') # Busca el primer número (entero o decimal)
    match_numero = patron_cualquier_numero.search(texto_limpio)

    if match_numero:
        try:
            # Asumir que este número es en metros cuadrados
            metros = float(match_numero.group(1).strip())
            # Considerar casos como '6,3hectareas(63.000m' donde ya está la conversión
            # Si el número es muy grande y no se detectó 'ha', podría ser un error,
            # pero siguiendo la lógica de fallback, lo asumimos como metros.
            # Una validación adicional podría ser útil aquí (ej: si > 1,000,000 m² y no es ha, quizás sea un error).
            # Por ahora, solo retornamos el número encontrado asumiendo metros.
            return metros
        except ValueError:
            pass # No se pudo convertir el número, retornar None

    # Si no se encontró patrón de hectáreas, no es texto no convertible explícito, y no se encontró ningún número
    return None # No se pudo estandarizar



# Aplicar la función a la columna 'superficie_total'
df_all['superficie_total_m2'] = df_all['superficie_total'].apply(estandarizar_superficie_a_metros)
df_all['superficie_cubierta_m2'] = df_all['superficie_cubierta'].apply(estandarizar_superficie_a_metros)

df_all.loc[df_all['precio'] == "Consultar", 'precio'] = None
df_all['moneda'] = df_all['precio'].str.extract(r'([^\d\s]+)')
df_all['precio'] = df_all['precio'].str.extract(r'(\d[\d,.]*)')
df_all['precio'] = df_all['precio'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

df_all['visitas'] = df_all['visitas'].str.replace('.', '').astype(int)
df_all['anuncio_id'] = df_all['anuncio_id'].astype(int)
df_all['superficie_total'] = df_all['superficie_total'].str.extract(r'(\d+)').astype(float)
df_all['superficie_cubierta'] = df_all['superficie_cubierta'].str.extract(r'(\d+)').astype(float)


df_all['apto_credito'] = df_all['apto_credito'].map({'SI': True, 'NO': False})
df_all['apto_credito'] = df_all['apto_credito'].astype(bool)
df_all['en_barrio_privado'] = df_all['en_barrio_privado'].map({'SI': True, 'NO': False})
df_all['en_barrio_privado'] = df_all['en_barrio_privado'].astype(bool)


# Borrar la columna 'procesado' si existe
df_all.drop(['procesado'], axis=1, inplace=True)

# Fecha de extracción
fecha_extraccion = datetime(2025, 4, 15)

# Función para convertir valores no correspondientes a fechas
def convertir_a_fecha(valor):
    if valor == 'Hoy':
        return fecha_extraccion.strftime('%d/%m/%Y')
    elif valor == 'Ayer':
        return (fecha_extraccion - timedelta(days=1)).strftime('%d/%m/%Y')
    elif re.match(r'Hace (\d+) días', valor):
        dias = int(re.search(r'(\d+)', valor).group(1))
        return (fecha_extraccion - timedelta(days=dias)).strftime('%d/%m/%Y')
    else:
        return valor

# Aplicar la función a la columna 'publicacion'
df_all['publicacion'] = df_all['publicacion'].apply(convertir_a_fecha)

# Convertir la columna 'publicacion' a tipo datetime
df_all['publicacion'] = pd.to_datetime(df_all['publicacion'], format='%d/%m/%Y', errors='coerce')


# Eliminar registros sin longitud y latitud
df_all = df_all.dropna(subset=['latitude', 'longitude'])

# Eliminar las columnas especificadas
df_all = df_all.drop(columns=['calle', 'barrio', 'numero'])


response = requests.get("https://dolarapi.com/v1/dolares/oficial")
dolar_bolsa_data = response.json()

datos_dolar = {
    "moneda": dolar_bolsa_data.get("moneda"),
    "casa": dolar_bolsa_data.get("casa"),
    "nombre": dolar_bolsa_data.get("nombre"),
    "compra": dolar_bolsa_data.get("compra"),
    "venta": dolar_bolsa_data.get("venta"),
    "fechaActualizacion": dolar_bolsa_data.get("fechaActualizacion")
}

valor_dolar = (datos_dolar['compra'] + datos_dolar['venta']) / 2

# cambiar los precios con moneda en pesos a dólares
df_all.loc[df_all['moneda'] == '$', 'precio'] = df_all['precio'] / valor_dolar
df_all.drop(columns=['moneda'], inplace=True)


# Configurar pandas para mostrar todas las columnas y filas sin recortar
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Mostrar los tipos de datos del DataFrame
df_all.dtypes

# Concatenar las columnas 'comentario_caracteristicas', 'comentario' y 'titulo', manejando valores nulos
df_all['comentarios'] = df_all[['comentario_caracteristicas', 'comentario', 'titulo']].fillna('').agg(' '.join, axis=1)

# Eliminar las columnas originales 'comentario_caracteristicas', 'comentario' y 'titulo'
df_all.drop(columns=['comentario_caracteristicas', 'comentario', 'titulo'], inplace=True)

# df_all['comentarios'] = df_all['comentarios'].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
# Mostrar todos los comentarios



import shutil

# Copy the database file to preserve other tables
shutil.copy('inmuebles_full.db', 'inmuebles_final.db')

conn = sqlite3.connect('inmuebles_final.db')
df_all.to_sql('inmuebles', conn, if_exists='replace', index=False)
conn.close()


