"""
Fixtures para os testes dos processos para a recomendação dos filmes
Autor: José Augusto
Data: 2023-10-09
"""

# Importa bibliotecas
import os
import pytest
import pandas as pd
from functions import clean_movie_title, download_zip_file

# Nome do diretório contendo os dataframes baixados
DIRECTORY_NAME = "ml-25m/"

@pytest.fixture
def load_clean_title() -> str:
    """
    Provê um título limpo a partir do filme "Women of Devil's Island (1962)"

    Return:
        str: título do filme apropriadamente limpo
    """
    clean_title = clean_movie_title("Women of Devil's Island (1962)")
    return clean_title

@pytest.fixture
def load_dataframes() -> list:
    """
    Carrega os dataframes contendo os filmes e as avalições para os filmes

    Return:
        list: Lista contendo dataframes 
    """
    # Verifica se o diretório DIRECTORY_NAME já existe
    if os.path.exists(DIRECTORY_NAME):
        # Lê os dataframes
        movies_df = pd.read_csv("ml-25m/movies.csv")
        ratings_df = pd.read_csv("ml-25m/ratings.csv")
    else:
        # Faz o download do arquivo zip
        download_zip_file()
    return [movies_df, ratings_df]
