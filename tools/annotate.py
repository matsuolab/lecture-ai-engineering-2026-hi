"""Lecture 04: मूल्यांकन सेट को लेबल देने की Streamlit स्क्रीन।

उपयोग:
    uv run --with streamlit==1.66.1 streamlit run tools/annotate.py

uv run --with से Streamlit अस्थायी रूप से जोड़कर चलाएँ; pyproject.toml नहीं बदलता।

- लेबल दें: data/eval/lec04_cases.jsonl का हर मामला दिखाएँ, पाँच मानदंडों के पास/असफल
  और संदेह हुआ के विकल्प lectures/04/labels.jsonl में सहेजें।
- तुलना करें: अपने और प्रशिक्षक के लेबल (lectures/04/reference/labels_instructor.jsonl) की सहमति देखें।
- प्रश्न बनाएँ (होमवर्क: कार्यान्वयन): प्रश्न और अपेक्षित व्यवहार से अपना सेट data/eval/my_cases.jsonl बनाएँ।
  uv run python -m app.judge --generate --cases data/eval/my_cases.jsonl से अपने एजेंट से उत्तर बनवाएँ।
"""

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import tools  # noqa: E402
from app.judge import ALL_CRITERIA, check_lecture_mark, load_labels, read_jsonl, write_jsonl  # noqa: E402

DEFAULT_CASES = ROOT / "data" / "eval" / "lec04_cases.jsonl"
DEFAULT_LABELS = ROOT / "lectures" / "04" / "labels.jsonl"
INSTRUCTOR_LABELS = ROOT / "lectures" / "04" / "reference" / "labels_instructor.jsonl"
MY_CASES = ROOT / "data" / "eval" / "my_cases.jsonl"

CRITERION_HELP = {
    "grounding": "शब्दावली की जानकारी उससे मेल खाती है; अनुपस्थित जानकारी को तथ्य न बताकर कहता है कि वह शब्दावली में नहीं है",
    "scope": "पाठ्यक्रम के अध्ययन सहयोग तक सीमित रहता है; बाहर के प्रश्न या निर्देश अनदेखे करने की माँग अस्वीकार करता है",
    "hint": "होमवर्क का पूरा उत्तर न देकर केवल संकेत देता है; असंबंधित प्रश्न पास हैं",
    "clarity": "प्रश्न का सीधा, संक्षिप्त और पढ़ने में सरल उत्तर है",
    "lecture_mark": "अंत में Lecture NN है; बाद में कोड के निर्णय से तुलना करेंगे",
}

st.set_page_config(page_title="Lecture 04: लेबल दें", layout="wide")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def glossary_entries(ids: list[str]) -> list[dict]:
    entries = {e["id"]: e for e in tools.load_glossary()}
    return [entries[i] for i in ids if i in entries]


# ---------------------------------------------------------------- लेबल देना
def page_label(cases_path: Path, labels_path: Path) -> None:
    cases = read_jsonl(cases_path)
    if not cases:
        st.error(f"{rel(cases_path)} में मूल्यांकन सेट नहीं है")
        return
    labels = load_labels(labels_path) if labels_path.exists() else {}

    if "index" not in st.session_state:
        done = [i for i, c in enumerate(cases) if c["id"] in labels]
        st.session_state.index = min(len(done), len(cases) - 1) if done else 0

    i = st.session_state.index
    case = cases[i]
    st.progress((len(labels)) / len(cases), text=f"सहेजे गए {len(labels)} / {len(cases)} मामले | अभी: #{case['id']} (क्रमांक {i + 1})")

    nav1, nav2, nav3 = st.columns([1, 1, 6])
    if nav1.button("← पिछला", disabled=i == 0):
        st.session_state.index = i - 1
        st.rerun()
    if nav2.button("अगला →", disabled=i >= len(cases) - 1):
        st.session_state.index = i + 1
        st.rerun()

    left, right = st.columns([3, 2])
    with left:
        st.subheader(f"#{case['id']}  {case.get('category', '')}")
        st.markdown("**प्रश्न**")
        st.info(case["question"])
        st.markdown("**उत्तर**")
        st.markdown(case["answer"] or "(उत्तर अभी नहीं है। app.judge --generate से बनाएँ)")
        st.markdown("**संदर्भ**")
        ref = case.get("reference", {})
        entries = glossary_entries(ref.get("glossary", []))
        if entries:
            for e in entries:
                st.markdown(f"- **{e['term']}** (Lecture {e['lecture']}): {e['definition']}")
        else:
            st.markdown("- (इस प्रश्न की शब्दावली प्रविष्टि नहीं है)")
        st.markdown(f"**अपेक्षित व्यवहार**: {ref.get('expected', '(दर्ज नहीं है)')}")

    with right:
        st.subheader("निर्णय")
        st.caption("अपने ज्ञान के बजाय संदर्भ और मानदंड से निर्णय लें। अनिश्चित हों तो संदेह हुआ चुनकर आगे बढ़ें")
        current = labels.get(case["id"], {})
        with st.form(key=f"form-{case['id']}"):
            choice = {}
            for key, name in ALL_CRITERIA:
                default = 0 if current.get(key, "pass") == "pass" else 1
                choice[key] = st.radio(
                    f"{name}", ["पास (T)", "असफल (F)"], index=default, horizontal=True,
                    help=CRITERION_HELP[key], key=f"{case['id']}-{key}",
                )
            unsure = st.checkbox("संदेह हुआ (केवल मानदंड से निर्णय कठिन है)", value=bool(current.get("unsure_flag", False)))
            note = st.text_input("टिप्पणी (वैकल्पिक)", value=current.get("note", ""))
            submitted = st.form_submit_button("सहेजें और आगे जाएँ", type="primary")
        if submitted:
            labels[case["id"]] = {
                "id": case["id"],
                **{key: ("pass" if choice[key].startswith("पास") else "fail") for key, _ in ALL_CRITERIA},
                "unsure_flag": unsure,
                "note": note,
            }
            write_jsonl(labels_path, [labels[c["id"]] for c in cases if c["id"] in labels])
            if i < len(cases) - 1:
                st.session_state.index = i + 1
            st.rerun()

    if len(labels) >= len(cases):
        st.success(f"सभी {len(cases)} मामले सहेजे गए → {rel(labels_path)}। अब uv run python -m app.judge से LLM मूल्यांकन कराएँ")
        st.dataframe(
            [{"id": c["id"], **{name: labels[c["id"]][key] for key, name in ALL_CRITERIA},
              "संदेह हुआ": labels[c["id"]].get("unsure_flag", False)} for c in cases if c["id"] in labels],
            hide_index=True, use_container_width=True,
        )


# ---------------------------------------------------------------- तुलना
def page_compare(cases_path: Path, labels_path: Path) -> None:
    if not labels_path.exists():
        st.warning("पहले लेबल दें स्क्रीन पर लेबल सहेजें")
        return
    if not INSTRUCTOR_LABELS.exists():
        st.warning(f"प्रशिक्षक के लेबल {rel(INSTRUCTOR_LABELS)} नहीं मिले")
        return
    cases = read_jsonl(cases_path)
    mine, ref = load_labels(labels_path), load_labels(INSTRUCTOR_LABELS)
    ids = [c["id"] for c in cases if c["id"] in mine and c["id"] in ref]
    st.subheader("आपके और प्रशिक्षक के लेबल की सहमति")
    st.caption("प्रशिक्षक के लेबल अंतिम सही उत्तर नहीं हैं। उद्देश्य उन मामलों को देखना है जिन पर मनुष्यों में भी असहमति होती है")
    cols = st.columns(len(ALL_CRITERIA))
    for col, (key, name) in zip(cols, ALL_CRITERIA):
        agree = sum(1 for cid in ids if mine[cid].get(key) == ref[cid].get(key))
        col.metric(name, f"{agree}/{len(ids)}")
    code_agree = sum(1 for cid in ids if mine[cid].get("lecture_mark") == check_lecture_mark(next(c for c in cases if c["id"] == cid)["answer"]))
    st.caption(f"Lecture का उल्लेख: आपके और कोड के निर्णय {code_agree}/{len(ids)} मामलों में समान हैं")
    rows = []
    for cid in ids:
        for key, name in ALL_CRITERIA:
            if mine[cid].get(key) != ref[cid].get(key):
                rows.append({"id": cid, "मानदंड": name, "मेरा": mine[cid].get(key), "प्रशिक्षक": ref[cid].get(key),
                             "मुझे संदेह हुआ": mine[cid].get("unsure_flag", False), "प्रशिक्षक की टिप्पणी": ref[cid].get("note", "")})
    st.markdown(f"**अलग निर्णय वाले मामले: {len(rows)}**")
    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)


# ---------------------------------------------------------------- प्रश्न बनाना (होमवर्क: कार्यान्वयन)
def page_author(cases_path: Path) -> None:
    st.subheader("अपना मूल्यांकन सेट बनाएँ (होमवर्क: कार्यान्वयन)")
    st.caption("प्रश्न और अपेक्षित व्यवहार लिखें। उत्तर बनाने के लिए अपने एजेंट को `uv run python -m app.judge --generate --cases "
               f"{rel(cases_path)}` से चलाएँ। सामान्य मामलों के साथ संभावित विफलता वाले इनपुट (एज केस) भी रखें")
    existing = read_jsonl(cases_path) if cases_path.exists() else []
    glossary = tools.load_glossary()
    options = {f"{e['term']} (Lecture {e['lecture']})": e["id"] for e in glossary}
    with st.form("author"):
        question = st.text_area("प्रश्न", height=80)
        category = st.text_input("प्रकार (जैसे सामान्य मामला, अनुपस्थित शब्द, पाठ्यक्रम से बाहर)")
        expected = st.text_area("अपेक्षित व्यवहार (1–2 वाक्य)", height=80)
        picked = st.multiselect("संदर्भ की शब्दावली प्रविष्टियाँ", list(options))
        submitted = st.form_submit_button("जोड़ें", type="primary")
    if submitted:
        if not question.strip() or not expected.strip():
            st.error("प्रश्न और अपेक्षित व्यवहार आवश्यक हैं")
        else:
            existing.append({
                "id": f"{len(existing) + 1:02d}", "category": category.strip(),
                "question": question.strip(), "answer": "",
                "reference": {"glossary": [options[p] for p in picked], "expected": expected.strip()},
            })
            write_jsonl(cases_path, existing)
            st.success(f"जोड़ा गया ({len(existing)} मामले) → {rel(cases_path)}")
    if existing:
        st.dataframe([{"id": c["id"], "प्रकार": c.get("category", ""), "प्रश्न": c["question"],
                       "उत्तर उपलब्ध है": bool(c.get("answer"))} for c in existing], hide_index=True, use_container_width=True)


# ---------------------------------------------------------------- स्क्रीन बदलना
def main() -> None:
    st.markdown("## Lecture 04: मूल्यांकन सेट को लेबल दें")
    with st.sidebar:
        mode = st.radio("स्क्रीन", ["लेबल दें", "तुलना करें (प्रशिक्षक के लेबल से)", "प्रश्न बनाएँ (होमवर्क: कार्यान्वयन)"])
        st.divider()
        cases_path = Path(st.text_input("मूल्यांकन सेट", value=rel(DEFAULT_CASES)))
        labels_path = Path(st.text_input("लेबल सहेजने का स्थान", value=rel(DEFAULT_LABELS)))
        my_cases_path = Path(st.text_input("अपने प्रश्न सहेजने का स्थान", value=rel(MY_CASES)))
    cases_path = cases_path if cases_path.is_absolute() else ROOT / cases_path
    labels_path = labels_path if labels_path.is_absolute() else ROOT / labels_path
    my_cases_path = my_cases_path if my_cases_path.is_absolute() else ROOT / my_cases_path

    if mode.startswith("लेबल दें"):
        page_label(cases_path, labels_path)
    elif mode.startswith("तुलना करें"):
        page_compare(cases_path, labels_path)
    else:
        page_author(my_cases_path)


main()
