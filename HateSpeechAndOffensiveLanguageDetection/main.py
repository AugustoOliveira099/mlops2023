#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import os
import re
import string
import gradio as gr
from enum import Enum

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV

import xgboost as xgb
import lightgbm as lgb
import seaborn as sns
import matplotlib.pyplot as plt

HATE_SPEECH = ['Neutral', 'Offensive Language', 'Hate Speech']

# Download necessary NLTK resources
nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('all')

sns.set(style="darkgrid")

# Data Exploration

data = pd.read_csv('./dataSet/train.csv')

print(data.head())
print(data['class'].value_counts())
print(data.describe())
print(data.isna().sum())
print(data.duplicated().sum())

fdata = data[['tweet', 'class']]

# Data Processing

# URL Removal
fdata["tweet"] = fdata["tweet"].apply(lambda x: re.sub(r'https?://\S+', ' ', str(x)))

# Lowercase Removal
fdata['tweet'] = fdata['tweet'].apply(lambda x: " ".join(x.lower() for x in x.split()))

# Punctuation Removal
fdata['tweet'] = fdata['tweet'].str.replace('[^\w\s]', '')

# Username/Handles Removal
fdata["tweet"] = fdata["tweet"].apply(lambda x: re.sub(r'@\w+', '', str(x)))

# Emoji Removal
def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

fdata["tweet"] = fdata["tweet"].apply(str)
fdata["tweet"] = fdata["tweet"].apply(remove_emoji)

# Single character and double space removal
fdata["tweet"] = fdata["tweet"].apply(lambda x: re.sub(r'\s+[a-zA-Z]\s+', '', x))
fdata["tweet"] = fdata["tweet"].apply(lambda x: re.sub(r'\s+', ' ', x, flags=re.I))

# Remove words "rt" and colons ":"
def remove_words_and_colons(text):
    words_to_remove = ["rt"]
    for word in words_to_remove:
        text = text.replace(word, "")
    text = text.replace(":", "")
    return text

fdata['tweet'] = fdata['tweet'].apply(remove_words_and_colons)

# Lambda function to remove special and numeric characters
remove_special_and_numeric = lambda text: re.sub(r"[^a-zA-Z\s]+", "", text)
fdata['tweet'] = fdata['tweet'].apply(remove_special_and_numeric)

# Stopword Removal
STOPWORDS = set(stopwords.words('english'))
def remove_stopwords(text):
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])

fdata["Text_stop"] = fdata["tweet"].apply(lambda text: remove_stopwords(text))

# Feature Engineering

# Tokenization of data
def tokenization(text):
    text = re.split('\W+', text)
    return text

fdata['Text_tokenized'] = fdata['Text_stop'].apply(lambda x: tokenization(x.lower()))

# Lemmatization of Data
nltk.download('wordnet')
wordNet = WordNetLemmatizer()
def lemmatizer(text):
    text = [wordNet.lemmatize(word) for word in text]
    return text

fdata['Text_lemmatized'] = fdata['Text_tokenized'].apply(lambda x: lemmatizer(x))

# Data Modeling

X = fdata["Text_stop"]
y = fdata["class"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

# Performing TF-IDF Conversion
vectoriser = TfidfVectorizer(ngram_range=(1,2), max_features=500000)
vectoriser.fit((X_train).values.astype('U'))
print('No. of feature_words: ', len(vectoriser.get_feature_names_out()))

X_train = vectoriser.transform((X_train).values.astype('U'))
X_test  = vectoriser.transform((X_test).values.astype('U'))

# Model Evaluation
def model_evaluate(model, X_test):
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    cf_matrix = confusion_matrix(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    cm_df = pd.DataFrame(cm,
                     index=['hate speech', 'offensive language', 'Neutral'],
                     columns=['hate speech', 'offensive language', 'Neutral'])

    plt.figure(figsize=(5, 4))
    sns.heatmap(cm_df, annot=True, cmap="Oranges", linecolor="gray")
    plt.title('Confusion Matrix')
    plt.ylabel('Actual Values')
    plt.xlabel('Predicted Values')
    plt.show()

# # Logistic Regression Model
# lr_model = LogisticRegression(C=1, max_iter=1000, penalty='l2', n_jobs=-1)
# lr_model.fit(X_train, y_train)

# model_evaluate(lr_model, X_test)

# # Decision Tree Model
# dtmodel = DecisionTreeClassifier()
# dtc = dtmodel.fit(X_train, y_train)
# model_evaluate(dtc, X_test)

# # K-Neighbors Classifier
# neigh = KNeighborsClassifier(n_neighbors=3)
# neigh.fit(X_train, y_train)
# model_evaluate(neigh, X_test)

# # Random Forest Classifier
# rfc = RandomForestClassifier(n_estimators=10)
# rfc.fit(X_train, y_train)
# model_evaluate(rfc, X_test)

# #XGB Classifier
# xgb_model=xgb.XGBClassifier(objective="multi:softprob")
# xgb_model.fit(X_train, y_train)
# model_evaluate(xgb_model, X_test)

# LGBM Classifier
modelLGBM = lgb.LGBMClassifier()
modelLGBM.fit(X_train,y_train)
model_evaluate(modelLGBM, X_test)

# Hyperparameter Tuning to LGBM Classifier
model = lgb.LGBMClassifier()
# Define hyperparameters for tuning
param_grid = {
    'n_estimators': [100, 200],
    'learning_rate': [0.01, 0.05, 0.1],
    'max_depth': [3, 5, 7]
}
# Initialize RandomizedSearchCV
random_search = RandomizedSearchCV(estimator=model, param_distributions=param_grid,
                                   n_iter=8, scoring='accuracy', cv=3, random_state=42)

# Fit the model
random_search.fit(X_train, y_train)

# Print the best parameters and the best score
print("Best Parameters:", random_search.best_params_)
print("Best Score:", random_search.best_score_)

# Evaluate the model with best parameters on the test set
best_model = random_search.best_estimator_
test_score = best_model.score(X_test, y_test)
print("Test Score:", test_score)

model_evaluate(best_model,X_test)

def preprocessing_entry(text):
  # URL Removal
  clean_text = re.sub(r'https?://\S+', '', text)
  # Lowercase
  clean_text = " ".join(word.lower() for word in clean_text.split())
  # Punctuation removal
  clean_text = clean_text.replace('[^\w\s]','')
  # Remove usernames/handles
  clean_text = re.sub(r'@\w+', '', clean_text)
  # Emoji Removal
  clean_text = remove_emoji(clean_text)
  # Single character and double space removal
  clean_text = re.sub(r'\s+[a-zA-Z]\s+', ' ', clean_text)
  clean_text = re.sub(r'\s+', ' ', clean_text, flags=re.I)
  # Remove words "rt" and colons ":"
  clean_text = remove_words_and_colons(clean_text)
  # Remove special and numeric characters
  clean_text = remove_special_and_numeric(clean_text)
  # Stopword removal
  clean_text = remove_stopwords(clean_text)

  return clean_text


def predict_entry(text):
  clean_text = preprocessing_entry(text)
  text_vetorized = vectoriser.transform([clean_text])

  prev = best_model.predict(text_vetorized)
  prevProba = best_model.predict_proba(text_vetorized)
  classes = best_model.classes_

  resp = f"O nível de discurso de ódio para a entrada é {HATE_SPEECH[prev[0]]}. Considerando uma probabilidade de {round(prevProba[0][0]*100, 2)}% para '{HATE_SPEECH[classes[0]]}', {round(prevProba[0][1]*100, 2)}% para '{HATE_SPEECH[classes[1]]}' e {round(prevProba[0][2]*100, 2)}% para '{HATE_SPEECH[classes[2]]}'."

  return resp


demo = gr.Interface(fn=predict_entry, inputs="text", outputs="text")
    
demo.launch(show_api=False)
