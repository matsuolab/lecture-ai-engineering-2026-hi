"""Lecture 05: शब्दावली और प्रत्येक Lecture के मुख्य बिंदु MCP सर्वर से उपलब्ध कराएँ।

उपयोग:
    uv run python -m app.agent --mcp --list-tools   # इस सर्वर के टूल की सूची देखें (API कुंजी आवश्यक नहीं)
    uv run python -m app.mcp_server --http          # Streamable HTTP से शुरू करें(http://127.0.0.1:8000/mcp)

बिना तर्क के चलाने पर stdio (मानक इनपुट/आउटपुट) पर प्रतीक्षा करता है। MCP क्लाइंट (app.agent का --mcp या
Copilot Chat) इसे उपप्रक्रिया के रूप में शुरू करता है; सीधे चलाने पर यह इनपुट की प्रतीक्षा में रुका दिखेगा।

Lecture 03 में tools.py के फ़ंक्शन agent.py में सीधे पंजीकृत किए गए थे। MCP सर्वर से वही फ़ंक्शन
Pydantic AI के अलावा दूसरे क्लाइंट (जैसे Copilot Chat) से भी समान तरीके से इस्तेमाल हो सकते हैं।
"""

import argparse

from mcp.server.mcpserver import MCPServer

from app import tools

# सर्वर का नाम और विवरण। यह क्लाइंट को दिखता है (सेटिंग फ़ाइल के "glossary" key से अलग है)
server = MCPServer(
    "aie2026-glossary",
    instructions="AI Engineering Pilot Course (AIE2026) की शब्दावली और प्रत्येक Lecture के मुख्य बिंदु देता है।",
)

# Lecture 03 के वही फ़ंक्शन MCP टूल के रूप में उपलब्ध कराएँ। docstring और type hints विवरण बनते हैं
server.tool()(tools.search_glossary)

# TODO(Lecture 05 अभ्यास): tools.get_lecture_summary भी उपलब्ध कराएँ (ऊपर की पंक्ति की तरह)
# जिन्होंने Lecture 03 में make_quiz बनाया है, वे उसे भी उपलब्ध करा सकते हैं


def main() -> None:
    parser = argparse.ArgumentParser(description="शब्दावली MCP सर्वर")
    parser.add_argument("--http", action="store_true", help="Streamable HTTP से शुरू करें (डिफ़ॉल्ट stdio)")
    args = parser.parse_args()
    if args.http:
        print("MCP सर्वर http://127.0.0.1:8000/mcp पर शुरू हो रहा है (Ctrl+C से रोकें)")
        server.run(transport="streamable-http")
    else:
        # stdio में मानक आउटपुट प्रोटोकॉल का संचार मार्ग है, इसलिए print न करें
        server.run()


if __name__ == "__main__":
    main()
