# AIE2026 अभ्यास और होमवर्क रिपॉज़िटरी

यह रिपॉज़िटरी AI Engineering Pilot Course (AIE2026) के अभ्यास और होमवर्क के लिए है। पूरे पाठ्यक्रम में हम **AI इंजीनियरिंग सीखने में मदद करने वाले एजेंट** को क्रमशः विकसित करेंगे।

## आवश्यक वातावरण

अभ्यास **केवल ब्राउज़र से** किए जा सकते हैं। अपने कंप्यूटर पर कुछ स्थापित करने की आवश्यकता नहीं है।

| साधन | उपयोग | ध्यान दें |
|---|---|---|
| GitHub का **व्यक्तिगत** खाता | इस रिपॉज़िटरी को fork करें और कार्य ब्रांच तथा PR से जमा करें | कंपनी या विद्यालय के प्रबंधित खातों पर Codespaces और Copilot प्रतिबंधित हो सकते हैं |
| GitHub Codespaces | Lecture 01, Lecture 03 और Lecture 05 आदि का विकास वातावरण। `.devcontainer/` सेटिंग्स से Python 3.12, uv और Node.js वाला कंटेनर अपने आप बनता है | व्यक्तिगत खातों को महीने में 120 core-hours मुफ्त मिलते हैं (2 core पर लगभग 60 घंटे)। **काम पूरा होने पर इसे बंद करें** |
| GitHub Copilot (Free पर्याप्त है) | कोड सुझाव और चैट। Lecture 06 के उन्नत कार्य में MCP क्लाइंट के रूप में भी | Free योजना में प्रति माह सुझावों और चैट की सीमा है |
| Gemini API (Google AI Studio की मुफ्त योजना) | LLM को कॉल करना। **व्यक्तिगत** Google खाते से कुंजी बनाएँ और Codespaces secret `GEMINI_API_KEY` में दें | मुफ्त योजना में प्रति मिनट और प्रति दिन सीमा है (नीचे "पूर्वापेक्षाएँ और सीमाएँ" देखें) |
| Google Colab (T4 GPU, मुफ्त योजना) | केवल Lecture 02 में LoRA प्रशिक्षण | GPU समय सीमित है। काम पूरा होने पर रनटाइम हटाएँ |

अपने कंप्यूटर पर चलाने के लिए Python 3.12 और [uv](https://docs.astral.sh/uv/) स्थापित करें, `uv sync --frozen` चलाएँ और पर्यावरण चर `GEMINI_API_KEY` सेट करें।

## शुरुआत (Lecture 01)

1. इस रिपॉज़िटरी को अपने खाते में **fork** करें।
2. [Google AI Studio](https://aistudio.google.com/apikey) में Gemini API कुंजी बनाएँ।
3. GitHub के **Settings → Codespaces → Secrets** में `GEMINI_API_KEY` जोड़ें और इस्तेमाल होने वाली repository के रूप में अपना fork चुनें।
4. अपने fork में **Code → Codespaces → Create codespace on main** चुनें।
5. टर्मिनल में चलाकर जाँचें:

```bash
uv run pytest -q
uv run python -m app.ask "LoRA क्या है?"
```

पूरे चरणों के लिए [lectures/01/problem.md](lectures/01/problem.md) देखें।

<a id="lecture05-rag"></a>

## Lecture 05: पाठ्यक्रम की सामग्री में खोज

इस रिपॉज़िटरी के साथ मिलने वाले खोज DB में Lecture 01–03 की मुख्य सामग्री के 214 पृष्ठ हैं। यह जापानी स्रोत की एम्बेडिंग इस्तेमाल करता है और अनुवादित पाठ लौटाता है। पूरा संदर्भ देने वाले मोड में अभी 6 दस्तावेज़ और 342 पृष्ठ हैं। पहले सत्र का परिचय और Lecture 01 तथा 02 के अभ्यास जोड़ना बाकी है।

अभ्यास और होमवर्क के चरण [lectures/05/problem.md](lectures/05/problem.md) में और उत्तर लिखने की फ़ाइल [lectures/05/answer.md](lectures/05/answer.md) है। खोज DB `data/rag_data/index.sqlite3` इस रिपॉज़िटरी के साथ आता है; इसमें Lecture 01–03 की मुख्य कक्षाओं के 214 पृष्ठ हैं। `GEMINI_API_KEY` सेट करें और रिपॉज़िटरी की मुख्य डायरेक्टरी में निर्भरताएँ स्थापित करके खोज या उत्तर आज़माएँ। खोज के समय प्रश्न की एम्बेडिंग और उत्तर बनाने के लिए API इस्तेमाल होता है।

```bash
uv sync --frozen
uv run python -m app.retrieval "LoRA QLoRA अंतर"
uv run python -m app.agent --trace "LoRA और QLoRA में क्या अंतर है?"
uv run python -m app.agent --graph --trace "LoRA और QLoRA में क्या अंतर है?"
```

शिक्षण सामग्री का पाठ या एम्बेडिंग सेटिंग बदलें, तो प्रयोग के लिए अलग DB बनाएँ। जिस टर्मिनल में `AIE_RAG_DB` सेट करेंगे, वहाँ DB बनाने और खोजने दोनों के लिए उसी पथ का इस्तेमाल होगा।

```bash
export AIE_RAG_DB="$PWD/.cache/rag/custom.sqlite3"
uv run python -m scripts.build_rag_index
```

उसी प्रयोग वाले DB को दोबारा बनाने के लिए निर्माण के कमांड में `--rebuild` जोड़ें। साथ दिए गए DB पर लौटने के लिए `unset AIE_RAG_DB` चलाएँ। Tree मोड (`--tree`) और पूरी सामग्री एक साथ देने वाले मोड (`--full-context`) को खोज DB की आवश्यकता नहीं है।

## संरचना

```
.devcontainer/   Codespaces का वातावरण (Python 3.12, uv, Node.js; शुरू होने पर uv sync --frozen)
.github/workflows/test.yml  हर PR पर परीक्षण चलाता है (fork में Actions टैब से सक्रिय करना होगा)
app/
  config.py      मॉडल का नाम और API कुंजी पढ़ता है
  ask.py         Lecture 01: LLM से प्रश्न पूछता है
  tools.py       Lecture 03: एजेंट के टूल (जैसे शब्दावली खोज)
  agent.py       Lecture 03: Pydantic AI का अध्ययन सहायक एजेंट (Lecture 06: --mcp से MCP के माध्यम से)
  judge.py       Lecture 04: LLM से मूल्यांकन सेट जाँचें और मानव लेबल से सहमति दर निकालें
  retrieval.py   Lecture 05: सामग्री की खोज, Tree में खोज, Graph में खोज और पूरी सामग्री एक साथ देना
  mcp_server.py  Lecture 06: शब्दावली उपलब्ध कराने वाला MCP सर्वर
  mcp_servers.json Lecture 06: MCP सर्वर की सेटिंग (mcpServers प्रारूप)
data/
  glossary.json  पाठ्यक्रम की शब्दावली
  lectures/      प्रत्येक Lecture के मुख्य बिंदु
  eval/          Lecture 04: मूल्यांकन सेट (lec04_cases.jsonl) और मानदंड (rubric.md)
  rag_data/      Lecture 05: पाठ्यक्रम की सामग्री (lectures.json), विषय सूची (tree.json), पृष्ठों और शब्दों के संबंध (graph.json), खोज DB (index.sqlite3)
tools/
  annotate.py    Lecture 04: मूल्यांकन सेट को लेबल देने की स्क्रीन (Streamlit; uv run --with से अस्थायी रूप से जोड़कर चलाएँ)
.streamlit/      Streamlit की सेटिंग (Codespaces port forwarding से खोलने के लिए)
lectures/NN/
  problem.md     उस Lecture का अभ्यास और होमवर्क
  answer.md      भरकर जमा की जाने वाली फ़ाइल
notebooks/       Lecture 02: Google Colab में चलने वाली LoRA नोटबुक (lora_format_tuning.ipynb)
scripts/
  build_rag_index.py Lecture 05: सामग्री की एम्बेडिंग बनाकर खोज DB तैयार करें
  make_sft_dataset.py Lecture 02: प्रशिक्षण डेटा तैयार करें
tests/           परीक्षण (API कुंजी आवश्यक नहीं)
pyproject.toml / uv.lock  निर्भरताएँ और उनके तय संस्करण
```

## जमा करने का तरीका

1. हर Lecture के लिए कार्य ब्रांच बनाएँ (उदाहरण: `git switch -c lec01`)।
2. अभ्यास और होमवर्क करके `lectures/NN/answer.md` भरें।
3. push करें और **अपने ही fork में** कार्य ब्रांच → `main` के लिए PR बनाएँ।

होमवर्क के तीन स्तर हैं: "बुनियादी", "कार्यान्वयन" और "उन्नत"। इनमें से किसी एक को पूरा करना पर्याप्त है।

## पूर्वापेक्षाएँ और सीमाएँ

- **निर्भरताओं के संस्करण तय हैं** (`uv.lock`: Python 3.12, pydantic-ai-slim 2.57.0, google-genai 2.31.0)। पाठ्यक्रम के दौरान इन्हें नहीं बढ़ाएँगे। `uv sync --frozen` से स्थापित करें।
- **डिफ़ॉल्ट मॉडल `gemini-3.5-flash-lite` है**। पर्यावरण चर `AIE_MODEL` से बदल सकते हैं (नीचे "मॉडल बदलना" देखें)। दूसरे मॉडल या अपनी सदस्यता वाला API भी इस्तेमाल कर सकते हैं।
- **Gemini API की मुफ्त योजना में दर सीमा है**। एजेंट (Lecture 03 से) एक प्रश्न के लिए LLM को कई बार कॉल करता है, इसलिए Lecture 01 से जल्दी सीमा तक पहुँच सकता है। `दर सीमा पूरी हो गई है` दिखे तो लगभग 1 मिनट प्रतीक्षा करें। `मॉडल व्यस्त है (503)` बार-बार आए तो `AIE_MODEL=gemini-3.1-flash-lite` आज़माएँ।
- **API कुंजी केवल पर्यावरण चर `GEMINI_API_KEY` से दें**। उसे कोड, कमिट या चैट में न डालें। लीक होने पर AI Studio में पुरानी कुंजी हटाकर नई बनाएँ।
- Codespaces से इंटरनेट पर जा सकते हैं, लेकिन बाहर से Codespaces में नहीं जुड़ सकते (port forwarding डिफ़ॉल्ट रूप से निजी है)। Lecture 06 का MCP सर्वर Codespaces के भीतर चलता है।
- परीक्षण (`uv run pytest -q`) API कुंजी के बिना चलते हैं (LLM की जगह TestModel का उपयोग होता है)।

## आवश्यक सावधानियाँ

- **API कुंजी को कोड या कमिट में न लिखें।** Codespaces secret से दें।
- **काम पूरा होने पर Codespaces बंद करें।** मुफ्त सीमा खत्म होने पर वह शुरू नहीं होगा।
- Copilot जैसे AI टूल इस्तेमाल कर सकते हैं। सुझाए गए कोड को पढ़ें, समझें, फिर स्वीकार करें।

## मॉडल बदलना

डिफ़ॉल्ट मॉडल `gemini-3.5-flash-lite` है। पर्यावरण चर `AIE_MODEL` से इसे बदल सकते हैं।

```bash
AIE_MODEL=gemini-3.5-flash uv run python -m app.ask "LoRA क्या है?"
```

मुफ्त योजना में प्रति मिनट और प्रति दिन अनुरोधों की सीमा है। [Gemini API दर सीमा पृष्ठ](https://ai.google.dev/gemini-api/docs/rate-limits) पर वर्तमान सीमा देखें।
