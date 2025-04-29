# Estimador de precios de inmuebles en la ciudad de San Juan, Argentina.
## Trabajo práctico para la cátedra Web Mining. Maestría en Ciencia de Datos. Universidad Austral.
## Grupo 16

---


## Descripción del proyecto
El proyecto **Estimador de Precios de Inmuebles en San Juan, Argentina** utiliza técnicas de web mining para recopilar, procesar y analizar datos de propiedades publicadas en [Compra en San Juan](https://www.compraensanjuan.com/). Su objetivo es desarrollar un modelo predictivo que estime los precios de inmuebles en la ciudad de San Juan, Argentina, basado en características como ubicación, tipo de propiedad, superficie, cantidad de habitaciones y otras variables relevantes.

## Funcionalidades
- **Extracción de Datos**: Web scraping automatizado de anuncios de propiedades desde Compra en San Juan.
- **Normalización**: Limpieza y estructuración de datos para garantizar consistencia.
- **Feature Engineering**: Creación de variables derivadas para mejorar el rendimiento del modelo.
- **Entrenamiento de Modelos**: Implementación de algoritmos de machine learning para predecir precios.
- **Análisis Exploratorio**: Generación de reportes y visualizaciones para entender el mercado inmobiliario.

## Tecnologías Utilizadas
- **Lenguaje**: Python
- **Librerías de Scraping**: BeautifulSoup
- **Procesamiento de Datos**: Pandas, NumPy
- **Machine Learning**: AutoML (H2O)
- **Bases de Datos**: SQLite
- **Análisis Exploratorio**: YData Profiling, Matplotlib, Seaborn
- **Entorno**: Jupyter Notebooks

## Fuente de Datos
Los datos provienen de [Compra en San Juan](https://www.compraensanjuan.com/), una plataforma de clasificados con anuncios de propiedades en venta en San Juan, Argentina.

## Estructura del Repositorio
```
├── best_model/                     # Modelos entrenados
│   └── GBM_3_AutoML_3_20250428_220120
├── db_ajustes.sql                  # Scripts SQL para ajustes en la base de datos
├── EDA_inmuebles_ydata_profiling.html  # Reporte de análisis exploratorio
├── extractor.py                    # Script para web scraping
├── feature_engineering.py          # Script para ingeniería de características
├── inmuebles_final.db              # Base de datos final procesada
├── inmuebles_full.db               # Base de datos completa
├── inmuebles_sanjuan_venta_con_precio.db  # Base de datos con propiedades en venta
├── model_train.py                  # Script para entrenamiento de modelos
├── normalizacion.py                # Script para normalización de datos
├── notebooks/                      # Notebooks para análisis y prototipado
│   ├── Auto_EDA.ipynb
│   ├── Extractor.ipynb
│   ├── FeatureEngineering.ipynb
│   ├── ModelTrain.ipynb
│   └── Normalizacion.ipynb
├── README.md                       # Documentación del proyecto
└── resultados.txt                  # Resultados del modelo o métricas
```

## Requisitos
### Entorno virtual
Creamos el entorno virtual y nos conectamos a él
```sh
python3 -m venv ./.venv
source ./.venv/bin/activate
```

## Instrucciones de Uso
1. Clonar el repositorio
2. Configurar el entorno para web scraping (venv)
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar el scraper: `python extractor.py`
5. Realizar ingeniería de características: `python feature_engineering.py`
6. Normalizar los datos: `python normalizacion.py`
7. Ejecutar script SQL y establecer escalas
8. Entrenar el modelo: `python model_train.py`
9. Consultar el reporte EDA: Abrir `EDA_inmuebles_ydata_profiling.html` en un navegador.
10. Revisar resultados en `resultados.txt`.

## Requisitos
- Python 3.8+
- Dependencias listadas en `requirements.txt` (crear si no existe).
- Conexión a internet para el web scraping.

## Limitaciones
- La calidad del modelo depende de la información disponible en Compra en San Juan.
- Los anuncios pueden tener datos incompletos o inconsistentes.
- El scraping se realiza respetando los términos de uso del sitio web.

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request.

## Licencia
Licencia MIT.

Autores:
Bello, Macarena
Espina, Nerio
Ludueña, Marcos
Raco, Fernando
Sarmiento, Patricia


