import re
from collections import Counter
from string import ascii_lowercase as letters
from pathlib import Path
import sys
import json

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

file = read_file(output_path)

letters = find_letters(file)
letters_dict = {'letters':letters}
write_file(letters_dict, letters_path)
print(letters_dict)

print('\n')

pairs = pairs_letters(file)
pairs_dict = {'pairs':pairs}
write_file(pairs_dict, pairs_path)
print(pairs_dict)

