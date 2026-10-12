# Brief: the LEVEL whole-conference quiz (25 questions)

First read `/home/claude/run-2026-10/quiz_prompt.md`. Everything it says about what makes a question good, fair wrong answers, faithfulness, sensitivity, exact quotations, and the work method applies here too. The differences are below.

## Your task

Write the **LEVEL** quiz for the whole October 2026 general conference: exactly 25 multiple-choice questions (easy: exactly 3 options each; medium and hard: exactly 4 options each). Two other writers are writing the other two levels, so stay in your lane:

- **easy**: for a family with children or someone who watched once. Memorable stories and pictures ("Who told about …?" / "In Elder X's story, what …?"), the plain main message of well-remembered talks, what President Oaks invited us to do, simple things many speakers repeated.
- **medium**: understanding. What a speaker meant by a key phrase; why a story was told; what a speaker said follows from a principle; matching a teaching to the speaker who gave it when the teaching is distinctive; what several speakers taught in common.
- **hard**: for someone who studied the conference. Fine distinctions a speaker actually drew; how two talks on a similar subject differed or agreed; the logic of an argument; which everyday situation best fits what a speaker taught; what a speaker said about a common misunderstanding. Hard means it takes real understanding, never that it is a trick or an obscure trifle.

Read `/home/claude/run-2026-10/quiz_in/conference.json` (every talk with a summary, the themes this site noticed, the direct invitations, and counted facts). Then read the full text of every talk you ask about (each talk's `full_text_file`; paragraphs carry `unit` ids like T05.12). You should read most or all of the 37 talks; never write a question from a summary alone.

Save to `/home/claude/run-2026-10/quiz_out/conference_LEVEL.json`, then run and fix until PASS:

    python3 /home/claude/run-2026-10/validate_quiz_conf.py LEVEL

## Rules particular to the conference quiz

- **Cover the conference.** Draw on at least 20 different talks, with no more than 2 questions about any one talk, and include all four sessions. Include 2 or 3 questions on President Oaks's talks (T27 and T37), at least one of them on a direct invitation he extended.
- **Name the speaker in the question** (or make naming the speaker the question), since people will not have a talk in front of them. Use each speaker's `short` name.
- **Meaning over numbers.** At most 3 of the 25 may be "fact" questions drawn from the counted `facts`, `stats` or `arc` in conference.json (mark these `"kind": "fact"`, with `"talk": null, "unit": null`). All others are `"kind": "talk"` and must give the `talk` id and the one `unit` that proves the answer. Up to 2 questions may be about something several speakers taught in common; cite one representative `unit` and name the others in `why`.
- **Themes are patterns this site noticed**, not official statements. If you ask about one, word it as "a pattern this site noticed" and mark it `"kind": "fact"`.
- In `why`, name the speaker so the person knows which talk to revisit.
- "Who said it" questions are fine at the easy level when the story is memorable; at medium and hard the question must turn on meaning, not on memory for names.

## Output schema

```json
{"level": "LEVEL", "questions": [
  {"q": "…", "options": ["…", "…", "…"], "a": 0, "why": "…", "kind": "talk", "talk": "T05", "unit": "T05.12"},
  {"q": "…", "options": ["…", "…", "…"], "a": 1, "why": "…", "kind": "fact", "talk": null, "unit": null}
]}
```

When you finish, reply with only: the level, "PASS", and one line on anything you were unsure of.
