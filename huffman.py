from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import heapq
import json
import math
from typing import Optional


@dataclass(order=True)
class HuffmanNode:
    weight: int
    order: int
    symbol: Optional[str] = field(default=None, compare=False)
    left: Optional["HuffmanNode"] = field(default=None, compare=False)
    right: Optional["HuffmanNode"] = field(default=None, compare=False)


def count_ngrams(text: str, n: int) -> dict[str, int]:
    if n <= 0:
        raise ValueError("n must be positive")
    return dict(Counter(text[i:i + n] for i in range(len(text) - n + 1)))


def shannon_entropy(frequencies: dict[str, int]) -> float:
    total = sum(frequencies.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in frequencies.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def build_huffman_codes(frequencies: dict[str, int]) -> dict[str, str]:
    if not frequencies:
        return {}

    heap: list[HuffmanNode] = []
    for order, (symbol, weight) in enumerate(sorted(frequencies.items())):
        heapq.heappush(heap, HuffmanNode(weight=weight, order=order, symbol=symbol))

    if len(heap) == 1:
        only = heap[0]
        return {only.symbol: "0"}  # type: ignore[index]

    next_order = len(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(
            weight=left.weight + right.weight,
            order=next_order,
            left=left,
            right=right,
        )
        next_order += 1
        heapq.heappush(heap, parent)

    root = heap[0]
    codes: dict[str, str] = {}

    def walk(node: HuffmanNode, prefix: str) -> None:
        if node.symbol is not None:
            codes[node.symbol] = prefix
            return
        if node.left is not None:
            walk(node.left, prefix + "0")
        if node.right is not None:
            walk(node.right, prefix + "1")

    walk(root, "")
    return codes


def encoded_length_huffman(text: str, codes: dict[str, str]) -> int:
    return sum(len(codes[ch]) for ch in text)


def run_huffman_analysis(input_path: str | Path = "data/text_clean.txt",
                         output_path: str | Path = "data/results/huffman_results.json") -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)

    text = input_path.read_text(encoding="utf-8")
    char_frequencies = count_ngrams(text, 1)
    pair_frequencies = count_ngrams(text, 2)

    huffman_codes = build_huffman_codes(char_frequencies)
    huffman_bits = encoded_length_huffman(text, huffman_codes)
    uniform_bits = len(text) * 5

    result = {
        "text_length": len(text),
        "alphabet_size": len(char_frequencies),
        "uniform_code_bits_per_symbol": 5,
        "uniform_bits": uniform_bits,
        "shannon_entropy_h1": shannon_entropy(char_frequencies),
        "shannon_entropy_h2_pairs": shannon_entropy(pair_frequencies),
        "huffman_bits": huffman_bits,
        "huffman_average_bits_per_symbol": huffman_bits / len(text) if text else 0,
        "huffman_compression_ratio_to_uniform": huffman_bits / uniform_bits if uniform_bits else 0,
        "char_frequencies": dict(sorted(char_frequencies.items(), key=lambda item: (-item[1], item[0]))),
        "pair_frequencies_top_50": dict(sorted(pair_frequencies.items(), key=lambda item: (-item[1], item[0]))[:50]),
        "huffman_codes": dict(sorted(huffman_codes.items())),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    data = run_huffman_analysis()
    print("Анализ Хаффмана завершён")
    print(f"Равномерный 5-битный код: {data['uniform_bits']} бит")
    print(f"Код Хаффмана: {data['huffman_bits']} бит")
