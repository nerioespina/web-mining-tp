
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

import os


# ### Buscar la base de datos
db_path_colab = 'inmuebles_sanjuan_venta_con_precio.db'

if os.path.exists(db_path_colab):
  db_exists = True
else:
  db_exists = False


# ## 2. Importación de datos base
all_data = []

if not db_exists:
    # Iterar sobre las páginas
    for page in range(1, 277):  # Ajusta el rango según el número de páginas disponibles
        try:
            page_url = f"https://www.compraensanjuan.com/b_in.php?tipo=0&operacion=03&zona=0&dormitorios=Todos&aptocredito=Todos&barrioprivado=Todos&vendedor=Todos&precio_desde=&precio_hasta=&pagina={page}&orden=0&conprecio=true&estado=&foto="

            # Realizar la solicitud GET
            response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()  # Verificar si la solicitud fue exitosa

            # Analizar el contenido HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            divs = soup.find_all('div', class_='lista-avisos')

            # Extraer los datos de cada aviso
            for div in divs:
                link_url = None
                img_url = None
                aviso_title = None
                precio = None
                publicacion = None
                visitas = None

                link_element = div.find('a', class_='title orange-link')
                if link_element:
                    link_url = link_element['href']

                img_element = div.find('img', class_='img-lista')
                if img_element:
                    img_url = img_element['src']

                aviso_title_element = div.find('p', class_='aviso-title')
                if aviso_title_element:
                    aviso_title = aviso_title_element.text.strip()

                precio_element = div.find('p', class_='precio')
                if precio_element:
                    precio = precio_element.text.strip()

                publicacion_element = div.find('p', class_='publicacion')
                if publicacion_element:
                    publicacion = publicacion_element.text.strip()

                visitas_element = div.find('p', class_='visitas')
                if visitas_element:
                    visitas = visitas_element.text.strip()
                
                categoria = div.find_all('a', class_='categoria')[1]
                if categoria:
                    categoria = categoria.text.strip()
                else:
                    categoria = None

                all_data.append([link_url, img_url, aviso_title, precio, publicacion, visitas, categoria])

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            continue  # Continuar con la siguiente página en caso de error

    # Crear un DataFrame con todos los datos
    df_all = pd.DataFrame(all_data, columns=['url', 'url_imagen', 'titulo', 'precio', 'publicacion', 'visitas', 'categoria'])
    df_all['html'] = None
    df_all['procesado'] = False
    df_all['anuncio_id'] = df_all['url'].str.extract(r'anuncio_in/(\d+)/')
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path_colab)
    # Create a cursor object
    cursor = conn.cursor()
    # Create a table if it doesn't exist

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inmuebles (
            url         text,
            url_imagen  text,
            titulo      text,
            precio      text,
            publicacion text,
            visitas     text,
            categoria   text,
            html        text,
            procesado   boolean default false,
            anuncio_id  integer primary key
        );
    ''')

    # Insert the data from the DataFrame into the table
    df_all.to_sql('inmuebles', conn, if_exists='replace', index=False)
    # Commit the changes
    conn.commit()
    # Close the connection
    conn.close()
else:
    conn = sqlite3.connect('inmuebles_sanjuan_venta_con_precio.db')
    df_all = pd.read_sql_query("SELECT * FROM inmuebles", conn)
    conn.close()



# ## 3. Extraemos la información de cada publicación:
# Definimos la función get_html_from_url que nos permitirá traer el html de cada detalle del inmueble

def get_html_from_url(url):
  try:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.content
  except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    return None


# Conectar a la base de datos SQLite
conn = sqlite3.connect('inmuebles_sanjuan_venta_con_precio.db')
cursor = conn.cursor()

while True:
    # Buscar el primer registro que tenga html null
    cursor.execute("SELECT * FROM inmuebles WHERE html IS NULL LIMIT 1")
    record = cursor.fetchone()

    if not record:
        print("No se encontraron más registros con html null")
        break

    url = record[0]  # Asumiendo que la URL está en la primera columna
    full_url = 'https://www.compraensanjuan.com/' + url
    html_content = get_html_from_url(full_url)

    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        html_str = str(soup)

        # Actualizar el registro con el HTML extraído
        cursor.execute("UPDATE inmuebles SET html = ? WHERE url = ?", (html_str, url))
        conn.commit()
        print(f"HTML extraído y actualizado para el registro con URL: {url}")
    else:
        print(f"No se pudo extraer el HTML para la URL: {url}")

# Cerrar la conexión
conn.close()


