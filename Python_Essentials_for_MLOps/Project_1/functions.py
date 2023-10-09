""""
Scrypt destinado às funções que serão utilizadas na
main - movie_recommendation_system.
"""

# import libraries
import os
import re
import logging
import zipfile
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuração inicial do logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def clean_title(title: str) -> str:
    """
    Função que faz com que uma string possua apenas letras, números e 
    espaços

    Arg:
        title (str): Título original

    Return:
        cleaned_title (str): Título apenas com letras, números e espaços
    """
    cleaned_title = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    return cleaned_title

def search_similar_movies(movies_df: pd.DataFrame, 
                          vectorizer: TfidfVectorizer,
                          title: str) -> pd.DataFrame:
    """
    Captura os 5 filmes mais similares, por nome

    Args:
        movies_df (pd.DataFrame): Dataframe que contém os filmes
        vectorizer (TfidfVectorizer): Instância da classe TfidfVectorizer
        title (str): Título do filme
    """
    cleaned_title = clean_title(title)
    query_vec = vectorizer.transform([cleaned_title])
    similarity = cosine_similarity(query_vec, 
                                   vectorizer.fit_transform(movies_df["clean_title"])).flatten()
    indices = np.argpartition(similarity, -5)[-5:]
    results = movies_df.iloc[indices].iloc[::-1]
    return results
