"""
Provê as fixtures para os testes que serão realizados
Autor: José Augusto
Data: 2023-10-14
"""

# Importa as bibliotecas
import pytest
import pandas as pd

@pytest.fixture
def heart_desease_df() -> pd.DataFrame:
    """
    Lê e retorna o arquivo CSV como um dataframe para ser
    utilizado nos testes.

    Returns:
        (pd.DataFrame): Dataframe contendo os dados que serão analisados
    """
    dataframe = pd.read_csv("heart_disease_prediction.csv")
    return dataframe
