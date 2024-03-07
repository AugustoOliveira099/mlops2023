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

# Reading the dataset
train_data = pd.read_csv("./dataSet/Corona_NLP_train.csv", encoding='latin_1')
test_data = pd.read_csv("./dataSet/Corona_NLP_test.csv", encoding='latin_1')

# Drop duplicates and 'NA' values
train_data.drop_duplicates(inplace=True)
test_data.drop_duplicates(inplace=True)
train_data.dropna(inplace=True)
test_data.dropna(inplace=True)

# Making checkpoint
train_df = train_data.copy()
test_df = test_data.copy()

# Applying the change_sen function/method
def change_sen(sentiment):
    """
    Return the sentiment type of the text
    """
    if sentiment == "Extremely Positive":
        return 'positive'
    elif sentiment == "Extremely Negative":
        return 'negative'
    elif sentiment == "Positive":
        return 'positive'
    elif sentiment == "Negative":
        return 'negative'
    else:
        return 'neutral'

train_df['Sentiment'] = train_df['Sentiment'].apply(lambda x: change_sen(x))
test_df['Sentiment'] = test_df['Sentiment'].apply(lambda x: change_sen(x))

# Data Clearning and processing
stop_word = stopwords.words('english')

def clean(text):
    text = re.sub(r'http\S+', " ", text)
    text = re.sub(r'@\w+', ' ', text)
    text = re.sub(r'#\w+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub('r<.*?>', ' ', text)
    text = text.split()
    text = " ".join([word for word in text if not word in stop_word])
    return text

train_df['OriginalTweet'] = train_df['OriginalTweet'].apply(lambda x: clean(x))
test_df['OriginalTweet'] = test_df['OriginalTweet'].apply(lambda x: clean(x))

# We only need "OriginalTweet" and "Sentiment"
df_train = train_df.iloc[:, 4:]
df_test = test_df.iloc[:, 4:]

# Now mapping the sentiment
l = {"neutral": 0, "positive": 1, "negative": 2}
df_train['Sentiment'] = df_train['Sentiment'].map(l)
df_test['Sentiment']  = df_test['Sentiment'].map(l)

x_train = df_train['OriginalTweet'].copy()
x_test = df_test['OriginalTweet'].copy()

y_train = df_train['Sentiment'].copy()
y_test = df_test['Sentiment'].copy()

# Maximum length of sequence
max_len = np.max(x_train.apply(lambda x: len(x)))

# Tokenizer initialization
tokenizer = Tokenizer()
tokenizer.fit_on_texts(x_train)
vocab_length = len(tokenizer.word_index) + 1

x_train = tokenizer.texts_to_sequences(x_train)
x_test = tokenizer.texts_to_sequences(x_test)

x_train = pad_sequences(x_train, maxlen=max_len, padding='post')
x_test = pad_sequences(x_test, maxlen=max_len, padding='post')

embedding_dim = 16

# Model Creation
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_length, embedding_dim, input_length=max_len),
    tf.keras.layers.Bidirectional(tf.keras.layers.GRU(256, return_sequences=True)),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(3, activation='softmax')
])
model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])

# Model training
num_epochs = 10
history = model.fit(x_train, to_categorical(y_train, 3), epochs=num_epochs, validation_data=(x_test, to_categorical(y_test, 3)))

# Model Accuracy and loss
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

print(f"Accuracy on training data is:- {acc[-1]*100} %")
print(f"Loss {loss[-1]*100}")
print(f"Accuracy on validation data is:- {val_acc[-1]*100} %")
print(f"Loss {val_loss[-1]*100}")

# Plotting
epochs = range(len(acc))
plt.plot(epochs, acc, 'b', label='training acc')
plt.plot(epochs, val_acc, 'r', label='validation acc')
plt.legend()
plt.show()

plt.plot(epochs, loss, 'b', label='training loss')
plt.plot(epochs, val_loss, 'r', label='validation loss')
plt.legend()
plt.show()

# Confusion Matrix
pred = model.predict(x_test)
pred = np.argmax(pred, axis=1)
cm = confusion_matrix(np.argmax(to_categorical(y_test, 3), 1), pred)
sns.heatmap(cm, annot=True)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# Classification Report
print(classification_report(np.argmax(to_categorical(y_test, 3), 1), pred))


def preprocess_text(text):
    # Aplicar as mesmas etapas de pré-processamento que foram feitas nos dados de treinamento
    text = clean(text)
    text_sequence = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(text_sequence, maxlen=max_len, padding='post')
    return padded_sequence

def predict_sentiment(input_text):
    preprocessed_text = preprocess_text(input_text)
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
    

description_text = "Submit a short text to simulate a tweet. Your tweet can be classified as:\n"\
                    "- <b>Neutral:</b> do not express a positive or negative opinion related to COVID-19\n"\
                    "- <b>Positive:</b> express positive emotions related to COVID-19\n"\
                    "- <b>Negative:</b> express negative emotions related to COVID-19\n"\
                    "- <b>Unexpected prediction.:</b> express a unknow input to COVID-19\n"

demo = gr.Interface(fn=predict_sentiment, inputs="text", outputs="text", title='Sentiment classifier for tweets related to COVID-19', description=description_text)
    
demo.launch(show_api=False)