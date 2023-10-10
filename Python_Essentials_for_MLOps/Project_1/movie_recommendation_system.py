""""
De um modo geral, este script indica 10 filmes baseados
no nome de um filme passado como parâmetro e na classificação
dos filmes pelos usuários
"""
# import libraries
import os
import zipfile
import argparse
import logging
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from functions import clean_movie_title, \
                      search_similar_movies_by_title, \
                      find_similar_movies, \
                      download_zip_file

# Verifica se o script está sendo executado como programa principal
if __name__ == '__main__':
    # Configuração inicial do logging
    # Com level logging.INFO, também é englobado o level logging.ERROR
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Iniciando o parse para receber o título do filme como parâmetro
    parser = argparse.ArgumentParser(description="Movie Recommendation System")
    parser.add_argument("--title", type=str, help="The title of the movie")
    args = parser.parse_args()

    # get the movie title
    movie_title = args.title

    # read the data
    try:
        if not os.path.exists("ml-25m"):
            logging.info("Downloading the zip file")

            download_zip_file()
        else:
            logging.info("The data is already downloaded")
    except requests.exceptions.ConnectionError:
        logging.error("Connection Error")
    except requests.exceptions.Timeout:
        logging.error("Timeout Error")
    except requests.exceptions.HTTPError:
        logging.error("HTTP Error")
    except zipfile.BadZipFile:
        logging.error("The downloaded file is not a valid ZIP file.")

    # Importando o arquivo
    logging.info("Getting the data")
    movies_df = pd.read_csv("ml-25m/movies.csv")

    # Limpando o título do filme
    logging.info("Cleaning the movie title")
    movies_df["clean_title"] = movies_df["title"].apply(clean_movie_title)

    # Instanciando o TF-IDF vectorizer
    logging.info("Instantiating the TF-IDF vectorizer")
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1,2))

    # Ajustando e transformando os dados com base na instância TF-IDF
    logging.info("Ajustando e transformando os dados")
    tfidf_matrix = tfidf_vectorizer.fit_transform(movies_df["clean_title"])

    # Obtém os 5 filmes mais similares a partir do título
    results = search_similar_movies_by_title(movies_df, tfidf_vectorizer, movie_title)

    # Lendo os dados de classificação dos filmes
    ratings_df = pd.read_csv("ml-25m/ratings.csv")

    # Encontrando os filmes similares
    logging.info("Finding the similar movies")
    movies_recommendations = find_similar_movies(results.iloc[0]["title"], movies_df, ratings_df)

    # Exibe as recomendações
    if movies_recommendations.empty:
        print(f"No recommendations could be found based on the movie {movie_title}.")
        print("Please, check if there are no spelling errors in the provided title.")
        print("If the error persists, change the movie title.")
    else:
        print(f"\n\nOur 10 recommendations for you, based on the movie {movie_title}, are:\n")
        i = 0
        for index, row in movies_recommendations.iterrows():
            i += 1
            title = row["title"]
            genres = row["genres"]
            print(f"{i}. {title} {genres}")
            