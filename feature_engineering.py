
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


# ## 2. Importación de Base de datos
# ### Buscar la base de datos

db_path_colab = 'inmuebles_sanjuan_venta_con_precio.db'

if os.path.exists(db_path_colab):
  db_exists = True
else:
  db_exists = False

conn = sqlite3.connect('inmuebles_sanjuan_venta_con_precio.db')
df_all = pd.read_sql_query("SELECT * FROM inmuebles", conn)
conn.close()


# ## 3. Parseamos las caracteristicas contenidas en el html
def parse_caracteristicas(html):
    if html is None:
        return {}
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    caracteristicas = {}
    for p in soup.find_all('p', class_='name-caracteristica'):
      try:
        # Extract the characteristic name (before the colon)
        characteristic_name = p.text.split(':')[0].strip()
        # Extract the characteristic value (within the span)
        characteristic_value = p.find('span').text.strip()
        caracteristicas[characteristic_name] = characteristic_value
      except:
        pass
    return caracteristicas

# Apply the function to the 'html' column
df_all['caracteristicas'] = df_all['html'].apply(parse_caracteristicas)

# Expand the dictionary into separate columns
df_all = pd.concat([df_all, pd.json_normalize(df_all['caracteristicas'])], axis=1)


# ### 4. Agregamos la Longitud y Latitud

def extract_lat_long(html):
    """
        Extrae la latitud y longitud de un string HTML que contiene el siguiente formato:
        L.marker([-31.538911593868313, -68.49121665865825],
    """
    if html is None:
        return None, None
    # Regex pattern to match the latitude and longitude
    
    pattern = r"L\.marker\(\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\]"
    match = re.search(pattern, html)
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        return latitude, longitude
    return None, None

# Apply the function to the 'html' column
df_all[['Latitude', 'Longitude']] = df_all['html'].apply(lambda x: pd.Series(extract_lat_long(x)))

df_all.head()


# ### 5. Extraemos la descripción del anuncio

def extract_comentario_caracteristicas(html):
    if html is None:
      return ""
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    comentario_element = soup.find('p', class_='comentario-caracteristicas-anuncio')
    if comentario_element:
      return comentario_element.text.strip()
    return ""

df_all['Comentario Caracteristicas'] = df_all['html'].apply(extract_comentario_caracteristicas)



def fetch_image_as_blob(url_imagen):
    full_url = 'https://www.compraensanjuan.com/' + url_imagen
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        return response.content  # Return the image as binary data (blob)
    except requests.RequestException as e:
        print(f"Error fetching image from {full_url}: {e}")
        return None

# Apply the function to the 'url_imagen' column and store the blob in a new column
df_all['image_blob'] = df_all['url_imagen'].apply(fetch_image_as_blob)


# ### 6. Borramos las columnas que no nos hacen falta
# Borramos las columnas que no nos interesan
df_all = df_all.drop(columns=['html', 'url', 'url_imagen', 'caracteristicas'])


# ### 7. Seteamos datos en null cuando está el texto "Sin especificar", texto vacío y nan. También arreglamos los nombres de las columnas

df_all = df_all.replace({'Sin especificar': None})
df_all = df_all.replace({'': None})
df_all = df_all.replace({'nan': None})
# Eliminamos los caracteres especiales de las columnas
df_all.columns = df_all.columns.str.replace(' ', '_')
df_all.columns = df_all.columns.str.replace('(', '')
df_all.columns = df_all.columns.str.replace(')', '')
df_all.columns = df_all.columns.str.replace('/', '_')
df_all.columns = df_all.columns.str.replace('-', '_')
df_all.columns = df_all.columns.str.replace('?', '')
df_all.columns = df_all.columns.str.replace('!', '')

df_all.columns = df_all.columns.str.lower()

def remove_diacritics(input_str):
	"""
	Removes diacritics from the input string.
	"""
	return ''.join(
		c for c in unicodedata.normalize('NFD', input_str)
		if unicodedata.category(c) != 'Mn'
	)

df_all.columns = [remove_diacritics(col) for col in df_all.columns]

# ### 8. Guardamos la base de datos final

# Save the DataFrame to a new SQLite database
conn_full = sqlite3.connect('inmuebles_full.db')
df_all.to_sql('inmuebles', conn_full, if_exists='replace', index=False)
conn_full.close()


