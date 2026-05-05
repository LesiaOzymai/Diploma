import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
    # Отримує функцію для створення небезпечного SSL-контексту (без перевірки сертифікатів)
except AttributeError:
    pass
    # Ігнорує помилку, якщо така функція відсутня
else:
    ssl._create_default_https_context = _create_unverified_https_context
    # Підміняє стандартний SSL-контекст для уникнення проблем із завантаженням ресурсів

nltk.download('punkt')
# Завантажує необхідний токенізатор для розбиття тексту на речення