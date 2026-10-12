# Brief: second revision of quiz questions

First read `/home/claude/run-2026-10/quiz_prompt.md` (and for conference files `/home/claude/run-2026-10/quiz_conf_prompt.md`): the standards. A second independent reviewer answered revised questions blind and left notes in `/home/claude/run-2026-10/quiz_review2/NAME`. Fix every noted question in `/home/claude/run-2026-10/quiz_out/NAME` (find it by id: `T05.hard.3` = talk file, level, question number counting from 1; `CONF.hard.3` = conference file for that level, under "questions"). Change ONLY questions with a note. Read the talk text first (`/home/claude/run-2026-10/lessons_in/Txx.json`).

The commonest note is that a HARD question is "still mere recall". A hard question must not be answerable by recognizing one sentence. Replace it using one of these patterns, all built strictly on what the speaker taught:

- **Apply it.** "Which of these situations best fits what Elder X taught about …?" Four short, realistic, everyday situations (generic people, no names needed); exactly one matches the principle as the speaker stated it; the others each miss it in a specific way the talk rules out (for example they show the very misunderstanding the speaker corrected). The `why` names the principle with a short exact quotation.
- **Trace the reasoning.** "Why, according to Sister X, does … follow from …?" or "Which statement best explains how X and Y fit together in this talk?" where the answer needs two parts of the talk put together.
- **Tell it from its neighbor.** "Elder X distinguished A from B. Which of these is an example of A?" or "Which of these would Elder X say is NOT what he meant by …?" (at most one NOT question per level).
- **Find the misreading.** "Someone summarizes the talk as '…'. What did the speaker say that corrects this?"

Rules for these: wrong options must be plausible to a thoughtful member, never plainly false doctrine and never the bare negation of the key; do not put the key's distinctive words in the stem; options alike in length and form; do not invent anything the speaker said. A scenario you invent is fine as a setting, but the judgement must rest on the speaker's stated teaching, and the `why` must show that.

Where a talk is very short and offers no further distinct hard question (T37 especially), write the fairest question you can on meaning rather than announcement details, and say so in your reply.

Other notes (give-away by wording or length, awkward stem, `why` citing the wrong paragraph or adding something the talk does not say, weak distractors, trivia at easy or medium): fix as the note says, against the talk text.

Run the checker until PASS (`python3 /home/claude/run-2026-10/validate_quiz.py Txx`, or `python3 /home/claude/run-2026-10/validate_quiz_conf.py LEVEL`). Then write `/home/claude/run-2026-10/quiz_review2/fixed_NAME` as a JSON list of the ids you changed.

Reply with only: files done, number of questions changed, and any note you rejected with a one-line reason.
