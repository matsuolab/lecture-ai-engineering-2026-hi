# Lecture 03 अभ्यास और होमवर्क: अध्ययन सहायक एजेंट बनाएँ

## इस Lecture के लक्ष्य

- अपने कोड में सत्यापित करें कि एजेंट = "मॉडल + लूप + टूल"।
- देखें कि कौन सा टूल किन तर्कों से बुलाया गया।
- एक टूल जोड़ें।

## तैयारी

पिछले Lecture का काम पूरा हो तो `main` से `lec03` ब्रांच बनाएँ।

```bash
git switch main && git switch -c lec03
```

अन्यथा पाठ्यक्रम रिपॉज़िटरी के प्रारंभिक कोड (`lec03-start` टैग) से ब्रांच बना सकते हैं।

```bash
git remote -v                     # upstream न हो तो अगली पंक्ति से जोड़ें
git remote add upstream https://github.com/matsuolab/lecture-ai-engineering-2026.git
git fetch upstream --tags
git switch -c lec03 lec03-start
```

## अभ्यास (30 मिनट)

### 1. एजेंट से Lecture 01 वाला प्रश्न पूछें

```bash
uv run python -m app.agent "AIE2026 में lecNN-start टैग क्या है?"
```

उत्तर की तुलना Lecture 01 के `app.ask` से करें।

### 2. टूल कॉल पढ़ें

```bash
uv run python -m app.agent --trace "LoRA और QLoRA में क्या अंतर है?"
```

`[tool call]` पंक्तियों में देखें कि मॉडल ने कौन से टूल किन तर्कों से बुलाए। `[usage]` में `requests` एक प्रश्न के लिए LLM कॉल की संख्या दिखाता है।

### 3. एक टूल जोड़ें

`app/tools.py` में `make_quiz` जोड़ें और `app/agent.py` में `TODO(Lecture 03 अभ्यास)` पर पंजीकृत करें।

- उदाहरण: दी गई Lecture (`lecture: int`) से एक शब्द चुनकर "इस शब्द का क्या अर्थ है?" प्रश्न और उसका उत्तर लौटाएँ।
- docstring में "इस टूल का उपयोग कब और क्यों करें" समझाएँ (मॉडल इसी से उपयोग तय करता है)।

```bash
uv run python -m app.agent --trace "Lecture 02 से एक पुनरावृत्ति प्रश्न दें"
uv run pytest -q
```

### 4. जमा करें

`lectures/03/answer.md` भरें और अपने fork में `lec03` से `main` को PR भेजें।

## होमवर्क (कोई एक स्तर पूरा करें)

| स्तर | कार्य |
|---|---|
| बुनियादी | `INSTRUCTIONS` या टूल docstring बदलें और `--trace` से टूल कॉल और उत्तरों का अंतर दर्ज करें |
| कार्यान्वयन | `learning_log/` में सीखने का रिकॉर्ड सहेजने वाला `save_learning_log` टूल बनाएँ। सहेजने से पहले उपयोगकर्ता की पुष्टि माँगें (Pydantic AI का `requires_approval=True`)। TestModel से परीक्षण भी लिखें |
| उन्नत | एक चुनें: (a) Google के ADK से वही एजेंट दोबारा बनाएँ और कोड तथा `adk web` में दिखने वाले व्यवहार की तुलना करें। (b) Lecture में बताए Pi को Codespaces में चलाएँ और उसके सार्वजनिक system prompt की अपने एजेंट के `INSTRUCTIONS` से तुलना करें |

### उन्नत विकल्प (b) कैसे करें

Pi कोडिंग एजेंट है जो फ़ाइलें पढ़-लिख सकता है और कमांड चला सकता है। हर टूल कॉल से पहले वह पुष्टि नहीं माँगता। इसे अपने PC के बजाय Codespaces के भीतर आज़माएँ।

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
pi
```

- Gemini `GEMINI_API_KEY` पर्यावरण चर पढ़ता है, इसलिए Codespaces secret सीधे काम करेगा। Pi में `/model` लिखकर Gemini मॉडल चुनें।
- npm पैकेज का नाम `@earendil-works/pi-coding-agent` है (पुराने लेखों का `@mariozechner/...` पुराना नाम है)।
- Pi का system prompt सार्वजनिक रिपॉज़िटरी में `packages/coding-agent/src/core/system-prompt.ts` पर है। इसे अपने `INSTRUCTIONS` से तुलना करके देखें कि क्या शामिल है और क्या नहीं। रिपॉज़िटरी: https://github.com/earendil-works/pi
- आधिकारिक दस्तावेज़: https://github.com/earendil-works/pi/tree/main/packages/coding-agent/docs

## संदर्भ

- Pydantic AI: https://ai.pydantic.dev/
- ADK: https://google.github.io/adk-docs/
