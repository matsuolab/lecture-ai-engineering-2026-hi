"""एजेंट के टूल कनेक्शन के परीक्षण।

TestModel एक नकली मॉडल है जो वास्तविक LLM को कॉल नहीं करता। यह सभी पंजीकृत टूल बुलाकर
नकली उत्तर लौटाता है। API कुंजी या उपयोग सीमा खर्च किए बिना
जाँच सकते हैं कि टूल पंजीकृत और बुलाए जाते हैं तथा परिणाम मॉडल को लौटते हैं।
"""

import json

from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import agent

BASE_TOOLS = {"search_materials"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called(monkeypatch):
    monkeypatch.setattr("app.retrieval.search", lambda *args, **kwargs: [])
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRA क्या है?")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # अभ्यास में टूल जोड़ने पर भी परीक्षण चले, इसलिए केवल समावेशन जाँचें

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    # मंज़ूरी वाले टूल (requires_approval=True) बिना निष्पादित हुए प्रतीक्षा करते हैं, इसलिए उनका कोई वापसी मान नहीं होता
    waiting = len(result.output.approvals) if isinstance(result.output, DeferredToolRequests) else 0
    assert len(_parts(result, ToolReturnPart)) + waiting == len(_parts(result, ToolCallPart))
    assert result.output


def test_material_result_reaches_the_model(monkeypatch):
    hit = {"page_id": "lec02-main-p052", "lecture": 2, "page": 52, "content": "मूल भार स्थिर रहते हैं"}
    monkeypatch.setattr("app.retrieval.search", lambda *args, **kwargs: [hit])
    model = TestModel(call_tools=["search_materials"])
    with agent.override(model=model):
        result = agent.run_sync("RAG क्या है?")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_materials"
    assert json.loads(returns[0].content)["results"] == [hit]
