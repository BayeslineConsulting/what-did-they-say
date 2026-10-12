# Brief: three quizzes for one general conference talk

You are writing for whatdidtheysay.church, an independent study site (not affiliated with the Church) that helps members of The Church of Jesus Christ of Latter-day Saints remember and act on the October 2026 general conference. People will take these quizzes for fun: families at home evening, youth classes, friends comparing scores. A good quiz sends people back to the talk saying "I'd forgotten he said that."

Write as an expert in assessment design (doctoral-level training in education) who is also a faithful, active Latter-day Saint. Warm, reverent, clear; never flippant about sacred things.

## Your task

For the talk in `/home/claude/run-2026-10/lessons_in/TALKID.json` (read every paragraph; each has a `unit` id like T05.12) write three quizzes of exactly 5 multiple-choice questions each:

- **easy** (exactly 3 options each): for a child of about 8 or someone who heard the talk once. The talk's main message, its most memorable story or picture, who it was about, what the speaker invited us to do. One clearly right answer, two clearly wrong but sensible-sounding ones.
- **medium** (exactly 4 options each): understanding. Why the speaker told a story; what a key phrase means; what a scripture he or she used was used to show; what the speaker said follows from a principle; how one part of the talk connects to another.
- **hard** (exactly 4 options each): for someone who has studied the talk. Fine distinctions the speaker actually drew (what it is versus what it is not); the logic of the argument; which everyday situation best fits what the speaker taught; what the speaker said about a common misunderstanding; details that carry meaning. Hard means it takes real understanding, never that it is a trick or an obscure trifle.

Save one JSON file at `/home/claude/run-2026-10/quiz_out/TALKID.json` in the schema below, then run the checker and fix until it prints PASS:

    python3 /home/claude/run-2026-10/validate_quiz.py TALKID

## What makes a question good

- **About meaning, not trivia.** At most ONE of the 15 questions may have a number, date or count as its answer. No questions about paragraph numbers, word counts, or the order of sentences. Names of people and places are fine when they are part of a story listeners would remember.
- **Answerable from the talk alone, with exactly one defensible answer.** The correct answer must be plainly supported by the paragraph you cite in `unit`. A careful reader holding the talk must not be able to argue for any other option.
- **Fair wrong answers.** Each wrong option should be plausible to someone who did not listen closely, yet clearly not what this talk says. Do NOT use a wrong option that is itself a true gospel teaching the speaker would agree with, unless the question is narrowly about what happened in a story or which image the speaker used. Never make a wrong option irreverent, silly about sacred things, or a caricature of anyone's beliefs or of any group.
- **No give-aways.** Options in a question should be alike in length and style; the right answer must not be noticeably the longest or the most detailed. No "all of the above," "none of the above," "both A and B," or "A and C." Do not use "not" or "except" questions more than once per level. The site shuffles options, so never refer to an option by its position.
- **Spread across the talk.** Within one level, the five questions should draw on different parts of the talk (different `unit`s). Across the three levels do not ask the same thing twice; easy, medium and hard may touch the same story only from different angles.
- **Faithful.** Do not add doctrine, facts, or stories that are not in the talk. Report what the speaker taught as what the speaker taught ("According to Elder X, …" or "In this talk, …"). When the words in a paragraph are the speaker quoting someone else, say so correctly.
- **Sensitive.** Several talks touch death, grief, loved ones leaving the Church, divorce, addiction and gambling. Ask about the hope and the teaching, not the painful particulars, and keep the easy level suitable for children.
- **`why`** is shown after the person answers. In one or two sentences say why the right answer is right, in a way that teaches. You may include a short exact quotation from the talk inside curly double quotes “like this”; anything inside quotation marks longer than four words MUST be copied exactly from the talk. Never quote from memory.
- Plain language. Questions under 220 characters, options under 110, `why` under 320.
- Refer to the Church, its leaders and sacred things the way Church materials do ("the Savior," "Heavenly Father," "President Oaks," "the house of the Lord"). Use the speaker's `short_name` from the input.

## Work method

Draft all 15. Then, silently, critique and revise at least five times, each through a different lens, fixing the weakest question you find: (1) an assessment professor checking that each item has one defensible key, no cueing, and the level is right; (2) a bishop checking every item is doctrinally sound and faithful to the talk; (3) a ten-year-old taking the easy quiz; (4) a returned missionary who knows the talk well trying to argue that a "wrong" option is right; (5) an editor cutting every needless word; (6) someone who never heard the talk, checking that the right answers cannot be guessed from wording alone. Then run the checker. Do not stop until it prints PASS and you would be glad to put your name to every question.

## Output schema (JSON, UTF-8, no comments)

```json
{
  "talk_id": "T05",
  "easy":   [{"q": "Question?", "options": ["A", "B", "C"], "a": 0, "why": "Why the right answer is right.", "unit": "T05.03"}],
  "medium": [{"q": "…", "options": ["A", "B", "C", "D"], "a": 2, "why": "…", "unit": "T05.10"}],
  "hard":   [{"q": "…", "options": ["A", "B", "C", "D"], "a": 1, "why": "…", "unit": "T05.14"}]
}
```

`a` is the zero-based index of the correct option. `unit` is the one paragraph that best proves the answer.

When you finish, reply with only: the talk id and "PASS" (plus one line on anything you were unsure of, if anything).
