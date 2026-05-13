import re
from collections import Counter
from string import ascii_lowercase as letters
from pathlib import Path
import sys
import json
import heapq
import math

# Определяем корень репозитория (папка 'repo')
script_dir = Path(__file__).resolve().parent  # папка scripts/
repo_root = script_dir.parent                 # папка repo/

# Добавляем корень репозитория в пути поиска модулей
sys.path.insert(0, str(repo_root))

# Путь к файлу относительно корня репозитория (repo/)
output_path = repo_root / "data" / "text_clean.txt"
letters_path = repo_root / "data" / "find_letters.json"
pairs_path = repo_root / "data" / "find_pairs.json"
# Проверяем наличие входного файла
if not output_path.exists():
    raise FileNotFoundError(
        f"Файл не найден: {output_path}\n"
        f"Текущая директория: {Path.cwd()}\n"
        f"Попробуйте запустить из папки: {repo_root.parent}"
    )

def read_file(path): # читаем файл
    with open(path, encoding="utf8") as file:
        text = file.read()
    return text

def clean_text(text):
    clean = re.sub(r'[^a-z]', '', text.lower())
    return clean

def find_letters(text): # подсчёт количества букв
    clean = clean_text(text)
    cnt = Counter(clean)
    for letter in letters:
        cnt[letter] = cnt.get(letter, 0)
    return dict(cnt)

def pairs_letters(text):
    clean = clean_text(text)
    cnt = Counter()
    for i in range(len(clean)-1):
        pair = clean[i] + clean[i+1]
        cnt[pair] += 1
    return cnt

# запись
def write_file(all_entities, path):
    with open(path, "w", encoding='utf-8') as file:
        json.dump(all_entities, file, indent = 4, ensure_ascii=False)

class Node:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequencies):
    """Построение дерева Хаффмана из частот символов."""
    # Создаём приоритетную очередь (min-heap)
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(heap)

    # Объединяем узлы, пока не останется один
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = Node(
            char=None,
            freq=left.freq + right.freq,
            left=left,
            right=right
        )
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def generate_huffman_codes(root):
    """Генерация кодов Хаффмана путём обхода дерева."""
    codes = {}

    def traverse(node, code):
        if node:
            if node.char is not None:  # Лист — содержит символ
                codes[node.char] = code
            else:  # Внутренний узел
                traverse(node.left, code + '0')
                traverse(node.right, code + '1')

    traverse(root, '')
    return codes

def calculate_shannon_entropy(frequencies):
    """Расчёт энтропии Шеннона в битах на символ."""
    total = sum(frequencies.values())
    entropy = 0
    for freq in frequencies.values():
        if freq > 0:
            p = freq / total
            entropy -= p * math.log2(p)
    return entropy

def compare_encodings(text, letter_codes, pairs_codes, letters_count, pairs_count):
    """Сравнение различных методов кодирования."""
    cleaned_text = clean_text(text)

    # 1. Равномерное 5-битовое кодирование (буквы)
    uniform_5bit_letters = len(cleaned_text) * 5

    # 2. Кодирование Хаффмана (буквы)
    huffman_letters = sum(len(letter_codes[char]) for char in cleaned_text)

    # 3. Энтропия Шеннона (буквы)
    letter_entropy = calculate_shannon_entropy(letters_count)
    shannon_letters = len(cleaned_text) * letter_entropy

    print("=== СРАВНЕНИЕ ДЛЯ ОТДЕЛЬНЫХ БУКВ ===")
    print(f"Длина текста: {len(cleaned_text)} символов")
    print(f"Равномерное 5-битовое: {uniform_5bit_letters} бит")
    print(f"Хаффман: {huffman_letters} бит")
    print(f"По Шеннону (энтропия): {shannon_letters:.2f} бит")

    # Коэффициенты сжатия относительно равномерного
    ratio_huffman = uniform_5bit_letters / huffman_letters if huffman_letters > 0 else 0
    ratio_shannon = uniform_5bit_letters / shannon_letters if shannon_letters > 0 else 0

    print(f"Выигрыш Хаффмана: {ratio_huffman:.2f}x")
    print(f"Теоретический предел (Шеннон): {ratio_shannon:.2f}x")

    # Для пар букв
    pairs_in_text = [
        cleaned_text[i] + cleaned_text[i + 1]
        for i in range(len(cleaned_text) - 1)
    ]

    if pairs_in_text:
        # 4. Равномерное кодирование для пар (5 бит на букву → 10 бит на пару)
        uniform_5bit_pairs = len(pairs_in_text) * 10

        # 5. Хаффман для пар
        huffman_pairs = sum(len(pairs_codes[pair]) for pair in pairs_in_text)

        # 6. Энтропия для пар
        pair_entropy = calculate_shannon_entropy(pairs_count)
        shannon_pairs = len(pairs_in_text) * pair_entropy

        print("\n=== СРАВНЕНИЕ ДЛЯ ПАР БУКВ ===")
        print(f"Количество пар: {len(pairs_in_text)}")
        print(f"Равномерное (10 бит/пара): {uniform_5bit_pairs} бит")
        print(f"Хаффман: {huffman_pairs} бит")
        print(f"По Шеннону: {shannon_pairs:.2f} бит")

        ratio_huffman_pairs = uniform_5bit_pairs / huffman_pairs if huffman_pairs > 0 else 0
        ratio_shannon_pairs = uniform_5bit_pairs / shannon_pairs if shannon_pairs > 0 else 0

        print(f"Выигрыш Хаффмана: {ratio_huffman_pairs:.2f}x")
        print(f"Теоретический предел: {ratio_shannon_pairs:.2f}x")



file_content = read_file(output_path)
cleaned_text = clean_text(file_content)

# Подсчёт частот
letters_count = find_letters(file_content)
pairs_count = pairs_letters(file_content)

# Построение кодов Хаффмана
letter_tree = build_huffman_tree(letters_count)
letter_codes = generate_huffman_codes(letter_tree)

pair_tree = build_huffman_tree(pairs_count)
pair_codes = generate_huffman_codes(pair_tree)

# Построение кодов Хаффмана для отдельных букв
print("Коды Хаффмана для букв:")
letter_tree = build_huffman_tree(letters_count)
letter_codes = generate_huffman_codes(letter_tree)
print(letter_codes)

# Построение кодов Хаффмана для пар букв
print("\nКоды Хаффмана для пар букв:")
pair_tree = build_huffman_tree(pairs_count)
pair_codes = generate_huffman_codes(pair_tree)
print(pair_codes)


# Сравнение кодирований
compare_encodings(file_content, letter_codes, pair_codes, letters_count, pairs_count)

'''file_content = read_file(output_path)
cleaned_text = clean_text(file_content)  # Очищенный текст

letters_count = find_letters
# Подсчёт отдельных букв
letters_count = find_letters(file_content)
letters_dict = {'letters': letters_count}
write_file(letters_dict, letters_path)
print("Подсчёт букв:")
print(letters_dict)

print('\n')

# Построение кодов Хаффмана для отдельных букв
print("Коды Хаффмана для букв:")
letter_tree = build_huffman_tree(letters_count)
letter_codes = generate_huffman_codes(letter_tree)
print(letter_codes)

# Подсчёт пар букв
pairs_count = pairs_letters(file_content)
pairs_dict = {'pairs': pairs_count}
write_file(pairs_dict, pairs_path)
print("\nПодсчёт пар букв:")
print(pairs_dict)

# Построение кодов Хаффмана для пар букв
print("\nКоды Хаффмана для пар букв:")
pair_tree = build_huffman_tree(pairs_count)
pair_codes = generate_huffman_codes(pair_tree)
print(pair_codes)

# Расчёт сжатия для букв
original_bits, compressed_bits, ratio = calculate_compression_ratio(
    cleaned_text, letter_codes
)
print(f"\nСжатие для отдельных букв:")
print(f"Исходный размер: {original_bits} бит")
print(f"Сжатый размер: {compressed_bits} бит")
print(f"Коэффициент сжатия: {ratio:.2f}x")

# Для пар букв нужно преобразовать текст в пары
pairs_in_text = [
    cleaned_text[i] + cleaned_text[i + 1]
    for i in range(len(cleaned_text) - 1)
]
original_pairs_bits = len(pairs_in_text) * 16  # 2 символа × 8 бит
compressed_pairs_bits = sum(
    len(pair_codes[pair]) for pair in pairs_in_text
)
pair_ratio = original_pairs_bits / compressed_pairs_bits if compressed_pairs_bits > 0 else 0
print(f"\nСжатие для пар букв:")
print(f"Исходный размер: {original_pairs_bits} бит")
print(f"Сжатый размер: {compressed_pairs_bits} бит")
print(f"Коэффициент сжатия: {pair_ratio:.2f}x")'''