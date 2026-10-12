# Deliverables (same shape every run)

## 1. Findings doc (Claude Doc), sections in this order
1. **Summary**: lead with the broadest and most concentrated theme and the session arc; theme table (claim, talks, units, anchor excerpt) sorted by talks; one line pointing to the action list and methodology.
2. **What to do in the next six months**: from `render_sections.py` → actions.md, built from bundles.json. Order is fixed: start with the President of the Church (his own invitations, then his earlier invitations repeated by others), then challenges asked by several speakers (bundled, most-repeated first), then single-speaker challenges for everyone, then items for specific groups. Promises excluded; bracketed corrections for transcription errors.
3. **The ten themes**: per theme: Claim; Prevalence (talks, units, sessions, lead codes with talk counts); 3–4 verbatim excerpts with speaker, unit ID, block time; Note (1–2 sentences, no unverifiable claims about intent); then the **coded examples table** (9–10 rows, grouped by category) from examples_md.json.
4. **Additional insights**: speakers and length (table by calling; women speakers); scripture (volume table; chapters reused across talks; shared stories; spoken-citation rate; caveat); who was quoted; language (Christ density median and extremes, recurring phrases, questions, invitations); **word cloud** (drawn chart, top 60 from Word_Frequencies; Christ/Jesus/God/Lord/love emphasized by rank, not hand-picked); **fun facts table** (Number | What it counts) built only from Fun_Facts, Talk_Metrics, Phrases and verified story details.
5. **Theory mapping**: construct table with fit (strong/partial/analogical), unmapped categories, candidate contributions, Painter level, one testable hypothesis.
6. **Patterns across themes**: theme × session heatmap (drawn chart), cross-theme patterns.
7. **Since last conference** (second run on): categories that rose or fell most in share, themes new or gone, scripture-volume shift, new codes.
8. **Episode notes**: cold open; 3 segments with talking points and one stat each; historian's angle; 3 discussion questions; listener takeaway.
9. **Methodology** (always last): fill `references/methodology.md` with this run's numbers.

## 2. Workbook
`conference-YYYY-MM-coding.xlsx` (build_workbook.py), recalculated with zero errors. Present with `present_files` with `master_codebook.json` and `history.json`.

## 3. Interactive report page (HTML, published)
One page per conference at the series link, built by `build_report_page.py` from the run folder, `report_content.json`, and history.json. Sections: hero with headline stats; the six-month list first (President of the Church panel, bundled challenges with speaker counts and expandable quotes, progress bar, per-viewer check-offs, hide-quotes toggle, print-ready two-page checklist); weekend-arc heatmap; ten themes as expandable claims with session counts, lead codes, note, and coded-example table; word cloud; fun facts; scripture and speakers; theory mapping; trends over time (baseline bars on the first run, lines after); methodology with design, trustworthiness, reflexivity, limitations, references. Republish to the same link each run.

## Quality loop (run before delivering)
Treat the first complete draft as a hypothesis. Run critique passes, each through a different lens, and fix the weakest point each time:
1. **Verifier**: `verify_quotes.py RUN_DIR` and, after exporting the doc to markdown, `verify_quotes.py RUN_DIR doc.md`. Zero failures.
2. **Skeptical academic**: any claim about intent, causation, or "independence" the transcript cannot show? Any count not traceable to a sheet?
3. **Member reading for action items**: is every action concrete, correctly attributed, and not a promise?
4. **Editor**: cryptic excerpts (lengthen to a self-explaining span), garbled ASR words (bracket the correction), inconsistent numbers between doc, workbook, and charts.
5. **Chart reviewer**: screenshot every chart; fix overlaps and clipping.
Report honestly how many passes ran and what changed; never pad.
