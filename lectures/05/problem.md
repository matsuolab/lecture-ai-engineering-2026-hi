# Lecture 05 अभ्यास और होमवर्क: MCP सर्वर से टूल उपलब्ध कराएँ और इस्तेमाल करें

## इस Lecture के लक्ष्य

- Lecture 03 में बने टूल को **MCP सर्वर** में अलग करें और उसी एजेंट से **MCP के माध्यम से** इस्तेमाल करें।
- मॉडल को दिखने वाले टूल के "नाम, विवरण और तर्क" पढ़ें।
- **केवल सेटिंग फ़ाइल बदलकर** तैयार बाहरी टूल जोड़ें।

## तैयारी

पिछले Lecture का काम पूरा हो तो `main` से `lec05` ब्रांच बनाएँ। इस Lecture में निर्भरताएँ जुड़ती हैं, इसलिए एक बार `uv sync --frozen` चलाएँ।

```bash
git switch main && git switch -c lec05
uv sync --frozen
```

अन्यथा पाठ्यक्रम रिपॉज़िटरी के प्रारंभिक कोड (`lec05-start` टैग) से ब्रांच बनाएँ।

```bash
git remote -v                     # upstream न हो तो अगली पंक्ति से जोड़ें
git remote add upstream https://github.com/matsuolab/lecture-ai-engineering-2026.git
git fetch upstream --tags
git switch -c lec05 lec05-start
uv sync --frozen
```

## अभ्यास (30 मिनट)

### 1. मॉडल को उपलब्ध टूल देखें

```bash
uv run python -m app.agent --list-tools          # Lecture 03: सीधे फ़ंक्शन के रूप में पंजीकृत टूल
uv run python -m app.agent --mcp --list-tools    # Lecture 05: MCP सर्वर से मिले टूल
```

दोनों कमांड LLM को कॉल नहीं करतीं, इसलिए API कुंजी के बिना चलेंगी। दूसरी कमांड `app/mcp_servers.json` में निर्धारित सर्वर (`app/mcp_server.py`) को उपप्रक्रिया बनाकर शुरू करती है और उसके टूल के नाम, विवरण और तर्क दिखाती है।

- जाँचें कि नाम के आगे **"server_name_" उपसर्ग** है, जैसे `glossary_search_glossary`। इससे अलग सर्वरों के समान नाम वाले टूल अलग पहचाने जाते हैं।
- विवरण सीधे `app/tools.py` के docstring से आते हैं। **मॉडल को फ़ंक्शन टूल और MCP टूल एक जैसे दिखते हैं**।

### 2. एजेंट से MCP के माध्यम से इस्तेमाल करें

```bash
uv run python -m app.agent --mcp --trace "AIE2026 के होमवर्क के 3 स्तर क्या हैं?"
```

उत्तर, टूल नाम और `requests` की संख्या की तुलना Lecture 03 (`--mcp` के बिना) से करें। भीतर `app/agent.py` का `build_mcp_agent()` सेटिंग फ़ाइल पढ़ता है, सर्वर शुरू करता है और टूल एजेंट को देता है।

### 3. एक और टूल उपलब्ध कराएँ

`app/mcp_server.py` में `TODO(Lecture 05 अभ्यास)` पर `get_lecture_summary` भी MCP से उपलब्ध कराएँ (`search_glossary` जैसी एक पंक्ति)।

```bash
uv run python -m app.agent --mcp --list-tools
uv run python -m app.agent --mcp --trace "Lecture 02 में क्या सीखेंगे?"
uv run pytest -q
```

देखें कि `--list-tools` में `glossary_get_lecture_summary` दिखता है और `--trace` में बुलाया जाता है। Lecture 03 में `make_quiz` बनाया हो तो उसे भी इसी तरह उपलब्ध करा सकते हैं।

### 4. केवल सेटिंग से तैयार बाहरी टूल जोड़ें

सार्वजनिक **fetch सर्वर** (URL का पृष्ठ लेकर Markdown में लौटाता है) `app/mcp_servers.json` में जोड़ें। कोड बदलने की आवश्यकता नहीं है।

```json
{
  "mcpServers": {
    "glossary": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

```bash
uv run python -m app.agent --mcp --list-tools
uv run python -m app.agent --mcp --trace "https://modelcontextprotocol.io/ के शुरुआती भाग का 3 हिंदी पंक्तियों में सार लिखें"
```

- पहली बार शुरू होने में लगभग 10 सेकंड लगते हैं क्योंकि `uvx` सर्वर डाउनलोड करता है।
- `--trace` में `fetch_fetch({'url': ...})` दिखने का अर्थ है कि **आपका Codespace वास्तव में मॉडल के चुने URL पर पहुँच रहा है**। बाहरी टूल जोड़ने से पहले समझें कि वह कहाँ और क्या डेटा भेजता है।
- `INSTRUCTIONS` शब्दावली के उपयोग को मानता है। URL प्रश्न पर fetch न बुलाया जाए तो `INSTRUCTIONS` में "URL मिले तो उसकी सामग्री पढ़ने के लिए fetch इस्तेमाल करें" जैसी पंक्ति जोड़ें।

### 5. जमा करें

`lectures/05/answer.md` भरें और अपने fork में `lec05` से `main` को PR भेजें।

## होमवर्क (कोई एक स्तर पूरा करें)

| स्तर | कार्य |
|---|---|
| बुनियादी | `uv run python -m app.mcp_server --http` से सर्वर शुरू करें; सेटिंग फ़ाइल में `glossary` को `{"url": "http://127.0.0.1:8000/mcp"}` से बदलें और वही प्रश्न पूछें। stdio और Streamable HTTP में शुरू होने, प्रक्रियाओं और पोर्ट का अंतर लिखें। टूल docstring बदलकर `--list-tools` और टूल कॉल में अंतर भी देखें |
| कार्यान्वयन | Lecture 03 का `make_quiz` (या नया टूल) MCP सर्वर में जोड़ें और `tests/test_mcp_server.py` में TestModel से परीक्षण लिखें। तर्क की सीमाएँ जाँचें (जैसे अनुपस्थित Lecture पर स्पष्ट संदेश) और `--trace` से देखें कि MCP त्रुटियाँ मॉडल को कैसे दिखती हैं |
| उन्नत | वही शब्दावली सर्वर **Copilot Chat** (VS Code MCP क्लाइंट; निर्देश नीचे) से इस्तेमाल करें। सत्यापित करें कि "एक सर्वर कई क्लाइंट से इस्तेमाल हो सकता है" और एजेंट (`app/agent.py`) से तुलना करें। टूल कॉल तक पहुँचने के चरणों का अंतर लिखें: सर्वर कौन शुरू करता है, क्या पहले मानव अनुमति मिलती है और परिणाम कैसे दिखते हैं |

### उन्नत होमवर्क कैसे करें

Copilot Chat, VS Code में MCP क्लाइंट है। Chat के **Agent** mode में सर्वर के टूल इस्तेमाल करने के लिए रिपॉज़िटरी में `.vscode/mcp.json` रखें (इसमें `app/mcp_servers.json` के `mcpServers` की जगह `servers` होता है। कमांड कार्य फ़ोल्डर, यानी रिपॉज़िटरी root में चलती है)।

```json
{
  "servers": {
    "aie-glossary": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"]
    }
  }
}
```

1. Codespaces के VS Code में ऊपर की फ़ाइल बनाएँ। `servers` के ऊपर **Start** दिखे तो क्लिक करें; अन्यथा command palette में **MCP: List Servers** → `aie-glossary` → Start चुनें। सर्वर Codespace के भीतर शुरू होगा।
2. Copilot Chat खोलकर **Agent** mode चुनें। टूल सूची (🔧) में `aie-glossary` का `search_glossary` देखें (अभ्यास 3 पूरा किया हो तो `get_lecture_summary` भी)।
3. पूछें: "AIE2026 के होमवर्क के 3 स्तर क्या हैं?"। टूल कॉल से पहले **Continue** से पुष्टि माँगे तो स्वीकार करें और देखें कि उत्तर में शब्दावली टूल इस्तेमाल हुआ।
4. `answer.md` में Chat का टूल कॉल और `uv run python -m app.agent --mcp --trace` का आउटपुट साथ लिखें।
5. `.vscode/mcp.json` को PR में जोड़ सकते हैं (इसमें API कुंजी जैसे secrets न रखें)।

- Copilot Free में Agent mode और MCP हैं, लेकिन चैट की मासिक सीमा है; कुछ ही परीक्षण करें।
- कंपनी या विद्यालय द्वारा प्रबंधित Copilot (Business / Enterprise) में संगठन की नीति MCP बंद कर सकती है। व्यक्तिगत खाते से आज़माएँ।

## ध्यान दें

- MCP सर्वर **कोड चलाने वाला प्रोग्राम** है। अज्ञात स्रोत के सर्वर सेटिंग फ़ाइल में न जोड़ें।
- fetch सर्वर मॉडल के चुने URL पर जाता है। कंपनी के आंतरिक URL या निजी जानकारी वाले URL न दें।
- अधिक टूल का अर्थ मॉडल को अधिक विवरण भेजना है। इससे प्रति कॉल टोकन बढ़ते हैं और सही टूल चुनना कठिन होता है। `--list-tools` से टूल संख्या देखें।

## संदर्भ

- आधिकारिक MCP साइट: https://modelcontextprotocol.io/
- Pydantic AI MCP क्लाइंट: https://pydantic.dev/docs/ai/mcp/client/
- MCP Python SDK (सर्वर लिखना): https://github.com/modelcontextprotocol/python-sdk
- सार्वजनिक MCP सर्वर: https://github.com/modelcontextprotocol/servers
- VS Code में MCP सर्वर: https://code.visualstudio.com/docs/copilot/customization/mcp-servers
