""""
De um modo geral, esse scrypt indica 10 filmes baseados
no nome de um filme passado como parâmetro. Ele leva em
conta uma lista de filmes, que faremos download, e faz 
uso de processamento de texto.
"""
# import libraries
import pandas as pd

# https://files.grouplens.org/datasets/movielens/ml-25m.zip
movies = pd.read_csv("movies.csv")
