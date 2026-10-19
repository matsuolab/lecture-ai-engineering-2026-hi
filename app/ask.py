"""Lecture 01: सामान्य LLM से एक प्रश्न पूछने की स्क्रिप्ट।

उपयोग:
    uv run python -m app.ask "LoRA क्या है?"
    uv run python -m app.ask            # प्रश्न न देने पर पाठ्यक्रम से जुड़ा प्रश्न पूछा जाता है

इस सामान्य कॉल में टूल या बातचीत का इतिहास नहीं होता।
पाठ्यक्रम के बारे में पूछने पर मॉडल या तो कह सकता है कि उसे पता नहीं, या सामान्य जानकारी के आधार पर भरोसेमंद लगने वाला उत्तर दे सकता है
(जो इस पाठ्यक्रम की वास्तविक जानकारी से अलग होगा)। इसे जाँचें।
(Lecture 03 में शब्दावली खोजने वाले एजेंट से इसे सुधारेंगे।)
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# पाठ्यक्रम से जुड़ा प्रश्न। सही उत्तर data/glossary.json में homework-levels के अंतर्गत है
DEFAULT_QUESTION = "AIE2026 के होमवर्क के 3 स्तर क्या हैं?"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    # TODO(Lecture 01 अभ्यास): response.usage_metadata से
    #   इनपुट और आउटपुट टोकन की संख्या दिखाएँ (Copilot की मदद ले सकते हैं)

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="सामान्य LLM से प्रश्न पूछें")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print(f"[प्रश्न] {args.question}\n")
    try:
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
