"""लेक्चर 06 का अध्ययन सहायक एजेंट और MCP क्लाइंट।

    uv run python -m app.mcp_agent --list-tools
    uv run python -m app.mcp_agent --trace "LoRA क्या है?"

लेक्चर 03 में tools.py के फ़ंक्शन सीधे एजेंट में पंजीकृत किए गए थे।
यहाँ एजेंट app/mcp_servers.json में दर्ज सर्वरों के उपलब्ध टूल खोजता है।
मॉडल, लूप और टूल की संरचना पहले जैसी रहती है।
"""

import argparse
import inspect
import json
from pathlib import Path

from fastmcp import Client
from mcp.shared.exceptions import MCPError
from pydantic_ai import Agent
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UserError
from pydantic_ai.mcp import MCPToolset, StdioTransport
from pydantic_ai.messages import RetryPromptPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.test import TestModel
from pydantic_ai.providers.google import GoogleProvider

from app.config import MODEL, api_error_message, get_api_key

# शब्दावली और सेटिंग में दर्ज अन्य सर्वरों के इस्तेमाल के निर्देश।
INSTRUCTIONS = """\
आप AI इंजीनियरिंग पाठ्यक्रम (AIE2026) के अध्ययन सहायक एजेंट हैं। हिंदी में उत्तर दें।
- किसी शब्द या पाठ्यक्रम से जुड़े सवाल का उत्तर देने से पहले search_glossary से शब्दावली देखें।
- किसी लेक्चर की सामग्री पूछे जाने पर get_lecture_summary इस्तेमाल करें।
- शब्दावली में जानकारी न मिले तो यह साफ़ बताएँ और अनुमान से जवाब न दें।
- उत्तर के अंत में संबंधित लेक्चर नंबर (Lecture N) लिखें।
- होमवर्क हल करने का तरीका सुझाएँ ताकि विद्यार्थी खुद उत्तर निकाल सके।
- वेब पेज और AWS दस्तावेज़ जैसे शब्दावली के बाहर के विषयों के लिए उपलब्ध उपयुक्त टूल इस्तेमाल करें।
"""

# Claude Desktop और Cursor की तरह "mcpServers" प्रारूप में सर्वर सेटिंग।
MCP_CONFIG = Path(__file__).resolve().parent / "mcp_servers.json"


class ConfigError(Exception):
    """app/mcp_servers.json की सेटिंग में त्रुटि।"""


def read_config(config_path: Path = MCP_CONFIG) -> dict:
    """mcpServers से सर्वरों के नाम और उनकी सेटिंग लौटाएँ।"""
    try:
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))["mcpServers"]
    except json.JSONDecodeError as e:
        raise ConfigError(f"पंक्ति {e.lineno} के पास अमान्य JSON ({e.msg})") from e
    except KeyError as e:
        raise ConfigError('"mcpServers" नहीं मिला') from e
    for name, spec in config.items():
        if "command" not in spec and "url" not in spec:
            raise ConfigError(f'सर्वर "{name}" के लिए "command" या "url" दें')
    return config


def load_mcp_servers(config_path: Path = MCP_CONFIG) -> list[MCPToolset]:
    """हर कॉन्फ़िगर किए गए सर्वर के लिए MCP टूलसेट बनाएँ।

    command से stdio पर एक उपप्रक्रिया शुरू होती है। url से पहले से चल रहे
    सर्वर से Streamable HTTP पर जुड़ते हैं। टूल के नाम में सर्वर का नाम
    जोड़ने से एक ही नाम वाले टूल अलग पहचाने जाते हैं।

    Pydantic AI में load_mcp_toolsets() भी है। legacy मोड तय करने से
    fetch जैसे पुराने SDK से जुड़ते समय ऑटो-डिटेक्शन की चेतावनियाँ नहीं आतीं।
    """
    toolsets = []
    for name, spec in read_config(config_path).items():
        if "url" in spec:
            transport = spec["url"]
        else:
            transport = StdioTransport(spec["command"], spec.get("args", []), env=spec.get("env"))
        toolsets.append(MCPToolset(Client(transport, mode="legacy")).prefixed(name))
    return toolsets


def describe_servers(config_path: Path = MCP_CONFIG) -> list[str]:
    """बताएँ कि हर सर्वर कैसे शुरू होगा या उससे कनेक्शन कैसे बनेगा।"""
    lines = []
    for name, spec in read_config(config_path).items():
        if "url" in spec:
            lines.append(f"[server] {name}: URL से कनेक्शन ({spec['url']})")
        else:
            command = " ".join([spec["command"], *spec.get("args", [])])
            lines.append(f"[server] {name}: कमांड से शुरू ({command})")
    return lines


def build_mcp_agent(config_path: Path = MCP_CONFIG) -> Agent:
    """MCP टूल वाला एजेंट बनाएँ। चलाते समय मॉडल दें।"""
    return Agent(instructions=INSTRUCTIONS, toolsets=load_mcp_servers(config_path))


def build_model() -> GoogleModel:
    return GoogleModel(MODEL, provider=GoogleProvider(api_key=get_api_key()))


def print_tools(target: Agent) -> None:
    """टेस्ट मॉडल से टूल के नाम, विवरण और आर्ग्युमेंट दिखाएँ।

    TestModel से LLM को कॉल किए बिना टूल की परिभाषाएँ पढ़ी जा सकती हैं।
    """
    model = TestModel(call_tools=[])
    target.run_sync("टूल की सूची", model=model)
    tools_seen = model.last_model_request_parameters.function_tools
    print(f"मॉडल को दिखने वाले टूल: {len(tools_seen)}")
    for tool in tools_seen:
        print(f"\n[{tool.name}]")
        print("  " + inspect.cleandoc(tool.description or "").replace("\n", "\n  "))
        params = tool.parameters_json_schema.get("properties", {})
        print(f"  आर्ग्युमेंट: {json.dumps(params, ensure_ascii=False)}")


def print_trace(result) -> None:
    """टूल कॉल, आर्ग्युमेंट और परिणाम दिखाएँ।"""
    print("\n--- trace ---")
    for message in result.all_messages():
        for part in message.parts:
            if isinstance(part, ToolCallPart):
                print(f"[tool call]   {part.tool_name}({part.args})")
            elif isinstance(part, ToolReturnPart):
                print(f"[tool return] {part.tool_name} -> {str(part.content)[:120]}…")
            elif isinstance(part, RetryPromptPart) and part.tool_name:
                # मॉडल इस त्रुटि से तय कर सकता है कि टूल को दोबारा कॉल करना है या नहीं।
                print(f"[tool error]  {part.tool_name} -> {str(part.content)[:120]}")
    usage = result.usage
    print(f"[usage] इनपुट {usage.input_tokens:,} टोकन / आउटपुट {usage.output_tokens:,} टोकन / मॉडल के जवाब {usage.requests}")


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP टूल वाले अध्ययन सहायक एजेंट से सवाल पूछें")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--trace", action="store_true", help="टूल कॉल दिखाएँ")
    parser.add_argument("--list-tools", action="store_true", help="मॉडल को दिखने वाले टूल की सूची दिखाकर बंद करें (API कुंजी आवश्यक नहीं)")
    args = parser.parse_args()
    if not args.list_tools and not args.question:
        parser.error("सवाल दें")

    try:
        target = build_mcp_agent()
        print("\n".join(describe_servers()))
    except ConfigError as e:
        print(f"app/mcp_servers.json नहीं पढ़ सके: {e}")
        print("सर्वरों के बीच कॉमा लगाएँ और अंतिम सर्वर के बाद का अतिरिक्त कॉमा हटाएँ।")
        raise SystemExit(1)
    try:
        if args.list_tools:
            print_tools(target)
            return
        model = build_model()
        print(f"[model] {MODEL}")
        print(f"[tools] MCP सर्वर ({MCP_CONFIG.relative_to(MCP_CONFIG.parent.parent)})")
        result = target.run_sync(args.question, model=model)
    except ModelHTTPError as e:
        print(api_error_message(e.status_code, str(e.body)[:200]))
        raise SystemExit(1)
    except (AgentRunError, UserError):
        raise  # एजेंट चलने की मूल त्रुटि दिखाएँ।
    except (MCPError, RuntimeError, OSError) as e:
        # सर्वर शुरू नहीं हुआ या उससे कनेक्शन नहीं बना।
        print(f"MCP सर्वर से कनेक्ट नहीं हो सके: {e}")
        print("app/mcp_servers.json में सर्वर की कमांड या URL जाँचें।")
        raise SystemExit(1)
    print(result.output)
    if args.trace:
        print_trace(result)


if __name__ == "__main__":
    main()
