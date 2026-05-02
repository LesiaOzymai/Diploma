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
    if not text or len(text.strip()) == 0:
        return "Текст відсутній для конспектування."

    sentences = sent_tokenize(text)

    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    sentences = [s for s in sentences if len(s.split()) > 6]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences)

    sentence_scores = tfidf_matrix.sum(axis=1)
    sentence_scores = np.array(sentence_scores).flatten()

    top_indices = sentence_scores.argsort()[-num_sentences:][::-1]
    top_indices = sorted(top_indices)

    summary = [sentences[i] for i in top_indices]

    return " ".join(summary)