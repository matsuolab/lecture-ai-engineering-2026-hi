# Hindi Lecture 03 corpus review

Prepared for the parent from Japanese source commit `1ce722c2816b70ef62891a6378b2478af555e3fd`. This is reviewed source text and graph terminology, not a finished embedding database.

## Deliverables

- `lec03-main.json`: 71 canonical pages, retaining the Japanese document/section/page-ID structure and all substantive Hindi teaching text.
- `provenance.json`: one record per canonical page, linking the actual uploaded Hindi PPTX slide when available, source/version hashes, correction history, and reviewed-content hashes.
- `graph-terms.json`: 72 term nodes with original IDs/kind and technical English aliases intact; Japanese human labels and aliases are translated into Hindi.
- `validation.json`: structural and coverage results. The two builder scripts reproduce these local artifacts without APIs, embeddings, or course-repository edits.

## Sources and page correspondence

The uploaded Hindi PPTX has 69 slides. The authoritative Japanese final deck and GitHub corpus have 71 pages. The Hindi PDF also has 69 pages, but its extracted text has corrupt glyphs; the clean PPTX is the textual source. PDF page-by-page equivalence has not been asserted: `translation_pdf_page` stays null. The verified reference is the original PPTX slide number.

The canonical corpus `page` field retains Japanese-final pagination. It must not be displayed as a Hindi PDF page. In particular, canonical page 3 corresponds to Hindi slide 4, page 4 to Hindi slide 3, pages 33–57 generally shift by one, and pages 59–71 shift by two. Canonical pages 32 (tool search) and 58 (harness RSI) have no uploaded Hindi slide and are explicitly marked as newly translated from the Japanese final source. Citation/UI code must use this provenance before activation.

## Review and changes

All 71 canonical pages were compared with the supplied Hindi text and Japanese source. The output reuses 44 uploaded pages without substantive changes, corrects or supplements 25 existing pages, and translates the two new source pages. Full correction details are recorded per page; the important changes are:

- Page 3: new final-source heading/introduction and explicit consequence of confusing data with instructions; old translated slide 4 is correctly remapped.
- Page 19: restored graph axes, tick values, probability-series labels, years, and model labels from the Japanese corpus. No unseen plotted coordinates were inferred.
- Pages 24, 26, 28: final-source MCP expansion, convenience/security trade-off, and revised data-leak heading. Approval becoming a formality remains a tendency, not an unconditional assertion.
- Page 29: restored the question about detecting stopped/failed background tasks and corrected the Hindi slide's erroneous Part 3 reference to Part 2.
- Page 30: verified both batch-call captions are already correct in Hindi: independent calls together; dependent calls in sequence. They were retained.
- Page 31: added the final-source discussion of stronger versus cheaper models and per-subagent model selection.
- Pages 32 and 58: translated all content of the new tool-search and harness-RSI pages, preserving the examples, technical names, quantitative claims, and the question about allowing evaluation/approval/isolation/stopping changes.
- Pages 34, 36, 50, 53, 59: incorporated source deletions/heading updates, reassembled a JSON sample split across text boxes, added all three configuration/Skill/memory risk explanations, and added the final summary point about evaluation/stopping remaining outside the agent's changes.
- Pages 61–64: restored an omitted ADK 1.x migration detail and the precise Quri relationship, clarified standard SDK support versus enabled-by-default execution, retained schema-validation caveats, restored the earlier tool-list/context connection, and clarified the meaning of cheating solutions in METR's measurement caveat.
- Pages 69–70: corrected inclusive quantitative bounds (`90%以上` → at least 90%; `100分の1以下` → at most 1/100), clarified developer review of evaluation wording, and preserved the within-15-minutes timing bound.
- Fixed two missing word-boundary spaces. Kept the source's illustrative system prompt instruction to respond in Japanese as lesson data, not a request to change this corpus's language.
- Independent Arabic-owner review additionally restored Graduate School in the lecturer affiliation (page 2), the high-autonomy qualifier (page 57), and corrected “after September” to “after the September incident” (page 70). These changes are reflected in the corpus, builder and provenance.

Repeated copyright/footer lines and the first slide's photography/disclosure boilerplate were removed from retrieval text; the original uploaded files and extracted text retain them. Course/date/lecturer attribution, citations, examples, code, probabilities, costs, and limitations are retained. No teaching content was summarized away as a cleaning step.

## Checks

- JSON parsing, exact 71-page coverage, page order 1–71, unique canonical IDs, original section boundaries, and nonempty titles/text pass.
- No untranslated Japanese characters remain in Hindi content or page titles.
- Original Hindi source file and canonical Japanese file hashes are recorded; every reviewed page has a content hash.
- New-page provenance explicitly has no Hindi slide reference. PDF page references are unverified and null, rather than guessed.
- Graph terminology has exactly 72 original node IDs; every non-Japanese source alias remains byte-for-byte unchanged. No Japanese human label or alias remains.
- Important quantitative examples and the independent/dependent tool-call distinction were checked against Japanese while reviewing the pages. Existing Hindi unit conversions such as 920,000 → 9.2 lakh and 89,000 → 89 thousand retain their quantities.

## Limits and source caveats

This is an AI editorial/source-faithfulness review, not native-speaker sign-off or a search-accuracy measurement. No embedding API call, DB construction, or live retrieval evaluation was performed. Only `lec03-main` is covered; this does not fill the missing Lecture 01/02 or other source documents.

The uploaded Hindi slides themselves remain the older 69-slide version. The new and corrected DB text will therefore differ from that deck until the slides are updated. The database must preserve both canonical and uploaded-slide provenance when citations are shown.

The Japanese final page 28 refers to an “EchoLeak paper on the previous page,” but its preceding page is about idempotency; that stale source reference is retained and flagged rather than replaced with an invented citation. Dated product claims, prices and incident reports are faithfully preserved as teaching-source claims; their current external accuracy was not re-researched.
