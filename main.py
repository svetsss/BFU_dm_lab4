from pathlib import Path
import json

from normalize import preprocess_file
from huffman import run_huffman_analysis
from lzw import run_lzw_analysis


def percent_saved(bits: int, base_bits: int) -> float:
    if base_bits == 0:
        return 0.0
    return (1 - bits / base_bits) * 100


def make_summary(huffman_result: dict, lzw_result: dict,
                 output_path: str | Path = "data/results/summary.json") -> dict:
    output_path = Path(output_path)

    uniform_bits = huffman_result["uniform_bits"]
    huffman_bits = huffman_result["huffman_bits"]
    lzw_bits = lzw_result["lzw_bits"]

    methods = [
        {
            "method": "uniform_5_bit_code",
            "bits": uniform_bits,
            "average_bits_per_symbol": 5.0,
            "compression_ratio_to_uniform": 1.0,
            "saved_percent_to_uniform": 0.0,
        },
        {
            "method": "huffman_code",
            "bits": huffman_bits,
            "average_bits_per_symbol": huffman_result["huffman_average_bits_per_symbol"],
            "compression_ratio_to_uniform": huffman_result["huffman_compression_ratio_to_uniform"],
            "saved_percent_to_uniform": percent_saved(huffman_bits, uniform_bits),
        },
        {
            "method": "lzw_code",
            "bits": lzw_bits,
            "average_bits_per_symbol": lzw_result["lzw_average_bits_per_symbol"],
            "compression_ratio_to_uniform": lzw_result["lzw_compression_ratio_to_uniform"],
            "saved_percent_to_uniform": percent_saved(lzw_bits, uniform_bits),
        },
    ]

    best = min(methods, key=lambda item: item["bits"])

    summary = {
        "text_length": huffman_result["text_length"],
        "alphabet_size": huffman_result["alphabet_size"],
        "shannon_entropy_h1": huffman_result["shannon_entropy_h1"],
        "methods": methods,
        "best_method": best["method"],
        "comment": "The best method is the one with the smallest encoded bit length for this text.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    print("Лабораторная работа №4: методы кодирования")

    preprocess_info = preprocess_file()
    print("\n1. Подготовка текста")
    print(f"   Длина текста: {preprocess_info['length']} символов")
    print(f"   Количество различных символов: {preprocess_info['unique_symbols_count']}")

    huffman_result = run_huffman_analysis()
    print("\n2. Энтропия Шеннона и кодирование Хаффмана")
    print(f"   Равномерный 5-битный код: {huffman_result['uniform_bits']} бит")
    print(f"   Код Хаффмана: {huffman_result['huffman_bits']} бит")
    print(f"   Энтропия H1: {huffman_result['shannon_entropy_h1']:.4f} бит/символ")

    lzw_result = run_lzw_analysis()
    print("\n3. Кодирование LZW")
    print(f"   Количество кодов LZW: {lzw_result['codes_count']}")
    print(f"   LZW: {lzw_result['lzw_bits']} бит")
    print(f"   Проверка декодирования: {'пройдена' if lzw_result['decode_check'] else 'не пройдена'}")

    summary = make_summary(huffman_result, lzw_result)
    print("\n4. Итоговое сравнение")
    method_names = {
        "uniform_5_bit_code": "Равномерный 5-битный код",
        "huffman_code": "Код Хаффмана",
        "lzw_code": "LZW",
    }
    for method in summary["methods"]:
        display_name = method_names.get(method["method"], method["method"])
        print(
            f"   {display_name}: {method['bits']} бит, "
            f"экономия {method['saved_percent_to_uniform']:.2f}%"
        )

    best_method_name = method_names.get(summary["best_method"], summary["best_method"])
    print(f"\nЛучший метод: {best_method_name}")
    print("Результаты сохранены в папку data/results/")


if __name__ == "__main__":
    main()
