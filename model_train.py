import requests
from bs4 import BeautifulSoup

import sqlite3
import re
import unicodedata
import os
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import re
import string
import joblib

import lightgbm as lgb

from sklearn.model_selection import train_test_split, GridSearchCV, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, RocCurveDisplay, ConfusionMatrixDisplay, roc_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.ensemble import VotingClassifier


import spacy
nlp = spacy.load('es_core_news_sm')
import optuna

conn = sqlite3.connect('inmuebles_final.db')
df_all = pd.read_sql_query("SELECT * FROM vista_inmuebles where categoria_id = 4 and departamento_id = 6", conn)
conn.close()
df_all.head()

# Eliminar filas con valores nulos en la columna 'precio'
df_all = df_all.dropna(subset=['precio'])

# Agregar una nueva columna 'clase' basada en el precio
df_all['clase'] = (df_all['precio'] // 25000).astype(int)

# Mostrar las primeras filas del DataFrame para verificar el resultado
df_all[['precio', 'clase']].head()

df_all = df_all.select_dtypes(exclude=['object'])
df_all.dtypes

# Eliminar registros con valores nulos en ambas columnas
df_all = df_all.dropna(subset=['superficie_total', 'superficie_cubierta'])

# Mostrar las primeras filas para verificar
df_all.head()

# Calcular la matriz de correlación
correlation_matrix = df_all.corr()

# Visualizar la matriz de correlación
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True)
plt.title("Matriz de Correlación")
plt.show()

from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans # <-- Añade esta línea

inertias = []
for k in range(2, 20):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(df_all[['longitude', 'latitude']])
    inertias.append(kmeans.inertia_)

plt.plot(range(2, 20), inertias, marker='o')
plt.xlabel('Número de clusters')
plt.ylabel('Inercia')
plt.show()

df_all['precio_m2'] = df_all['precio'] / df_all['superficie_cubierta_m2']

df_all = df_all[df_all['precio_m2'] != float('inf')]

X = df_all[['longitude', 'latitude']]

# Elegir número de clusters (puedes ajustar esto según la cantidad de barrios esperados)
n_clusters = 10  # Ejemplo, usa un método como Elbow para optimizar
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df_all['cluster'] = kmeans.fit_predict(X)

# Calcular precio promedio por m² por cluster
cluster_precios = df_all.groupby('cluster')['precio_m2'].mean().reset_index()
cluster_precios.columns = ['cluster', 'precio_m2_promedio']

# Añadir centroides de los clusters (para uso futuro)
cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=['longitud_centro', 'latitud_centro'])
cluster_centros = pd.concat([pd.Series(range(n_clusters), name='cluster'), cluster_centers], axis=1)

# Combinar información de clusters
clusters_info = pd.merge(cluster_precios, cluster_centros, on='cluster')
print(clusters_info)

from scipy.spatial.distance import cdist

def predecir_precio_m2(longitud, latitud):
    # Cargar información de clusters desde la base de datos
    # clusters_info = pd.read_sql('clusters', engine)
    
    # Coordenadas nuevas
    nueva_coord = np.array([[longitud, latitud]])
    
    # Encontrar el cluster más cercano
    centroides = clusters_info[['longitud_centro', 'latitud_centro']].values
    distancia = cdist(nueva_coord, centroides, metric='euclidean')
    cluster_asignado = np.argmin(distancia)
    
    # Obtener precio por m² del cluster
    precio_m2 = clusters_info.loc[clusters_info['cluster'] == cluster_asignado, 'precio_m2_promedio'].values[0]
    
    return cluster_asignado, precio_m2



# Agregar la columna 'precio_cluster' al DataFrame
df_all['precio_cluster'] = df_all.apply(lambda row: predecir_precio_m2(row['longitude'], row['latitude'])[1], axis=1)

# Mostrar las primeras filas para verificar
df_all[['longitude', 'latitude', 'precio_cluster']].head()


df_all = df_all.drop(columns=['precio'])

!pip install h2o

import h2o
from h2o.automl import H2OAutoML

# Initialize H2O
h2o.init()

# Convert pandas DataFrame to H2OFrame
h2o_df = h2o.H2OFrame(df_all)

# Specify predictors and target
predictors = [col for col in h2o_df.columns if col != 'clase']
target = 'clase'

# Split data into train and test sets
train, test = h2o_df.split_frame(ratios=[0.8], seed=42)

# Train an H2O AutoML model
aml = H2OAutoML(max_models=10, seed=42)
aml.train(x=predictors, y=target, training_frame=train)

# View the leaderboard
lb = aml.leaderboard
print(lb)

# Predict on the test set
predictions = aml.leader.predict(test)
print(predictions)

# Convert H2OFrame predictions to pandas DataFrame
predictions_df = predictions.as_data_frame()

# Convert H2OFrame test set to pandas DataFrame
test_df = test.as_data_frame()

# Add predictions to the test DataFrame
test_df['predicted_clase'] = predictions_df['predict']

# Compare predictions with actual 'clase' values
comparison = test_df[['clase', 'predicted_clase']]

# Calcular el porcentaje de error para cada fila
test_df['error_porcentaje'] = abs(test_df['clase'] - test_df['predicted_clase']) / test_df['clase'] * 100

# Calcular el promedio de los errores porcentuales
error_promedio = test_df['error_porcentaje'].mean()

print(f"El porcentaje promedio de error es: {error_promedio:.2f}%")

# Save the best model
model_path = h2o.save_model(model=aml.leader, path="./best_model", force=True)
print(f"Model saved to: {model_path}")


