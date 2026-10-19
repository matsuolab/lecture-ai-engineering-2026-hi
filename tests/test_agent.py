"""एजेंट के टूल कनेक्शन के परीक्षण।

TestModel एक नकली मॉडल है जो वास्तविक LLM को कॉल नहीं करता। यह सभी पंजीकृत टूल बुलाकर
नकली उत्तर लौटाता है। API कुंजी या उपयोग सीमा खर्च किए बिना
जाँच सकते हैं कि टूल पंजीकृत और बुलाए जाते हैं तथा परिणाम मॉडल को लौटते हैं।
"""

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import agent

BASE_TOOLS = {"search_glossary", "get_lecture_summary"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRA क्या है?")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # अभ्यास में टूल जोड़ने पर भी परीक्षण चले, इसलिए केवल समावेशन जाँचें

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    assert len(_parts(result, ToolReturnPart)) == len(_parts(result, ToolCallPart))
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAG क्या है?")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"
