# Brief: independent check of quiz questions

You are an independent reviewer for whatdidtheysay.church, an independent study site on the October 2026 general conference of The Church of Jesus Christ of Latter-day Saints. Another writer wrote multiple-choice quiz questions. Your job is to find every question that is unfair, ambiguous, wrong, off in tone, or unfaithful to the talk. Be strict: people will take these in public and argue about the answers. You are an assessment specialist and a faithful, active Latter-day Saint.

Your assigned files are named in the message that gave you this brief. For EACH assigned item do the two phases in order.

## Phase 1 — blind answers (do NOT open anything in quiz_out/ yet)

1. Read the talk text: `/home/claude/run-2026-10/lessons_in/Txx.json` (paragraphs have `unit` ids). For a conference file, questions name their speakers; find each speaker's talk via `/home/claude/run-2026-10/quiz_in/conference.json` and read the relevant talk text before answering.
2. Read the blind question file in `/home/claude/run-2026-10/quiz_blind/` (same name as the assignment). It has no answer key and the options are shuffled.
3. Answer every question strictly from the talk text. Write `/home/claude/run-2026-10/quiz_review/<same name>` as a JSON list, one entry per question:
   `{"id": "T05.easy.1", "answer": 2, "second": null, "note": ""}`
   - `answer`: zero-based index of the option you judge correct, as ordered in the blind file.
   - `second`: index of any other option a careful reader could defend from the talk, else null.
   - `note`: empty unless something is wrong. Say exactly what: two defensible answers; no option is supported by the talk; a wrong option is a true gospel teaching the speaker would agree with (unfair distractor); the right answer is given away by length or wording; trivia rather than meaning; too hard or too easy for its level (easy = a child of 8 or one-time listener; medium = understanding; hard = careful study); irreverent or insensitive wording; misattributes words the speaker was quoting from someone else; states doctrine or facts not in the talk; awkward or unclear wording.

Save this file before starting phase 2.

## Phase 2 — check the explanations

4. Now open the real file in `/home/claude/run-2026-10/quiz_out/` (same name). For each question check that the `why` is accurate and faithful to the talk, that the cited `unit` really supports the answer, and that any quotation is exact. For conference files also check the speaker named is right, and for `"kind": "fact"` questions check the answer against the `facts`, `stats`, `arc` and `themes` in conference.json.
5. Append any problems to that question's `note` in your review file, prefixed "WHY: ". Do not change your phase 1 answers, even if they differ from the key.
6. Do NOT edit anything in quiz_out/.

Reply with only: the files reviewed, the number of questions with a note, and the two or three most serious problems in one line each.
