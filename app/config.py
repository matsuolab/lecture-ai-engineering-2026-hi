"""पूरे पाठ्यक्रम के लिए साझा सेटिंग्स।

API कुंजी और मॉडल का नाम कोड में लिखने के बजाय पर्यावरण चर से पढ़ें।
"""

import os
from pathlib import Path

# डिफ़ॉल्ट मॉडल। पर्यावरण चर AIE_MODEL सेट करके इसे बदला जा सकता है।
#   उदाहरण: export AIE_MODEL=gemini-3.5-flash
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MODEL = os.getenv("AIE_MODEL", DEFAULT_MODEL)


# Lecture 05: हर पृष्ठ को एक खंड मानकर खोजें। इंडेक्स scripts/build_rag_index.py से बनता है।
ROOT = Path(__file__).resolve().parent.parent
RAG_SOURCE = ROOT / "data/rag_data/lectures.json"
RAG_TREE = ROOT / "data/rag_data/tree.json"
RAG_GRAPH = ROOT / "data/rag_data/graph.json"
RAG_DB = Path(os.getenv("AIE_RAG_DB", str(ROOT / "data/rag_data/index.sqlite3")))
RAG_DOCUMENT_IDS = ("lec01-main", "lec02-main", "lec03-main")
RAG_TOP_K = 5
GRAPH_START_K = 3
GRAPH_HOPS = 2
GRAPH_MAX_RESULTS = 10
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768
# 2,048 टोकन की सीमा में कार्य के निर्देश आदि के लिए जगह छोड़ें। सीमा पार हो तो पाठ काटने के बजाय रुकें।
EMBEDDING_MAX_TOKENS = 2000


def api_error_message(status: int, detail: str = "") -> str:
    """HTTP स्थिति कोड को विद्यार्थियों के लिए समझने योग्य संदेश में बदलें (ask.py और agent.py में साझा)।"""
    if status == 429:
        return "दर सीमा पूरी हो गई है। लगभग 1 मिनट प्रतीक्षा करके फिर चलाएँ।"
    if status == 503:
        return "मॉडल व्यस्त है (503)। थोड़ी देर प्रतीक्षा करके फिर चलाएँ।"
    if status in (400, 401, 403, 404):
        return f"API कुंजी या मॉडल के नाम में समस्या है ({status}): {detail}"
    return f"API त्रुटि ({status}): {detail}"


def get_api_key() -> str:
    """पर्यावरण चर GEMINI_API_KEY लौटाएँ। यह सेट न हो तो निर्देश दिखाकर प्रोग्राम बंद करें।"""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise SystemExit(
            "पर्यावरण चर GEMINI_API_KEY नहीं मिला।\n"
            "1. GitHub के Settings → Codespaces → Secrets में GEMINI_API_KEY जोड़ें और\n"
            "   इस्तेमाल की जाने वाली रिपॉज़िटरी के रूप में अपना fork चुनें।\n"
            "2. अगर Codespaces चालू करने के बाद secret जोड़ा है, तो Codespaces फिर से शुरू करें।\n"
            "   (नीचे बाएँ Codespaces → Stop Current Codespace → फिर से खोलें)"
        )
    return key
