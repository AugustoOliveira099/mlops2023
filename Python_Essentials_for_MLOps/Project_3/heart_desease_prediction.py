"""
Previsão de doenças cardíacas
Autor: José Augusto
Data: 2023-10-12
"""

# import libraries
import os
import sys
import logging
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, GridSearchCV

from functions import create_graphs, clean_data

# Configuração inicial do logging
# Com level logging.INFO, também é englobado o level logging.ERROR
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Iniciando o parse
parser = argparse.ArgumentParser(description="Movie Recommendation System")

# Tamanho do do conjunto de teste como parâmetro de linha de comando
parser.add_argument("-ts", "--test_size", type=str, help="Proportion of test size to data size")

args = parser.parse_args()

# Obtém o test_size como float
test_size = float(args.test_size)

# Verifica se os argumentos são válidos
if test_size <= 0 or test_size >= 1:
    logging.error("The test size you chose is out of limits: 0 < test_size < 1")
    sys.exit(1)

# Lê os dados
try:
    heart_desease_df = pd.read_csv('./heart_disease_prediction.csv')
except FileNotFoundError:
    logging.error("The CSV file is not available.")
except pd.errors.EmptyDataError:
    logging.error("The CSV file is empty or corrupt.")
except ValueError as e:
    logging.error("ValueError while read data:\n")
    logging.error(e)

# Imprime as 5 primeiras linhas do dataframe
logging.info("Current dataframe: \n %s", heart_desease_df.head)
# Imprime uma descrição do dataframe
logging.info("Current dataframe describe: \n %s", heart_desease_df.describe)

# Cria os gráficos e os salva como imagens
try:
    logging.info("Starting EDA")
    if not os.path.exists("images/results"):
        os.makedirs("images/results")
    create_graphs(heart_desease_df)
except ValueError as e:
    logging.error("ValueError building graphs:\n")
    logging.error(e)
except IOError as e:
    logging.error("IOError while save the graphs:\n")
    logging.error(e)

# Limpa os dados
try:
    logging.info("Starting data cleaning")
    heart_desease_df = clean_data(heart_desease_df)
except ValueError as e:
    logging.error("ValueError while data clean.")
    logging.error(e)

# Converte recursos categóricos em variáveis fictícias
heart_desease_df = pd.get_dummies(heart_desease_df, drop_first=True)
logging.info("Data after converting the categorical features into dummy variables:\n")
logging.info(heart_desease_df.head)

# Define a matriz de correlação
logging.info("Getting the correlated matrix")
correlations = abs(heart_desease_df.corr())

# Plota o mapa de calor para a matriz de correlação de Pearson
# e o salva como imagem .png
logging.info("Plotting the heatmap for the data")
fig = plt.figure(figsize=(10, 14))
fig.suptitle("Pearson's correlation heat map", fontsize=16)
sns.heatmap(correlations, annot=True)
plt.savefig("./images/results/Pearsons_correlation_heat_map.png")
logging.info("Heatmap saved in images folder")

# Captura e imprime as colunas que tem melhor correlação com a coluna
# HeartDisease e a sua porcentagem
most_correlated_col = correlations["HeartDisease"].sort_values(ascending=False)[1:6]
logging.info(
    "As seen in the heatmap, the columns most correlated with the 'HeartDisease' column are")
logging.info(most_correlated_col)

# Define X e y para ajustar o modelo
X = heart_desease_df.drop("HeartDisease", axis=1)
y = heart_desease_df["HeartDisease"]

# Separa os dados de treinamento e de teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=3)

# Define as 5 melhores features para se observar
top_5_features = ["Sex_M", "Oldpeak", "ExerciseAngina_Y", "ST_Slope_Flat", "ST_Slope_Up"]

# Ajusta o modelo para cada uma das 5 melhores features separadamente
for feature in top_5_features:
    # Transforma a Série em uma matriz bidimensional
    X_train_feature = X_train[feature].values.reshape(-1, 1)
    X_test_feature = X_test[feature].values.reshape(-1, 1)

    # Instancia classe KNeighborsClassifier com 5 vizinhos e dando peso
    # para a distância entre os vizinhos
    knn = KNeighborsClassifier(n_neighbors = 5, weights = "distance")
    knn.fit(X_train_feature, y_train)

    # Obtém e imprime a acurácia do modelo
    accuracy = knn.score(X_test_feature, y_test)
    accuracy *= 100
    logging.info("The accuracy to %s feature was: %.2f%%", feature, accuracy)

# Especifica o próximo passo
logging.info("Fitting the model to 5 most correlated columns, together")

# Dimensiona os valores para o intervalo (0, 1)
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train[top_5_features])
X_test_scaled = scaler.transform(X_test[top_5_features])

# Instancia classe KNeighborsClassifier com 5 vizinhos e dando peso
# para a distância entre os vizinhos
knn = KNeighborsClassifier(n_neighbors = 5, weights = "distance")

# Ajusta o modelo para os dados de treinamento
knn.fit(X_train_scaled, y_train)

# Obtém e imprime a acurácia do modelo
accuracy = knn.score(X_test_scaled, y_test)
accuracy *= 100
logging.info("The model's accuracy to 5 neighbors and weights = 'distance' is: %.2f%%", accuracy)

# Especifica o que será feito a seguir
logging.info("Searching all appropriate hyperparameters at once with GridSearchCV")

# Define os hiperparâmetros
hyperparameters = {"n_neighbors": [3, 5, 7, 9, 11, 13, 15, 20],
                   "metric": ["euclidean", "manhattan", "minkowski"],
                   "weights": ["uniform", "distance"],
                   "p": [1, 2, 3, 5]
                   }

# Instancia KNN e GridSearchCV com os hiperparâmetros definidos
knn = KNeighborsClassifier()
knn_grid = GridSearchCV(knn, hyperparameters, scoring="accuracy")

# Ajusta o modelo com GridSearchCV
knn_grid.fit(X_train_scaled, y_train)

# Obtém e imprime o melhor score e melhores parâmetros
best_score = knn_grid.best_score_
best_score *= 100
best_params = knn_grid.best_params_
logging.info("Best model's accuracy: %.2f%%", best_score)
logging.info("Best model's parameters: %s", best_params)

# Descobre e imprime a acurácia do melhor modelo para o conjunto de teste
best_estimator_accuracy = knn_grid.best_estimator_.score(X_test_scaled, y_test)
best_estimator_accuracy *= 100
logging.info("Model's accuracy on the test set: %.2f%%", best_estimator_accuracy)
