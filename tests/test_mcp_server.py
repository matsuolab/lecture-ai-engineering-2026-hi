"""Lecture 05: MCP सर्वर और क्लाइंट कनेक्शन का परीक्षण (LLM और API कुंजी के बिना)।

app/mcp_servers.json का glossary सर्वर वास्तव में शुरू करें (stdio), फिर TestModel से
जाँचें कि टूल MCP से उपलब्ध होता है, बुलाया जाता है और परिणाम लौटता है।
"""

import json

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import MCP_CONFIG, build_mcp_agent

GLOSSARY_TOOL = "glossary_search_glossary"  # सेटिंग फ़ाइल का सर्वर नाम "glossary" आगे जुड़ता है


def _glossary_only_config(tmp_path):
    """केवल glossary सर्वर लें (अभ्यास में जोड़े fetch जैसे बाहरी सर्वर शुरू न करें)।"""
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    assert "glossary" in config["mcpServers"], "app/mcp_servers.json में glossary सर्वर आवश्यक है"
    path = tmp_path / "mcp_servers.json"
    path.write_text(
        json.dumps({"mcpServers": {"glossary": config["mcpServers"]["glossary"]}}), encoding="utf-8"
    )
    return path


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_glossary_server_exposes_search_tool(tmp_path):
    model = TestModel(call_tools=[])
    build_mcp_agent(_glossary_only_config(tmp_path)).run_sync("टूल सूची", model=model)

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert GLOSSARY_TOOL in offered  # अभ्यास में टूल जोड़ने पर भी परीक्षण चले, इसलिए केवल समावेशन जाँचें


def test_glossary_result_comes_back_through_mcp(tmp_path):
    model = TestModel(call_tools=[GLOSSARY_TOOL])
    result = build_mcp_agent(_glossary_only_config(tmp_path)).run_sync("LoRA क्या है?", model=model)

    assert [p.tool_name for p in _parts(result, ToolCallPart)] == [GLOSSARY_TOOL]
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == GLOSSARY_TOOL
    assert str(returns[0].content).strip()  # खोज परिणाम (या "नहीं मिला") लौटता है
    assert result.output
