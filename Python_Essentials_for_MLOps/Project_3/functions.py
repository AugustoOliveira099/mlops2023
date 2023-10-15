"""
Funções para usar em heart_desease.py
Autor: José Augusto
Data: 2023-10-12
"""

import logging
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração inicial do logging
# Com level logging.INFO, também é englobado o level logging.ERROR
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def create_graphs(heart_desease_df: pd.DataFrame) -> None:
    """
    Cria gráficos de barra com base no dataframe recebido

    Args:
        heart_desease_df (pd.DataFrame): dados que serão convertidos em gráficos

    Returns:
        None
    """
    categorical_cols = ["FastingBS",
                         "HeartDisease",
                         "ST_Slope",
                         "ExerciseAngina",
                         "RestingECG",
                         "ChestPainType",
                         "Sex"]

    logging.info("Building distribution of categorical features graph")
    fig = plt.figure(figsize=(10, 14))
    fig.suptitle("Distribution of categorical features", fontsize=16)

    # Iterando sobre as colunas categóricas
    for i, col in enumerate(categorical_cols):
        position = i + 1
        ax = plt.subplot(4, 2, position)
        # Criando um gráfico de barras com Seaborn
        sns.countplot(x=heart_desease_df[col], ax=ax, hue=None, palette="pastel")

        # Adiciona rótulo a cada barra
        for container in ax.containers:
            ax.bar_label(container, label_type="center")

        # Configurando rótulos e título
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")

    # Ajustando o layout e salvando a figura
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig("./images/results/Distribution_of_categorical_features.png")
    logging.info("Graph saved as Distribution_of_categorical_features.png in images/")

    logging.info("Building clustered distribution of categorical features graph")
    fig = plt.figure(figsize=(10, 14))
    fig.suptitle("Distribution of categorical features grouped by 'HeartDisease'", fontsize=16)

    # Iterando sobre as colunas categóricas
    for i, col in enumerate(categorical_cols):
        position = i + 1
        ax = plt.subplot(4, 2, position)
        # Criando um gráfico de barras com Seaborn
        sns.countplot(x=col,
                      data=heart_desease_df,
                      hue=heart_desease_df["HeartDisease"],
                      ax=ax,
                      palette="pastel")

        for container in ax.containers:
            ax.bar_label(container, label_type="center")

        # Configurando rótulos e título
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")

    # Ajustando o layout e salvando a figura
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig("./images/results/Distribution_of_grouped_categorical_features.png")
    logging.info("Graph saved as Distribution_of_grouped_categorical_features.png in images/")


def clean_data(heart_desease_df: pd.DataFrame) -> pd.DataFrame:
    """
    Retira do dataframe as linhas que possuem valores iguais a 0 para
    as colunas RestingBP ou Cholesterol

    Args:
        heart_desease_df (pd.DataFrame): dados que serão convertidos em gráficos

    Returns:
        df_partial_clean (pd.DataFrame): Dataframe limpo
    """
    resting_count = (heart_desease_df["RestingBP"] == 0).sum()
    cholesterol_count = (heart_desease_df["Cholesterol"] == 0).sum()

    df_partial_clean = heart_desease_df[heart_desease_df["RestingBP"] != 0]
    df_partial_clean = df_partial_clean[df_partial_clean["Cholesterol"] != 0]

    logging.info("%d rows were deleted because RestingBP = 0", resting_count)
    logging.info("%d rows were deleted because Cholesterol = 0", cholesterol_count)

    return df_partial_clean
