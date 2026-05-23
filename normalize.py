from pathlib import Path
import string

ALPHABET = string.ascii_lowercase + " .,!?;"
TARGET_LENGTH = 12_000


def normalize_text(text: str, target_length: int = TARGET_LENGTH) -> str:
    text = text.lower()

    text = " ".join(text.split())

    cleaned = []
    for ch in text:
        if ch in ALPHABET:
            cleaned.append(ch)
        elif ch in "\n\r\t":
            cleaned.append(" ")

    result = "".join(cleaned)
    result = " ".join(result.split())

    if not result:
        raise ValueError("After normalization the text is empty. Check data/raw.txt.")

    while len(result) < target_length:
        result += " " + result

    return result[:target_length]


def preprocess_file(input_path: str | Path = "data/raw.txt",
                    output_path: str | Path = "data/text_clean.txt",
                    target_length: int = TARGET_LENGTH) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)

    raw_text = input_path.read_text(encoding="utf-8")
    clean_text = normalize_text(raw_text, target_length=target_length)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(clean_text, encoding="utf-8")

    return {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "length": len(clean_text),
        "unique_symbols_count": len(set(clean_text)),
        "unique_symbols": "".join(sorted(set(clean_text))),
        "allowed_symbols_count": len(ALPHABET),
    }


if __name__ == "__main__":
    info = preprocess_file()
    print("Подготовка текста завершена")
    print(f"Длина текста: {info['length']} символов")
    print(f"Количество различных символов: {info['unique_symbols_count']}")
