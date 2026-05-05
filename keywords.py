from sklearn.feature_extraction.text import TfidfVectorizer

UKR_STOP_WORDS = [
    'і', 'та', 'або', 'а', 'але', 'що', 'як', 'це', 'на', 'в', 'у',
    'до', 'з', 'за', 'про', 'для', 'від', 'ми', 'вони', 'він', 'вона',
    'є', 'не', 'так', 'чи', 'щоб', 'я', 'ти', 'то', 'якщо', 'її', 'його', 'їх',
    'тому', 'при', 'цих', 'відповідно', 'саме', 'може', 'бути', 'яка', 'який', 'які',
    'цею', 'цього', 'даний', 'дана', 'також'
]


def extract_keywords(text, top_n=10):
    # Виділяє ключові слова з тексту на основі TF-IDF з урахуванням стоп-слів
    vectorizer = TfidfVectorizer(
        stop_words=UKR_STOP_WORDS,
        max_features=1000
    )

    tfidf_matrix = vectorizer.fit_transform([text])
    # Перетворює текст у TF-IDF матрицю

    feature_names = vectorizer.get_feature_names_out()
    # Отримує список усіх знайдених слів

    scores = tfidf_matrix.toarray()[0]
    # Отримує ваги (важливість) кожного слова

    word_scores = list(zip(feature_names, scores))

    # фільтр: довжина слова > 3 Відсіює занадто короткі слова
    word_scores = [ws for ws in word_scores if len(ws[0]) > 3]

    # Сортує слова за спаданням важливості
    sorted_words = sorted(word_scores, key=lambda x: x[1], reverse=True)


    keywords = []
    seen_roots = set()

    for word, score in sorted_words:
        # Проходить по словах у порядку важливості
        root = word[:5]

        if root not in seen_roots:
            # Уникає додавання схожих слів із однаковим коренем
            keywords.append(word)
            seen_roots.add(root)

        if len(keywords) >= top_n:
            break

    return keywords
