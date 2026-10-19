# AIE2026 अभ्यास और होमवर्क रिपॉज़िटरी

यह रिपॉज़िटरी AI Engineering Pilot Course (AIE2026) के अभ्यास और होमवर्क के लिए है। पूरे पाठ्यक्रम में हम **AI इंजीनियरिंग सीखने में मदद करने वाले एजेंट** को क्रमशः विकसित करेंगे।

## आवश्यक वातावरण

अभ्यास **केवल ब्राउज़र से** किए जा सकते हैं। अपने कंप्यूटर पर कुछ स्थापित करने की आवश्यकता नहीं है।

| साधन | उपयोग | ध्यान दें |
|---|---|---|
| GitHub का **व्यक्तिगत** खाता | इस रिपॉज़िटरी को fork करें और कार्य ब्रांच तथा PR से जमा करें | कंपनी या विद्यालय के प्रबंधित खातों पर Codespaces और Copilot प्रतिबंधित हो सकते हैं |
| GitHub Codespaces | Lecture 01, Lecture 03 और Lecture 05 आदि का विकास वातावरण। `.devcontainer/` सेटिंग्स से Python 3.12, uv और Node.js वाला कंटेनर अपने आप बनता है | व्यक्तिगत खातों को महीने में 120 core-hours मुफ्त मिलते हैं (2 core पर लगभग 60 घंटे)। **काम पूरा होने पर इसे बंद करें** |
| GitHub Copilot (Free पर्याप्त है) | कोड सुझाव और चैट। Lecture 05 के उन्नत कार्य में MCP क्लाइंट के रूप में भी | Free योजना में प्रति माह सुझावों और चैट की सीमा है |
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

## संरचना

```
.devcontainer/   Codespaces का वातावरण (Python 3.12, uv, Node.js; शुरू होने पर uv sync --frozen)
.github/workflows/test.yml  हर PR पर परीक्षण चलाता है (fork में Actions टैब से सक्रिय करना होगा)
app/
  config.py      मॉडल का नाम और API कुंजी पढ़ता है
  ask.py         Lecture 01: LLM से प्रश्न पूछता है
  tools.py       Lecture 03: एजेंट के टूल (जैसे शब्दावली खोज)
  agent.py       Lecture 03: Pydantic AI का अध्ययन सहायक एजेंट (Lecture 05: --mcp से MCP के माध्यम से)
  mcp_server.py  Lecture 05: शब्दावली उपलब्ध कराने वाला MCP सर्वर
  mcp_servers.json Lecture 05: MCP सर्वर की सेटिंग (mcpServers प्रारूप)
data/
  glossary.json  पाठ्यक्रम की शब्दावली
  lectures/      प्रत्येक Lecture के मुख्य बिंदु
lectures/NN/
  problem.md     उस Lecture का अभ्यास और होमवर्क
  answer.md      भरकर जमा की जाने वाली फ़ाइल
notebooks/       Lecture 02: Google Colab में चलने वाली LoRA नोटबुक (lora_format_tuning.ipynb)
scripts/         सहायक स्क्रिप्ट
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
- Codespaces से इंटरनेट पर जा सकते हैं, लेकिन बाहर से Codespaces में नहीं जुड़ सकते (port forwarding डिफ़ॉल्ट रूप से निजी है)। Lecture 05 का MCP सर्वर Codespaces के भीतर चलता है।
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
