"""
Realiza os teste no dataframe 'heart_disease_prediction.csv'
Autor: José Augusto
Data: 2023-10-14
"""

# Importa as bibliotecas
import pandas as pd

def test_dataframe_columns(heart_desease_df: pd.DataFrame) -> None:
    """
    Testa a quantidade de colunas no dataframe

    Args:
        heart_desease_df (pd.DataFrame): Dataframe contendo os dados que
            serão analisados.
    """
    assert heart_desease_df.shape[1] == 12

def test_dataframe_columns_name(heart_desease_df: pd.DataFrame) -> None:
    """
    Testa o nome de cada coluna no dataframe

    Args:
        heart_desease_df (pd.DataFrame): Dataframe contendo os dados que
            serão analisados.
    """
    expected_columns_set = {"Age", "Sex", "ChestPainType", "RestingBP", "Cholesterol",
                            "FastingBS", "RestingECG", "MaxHR", "ExerciseAngina", 
                            "Oldpeak", "ST_Slope", "HeartDisease"}
    assert set(heart_desease_df.columns) == expected_columns_set

def test_dataframe_columns_type(heart_desease_df: pd.DataFrame) -> None:
    """
    Testa o tipo de dado de cada coluna no dataframe

    Args:
        heart_desease_df (pd.DataFrame): Dataframe contendo os dados que
            serão analisados.
    """
    expected_columns_types = {
        "RestingBP": "int64",
        "ChestPainType": "object",
        "MaxHR": "int64",
        "Sex": "object",
        "Cholesterol": "int64",
        "RestingECG": "object",
        "Age": "int64",
        "ExerciseAngina": "object",
        "Oldpeak": "float64",
        "FastingBS": "int64",
        "HeartDisease": "int64",
        "ST_Slope": "object"
    }
    for column, column_type in expected_columns_types.items():
        assert str(heart_desease_df[column].dtype) == column_type

def test_dataframe_size(heart_desease_df: pd.DataFrame) -> None:
    """
    Testa a quantidade de linhas no dataframe. Mesmo com limpezas futuras,
    é importante uma certa quantidade de dados para o que o modelo de
    previsão consiga se ajustar bem.

    Args:
        heart_desease_df (pd.DataFrame): Dataframe contendo os dados que
            serão analisados.
    """
    assert heart_desease_df.shape[0] > 700
