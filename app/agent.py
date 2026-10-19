"""Lecture 03: Pydantic AI से बना अध्ययन सहायक एजेंट।

उपयोग:
    uv run python -m app.agent "AIE2026 में इस्तेमाल होने वाला lecNN-start टैग क्या है?"
    uv run python -m app.agent --trace "LoRA और QLoRA में क्या अंतर है?"   # टूल कॉल दिखाएँ
    uv run python -m app.agent --mcp --trace "LoRA क्या है?"        # Lecture 05: MCP सर्वर से टूल लें
    uv run python -m app.agent --mcp --list-tools               # Lecture 05: मॉडल को उपलब्ध टूल की सूची (API कुंजी की आवश्यकता नहीं)

एजेंट = मॉडल + लूप + टूल।
मॉडल tools.py के फ़ंक्शन को टूल के रूप में बुलाता है और परिणाम से उत्तर बनाता है।
Lecture 05 में वही टूल MCP सर्वर (app/mcp_server.py) के माध्यम से मिलते हैं।
"""

import argparse
import inspect
import json
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError
from fastmcp import Client
from pydantic_ai.mcp import MCPToolset, StdioTransport
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.google import GoogleProvider

from app import tools
from app.config import MODEL, api_error_message, get_api_key

INSTRUCTIONS = """\
आप AI Engineering Pilot Course (AIE2026) के अध्ययन सहायक एजेंट हैं।
- किसी शब्द या पाठ्यक्रम से जुड़ी बात का उत्तर देने से पहले हमेशा search_glossary से शब्दावली जाँचें।
- किसी Lecture की सामग्री के बारे में पूछा जाए तो get_lecture_summary इस्तेमाल करें।
- जो बात शब्दावली में न मिले, उस पर अनुमान को तथ्य की तरह न कहें; बताएँ कि वह शब्दावली में नहीं है।
- उत्तर के अंत में संबंधित Lecture को "Lecture 03" जैसे प्रारूप में बताएँ।
- होमवर्क का सीधा उत्तर न लिखें; सोचने के संकेत देकर मार्गदर्शन करें।
"""

# मॉडल रनटाइम पर दें (ताकि परीक्षण में API कॉल के बिना TestModel लगा सकें)
agent = Agent(instructions=INSTRUCTIONS)
agent.tool_plain(tools.search_glossary)
agent.tool_plain(tools.get_lecture_summary)

# TODO(Lecture 03 अभ्यास): tools.py में make_quiz बनाएँ और यहाँ पंजीकृत करें

# Lecture 05: इस्तेमाल होने वाले MCP सर्वर की सेटिंग फ़ाइल। Claude Desktop और Cursor वाला "mcpServers" प्रारूप
MCP_CONFIG = Path(__file__).resolve().parent / "mcp_servers.json"


def load_mcp_servers(config_path: Path = MCP_CONFIG) -> list[MCPToolset]:
    """सेटिंग फ़ाइल (mcpServers प्रारूप) पढ़कर हर सर्वर के लिए कनेक्शन (MCPToolset) बनाएँ।

    - "command" हो तो stdio: सर्वर को उपप्रक्रिया के रूप में शुरू करें
    - "url" हो तो Streamable HTTP: चल रहे सर्वर से जुड़ें
    टूल के नाम के आगे "सर्वरनाम_" लगाएँ (जैसे glossary_search_glossary), ताकि कई सर्वरों में
    एक नाम के टूल होने पर भी उन्हें अलग पहचाना जा सके।

    Pydantic AI का load_mcp_toolsets() भी यही करता है। यहाँ इसे अलग से बनाया गया है क्योंकि
    पुराने SDK से बने सर्वर (जैसे fetch) से जुड़ते समय कनेक्शन का स्वतः चयन ("auto")
    बहुत चेतावनियाँ देता है। "legacy" रखने पर पुराने और नए दोनों सर्वर बिना अतिरिक्त चेतावनी के जुड़ते हैं।
    """
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))["mcpServers"]
    toolsets = []
    for name, spec in config.items():
        if "url" in spec:
            transport = spec["url"]
        else:
            transport = StdioTransport(spec["command"], spec.get("args", []), env=spec.get("env"))
        toolsets.append(MCPToolset(Client(transport, mode="legacy")).prefixed(name))
    return toolsets


def build_mcp_agent(config_path: Path = MCP_CONFIG) -> Agent:
    """Lecture 05: फ़ंक्शन सीधे पंजीकृत करने के बजाय MCP सर्वर के टूल इस्तेमाल करने वाला एजेंट। INSTRUCTIONS समान हैं।"""
    return Agent(instructions=INSTRUCTIONS, toolsets=load_mcp_servers(config_path))


def build_model() -> GoogleModel:
    return GoogleModel(MODEL, provider=GoogleProvider(api_key=get_api_key()))


def print_tools(target: Agent) -> None:
    """मॉडल को उपलब्ध टूल की सूची (नाम, विवरण और तर्क) दिखाएँ। LLM को कॉल नहीं करते।

    टूल सूची TestModel (परीक्षण के नकली मॉडल) को दें और उससे पढ़ें।
    मॉडल की दृष्टि में MCP सर्वर के टूल और Lecture 03 के फ़ंक्शन टूल एक जैसे होते हैं।
    """
    model = TestModel(call_tools=[])
    target.run_sync("टूल सूची", model=model)
    tools_seen = model.last_model_request_parameters.function_tools
    print(f"मॉडल को उपलब्ध टूल: {len(tools_seen)}")
    for tool in tools_seen:
        print(f"\n[{tool.name}]")
        print("  " + inspect.cleandoc(tool.description or "").replace("\n", "\n  "))
        params = tool.parameters_json_schema.get("properties", {})
        print(f"  तर्क: {json.dumps(params, ensure_ascii=False)}")


def print_trace(result) -> None:
    """दिखाएँ कि कौन सा टूल किन तर्कों से बुलाया गया और उसने क्या लौटाया।"""
    print("\n--- trace ---")
    for message in result.all_messages():
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                print(f"[tool call]   {part.tool_name}({part.args})")
            elif isinstance(part, ToolReturnPart):
                print(f"[tool return] {part.tool_name} -> {str(part.content)[:120]}…")
    print(f"[usage] {result.usage}")


def main() -> None:
    parser = argparse.ArgumentParser(description="अध्ययन सहायक एजेंट से प्रश्न पूछें")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--trace", action="store_true", help="टूल कॉल दिखाएँ")
    parser.add_argument("--mcp", action="store_true", help="Lecture 05: MCP सर्वर (app/mcp_servers.json) से टूल लें")
    parser.add_argument("--list-tools", action="store_true", help="मॉडल को उपलब्ध टूल की सूची दिखाकर बंद करें (API कुंजी आवश्यक नहीं)")
    args = parser.parse_args()

    target = build_mcp_agent() if args.mcp else agent
    if args.list_tools:
        print_tools(target)
        return
    if not args.question:
        parser.error("प्रश्न दें")

    print(f"[model] {MODEL}")
    if args.mcp:
        print("[tools] MCP सर्वर (app/mcp_servers.json)")
    try:
        result = target.run_sync(args.question, model=build_model())
    except ModelHTTPError as e:
        print(api_error_message(e.status_code, str(e.body)[:200]))
        raise SystemExit(1)
    print(result.output)
    if args.trace:
        print_trace(result)


if __name__ == "__main__":
    main()
