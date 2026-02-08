import sys
from pathlib import Path

# Определяем корень репозитория (папка 'repo')
script_dir = Path(__file__).resolve().parent  # папка scripts/
repo_root = script_dir.parent                 # папка repo/

# Добавляем корень репозитория в пути поиска модулей
sys.path.insert(0, str(repo_root))

from src.preprocess.normalize import normalize_text

# Пути к файлам относительно корня репозитория (repo/)
raw_path = repo_root / "data" / "raw.txt"
output_path = repo_root / "data" / "text_clean.txt"

# Проверяем наличие входного файла
if not raw_path.exists():
    raise FileNotFoundError(
        f"Файл не найден: {raw_path}\n"
        f"Текущая директория: {Path.cwd()}\n"
        f"Попробуйте запустить из папки: {repo_root.parent}"
    )

# Читаем и обрабатываем текст
raw_text = raw_path.read_text(encoding="utf-8")
clean_text = normalize_text(raw_text)

# Сохраняем результат
output_path.parent.mkdir(exist_ok=True)
output_path.write_text(clean_text, encoding="utf-8")

print("✅ Готово! Результат сохранён в:", output_path)
print(f"   Длина: {len(clean_text)} символов")
print(f"   Уникальных символов: {len(set(clean_text))}")
print(f"   Разрешённые символы: {''.join(sorted(set(clean_text)))}")