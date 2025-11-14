import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from services.train_data import dataset

def treinar_modelo():
    textos = [t[0] for t in dataset]
    labels = [t[1] for t in dataset]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textos)

    modelo = LogisticRegression()
    modelo.fit(X, labels)

    with open("instance/model.pkl", "wb") as f:
        pickle.dump((vectorizer, modelo), f)

def carregar_modelo():
    with open("instance/model.pkl", "rb") as f:
        vectorizer, modelo = pickle.load(f)
    return vectorizer, modelo