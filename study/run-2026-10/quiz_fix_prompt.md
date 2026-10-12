# Brief: revise quiz questions after independent review

First read `/home/claude/run-2026-10/quiz_prompt.md` (and, for a conference file, `/home/claude/run-2026-10/quiz_conf_prompt.md`): those are the standards. An independent reviewer answered every question blind from the talk text and left notes on the ones with problems. Your job is to fix every noted problem so well that the reviewer would have nothing left to say.

For each assigned file NAME:

1. Read the reviewer's notes in `/home/claude/run-2026-10/quiz_review/NAME`. Ids look like `T05.hard.3` (talk, level, question number within the level, counting from 1) or `CONF.hard.3`. The option indexes in the review refer to a shuffled copy, so ignore index numbers and go by the note's words.
2. Read the talk text (`/home/claude/run-2026-10/lessons_in/Txx.json`; for conference questions, the talk named by the question's `talk` field).
3. Edit `/home/claude/run-2026-10/quiz_out/NAME`. Change ONLY questions that have a note. For each:
   - Wrong, overstated or unfaithful wording (in the question, an option, or `why`): correct it against the talk text. `why` must state or clearly support the right answer.
   - Cited `unit` off by a paragraph, or quotation not exact: fix the `unit` or the quotation by copying from the talk text.
   - "Too easy for hard" / "plain recall" at the hard level: REPLACE the question with a truly hard one on the same part of the talk: a fine distinction the speaker drew, the logic of the argument, what the speaker said about a misunderstanding, or which everyday situation best fits the teaching, with four plausible options and exactly one defensible answer. Not a trick, not trivia.
   - "Too hard for easy" or trivia at the easy level: replace with a question on the plain main point or a memorable picture from the same talk that a child of 8 could answer.
   - Give-away by length or wording: rewrite options so they match in length and form.
   - An arguable second answer or an unfair distractor: replace the distractor with one that is plausible but clearly not what the talk says.
   - Near-duplicate questions: replace one with a question on a different point.
   If you judge a note mistaken, leave the question and say why in your reply.
4. Run the checker until PASS: `python3 /home/claude/run-2026-10/validate_quiz.py Txx` (talk files) or `python3 /home/claude/run-2026-10/validate_quiz_conf.py LEVEL` (conference files).
5. Write `/home/claude/run-2026-10/quiz_review/fixed_NAME` as a JSON list of the ids you changed, e.g. `["T05.hard.3", "T05.easy.2"]`.

Every rule in the standards still holds: exact quotations only, nothing added to what the speaker taught, reverent and child-suitable at the easy level. Reply with only: files done, how many questions changed, and any note you rejected with a one-line reason.
