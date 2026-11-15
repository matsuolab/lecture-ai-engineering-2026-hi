"""Lecture 05: पृष्ठ के स्तर पर वेक्टर खोज।"""

import argparse
import json
import math
import re
import sqlite3
from contextlib import contextmanager
from collections import defaultdict, deque
from pathlib import Path

from google import genai
from google.genai import types
from pydantic_ai.exceptions import ModelHTTPError
import sqlite_vec

from app.config import (
    EMBEDDING_DIMENSIONS, EMBEDDING_MAX_TOKENS, EMBEDDING_MODEL,
    RAG_DB, RAG_DOCUMENT_IDS, RAG_SOURCE, RAG_TOP_K, RAG_TREE, get_api_key,
    RAG_GRAPH, GRAPH_START_K, GRAPH_HOPS, GRAPH_MAX_RESULTS,
)


def get_all_materials() -> str:
    """Lecture, अध्याय और पृष्ठ की जानकारी सहित सारी सामग्री को एक स्ट्रिंग में जोड़ें।"""
    documents = json.loads(RAG_SOURCE.read_text(encoding="utf-8"))
    return "\n\n".join(
        f"सामग्री: {document['id']} / {document['title']}\n"
        f"अध्याय: {section['section']}\n"
        f"पृष्ठ: PDF p.{page['page']} / {page['title']}\n{page['content']}"
        for document in documents
        for section in document["content"]
        for page in section["content"]
    )

def load_pages(source: Path = RAG_SOURCE) -> list[dict]:
    """सामग्री → अध्याय → पृष्ठ वाले JSON से चुनी हुई सामग्री के पृष्ठों की सूची बनाएँ।"""
    documents = json.loads(source.read_text(encoding="utf-8"))
    pages = []
    for document in documents:
        if document["id"] not in RAG_DOCUMENT_IDS:
            continue
        for section in document["content"]:
            for page in section["content"]:
                pages.append({"page_id": page["id"], "document_id": document["id"],
                              "lecture": int(document["id"][3:5]), "document_title": document["title"],
                              "section": section["section"], "title": page["title"],
                              "page": page["page"], "content": page["content"]})
    return pages


def browse_tree(node_id: str | None = None) -> dict:
    """नीचे के पृष्ठों का पहला वाक्य लौटाएँ; निर्दिष्ट पृष्ठ स्वयं हो तो उसका पूरा पाठ दें।"""
    tree = json.loads(RAG_TREE.read_text(encoding="utf-8"))
    tree["children"] = [node for node in tree["children"] if node["id"] in RAG_DOCUMENT_IDS]
    node_id = node_id or tree["id"]
    pages = {page["page_id"]: page for page in load_pages(RAG_SOURCE)}

    def describe(node, full=False):
        info = {key: node[key] for key in ("id", "kind", "title")}
        if node["kind"] == "page":
            info.update({key: value for key, value in pages[node["id"]].items() if key != "page_id"})
            if not full:
                info["content"] = re.split(r"(?<=[。！？])|\n", info["content"].strip(), maxsplit=1)[0]
        return info

    remaining = [tree]
    while remaining:
        node = remaining.pop()
        if node["id"] == node_id:
            return {
                "node": describe(node, full=True),
                "children": [describe(child) for child in node.get("children", [])],
            }
        remaining.extend(node.get("children", []))
    raise ValueError("विषय सूची का निर्दिष्ट नोड नहीं मिला।")


def read_page(page_id: str) -> dict:
    """Lecture 01 से Lecture 03 की मुख्य सामग्री के निर्दिष्ट पृष्ठ का पाठ और उद्धरण की जानकारी दें।"""
    for page in load_pages(RAG_SOURCE):
        if page["page_id"] == page_id:
            return page
    raise ValueError("निर्दिष्ट पृष्ठ नहीं मिला।")


def normalized_vector(values: list[float]) -> list[float]:
    """वेक्टर की लंबाई 1 करें।"""
    norm = math.hypot(*values)
    if norm == 0:
        raise ValueError("एम्बेडिंग शून्य वेक्टर है।")
    return [value / norm for value in values]


def embed_text(text: str, task_type: str) -> list[float]:
    """Gemini से पाठ की एम्बेडिंग बनाएँ। इनपुट सीमा पार हो तो पाठ काटने के बजाय रुकें।"""
    with genai.Client(api_key=get_api_key()) as client:
        count = client.models.count_tokens(model=EMBEDDING_MODEL, contents=text).total_tokens
        if count is None or count > EMBEDDING_MAX_TOKENS:
            raise ValueError(f"एम्बेडिंग इनपुट सीमा से अधिक है या मापा नहीं जा सकता: {count} टोकन।")
        response = client.models.embed_content(
            model=EMBEDDING_MODEL, contents=text,
            config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=EMBEDDING_DIMENSIONS),
        )
    embedding = response.embeddings[0]
    if embedding.statistics and embedding.statistics.truncated:
        raise ValueError("एम्बेडिंग API ने पाठ काट दिया।")
    return normalized_vector(embedding.values)


@contextmanager
def open_index(path: Path):
    """मौजूदा खोज DB केवल पढ़ने के लिए खोलें और अंत में बंद करें।"""
    if not path.is_file():
        raise FileNotFoundError("खोज DB नहीं मिला।")
    db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        db.row_factory = sqlite3.Row
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        yield db
    finally:
        db.close()


def search(query: str) -> list[dict]:
    """प्रश्न की एम्बेडिंग बनाएँ और अधिकतम RAG_TOP_K निकट पृष्ठ लौटाएँ।"""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("खोज शब्द खाली है।")
    with open_index(RAG_DB) as db:
        vector = embed_text(query.strip(), "RETRIEVAL_QUERY")
        rows = db.execute("""
            SELECT page_id, document_id, lecture, document_title, section, title, page, content,
                   vec_distance_cosine(embedding, ?) AS distance
            FROM chunks ORDER BY distance, page_id LIMIT ?
        """, (sqlite_vec.serialize_float32(vector), RAG_TOP_K))
        return [dict(row) for row in rows]


def search_graph(query: str) -> dict:
    """वेक्टर खोज से शुरू करके आगे-पीछे के पृष्ठों और साझा शब्दों से उम्मीदवार बढ़ाएँ।"""
    pages = {page["page_id"]: page for page in load_pages(RAG_SOURCE)}
    graph = json.loads(RAG_GRAPH.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in graph["nodes"]
             if node["kind"] == "term" or node["id"] in pages}
    adjacent = defaultdict(set)
    for edge in graph["edges"]:
        a, b = edge["source"], edge["target"]
        if edge["relation"] in ("next_page", "mentions") and a in nodes and b in nodes:
            adjacent[a].add(b)
            adjacent[b].add(a)

    seeds = [hit for hit in search(query) if hit["page_id"] in pages][:min(GRAPH_START_K, GRAPH_MAX_RESULTS)]
    seed_ids = {seed["page_id"] for seed in seeds}
    results, candidates = [], {}
    for rank, seed in enumerate(seeds):
        root = seed["page_id"]
        results.append({**pages[root], "distance": seed["distance"], "hops": 0,
                        "path": [{"id": root, "title": pages[root]["title"]}]})
        queue = deque([(root, [root])])
        visited = {root}
        while queue:
            current, path = queue.popleft()
            if len(path) - 1 >= GRAPH_HOPS:
                continue
            # समान गहराई पर पहले कम कनेक्शन वाले शब्दों से आगे बढ़ें।
            neighbors = sorted(adjacent[current], key=lambda n: (len(adjacent[n]), n))
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                route = path + [neighbor]
                queue.append((neighbor, route))
                if neighbor not in pages or neighbor in seed_ids:
                    continue
                frequency = max((len(adjacent[n]) for n in route if nodes[n]["kind"] == "term"), default=0)
                priority = (len(route) - 1, frequency, rank, neighbor)
                candidate = {**pages[neighbor], "hops": len(route) - 1,
                             "path": [{"id": n, "title": nodes[n]["title"]} for n in route]}
                if neighbor not in candidates or priority < candidates[neighbor][0]:
                    candidates[neighbor] = (priority, candidate)
    expanded = [candidate for _, candidate in sorted(candidates.values())]
    return {"seeds": results, "expanded": expanded[:max(0, GRAPH_MAX_RESULTS - len(results))],
            "max_hops": GRAPH_HOPS}



def run_full_context(agent, question: str, model, instructions: str, prompt_template: str):
    """सारी सामग्री एक साथ दें और खोज टूल के बिना उत्तर बनाएँ।"""
    prompt = prompt_template.format(materials=get_all_materials(), question=question)
    print(f"[full-context] इनपुट में {len(prompt):,} अक्षर")
    try:
        with agent.override(tools=[], instructions=instructions):
            return agent.run_sync(prompt, model=model)
    except ModelHTTPError as e:
        print(f"[full-context] API त्रुटि HTTP {e.status_code}: {e.body}")
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="एजेंट के बिना केवल Lecture की सामग्री में खोज करें")
    parser.add_argument("query", help="खोजने का विषय")
    args = parser.parse_args()
    for i, result in enumerate(search(args.query), 1):
        print(f"\n{'=' * 60}\nखोज परिणाम {i}\n{'=' * 60}")
        print(f"Lecture: {result['document_title']}")
        print(f"अध्याय: {result['section']}")
        print(f"शीर्षक: {result['title']}")
        print(f"पृष्ठ: {result['page']}")
        print(f"\n{result['content']}")
