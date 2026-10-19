"""Lecture 03: एजेंट को दिए जाने वाले टूल।

यहाँ लिखे फ़ंक्शन के docstring और type hints ही मॉडल के लिए टूल का विवरण बनते हैं।
विवरण बदलने से मॉडल का टूल इस्तेमाल करने का निर्णय और दिए जाने वाले तर्क बदल सकते हैं।
"""

import json
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3


@cache
def load_glossary() -> list[dict]:
    with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
        return json.load(f)["terms"]


def _normalize(text: str) -> str:
    return text.casefold().replace(" ", "").replace("　", "")


def _names(entry: dict) -> list[str]:
    return [_normalize(entry["term"]), _normalize(entry["id"])] + [
        _normalize(a) for a in entry["aliases"]
    ]


def search_glossary(query: str) -> str:
    """पाठ्यक्रम की शब्दावली में शब्द खोजें और उसकी परिभाषा तथा संबंधित Lecture लौटाएँ।

    AI इंजीनियरिंग या इस पाठ्यक्रम (AIE2026) से जुड़े किसी विशेष शब्द का
    उत्तर देने से पहले इसे इस्तेमाल करें। query में केवल एक खोज शब्द दें (जैसे "LoRA")।
    """
    q = _normalize(query)
    if not q:
        return "खोज शब्द खाली है। खोजने के लिए एक शब्द दें।"
    glossary = load_glossary()

    exact = [e for e in glossary if q in _names(e)]
    # "r" जैसे छोटे उपनाम हर चीज़ से न मिलें, इसलिए छोटे नामों को छोड़ें
    partial = [
        e for e in glossary
        if e not in exact and any(q in n or (len(n) >= 3 and n in q) for n in _names(e))
    ]
    in_definition = [
        e for e in glossary
        if e not in exact and e not in partial and q in _normalize(e["definition"])
    ]
    hits = (exact + partial + in_definition)[:MAX_RESULTS]

    if not hits:
        return f"शब्दावली में '{query}' नहीं मिला।"
    return json.dumps(
        [
            {
                "term": e["term"],
                "lecture": e["lecture"],
                "definition": e["definition"],
                "related": e["related"],
            }
            for e in hits
        ],
        ensure_ascii=False,
    )


def get_lecture_summary(lecture: int) -> str:
    """निर्दिष्ट Lecture (1 से शुरू होने वाला पूर्णांक) के मुख्य बिंदु लौटाएँ।

    "Lecture 03 में क्या सीखेंगे?" जैसे पाठ या संबंधों से जुड़े प्रश्नों के लिए इस्तेमाल करें।
    """
    path = DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = sorted(p.stem for p in (DATA_DIR / "lectures").glob("*.md"))
        return f"Lecture {lecture:02d} के मुख्य बिंदु अभी उपलब्ध नहीं हैं। उपलब्ध Lecture: {', '.join(available)}"
    return path.read_text(encoding="utf-8")
