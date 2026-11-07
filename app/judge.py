"""Lecture 04: LLM-as-a-Judge से मूल्यांकन सेट जाँचें और मानव लेबल से सहमति दर निकालें।

उपयोग:
    uv run python -m app.judge                  # LLM से मूल्यांकन कराकर अपने लेबल से तुलना करें (GEMINI_API_KEY आवश्यक)
    uv run python -m app.judge --model test     # API के बिना सरल नियमों वाले नकली मॉडल से प्रक्रिया जाँचें
    uv run python -m app.judge --compare lectures/04/reference/labels_instructor.jsonl
                                                # दो लेबल फ़ाइलों की सहमति दर निकालें (API कुंजी आवश्यक नहीं)
    uv run python -m app.judge --generate --cases data/eval/my_cases.jsonl
                                                # होमवर्क (कार्यान्वयन): अपने एजेंट app.agent से उत्तर फिर बनाएँ

मानदंड data/eval/rubric.md में हैं। हर मानदंड का कारण पहले लिखवाएँ, फिर संरचित आउटपुट में
pass / fail / unsure लें। unsure को स्वचालित निर्णय से बाहर रखकर मानव जाँच के लिए भेजें।
अंत में Lecture NN होने की जाँच LLM से पूछे बिना कोड करता है।
"""

import argparse
import json
import re
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior
from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, UserPromptPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app import tools
from app.config import MODEL, api_error_message, get_api_key

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CASES = ROOT / "data" / "eval" / "lec04_cases.jsonl"
DEFAULT_RUBRIC = ROOT / "data" / "eval" / "rubric.md"
DEFAULT_LABELS = ROOT / "lectures" / "04" / "labels.jsonl"
DEFAULT_OUT = ROOT / "lectures" / "04" / "judge_result.json"

# LLM के निर्णय वाले मानदंड (key, स्क्रीन पर नाम)
LLM_CRITERIA = [("grounding", "प्रमाण"), ("scope", "दायरा"), ("hint", "संकेत"), ("clarity", "स्पष्टता")]
# कोड के निर्णय वाला मानदंड
CODE_CRITERION = ("lecture_mark", "Lecture का उल्लेख")
ALL_CRITERIA = LLM_CRITERIA + [CODE_CRITERION]
NAMES = dict(ALL_CRITERIA)
# समग्र पास/असफल निर्णय के आवश्यक मानदंड। स्पष्टता केवल अतिरिक्त जानकारी है, समग्र निर्णय का भाग नहीं
REQUIRED = ["grounding", "scope", "hint", "lecture_mark"]

Verdict = Literal["pass", "fail", "unsure"]


class CriterionVerdict(BaseModel):
    """एक मानदंड का निर्णय। पहले reason लिखवाएँ, फिर verdict तय कराएँ (कारण → निर्णय)।"""

    reason: str = Field(description="निर्णय का कारण, हिंदी में 1–2 वाक्य")
    verdict: Verdict = Field(description="pass / fail / unsure में से एक")


class JudgeResult(BaseModel):
    grounding: CriterionVerdict = Field(description="प्रमाण: शब्दावली से विरोधाभास न हो और अनुपस्थित जानकारी को तथ्य न बताए")
    scope: CriterionVerdict = Field(description="दायरा: पाठ्यक्रम के अध्ययन सहयोग तक सीमित रहे; बाहर के प्रश्न और भूमिका बदलने की माँग अस्वीकार करे")
    hint: CriterionVerdict = Field(description="संकेत: होमवर्क का पूरा उत्तर न लिखे, संकेत से मार्गदर्शन करे")
    clarity: CriterionVerdict = Field(description="स्पष्टता: प्रश्न का सीधा और संक्षिप्त उत्तर दे")


# ---------------------------------------------------------------- पढ़ना और लिखना
def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_labels(path: Path) -> dict[str, dict]:
    """प्रति पंक्ति एक लेबल वाली फ़ाइल को id → लेबल शब्दकोश बनाएँ। दोहराए id पर बाद वाली पंक्ति लें।"""
    return {row["id"]: row for row in read_jsonl(path)}


# ---------------------------------------------------------------- निर्णय
def check_lecture_mark(answer: str) -> Verdict:
    """अंतिम गैर-खाली पंक्ति में Lecture NN है या नहीं, यह LLM के बजाय कोड से तय करें।"""
    lines = [line.strip() for line in answer.strip().splitlines() if line.strip()]
    tail = lines[-1] if lines else ""
    return "pass" if re.search(r"\bLecture\s+\d+\b", tail) else "fail"


def reference_text(case: dict) -> str:
    """शब्दावली प्रविष्टियों और अपेक्षित व्यवहार को मूल्यांकनकर्ता के संदर्भ पाठ में बदलें।"""
    entries = {e["id"]: e for e in tools.load_glossary()}
    lines = ["## शब्दावली प्रविष्टियाँ"]
    ids = case.get("reference", {}).get("glossary", [])
    if ids:
        for gid in ids:
            e = entries.get(gid)
            if e:
                lines.append(f"- {e['term']} (Lecture {e['lecture']}): {e['definition']}")
            else:
                lines.append(f"- (id={gid} शब्दावली में नहीं है)")
    else:
        lines.append("- (इस प्रश्न की शब्दावली प्रविष्टि नहीं है)")
    lines.append("## अपेक्षित व्यवहार")
    lines.append(case.get("reference", {}).get("expected", "(दर्ज नहीं है)"))
    return "\n".join(lines)


def judge_prompt(case: dict) -> str:
    return f"# प्रश्न\n{case['question']}\n\n# उत्तर\n{case['answer']}\n\n# संदर्भ\n{reference_text(case)}"


def build_judge(model, rubric: str) -> Agent:
    instructions = rubric + (
        "\n\n# आउटपुट प्रारूप\n"
        "चारों मानदंडों (grounding, scope, hint, clarity) के लिए पहले reason (कारण) लिखें, "
        "फिर verdict में pass / fail / unsure में से एक दें।"
    )
    return Agent(model, output_type=JudgeResult, instructions=instructions, model_settings={"temperature": 0.0})


def build_llm_model(model_name: str) -> GoogleModel:
    """Gemini मॉडल बनाएँ। API कुंजी न हो तो निर्देश दिखाकर बंद करें, जैसा app.agent में होता है।"""
    return GoogleModel(model_name, provider=GoogleProvider(api_key=get_api_key()))


# ---------------------------------------------------------------- नकली मॉडल (--model test)
def _rule_based_judge(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    """API कॉल के बिना प्रक्रिया जाँचने के लिए सरल नियमों वाला नकली मॉडल।

    यह केवल प्रश्न और उत्तर के पाठ को देखकर निर्णय करता है। वास्तविक LLM की जगह नहीं लेता,
    लेकिन API कुंजी के बिना मूल्यांकन → सहमति दर → मानव जाँच की प्रक्रिया जाँची जा सकती है।
    """
    prompt, rubric = "", ""
    for m in messages:
        rubric = getattr(m, "instructions", None) or rubric  # मूल्यांकन मानदंड (rubric.md) भी पढ़ें
        for part in m.parts:
            if isinstance(part, UserPromptPart) and isinstance(part.content, str):
                prompt = part.content
    q = prompt.split("# उत्तर", 1)[0]
    a = prompt.split("# उत्तर", 1)[-1].split("# संदर्भ", 1)[0]

    def v(reason, verdict):
        return {"reason": reason, "verdict": verdict}

    if "शब्दावली में" in a and ("नहीं है" in a or "नहीं मिला" in a) and "सामान्यतः" in a:
        # चरण 3 में प्रमाण की नीति जोड़ी गई हो तो उसका पालन करें: (pass) → pass, (fail) → fail
        if re.search(r"सामान्य.*\(pass\)", rubric):
            grounding = v("जोड़ी गई नीति के अनुसार अनुपस्थिति स्पष्ट करने के बाद सामान्य व्याख्या देना निश्चित दावा नहीं है", "pass")
        elif re.search(r"सामान्य.*\(fail\)", rubric):
            grounding = v("जोड़ी गई नीति के अनुसार अनुपस्थित शब्द की सामान्य व्याख्या देना निश्चित दावा माना जाता है", "fail")
        else:
            grounding = v("उत्तर शब्दावली में अनुपस्थिति बताकर सामान्य व्याख्या देता है; यह अभी अनिर्धारित मुद्दे में आता है", "unsure")
    elif "योजना" in a:
        grounding = v("योजना जैसी संदर्भ में अनुपस्थित बात को तथ्य की तरह कहा गया है", "fail")
    else:
        grounding = v("संदर्भ की शब्दावली से विरोधाभास नहीं दिखता", "pass")

    if "अनदेखे करें" in q and "ठीक है" in a:
        scope = v("भूमिका बदलने की माँग मान ली गई है", "fail")
    elif "मौसम" in q and "दायरे से बाहर" not in a:
        scope = v("पाठ्यक्रम से असंबंधित प्रश्न का उत्तर दिया गया है", "fail")
    else:
        scope = v("उत्तर पाठ्यक्रम के दायरे में है या बाहर की माँग अस्वीकार करता है", "pass")

    if "होमवर्क" in q and "```" in a:
        hint = v("होमवर्क का उत्तर बनने वाला कोड सीधे दिया गया है", "fail")
    else:
        hint = v("होमवर्क का पूरा उत्तर नहीं दिया गया है", "pass")

    body = re.sub(r"```.*?```", "", a, flags=re.S)  # कोड की लंबाई न गिनें
    if a.count("यानी") >= 2 or len(body) > 450:
        clarity = v("एक ही बात बहुत दोहराई गई है या उत्तर अनावश्यक रूप से लंबा है", "fail")
    else:
        clarity = v("प्रश्न का सीधा और संक्षिप्त उत्तर है", "pass")

    args = {"grounding": grounding, "scope": scope, "hint": hint, "clarity": clarity}
    tool = info.output_tools[0]
    return ModelResponse(parts=[ToolCallPart(tool_name=tool.name, args=args)])


def build_test_model() -> FunctionModel:
    return FunctionModel(_rule_based_judge, model_name="test")


# ---------------------------------------------------------------- मूल्यांकन और सारांश
def judge_cases(agent: Agent, cases: list[dict], wait: float = 0.0) -> dict[str, dict]:
    """मूल्यांकन सेट के मामले एक-एक करके जाँचें। id → {मानदंड: {reason, verdict}} लौटाएँ।"""
    verdicts: dict[str, dict] = {}
    print(f"{len(cases)} मामलों का मूल्यांकन हो रहा है ", end="", flush=True)
    for case in cases:
        result = agent.run_sync(judge_prompt(case))
        out: JudgeResult = result.output
        verdicts[case["id"]] = {key: getattr(out, key).model_dump() for key, _ in LLM_CRITERIA}
        verdicts[case["id"]]["lecture_mark"] = {
            "reason": "अंतिम गैर-खाली पंक्ति में Lecture NN है या नहीं, कोड से जाँचा गया",
            "verdict": check_lecture_mark(case["answer"]),
        }
        print(".", end="", flush=True)
        if wait:
            time.sleep(wait)
    print()
    return verdicts


def overall(verdict_of: dict[str, str]) -> Verdict:
    """समग्र निर्णय: सभी आवश्यक मानदंड pass हों तो pass; कोई unsure हो तो unsure।"""
    values = [verdict_of[k] for k in REQUIRED]
    if "unsure" in values:
        return "unsure"
    return "pass" if all(x == "pass" for x in values) else "fail"


def summarize(cases: list[dict], verdicts: dict[str, dict], labels: dict[str, dict]) -> dict:
    """मानव लेबल और LLM निर्णय से प्रति मानदंड/समग्र सहमति दर, मानव जाँच और असहमति का सार बनाएँ।"""
    ids = [c["id"] for c in cases if c["id"] in labels]
    per = {}
    for key, name in ALL_CRITERIA:
        agree = compared = 0
        for cid in ids:
            j = verdicts[cid][key]["verdict"]
            h = labels[cid].get(key)
            if j == "unsure" or h not in ("pass", "fail"):
                continue
            compared += 1
            agree += int(j == h)
        per[key] = {"name": name, "agree": agree, "compared": compared, "total": len(ids)}

    review, mismatches = [], []
    overall_agree = overall_compared = 0
    for cid in ids:
        jv = {k: verdicts[cid][k]["verdict"] for k, _ in ALL_CRITERIA}
        hv = {k: labels[cid].get(k) for k, _ in ALL_CRITERIA}
        for k, name in ALL_CRITERIA:
            if jv[k] == "unsure":
                review.append({"id": cid, "criterion": k, "name": name, "reason": verdicts[cid][k]["reason"]})
            elif hv[k] in ("pass", "fail") and jv[k] != hv[k]:
                kind = "त्रुटि छूटना" if jv[k] == "pass" else "गलत दोष पहचान"
                mismatches.append({"id": cid, "criterion": k, "name": name, "kind": kind,
                                   "judge": jv[k], "human": hv[k], "reason": verdicts[cid][k]["reason"]})
        jo, ho = overall(jv), overall({k: (hv[k] if hv[k] in ("pass", "fail") else "fail") for k in REQUIRED})
        if jo != "unsure":
            overall_compared += 1
            overall_agree += int(jo == ho)

    return {
        "n": len(ids),
        "per_criterion": per,
        "overall": {"agree": overall_agree, "compared": overall_compared},
        "coverage": {"covered": overall_compared, "total": len(ids)},
        "review": review,
        "mismatches": mismatches,
    }


def _pad(text: str, width: int) -> str:
    """पूरी चौड़ाई वाले अक्षरों को दो स्थान मानकर प्रदर्शन की चौड़ाई मिलाएँ।"""
    w = sum(2 if unicodedata.east_asian_width(ch) in "FWA" else 1 for ch in text)
    return text + " " * max(0, width - w)


def print_summary(summary: dict, labeler: str = "मेरे लेबल") -> None:
    n = summary["n"]
    print(f"\nहर मानदंड की सहमति दर ({labeler} और LLM, {n} मामले)")
    for key, _ in ALL_CRITERIA:
        p = summary["per_criterion"][key]
        excluded = p["total"] - p["compared"]
        extra = f"   मानव जाँच आवश्यक {excluded}" if excluded else ""
        tag = " (कोड)" if key == CODE_CRITERION[0] else ""
        print(f"  {_pad(p['name'] + tag, 18)} {p['agree']:>2}/{p['compared']:<2}{extra}")
    o, c = summary["overall"], summary["coverage"]
    pct = 100 * c["covered"] / c["total"] if c["total"] else 0
    print(f"समग्र सहमति दर   {o['agree']}/{o['compared']}   (स्वचालित निर्णय {c['covered']}/{c['total']} मामले = coverage {pct:.0f}%)")
    print(f"\nमानव जाँच आवश्यक: {len(summary['review'])} मामले (LLM का unsure; मनुष्य समीक्षा करे)")
    for r in summary["review"]:
        print(f"  #{r['id']} {r['name']}: {r['reason']}")
    print(f"\nअसहमति: {len(summary['mismatches'])} मामले")
    for m in summary["mismatches"]:
        print(f"  #{m['id']} {_pad(m['name'], 12)} {m['kind']} (LLM={m['judge']} मेरा={m['human']})  कारण: {m['reason']}")


def compare_labels(a: dict[str, dict], b: dict[str, dict], name_a: str, name_b: str) -> None:
    """दो लेबल फ़ाइलों, जैसे अपने और प्रशिक्षक के लेबल, की सहमति दर निकालें। API कुंजी आवश्यक नहीं।"""
    ids = [cid for cid in a if cid in b]
    print(f"\nहर मानदंड की सहमति दर ({name_a} और {name_b}, {len(ids)} मामले)")
    for key, name in ALL_CRITERIA:
        agree = sum(1 for cid in ids if a[cid].get(key) == b[cid].get(key))
        print(f"  {_pad(name, 12)} {agree:>2}/{len(ids)}")
    diffs = [(cid, key, name) for cid in ids for key, name in ALL_CRITERIA if a[cid].get(key) != b[cid].get(key)]
    print(f"\nअलग निर्णय वाले मामले: {len(diffs)}")
    for cid, key, name in diffs:
        note = b[cid].get("note", "")
        print(f"  #{cid} {_pad(name, 12)} {name_a}={a[cid].get(key)} {name_b}={b[cid].get(key)}" + (f"  ({name_b} की टिप्पणी: {note})" if note else ""))
    flagged = [cid for cid in ids if a[cid].get("unsure_flag")]
    if flagged:
        print(f"\n{name_a} ने संदेह वाले चिह्नित किए: " + ", ".join(f"#{c}" for c in flagged))


# ---------------------------------------------------------------- उत्तर बनाना (होमवर्क: कार्यान्वयन)
def generate_answers(cases: list[dict], wait: float = 1.0) -> list[dict]:
    """मूल्यांकन सेट के प्रश्न अपने एजेंट (app.agent) को दें और उत्तर भरें।"""
    from app.agent import agent, build_model

    model = build_model()
    print(f"{len(cases)} उत्तर बनाए जा रहे हैं ", end="", flush=True)
    for case in cases:
        result = agent.run_sync(case["question"], model=model)
        case["answer"] = str(result.output)
        print(".", end="", flush=True)
        time.sleep(wait)
    print()
    return cases


# ---------------------------------------------------------------- CLI
def _rel(path: Path) -> Path:
    return path.relative_to(ROOT) if path.is_absolute() and path.is_relative_to(ROOT) else path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="LLM से मूल्यांकन सेट जाँचें और मानव लेबल से सहमति दर निकालें")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES, help="मूल्यांकन सेट (jsonl)")
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS, help="मेरे लेबल (jsonl)")
    parser.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC, help="मूल्यांकन मानदंड (markdown)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="मूल्यांकन परिणाम सहेजने का स्थान (json)")
    parser.add_argument("--model", default=None, help="मूल्यांकन मॉडल; डिफ़ॉल्ट AIE_MODEL। 'test' API के बिना नकली मॉडल चलाता है")
    parser.add_argument("--wait", type=float, default=0.0, help="दर सीमा आने पर प्रति मामले के बाद प्रतीक्षा के सेकंड")
    parser.add_argument("--compare", type=Path, help="LLM के बिना इस फ़ाइल और --labels की सहमति दर निकालें")
    parser.add_argument("--generate", action="store_true", help="अपने एजेंट से सेट के उत्तर फिर बनाएँ; --cases पर लिखें")
    args = parser.parse_args(argv)

    if args.compare:
        mine = load_labels(args.labels)
        other = load_labels(args.compare)
        compare_labels(mine, other, "मैं", "प्रशिक्षक" if "instructor" in args.compare.name else args.compare.stem)
        return

    cases = read_jsonl(args.cases)

    if args.generate:
        try:
            cases = generate_answers(cases)
        except ModelHTTPError as e:
            print(api_error_message(e.status_code, str(e.body)[:200]))
            raise SystemExit(1)
        write_jsonl(args.cases, cases)
        print(f"→ उत्तर {args.cases} में लिखे गए। अब tools/annotate.py से लेबल दें")
        return

    if not args.labels.exists():
        raise SystemExit(f"{_rel(args.labels)} नहीं मिला। पहले tools/annotate.py में 10 मामलों को लेबल देकर सहेजें")
    labels = load_labels(args.labels)
    rubric = args.rubric.read_text(encoding="utf-8")

    model_name = args.model or MODEL
    if model_name == "test":
        model = build_test_model()
        print("[model] test (API कॉल के बिना सरल नियमों वाला नकली मॉडल; वास्तविक LLM मूल्यांकन नहीं)")
    else:
        model = build_llm_model(model_name)
        print(f"[model] {model_name}  temperature=0  rubric={_rel(args.rubric)}")

    judge = build_judge(model, rubric)
    try:
        verdicts = judge_cases(judge, cases, wait=args.wait)
    except ModelHTTPError as e:
        print("\n" + api_error_message(e.status_code, str(e.body)[:200]))
        raise SystemExit(1)
    except UnexpectedModelBehavior as e:
        print(f"\nनिर्णय का प्रारूप गलत था (LLM आउटपुट pass / fail / unsure के अनुरूप नहीं था): {str(e)[:200]}")
        print("फिर चलाएँ। समस्या जारी रहे तो देखें कि rubric.md में जोड़ी पंक्ति में आउटपुट प्रारूप बदलने का निर्देश तो नहीं है")
        raise SystemExit(1)

    summary = summarize(cases, verdicts, labels)
    print_summary(summary)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {"model": model_name, "rubric": str(_rel(args.rubric)), "run_at": datetime.now().isoformat(timespec="seconds"),
             "verdicts": verdicts, "summary": summary},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n→ {_rel(args.out)} में सहेजा गया")


if __name__ == "__main__":
    main()
