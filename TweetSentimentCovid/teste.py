import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import tensorflow as tf
import gradio as gr

def load_data(train_path='./dataSet/Corona_NLP_train.csv', test_path='./dataSet/Corona_NLP_test.csv'):
    train_data = pd.read_csv(train_path, encoding='latin_1')
    test_data = pd.read_csv(test_path, encoding='latin_1')

    train_data.drop_duplicates(inplace=True)
    test_data.drop_duplicates(inplace=True)
    train_data.dropna(inplace=True)
    test_data.dropna(inplace=True)

    train_df = train_data.copy()
    test_df = test_data.copy()

    return train_df, test_df

def apply_sentiment_changes(data):
    def change_sen(sentiment):
        sentiment_mapping = {
            "Extremely Positive": 'positive',
            "Extremely Negative": 'negative',
            "Positive": 'positive',
            "Negative": 'negative',
        }
        return sentiment_mapping.get(sentiment, 'neutral')

    data['Sentiment'] = data['Sentiment'].apply(lambda x: change_sen(x))
    return data

def clean_text(text):
    stop_word = stopwords.words('english')
    text = re.sub(r'http\S+', " ", text)
    text = re.sub(r'@\w+', ' ', text)
    text = re.sub(r'#\w+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'<.*?>', ' ', text)
    text = text.split()
    text = " ".join([word for word in text if not word in stop_word])
    return text

def preprocess_data(data):
    data['OriginalTweet'] = data['OriginalTweet'].apply(lambda x: clean_text(x))
    return data

def map_sentiment_labels(data):
    df = data.iloc[:, 4:]
    sentiment_mapping = {"neutral": 0, "positive": 1, "negative": 2}
    df['Sentiment'] = df['Sentiment'].map(sentiment_mapping)
    return df

def prepare_data_for_model(df_train, df_test):
    x_train = df_train['OriginalTweet'].copy()
    x_test = df_test['OriginalTweet'].copy()
    y_train = df_train['Sentiment'].copy()
    y_test = df_test['Sentiment'].copy()

    max_len = np.max(x_train.apply(lambda x: len(x)))
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(x_train)
    vocab_length = len(tokenizer.word_index) + 1

    x_train = tokenizer.texts_to_sequences(x_train)
    x_test = tokenizer.texts_to_sequences(x_test)
    x_train = pad_sequences(x_train, maxlen=max_len, padding='post')
    x_test = pad_sequences(x_test, maxlen=max_len, padding='post')

    return x_train, x_test, y_train, y_test, vocab_length, max_len

def create_model(vocab_length, embedding_dim=16, max_len=0):
    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(vocab_length, embedding_dim, input_length=max_len),
        tf.keras.layers.Bidirectional(tf.keras.layers.GRU(256, return_sequences=True)),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])
    return model

def train_model(model, x_train, y_train, num_epochs=1, validation_data=None):
    history = model.fit(x_train, to_categorical(y_train, 3), epochs=num_epochs, validation_data=validation_data)
    return history

def evaluate_model(model, history, x_test, y_test):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    print(f"Accuracy on training data is: {acc[-1] * 100} %")
    print(f"Loss {loss[-1] * 100}")
    print(f"Accuracy on validation data is: {val_acc[-1] * 100} %")
    print(f"Loss {val_loss[-1] * 100}")

    epochs = range(len(acc))
    plt.plot(epochs, acc, 'b', label='training acc')
    plt.plot(epochs, val_acc, 'r', label='validation acc')
    plt.legend()
    plt.show()

    plt.plot(epochs, loss, 'b', label='training loss')
    plt.plot(epochs, val_loss, 'r', label='validation loss')
    plt.legend()
    plt.show()

    pred = model.predict(x_test)
    pred = np.argmax(pred, axis=1)
    cm = confusion_matrix(np.argmax(to_categorical(y_test, 3), 1), pred)
    sns.heatmap(cm, annot=True)

    print(classification_report(np.argmax(to_categorical(y_test, 3), 1), pred))

    return model

def preprocess_text(text, tokenizer, max_len):
    text = clean_text(text)
    text_sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(text_sequence, maxlen=max_len, padding='post')
    return padded_sequence

def predict_sentiment(input_text, model, tokenizer, max_len):
    preprocessed_text = preprocess_text(input_text, tokenizer, max_len)
    prediction = model.predict(preprocessed_text)
    predicted_class = np.argmax(prediction, axis=1)[0]

    output = "The input is classified as "

    if predicted_class == 0:
        output += "'neutral'."
    elif predicted_class == 1:
        output += "'positive'."
    elif predicted_class == 2:
        output += "'negative'."
    else:
        output = "Unexpected prediction."

    return output

    

def main():
    train_df, test_df = load_data()
    train_df = apply_sentiment_changes(train_df)
    test_df = apply_sentiment_changes(test_df)

    train_df = preprocess_data(train_df)
    test_df = preprocess_data(test_df)

    df_train = map_sentiment_labels(train_df)
    df_test = map_sentiment_labels(test_df)

    x_train, x_test, y_train, y_test, vocab_length, max_len = prepare_data_for_model(df_train, df_test)

    model = create_model(vocab_length, embedding_dim=16, max_len=max_len)

    num_epochs = 1
    history = train_model(model, x_train, y_train, num_epochs, validation_data=(x_test, to_categorical(y_test, 3)))

    evaluate_model(model, history, x_test, y_test)


main()

description_text = "Submit a short text to simulate a tweet. Your tweet can be classified as:\n"\
                    "- <b>Neutral:</b> do not express a positive or negative opinion related to COVID-19\n"\
                    "- <b>Positive:</b> express positive emotions related to COVID-19\n"\
                    "- <b>Negative:</b> express negative emotions related to COVID-19\n"

demo = gr.Interface(fn=predict_sentiment, inputs="text", outputs="text", title='Sentiment classifier for tweets related to COVID-19', description=description_text)
    
demo.launch(show_api=False)