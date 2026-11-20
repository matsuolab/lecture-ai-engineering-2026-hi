"""लेक्चर 06 का MCP सर्वर, जो शब्दावली और लेक्चर सारांश देता है।

    uv run python -m app.mcp_agent --list-tools
    uv run python -m app.mcp_server --http

पहली कमांड API कुंजी के बिना टूल की सूची दिखाती है। दूसरी कमांड
http://127.0.0.1:8000/mcp पर Streamable HTTP शुरू करती है।

डिफ़ॉल्ट रूप से सर्वर stdio पर इनपुट की प्रतीक्षा करता है। app.mcp_agent
जैसे MCP क्लाइंट इसे उपप्रक्रिया के रूप में शुरू करते हैं। सीधे चलाने पर यह
इनपुट के इंतज़ार में रहेगा। लेक्चर 03 के फ़ंक्शन उसी प्रोटोकॉल के ज़रिए
एजेंट और अन्य MCP क्लाइंट के लिए उपलब्ध हैं।
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

# TODO(बुनियादी होमवर्क): get_lecture_summary भी उपलब्ध कराएँ


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
