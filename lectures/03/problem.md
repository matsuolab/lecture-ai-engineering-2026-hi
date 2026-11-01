# Lecture 03 अभ्यास और होमवर्क: अध्ययन सहायक एजेंट बनाएँ

## इस सत्र के लक्ष्य

- अपने कोड में जाँचें कि एजेंट «मॉडल + लूप + टूल» से बनता है
- पढ़ सकें कि कौन से टूल किन arguments के साथ कॉल हुए
- एक टूल जोड़ सकें

## अभ्यास (30 मिनट)

पहले लगभग पाँच मिनट में Lecture 02 के होमवर्क की व्याख्या की जाएगी। उस दौरान चरण 1 में Sync fork दबाएँ और Codespaces शुरू कर लें (शुरू होने में कुछ मिनट लगते हैं)।

### 1. पाठ्यक्रम रिपॉज़िटरी के अपडेट लें और lec03 ब्रांच बनाएँ

कार्य ब्रांच बनाने से पहले पाठ्यक्रम रिपॉज़िटरी के बदलाव अपने fork में लाएँ।

1. GitHub में अपना fork खोलें और **Sync fork → Update branch** दबाएँ (यदि fork पहले से अपडेट है, तो Update branch नहीं दिखेगा और कुछ करने की ज़रूरत नहीं है)
2. Codespaces शुरू करें और टर्मिनल में ये कमांड चलाएँ

```bash
git switch main
git pull --no-rebase
git switch -c lec03
```

- यदि `git switch main` रुक जाए, तो पिछली Lecture की ब्रांच में ऐसे बदलाव बचे हैं जिनका commit नहीं हुआ है। उसी ब्रांच में उनका commit करके फिर प्रयास करें
- यदि `a branch named 'lec03' already exists` दिखे, तो `lec03` पहले ही बन चुकी है। `git switch lec03` से उस पर जाएँ
- यदि `git pull --no-rebase` में `CONFLICT` दिखे, तो `git merge --abort` से पिछली स्थिति में लौटें और नीचे दी विधि से शुरू करें (merge रद्द करने पर आपके अपने बदलाव सुरक्षित रहते हैं)

#### यदि main काम नहीं कर रही है या पिछली Lectures का काम पूरा नहीं हुआ है

यदि Sync fork में टकराव दिखे और Pull Request बनाने या «Discard commits» का विकल्प आए, तो **उन विकल्पों को न दबाएँ** और नीचे दी विधि से शुरू करें। «Discard commits» दबाने पर आपके अपने commits मिट जाते हैं।

पाठ्यक्रम रिपॉज़िटरी के शुरुआती कोड (`lec03-start` टैग) से ब्रांच बनाएँ।

```bash
git fetch https://github.com/matsuolab/lecture-ai-engineering-2026.git tag lec03-start
git switch -c lec03 lec03-start
```

### 2. एजेंट से वही प्रश्न पूछें जो Lecture 01 में पूछा था

```bash
uv run python -m app.agent "AIE2026 के होमवर्क के 3 स्तर क्या हैं?"
```

Lecture 01 के `app.ask` के उत्तर से तुलना करें। एजेंट उत्तर देने से पहले शब्दावली खोजता है। सही जानकारी `data/glossary.json` की `homework-levels` प्रविष्टि में है।

### 3. टूल कॉल पढ़ें

```bash
uv run python -m app.agent --trace "LoRA और QLoRA में क्या अंतर है?"
```

`[tool call]` वाली पंक्तियों में देखें कि मॉडल ने कौन से टूल किन arguments के साथ कॉल किए। `[usage]` का `requests` बताता है कि एक प्रश्न के लिए LLM को कितनी बार कॉल किया गया।

उत्तर देने से पहले खोजने और एक बार में एक ही शब्द खोजने का कारण मॉडल के निर्देशों में लिखा है। ये निर्देश दो जगह हैं:

- `app/agent.py` का `INSTRUCTIONS` (लगभग पंक्ति 31): पूरे एजेंट के निर्देश, जैसे «हमेशा search_glossary से शब्दावली जाँचें» और «उत्तर के अंत में संबंधित Lecture बताएँ (Lecture NN)»
- `app/tools.py` में हर टूल की docstring: यह टूल के विवरण के रूप में मॉडल को दी जाती है। `search_glossary` की docstring कहती है कि `query` में खोजने के लिए केवल एक शब्द डालें

होमवर्क के बुनियादी स्तर में इन निर्देशों को बदलकर व्यवहार में आने वाले अंतर की तुलना करेंगे।

### 4. make_quiz टूल लिखें और पंजीकृत करें

एजेंट को ऐसा बनाएँ कि «Lecture 02 से एक पुनरावृत्ति प्रश्न पूछो» कहने पर वह शब्दावली से प्रश्न बना सके। मॉडल `lecture=2` के साथ `make_quiz` कॉल करता है। टूल Lecture 02 का एक शब्द चुनकर प्रश्न और उत्तर लौटाता है, और मॉडल उनका उपयोग करके प्रश्न पूछता है।

1. `app/tools.py` में `make_quiz(lecture: int) -> str` फ़ंक्शन जोड़ें
2. docstring में लिखें कि टूल कब और किसलिए इस्तेमाल होना चाहिए (मॉडल इसे पढ़कर तय करता है कि टूल का उपयोग करना है या नहीं)
3. शब्दावली (`load_glossary()`) से वे शब्द चुनें जिनका `lecture` दिए गए सत्र से मेल खाता है, फिर उनमें से एक चुनें (जैसे `random.choice` से)
4. «इस शब्द का अर्थ क्या है?» जैसा प्रश्न और उसका उत्तर (उस शब्द की `definition`) एक स्ट्रिंग में लौटाएँ (जैसे `json.dumps` से)
5. `app/agent.py` के `TODO(Lecture 03 अभ्यास)` वाले स्थान पर `agent.tool_plain(tools.make_quiz)` से पंजीकृत करें

`make_quiz(2)` के लौटाए गए मान का उदाहरण:

```text
{"question": "PEFT का अर्थ क्या है?", "answer": "मॉडल के सभी पैरामीटरों के बजाय, …"}
```

### 5. जाँचें कि make_quiz कॉल होता है

```bash
uv run python -m app.agent --list-tools    # मॉडल को दिखाई देने वाले टूल (API कुंजी आवश्यक नहीं)
uv run python -m app.agent --trace "Lecture 02 की सामग्री से एक पुनरावृत्ति प्रश्न पूछो"
uv run pytest -q
```

यदि सूची में `make_quiz` और आपकी docstring दिखे तथा `[tool call] make_quiz({'lecture': 2})` जैसी पंक्ति आए, तो यह सफल है।

`uv run pytest -q` API कुंजी के बिना सभी टूल को, आपके जोड़े हुए `make_quiz` समेत, काल्पनिक arguments (जैसे `lecture=0`) के साथ कॉल करके जाँचता है कि वे त्रुटि से न रुकें। Lecture 0 मौजूद नहीं है, इसलिए कोई शब्द न मिलने की स्थिति को नहीं सँभाला हो तो परीक्षण असफल होगा। ऐसे में, शब्द न मिलने पर टूल से स्पष्ट संदेश लौटाएँ।

- सूची में नहीं है → `app/agent.py` में पंजीकृत नहीं किया है
- सूची में है पर कॉल नहीं होता → docstring में उपयोग की कोई स्पष्ट स्थिति लिखें। `INSTRUCTIONS` में «पुनरावृत्ति प्रश्न माँगे जाने पर make_quiz इस्तेमाल करें» जैसा निर्देश जोड़ें

### 6. जमा करें और Codespaces बंद करें

`lectures/03/answer.md` भरें और अपने ही fork में `lec03` से `main` के लिए PR बनाएँ। **जाँचें कि base repository आपका अपना fork है।**

```bash
git add -A
git commit -m "Lecture 03 अभ्यास"
git push -u origin lec03
```

यदि चरण 4 पूरा नहीं हुआ, तो चरण 3 तक के परिणाम जमा कर सकते हैं। आगे का काम उसी ब्रांच पर push करने से PR अपडेट हो जाएगा।

अंत में, नीचे बाईं ओर «Codespaces» → **Stop Current Codespace** चुनकर बंद करें।

## होमवर्क (कोई एक स्तर पूरा करें)

बुनियादी, कार्यान्वयन और उन्नत — इन तीन स्तरों में से एक चुनें। किसी एक स्तर पर काम करना होमवर्क पूरा करने के लिए पर्याप्त है।

| स्तर | कार्य |
|---|---|
| बुनियादी | अभ्यास में देखे गए `app/agent.py` के `INSTRUCTIONS` या `app/tools.py` के टूल की docstrings बदलें। वही प्रश्न `--trace` के साथ चलाएँ और टूल कॉल तथा उत्तरों में आए अंतर की तुलना करके लिखें |
| कार्यान्वयन | अध्ययन का रिकॉर्ड `learning_log/` फ़ोल्डर में सहेजने वाला `save_learning_log` टूल बनाएँ। सहेजना ऐसी कार्रवाई है जिसे वापस लेना कठिन है, इसलिए सहेजने से पहले उपयोगकर्ता की मंज़ूरी लें (Pydantic AI का `requires_approval=True`) |
| उन्नत | इनमें से एक चुनें: (a) अभ्यास वाले एजेंट के वही निर्देश और टूल रखें, केवल एजेंट बनाने वाला भाग Google के ADK में दोबारा लिखें, `adk run` से चलाएँ और कोड तथा उत्तरों की तुलना करें। (b) कोडिंग एजेंट Pi को Codespaces में चलाएँ और उसके सार्वजनिक सिस्टम प्रॉम्प्ट की तुलना अपने एजेंट के `INSTRUCTIONS` से करें |

जमा करने के लिए अभ्यास वाले `lectures/03/answer.md` के «होमवर्क» खंड में लिखें।

### बुनियादी स्तर पर कैसे काम करें

अभ्यास के चरण 3 में देखी गई दो जगहों में से एक बार में केवल एक जगह बदलें। वही प्रश्न `--trace` के साथ चलाएँ और तुलना करें।

- `app/agent.py` का `INSTRUCTIONS` (लगभग पंक्ति 31): पूरे एजेंट के निर्देश
- `app/tools.py` में हर टूल की docstring: टूल के विवरण के रूप में मॉडल को दी जाती है

उदाहरण के लिए ये बदलाव कर सकते हैं। कौन से टूल कॉल हुए, कितनी बार हुए, उनके arguments और उत्तर कैसे बदले, यह लिखें।

- `INSTRUCTIONS` से «हमेशा search_glossary से शब्दावली जाँचें» वाला निर्देश हटाने पर क्या एजेंट खोजे बिना उत्तर देता है?
- `search_glossary` की docstring में «query में केवल एक शब्द डालें» को «कई शब्द एक साथ डालें» करने पर खोज की संख्या और arguments कैसे बदलते हैं?
- `INSTRUCTIONS` में «उत्तर के अंत में संबंधित Lecture बताएँ (Lecture NN)» की जगह दूसरा निर्देश (जैसे «अंत में एक पुनरावृत्ति प्रश्न पूछें») देने पर उत्तर कैसे बदलता है?

### कार्यान्वयन स्तर पर कैसे काम करें

1. `app/tools.py` में `save_learning_log` बनाएँ और `app/agent.py` में `requires_approval=True` के साथ पंजीकृत करें
2. जब मॉडल यह टूल कॉल करता है, तो निष्पादन मंज़ूरी की प्रतीक्षा में रुकता है और परिणाम (`result.output`) के रूप में `DeferredToolRequests` लौटता है। इसलिए एजेंट के `output_type` में `DeferredToolRequests` जोड़ें (न जोड़ने पर त्रुटि होगी)

   ```python
   from pydantic_ai import Agent, DeferredToolRequests

   agent = Agent(instructions=INSTRUCTIONS,
                 output_type=[str, DeferredToolRequests])
   ```

3. CLI में `result.output.approvals` के हर कॉल के लिए उपयोगकर्ता से पूछें कि सहेजने की मंज़ूरी है या नहीं। इन निर्णयों (`DeferredToolResults`) और अब तक की बातचीत (`message_history=result.all_messages()`) को देकर `run_sync` फिर चलाएँ

विस्तार के लिए Pydantic AI के आधिकारिक «Deferred Tools» दस्तावेज़ में Human-in-the-Loop Tool Approval देखें: https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/

### उन्नत विकल्प (a) पर कैसे काम करें: ADK में दोबारा बनाएँ

अभ्यास वाले एजेंट के वही निर्देश और टूल इस्तेमाल करें और केवल एजेंट बनाने वाला भाग ADK में दोबारा लिखें।

| दायरा | विवरण |
|---|---|
| फिर इस्तेमाल करें | `app/agent.py` का `INSTRUCTIONS` और `app/tools.py` के `search_glossary` तथा `get_lecture_summary` (अभ्यास में `make_quiz` बनाया हो तो वह भी) |
| नया लिखें | `adk_agent/glossary_agent/` में `agent.py` (नीचे का कोड) और `__init__.py` (केवल `from . import agent` की एक पंक्ति) बनाएँ |
| आवश्यक नहीं | `--trace` जैसी कमांड सुविधाएँ, परीक्षण और मंज़ूरी वाले टूल। `app/` की फ़ाइलें न बदलें |
| तुलना करें | कोड लिखने का तरीका (निर्देश और टूल कैसे दिए जाते हैं) तथा अभ्यास वाले प्रश्नों के उत्तरों में अंतर |

`adk_agent/glossary_agent/agent.py` की संरचना:

```python
from google.adk.agents import Agent
from app import tools
from app.agent import INSTRUCTIONS

root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="glossary_agent",
    instruction=INSTRUCTIONS,
    tools=[...],  # अभ्यास में इस्तेमाल किए गए टूल
)
```

चलाने के लिए रिपॉज़िटरी के मूल फ़ोल्डर में यह कमांड चलाएँ:

```bash
PYTHONPATH=. uv run --with google-adk adk run adk_agent/glossary_agent
```

- `adk run` टर्मिनल में बातचीत करने का तरीका है। प्रश्न लिखकर Enter दबाएँ तो उत्तर मिलता है। समाप्त करने के लिए `exit` लिखें
- `uv run --with google-adk` इस बार चलाने के लिए ADK को पाठ्यक्रम के वातावरण में अस्थायी रूप से जोड़ता है। `pyproject.toml` या `uv.lock` नहीं बदलते
- रिपॉज़िटरी के मूल फ़ोल्डर से `app` आयात करने के लिए `PYTHONPATH=.` आवश्यक है
- Codespaces के मौजूदा `GEMINI_API_KEY` secret की API कुंजी इस्तेमाल होती है
- पहली बार ADK डाउनलोड होने में लगभग एक मिनट लगता है

अभ्यास वाले प्रश्न पूछें और Pydantic AI संस्करण से कोड तथा उत्तरों के अंतर लिखें।

ADK 2.0 में बड़े बदलाव हुए थे। वेब के कुछ परिचयात्मक लेखों में इन बदलावों से पहले की पुरानी जानकारी हो सकती है, इसलिए आधिकारिक दस्तावेज़ों के अनुसार लागू करने से गलतियाँ कम होंगी।

- आधिकारिक दस्तावेज़: https://adk.dev/

### उन्नत विकल्प (b) पर कैसे काम करें: Pi को Codespaces में चलाएँ

Pi एक कोडिंग एजेंट है जो मंज़ूरी माँगे बिना फ़ाइलें बदलता और कमांड चलाता है। इसे अपने PC के बजाय Codespaces में आज़माएँ।

1. **स्थापित करें**: Codespaces की टर्मिनल में यह कमांड चलाएँ

   ```bash
   npm install -g --ignore-scripts @earendil-works/pi-coding-agent
   ```

2. **शुरू करें**: टर्मिनल में `pi` लिखें
3. **मॉडल सेट करें**: Pi के अंदर `/model` लिखकर Gemini का मॉडल चुनें। Codespaces के मौजूदा `GEMINI_API_KEY` secret की API कुंजी इस्तेमाल होगी
4. **तुलना करें**: Pi का सिस्टम प्रॉम्प्ट सार्वजनिक रिपॉज़िटरी https://github.com/earendil-works/pi की `packages/coding-agent/src/core/system-prompt.ts` फ़ाइल में है। इसकी तुलना अपने `INSTRUCTIONS` से करें और देखें कि इसमें क्या है और क्या नहीं है

- Pi के आधिकारिक दस्तावेज़: https://github.com/earendil-works/pi/tree/main/packages/coding-agent/docs

## संदर्भ

- Pydantic AI: https://pydantic.dev/docs/ai/
- ADK: https://adk.dev/
