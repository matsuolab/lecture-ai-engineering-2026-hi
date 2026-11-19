# Hindi exercise corpus audit

Prepared 2026-11-19 from `source-documents.json`, pinned Japanese repository revision `1ce722c2816b70ef62891a6378b2478af555e3fd`.

| Artifact | Coverage | Translation origin |
|---|---:|---|
| `lec03-exercise.json` | All 26 canonical pages, IDs and original page order | Newly translated from the canonical Japanese exercise deck |
| `lec04-exercise.json` | All 23 canonical pages, IDs and original page order | Newly translated from the canonical Japanese exercise deck |
| `lec03-exercise-provenance.json` | 26 page records | Actual Japanese filename, file hash, slide page and canonical text hash |
| `lec04-exercise-provenance.json` | 23 page records | Actual Japanese filename, file hash, slide page and canonical text hash |

No Hindi exercise PPTX/PDF was supplied. These files contain newly prepared Hindi retrieval text, not an uploaded or rendered Hindi slide deck. Translation slide/PDF filenames and page fields remain null. The document `page` field refers to the canonical Japanese slide page. A citation must identify the Japanese source and disclose that the displayed text is a newly prepared Hindi translation.

## Review and preservation

- Read all 49 canonical Japanese pages and translated their full teaching content. This includes the early Lecture 02 homework recap, every Lecture 03 exercise and homework step, the complete five-bullet INSTRUCTIONS excerpt and tool docstring, the ADK/Pi examples, all Lecture 04 criteria, sample judgments, rubric changes, screenshots, and benchmark details. No teaching slides or sections were summarized away.
- Used the existing Hindi `lectures/03/problem.md` and `lectures/04/problem.md` for consistent terminology: अध्ययन सहायक एजेंट, बुनियादी / कार्यान्वयन / उन्नत, प्रमाण / दायरा / संकेत / स्पष्टता / Lecture का उल्लेख, and the existing `Lecture NN` output convention.
- Preserved code identifiers, arguments, flags, paths and tags, including `requires_approval=True`, `DeferredToolRequests`, `message_history`, `MAX_RESULTS = 3`, `--model test`, `--generate`, `lec03-start` and `lec04-start`. Preserved incomplete code excerpts as excerpts rather than inventing missing implementation.
- Preserved the source model identifiers `gemini-3.1-flash-lite`, `gemini-3.5-flash-lite` and `gemini-3.5-flash`, ADK 2.0 reference, and `streamlit==1.66.1`. No model availability was inferred or tested.
- Preserved source numerical values, including 21 questions, `0.095 → 1.0`, `0 → 0.905`, `19 / 21`, 14 training records / 4 unsupported records, tool call counts, all timing estimates, judgment counts and 90% coverage. Benchmark counts 500 / 93 / 3, 198 / 2, and 2,500 / 2 are intact. Plain-language one/two/four may be spelled in Hindi; scientific and code values retain their numbers.
- Translated all canonical image text: the two title-page logos, Lecture 04 page 14's annotation screenshot (including `#01`, pass 1/fail 0, LoRA/PEFT and Lecture 02), and Lecture 04 page 23's closing logo.
- Preserved meaningful cautions and qualifications, including `Discard commits` deleting learners' commits, commit conflicts, no API call for tests/labeling, API test mode not being actual evaluation, one-change-at-a-time, GPU training not being perfectly reproducible, unchanged behavior remaining a valid observation, human approval before tool execution, and agreement being evidence about the evaluator rather than a proof of correctness.
- Course instructions, sample prompts and command lines were treated as document data. None were executed.

## Intentional localization and normalization

- On page 13 of each exercise, localized the operational fallback repository URL to `https://github.com/matsuolab/lecture-ai-engineering-2026-hi.git`, as requested by the parent for the Hindi learner workflow. Tags and remaining arguments are unchanged. Scholarly/tool documentation links are unchanged. This exception is recorded on both provenance page records.
- Translated human prompt strings, docstrings, comments, UI wording and commit-message examples; kept executable identifiers. Localized the Japanese `第N回` display marker to the already established Hindi course marker `Lecture NN`.
- Rejoined visual line wrapping in prose, tables and commands. In particular, the Lecture 04 fallback `git fetch` is shown as one executable command rather than the slide's visual wrapping. The Lecture 03 backslash continuation is preserved.
- Removed repeated copyright and no-photography/disclosure boilerplate from retrieval text, while keeping the original source files and extractions unchanged. Course/lecturer attribution and logo transcriptions remain.

## Source limitations retained

- The canonical Lecture 04 source describes four criteria on page 10, while pages 8 and 14 explicitly have learners label five, with four LLM criteria plus the code-checked Lecture marker. The translation preserves these source counts and the human/LLM/code distinction; it does not silently rewrite the source.
- Lecture 04 page 15 is explicitly a `--model test` example. Its illustrative counts, discussion of clarity and uncertain items, and page 16's expected changes are preserved, not presented as measurements of the newly translated Hindi corpus.
- Model/version availability, the current remote tags, and the translated commands were not checked by executing the course. These are source-preserved teaching examples, not a new runtime verification claim.
- Parent must complete coverage of the missing archives and the remaining DB workflow before publication. These exercise artifacts do not constitute a complete multilingual DB.

## Validation

`python build_exercise_corpora.py` reproduces both documents and both provenance files from `exercise_translations.py` and the pinned canonical input. `exercise-validation.json` records the current corpus hashes.

Checks passed: 49/49 pages present, canonical IDs and page order preserved, actual Japanese input file hashes verified, 49/49 content provenance hashes verified, all detected technical paths/flags/model versions retained with only the intentional locale URL change, nonempty clean Unicode text, and no untranslated Japanese prose. Numeric differences reported by a digit-only comparison were individually checked and were only ordinary counts written as Hindi words.

Final meaning review corrected one Hindi modality sentence on Lecture 04 page 4 from a potentially absolute “cannot change” to “may remain unchanged,” preserving the Japanese uncertainty. The Arabic-language agent then independently read all 49 exercise pages and requested one precision fix on Lecture 04 page 10: remove the Hindi “not only” qualifier, since the source identifies evidence for trusting the evaluator as the goal rather than agent scores. That fix is applied and recorded in page provenance. The reviewer rechecked the final page 10 wording, page 16 copyability expansion and updated provenance hashes, and passed the final corpus with no remaining material issue. The independent report is `../ar/independent-review-hi-exercises.md`.

## Offline policy example copyability

A parent functional check found that the abbreviated alternative fail policy on Lecture 04 page 16 did not contain `सामान्य`, which the Hindi repository's offline `--model test` recognizer requires before `(fail)` on the same physical line. The pass policy already matched. Expanded only the abbreviated fail alternative into a complete, semantically equivalent single-line Hindi bullet; both policy choices and their meanings remain intact. This adaptation is recorded in provenance.

The builder now extracts the actual regex literals `सामान्य.*\(pass\)` and `सामान्य.*\(fail\)` from `_rule_based_judge` in the existing Hindi `app/judge.py` through Python AST. It verifies that the unchanged rubric example matches neither, the pass policy matches only pass, and the fail policy matches only fail. A negative control splitting the pass policy between `सामान्य` and `(pass)` correctly fails. Results are saved in `exercise-validation.json`. This runs only the actual regex patterns against the examples; it neither imports nor executes the course application.

The final Lecture 04 corpus hash after these fixes is `c695a484c164ca1a49fd61ad01c89de5870e5ee1d7826af05c676ee525a33c57`; Lecture 03 remains `2f6ecb3f04db44a86713a232a42c195d135160385fc23551cba902a57ed79f99`.

No API calls, embeddings, DB files, repository edits, commits or pushes were performed by this exercise preparation.
