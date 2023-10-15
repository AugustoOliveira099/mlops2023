"""
Testa os processos para a recomendação dos filmes
Autor: José Augusto
Data: 2023-10-09
"""

import pandas as pd

def test_clean_movie_title(load_clean_title: str) -> None:
    """
    Testa se o título retornado está limpo.

    Arg:
        load_clean_title (str): Título limpo
    """
    assert load_clean_title == "Women of Devils Island 1962"

def test_size_of_the_dataframes(load_dataframes: list[pd.DataFrame, pd.DataFrame]) -> None:
    """
    Testa um tamanho mínumo dos dataframes, tendo-se em vista que já possuem um valor
    considerável e precisamos de uma quantidade mínima de dadaos para que o script
    duncione com eficiência.

    Arg:
        load_dataframes (list[pd.DataFrame, pd.DataFrame]): Lista de dataframes contendo 
            os filmes e as avaliações
    """

    movie_df, ratings_df = load_dataframes

    assert movie_df.shape[0] > 60000
    assert ratings_df.shape[0] > 24000000
    assert movie_df.shape[1] == 3
    assert ratings_df.shape[1] == 4

def test_columns_type_of_the_dataframes(load_dataframes: list[pd.DataFrame, pd.DataFrame]) -> None:
    """
    Testa o tipo das columns dos dataframes

    Arg:
        load_dataframes (list[pd.DataFrame, pd.DataFrame]): Lista de dataFrames
    """
    movies_df, ratings_df = load_dataframes

    assert movies_df["movieId"].dtype == "int64"
    assert movies_df["title"].dtype == "object"
    assert movies_df["genres"].dtype == "object"
    assert ratings_df["userId"].dtype == "int64"
    assert ratings_df["movieId"].dtype == "int64"
    assert ratings_df["rating"].dtype == "float64"
    assert ratings_df["timestamp"].dtype == "int64"
