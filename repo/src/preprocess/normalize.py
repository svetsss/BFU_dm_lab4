def normalize_text(text: str) -> str:
    """
    Нормализует текст по требованиям лабы:
    1. Переводит в lowercase
    2. Оставляет ТОЛЬКО 32 разрешённых символа
    3. Гарантирует длину 12 000 символов

    Разрешённые символы (ровно 32):
    - Буквы a-z (26)
    - Пробел (1)
    - Знаки препинания: . , ! ? ; (5)
    """
    # 1. Приводим к lowercase
    text = text.lower()

    # 2. Фильтруем символы (оставляем ТОЛЬКО разрешённые)
    allowed_chars = "abcdefghijklmnopqrstuvwxyz .,!?;"
    cleaned_text = "".join(char for char in text if char in allowed_chars)

    # 3. Регулируем длину до 12 000 символов
    if len(cleaned_text) > 12000:
        # Обрезаем, если слишком длинный
        cleaned_text = cleaned_text[:12000]
    else:
        # Дополняем, если короткий (повторяем начало текста)
        while len(cleaned_text) < 12000:
            needed = 12000 - len(cleaned_text)
            cleaned_text += cleaned_text[:needed]

    return cleaned_text
