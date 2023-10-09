""""
Scrypt destinado às funções que serão utilizadas na
main - movie_recommendation_system.
"""

# import libraries
import re
import os
import zipfile
import logging
import tqdm
import requests
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer