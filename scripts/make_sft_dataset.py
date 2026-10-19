"""Lecture 02 होमवर्क (उन्नत): शब्दावली से SFT के लिए प्रश्नोत्तर डेटा (JSONL) बनाएँ।

उपयोग:
    uv run python scripts/make_sft_dataset.py > glossary_sft.jsonl

बनी हुई फ़ाइल Colab में अपलोड करें और LoRA प्रशिक्षण डेटा के रूप में इस्तेमाल करें।
प्रश्न के अलग रूप जोड़ें, उपनामों से भी प्रश्न बनाएँ और कुछ डेटा सत्यापन के लिए अलग रखें।
"""

import json
import sys
from pathlib import Path

GLOSSARY = Path(__file__).resolve().parent.parent / "data" / "glossary.json"
TEMPLATES = ["{term} क्या है?", "{term} को संक्षेप में समझाएँ।"]


def main() -> None:
    terms = json.loads(GLOSSARY.read_text(encoding="utf-8"))["terms"]
    for t in terms:
        for template in TEMPLATES:
            record = {
                "messages": [
                    {"role": "user", "content": template.format(term=t["term"])},
                    {"role": "assistant", "content": t["definition"]},
                ]
            }
            sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
