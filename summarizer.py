import ssl
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import nltk
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

def summarize_text(text, num_sentences=5):
    # Виконує автоматичне узагальнення тексту, обираючи найбільш значущі речення за TF-IDF
    if not text or len(text.strip()) == 0:
        # Перевіряє чи текст порожній або складається лише з пробілів
        return "Текст відсутній для конспектування."

    sentences = sent_tokenize(text)
    # Розбиває текст на окремі речення

    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    sentences = [s for s in sentences if len(s.split()) > 6]
    # Фільтрує короткі речення, залишаючи лише змістовні

    vectorizer = TfidfVectorizer()
    # Ініціалізує TF-IDF векторизатор для оцінки важливості слів

    tfidf_matrix = vectorizer.fit_transform(sentences)
    # Перетворює речення у TF-IDF матрицю

    sentence_scores = tfidf_matrix.sum(axis=1)
    # Обчислює вагу кожного речення як суму TF-IDF значень

    sentence_scores = np.array(sentence_scores).flatten()
    # Перетворює результати у зручний одновимірний масив

    top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
    # Обирає індекси речень з найвищими оцінками

    top_indices = sorted(top_indices)
    summary = [sentences[i] for i in top_indices]
    return " ".join(summary)