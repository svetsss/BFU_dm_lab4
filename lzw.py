from __future__ import annotations

from pathlib import Path
import json
import math


def bits_needed(dictionary_size: int) -> int:
    return max(1, math.ceil(math.log2(max(dictionary_size, 2))))


def lzw_encode(text: str) -> tuple[list[int], list[int], list[str]]:
    if not text:
        return [], [], []

    alphabet = sorted(set(text))
    dictionary: dict[str, int] = {symbol: index for index, symbol in enumerate(alphabet)}
    next_code = len(dictionary)

    current = ""
    codes: list[int] = []
    widths: list[int] = []

    for symbol in text:
        candidate = current + symbol
        if candidate in dictionary:
            current = candidate
        else:
            codes.append(dictionary[current])
            widths.append(bits_needed(next_code))
            dictionary[candidate] = next_code
            next_code += 1
            current = symbol

    if current:
        codes.append(dictionary[current])
        widths.append(bits_needed(next_code))

    return codes, widths, alphabet


def lzw_decode(codes: list[int], alphabet: list[str]) -> str:
    if not codes:
        return ""

    dictionary: dict[int, str] = {index: symbol for index, symbol in enumerate(alphabet)}
    next_code = len(dictionary)

    previous = dictionary[codes[0]]
    result = [previous]

    for code in codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            entry = previous + previous[0]
        else:
            raise ValueError(f"Invalid LZW code: {code}")

        result.append(entry)
        dictionary[next_code] = previous + entry[0]
        next_code += 1
        previous = entry

    return "".join(result)


def run_lzw_analysis(input_path: str | Path = "data/text_clean.txt",
                     output_path: str | Path = "data/results/lzw_results.json") -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)

    text = input_path.read_text(encoding="utf-8")
    codes, widths, alphabet = lzw_encode(text)
    decoded = lzw_decode(codes, alphabet)

    if decoded != text:
        raise ValueError("LZW decode check failed: decoded text differs from input text.")

    lzw_bits = sum(widths)
    uniform_bits = len(text) * 5
    final_dictionary_size = len(alphabet) + max(0, len(codes) - 1)

    result = {
        "text_length": len(text),
        "alphabet_size": len(alphabet),
        "initial_alphabet": alphabet,
        "codes_count": len(codes),
        "final_dictionary_size": final_dictionary_size,
        "max_code_bit_width": max(widths) if widths else 0,
        "uniform_bits": uniform_bits,
        "lzw_bits": lzw_bits,
        "lzw_average_bits_per_symbol": lzw_bits / len(text) if text else 0,
        "lzw_compression_ratio_to_uniform": lzw_bits / uniform_bits if uniform_bits else 0,
        "decode_check": decoded == text,
        "encoded_codes": codes,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    data = run_lzw_analysis()
    print("Анализ LZW завершён")
    print(f"Количество кодов LZW: {data['codes_count']}")
    print(f"LZW: {data['lzw_bits']} бит")
