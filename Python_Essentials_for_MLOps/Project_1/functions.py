""""
Script destinado às funções que serão utilizadas na
main: ./movie_recommendation_system.py.
"""

# Importa bibliotecas
import os
import re
import logging
import zipfile
import requests
import numpy as np
import pandas as pd
import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuração inicial do logging
# Com level logging.INFO, também é englobado o level logging.ERROR
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def clean_movie_title(title: str) -> str:
    """
    Função que faz com que uma string possua apenas letras, números e 
    espaços

    Arg:
        title (str): Título original

    Return:
        cleaned_title (str): Título apenas com letras, números e espaços
    """
    clean_title = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    return clean_title

def search_similar_movies_by_title(movies_df: pd.DataFrame, 
                          vectorizer: TfidfVectorizer,
                          title: str) -> pd.DataFrame:
    """
    Captura os 5 filmes mais similares, por nome

    Args:
        movies_df (pd.DataFrame): Dataframe que contém os filmes
        vectorizer (TfidfVectorizer): Instância da classe TfidfVectorizer
        title (str): Título do filme
    """
    clean_title = clean_movie_title(title)
    query_vec = vectorizer.transform([clean_title])
    similarity = cosine_similarity(query_vec, 
                                   vectorizer.fit_transform(movies_df["clean_title"])).flatten()
    indices = np.argpartition(similarity, -5)[-5:]
    results = movies_df.iloc[indices].iloc[::-1]
    return results

def find_similar_movies(movie_title: str,
                        movies_df: pd.DataFrame,
                        ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Encontra 10 filmes recomendados com base no nome do filme, baseado em usuários
    com gostos similares e com usuários no geral

    Args:
        movie_title (str): Título do filme que será analisado
        movies_df (pd.DataFrame): Dataframe contendo todos os filmes
        ratings_df (pd.DataFrame): Dataframe com a classificação de usuários para os filmes

    Return:
        rec_percentages (pd.DataFrame): Os 10 filmes recomendados
    """
    # Obtém o id do filme
    movie_id = movies_df[movies_df["title"] == movie_title]["movieId"].values[0]

    # Encontra os usuários que deram uma nota maior que 4 para o filme informado
    similar_users = ratings_df[(ratings_df["movieId"] == movie_id) & \
                               (ratings_df["rating"] > 4.5)]["userId"].unique()

    # Encontra as ids dos filmes cujas classiciações dos usuários "similar_users"
    # foram maior que 4.5 (os ids dos filmes podem se repetir). Ou seja, os filmes
    # que são recomendados para nós por aquele que também gostaram do mesmo filme
    # que a gente
    similar_user_recs = ratings_df[(ratings_df["userId"].isin(similar_users)) & \
                                   (ratings_df["rating"] > 4.5)]["movieId"]

    # Calcula a porcentagem das recomendações
    similar_user_recs = similar_user_recs.value_counts() / len(similar_users)

    # Filtra as recomendações de filmes para que apenas aquelas que tiveram
    # uma recorrência maior que 10% estejam presentes
    similar_user_recs = similar_user_recs[similar_user_recs > .10]

    # Todos os usários que classificaram os filmes recomendados com uma nota maior que 4.5
    all_users = ratings_df[(ratings_df["movieId"].isin(similar_user_recs.index)) & \
                           (ratings_df["rating"] > 4.5)]

    # Porcentagem de usuários que também classificaram os filmes recomendados
    # com uma nota maior que 4.5
    all_users_recs = all_users["movieId"].value_counts() / len(all_users["userId"].unique())

    # Junta as duas séries em um dataframe
    rec_percentages = pd.concat([similar_user_recs, all_users_recs], axis=1)

    # Renomeia as colunas
    rec_percentages.columns = ["similar", "all"]

    # Obtém o score
    rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]

    # Ordena os scores em ordem descrescente
    rec_percentages = rec_percentages.sort_values("score", ascending=False)

    # Retorna os 10 filmes com melhor score
    return rec_percentages.head(10).merge(movies_df, \
                                          left_index=True, \
                                          right_on="movieId")[["score", "title", "genres"]]

def download_zip_file() -> None:
    """
    Faz download dos arquivos necessários para que o script funcione corretamente
    """
    # URL do arquivo
    url="http://files.grouplens.org/datasets/movielens/ml-25m.zip"

    # Nome do arquivo zip a ser baixado
    zip_filename = "ml-25m.zip"

    with requests.Session() as session:
        response = session.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        # Definindo o chunk size
        chunk_size = 128 * 1024

        # Download do arquivo
        with open(zip_filename, 'wb') as file:
            for data in tqdm.tqdm(response.iter_content(chunk_size=chunk_size),
                            total=total_size // chunk_size,
                            unit='KB',
                            desc=zip_filename,
                            leave=True):
                file.write(data)

    # Descompacta os arquivos
    logging.info("Unzipping the file")
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(".")

    # Remove o arquivo ZIP
    os.remove(zip_filename)
