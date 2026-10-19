"""टूल परीक्षण (LLM और API कुंजी के बिना)।"""

import json

from app import tools


def test_glossary_ids_are_unique_and_related_links_exist():
    terms = tools.load_glossary()
    ids = [t["id"] for t in terms]
    assert len(ids) == len(set(ids))
    for t in terms:
        for r in t["related"]:
            assert r in ids, f"{t['id']} के related में मौजूद नहीं है: {r}"


def test_search_finds_term_by_name_and_alias():
    for query in ["LoRA", "lora", "Low-Rank Adaptation"]:
        hits = json.loads(tools.search_glossary(query))
        assert hits[0]["term"] == "LoRA", query


def test_search_finds_course_specific_term():
    hits = json.loads(tools.search_glossary("lecNN-start"))
    assert hits[0]["term"] == "lecNN-start टैग"


def test_search_limits_number_of_results():
    hits = json.loads(tools.search_glossary("एजेंट"))
    assert 1 <= len(hits) <= tools.MAX_RESULTS


def test_search_reports_not_found():
    assert "नहीं मिला" in tools.search_glossary("अनुपस्थितशब्दxyz")


def test_lecture_summary():
    assert "एजेंट" in tools.get_lecture_summary(3)
    assert "अभी उपलब्ध नहीं" in tools.get_lecture_summary(99)


def test_default_question_of_lecture1_is_answerable_from_glossary():
    """Lecture 01 के डिफ़ॉल्ट प्रश्न (app.ask) का उत्तर Lecture 03 का एजेंट शब्दावली से सही ढंग से दे सके।"""
    from app.ask import DEFAULT_QUESTION

    assert "3 स्तर" in DEFAULT_QUESTION
    hits = json.loads(tools.search_glossary("3 स्तर"))
    assert hits[0]["term"] == "होमवर्क के 3 स्तर"
