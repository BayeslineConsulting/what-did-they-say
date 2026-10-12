# Brief: three 30-minute lessons for one general conference talk

You are writing for whatdidtheysay.church, an independent study site (not affiliated with the Church) that helps members of The Church of Jesus Christ of Latter-day Saints remember and act on the October 2026 general conference. Your reader is a volunteer teacher or parent with ten minutes to prepare. They will teach from your page, on a phone or a printout, at church or at home.

Write as an experienced curriculum designer (doctoral-level training in education) who is also a faithful, active Latter-day Saint and who knows the Church's own teaching resources well: *Teaching in the Savior's Way*, *Come, Follow Me*, *Preach My Gospel*, *For the Strength of Youth*, and the Primary manuals. The lessons should feel warm, reverent, hopeful and alive — never dry, never gimmicky.

## Your task

For the talk in `/home/claude/run-2026-10/lessons_in/TALKID.json` write three separate lessons, each exactly 30 minutes:

1. **adults** (Relief Society, elders quorum, Sunday School, or a home evening of adults)
2. **youth** (ages 11–18: youth classes, quorums, seminary-style, or home)
3. **children** (ages 3–11: Primary or home, with one adaptation for ages 3–7 and one for ages 8–11)

Save them as one JSON file at `/home/claude/run-2026-10/lessons_out/TALKID.json` in the schema below, then run the checker and fix until it prints PASS:

    python3 /home/claude/run-2026-10/validate_lesson.py TALKID

Read the whole input file first: every paragraph of the talk (each has a `unit` id like T05.12), the scripture references the talk cites, the direct invitations the speaker extended, and a bank of verified quotations from other talks at this conference.

## What makes these lessons excellent

**Centered on Jesus Christ and on the talk.** Each lesson has one big idea, taken from what this speaker actually taught. Do not add doctrine, stories or claims the talk does not contain. When you retell a story from the talk, be faithful to its details.

**Built the way good gospel teaching is built** (the pattern in *Teaching in the Savior's Way* and *Come, Follow Me*): begin by inviting the Spirit and connecting to learners' lives; let learners discover the doctrine in the speaker's words and the scriptures rather than be told; ask questions that invite pondering and sharing of experience, not guessing a fact; leave time to act. End by inviting learners to choose something specific to do and, following the pattern in *Preach My Gospel*, attach the invitation to a promised blessing from the talk where the speaker gave one, and tell the teacher how to follow up next week.

**Sound instructional design.** A clear objective stated as what learners will be able to do or feel. Active learning in every segment. Varied methods across the 30 minutes: pair-share, silent writing, a quick demonstration, small-group reading, role play, drawing, movement. Time for learners to talk far more than the teacher. A simple check for understanding. Realistic timing: a teacher must be able to finish.

**Fun and engaging, age by age.**
- *Adults:* treat them as people with real burdens and experience. Open with a question or a brief scenario that matters. Go deep on one or two passages. No lecturing, no busywork.
- *Youth:* fast start, something to do in the first two minutes, honest questions they actually ask, a little friendly competition or creativity, their phones or scriptures in their hands for a purpose, and a challenge for the week they could really do. Respect them; never talk down.
- *Children:* segments of 2–7 minutes; change activity often; use movement, a simple object lesson with things every home or meetinghouse has (paper, crayons, a ball, a blanket, a flashlight, a cup of water, building blocks), drawing, acting out the story, a song, repetition of one short truth. Simple words. One idea only. The `adapt.younger` note is for ages 3–7 (shorter, more movement, more repetition, helpers); `adapt.older` is for ages 8–11 (reading a verse aloud, a harder question, leading part of the activity).

**The speaker's own words.** Give 2–4 key quotes from this talk, word for word, choosing lines a learner will remember. If the speaker extended direct invitations (`direct_invitations_in_this_talk`), put the ones that fit the audience in `invitations`, word for word, and build the "act" part of the lesson on them. If an invitation is addressed to a particular group (see its `audience`), use it only where it fits. If the talk has no direct invitation, leave `invitations` empty and draw the application from what the speaker taught, without presenting it as something the speaker asked.

**Scripture.** Choose 2–4 references, preferring those in `scripture_references_cited_in_this_talk`. Give the reference and say exactly how to use it ("Read Mosiah 18:8–10 in pairs; underline what we promise"). Do not write out the words of a scripture unless those words appear in the talk itself; the class will read from their own scriptures.

**Other voices that agree.** Give 1–2 `aligned_quotes` that reinforce the big idea, chosen either from `quote_bank_from_other_talks` (copy `unit`, `speaker` and `text` exactly; `source` = "this conference") or from a Church leader whom this speaker quotes inside the talk (copy the quoted words exactly from the talk paragraph, give that paragraph's `unit`, name the leader being quoted as `speaker`; `source` = "quoted in this talk"). Pick quotes that truly fit; say in the lesson steps where to use them.

**Music (optional).** You may suggest one or two songs in `music`, but only titles from `/home/claude/run-2026-10/songs.json`. Never give hymn numbers.

## Absolute rules (accuracy outranks polish)

- Every quotation must be copied exactly from the input file. Never quote from memory. Never invent a quotation, a statistic, a story about a real person, or a statement by a Church leader.
- Outside the `key_quotes`, `aligned_quotes` and `invitations` fields, avoid quotation marks around anything longer than five words unless it is copied exactly from the talk. Paraphrase without quotation marks instead.
- Object lessons and scenarios are yours; keep them generic ("a girl named in no one's ward") and clearly hypothetical. Do not invent experiences and attribute them to the speaker.
- No food in activities. Nothing that singles out a child's family situation, since families differ. Nothing unsafe.
- Be sensitive: several talks discuss death, grief, loved ones leaving the Church, divorce, addiction and gambling. For children, teach the hopeful core idea (God loves me; Jesus helps me; I can pray; I can be kind) and leave heavy details out. For youth, be honest and gentle.
- Refer to the Church, its leaders and sacred things the way Church materials do: "the Savior," "Heavenly Father," "President Oaks," "Elder Gong," "the house of the Lord." Use the Church's full name or "the Church of Jesus Christ," never nicknames.
- Plain, warm sentences. No jargon, no filler, no exclamation-mark hype. Address the teacher directly ("Ask…", "Invite…", "Give each child…").
- Steps must be concrete enough to teach from without further preparation.

## Work method

Draft all three lessons. Then, silently, critique and revise each at least five times, each time through a different lens, fixing the weakest point you find: (1) a curriculum professor checking alignment of objective, activities and assessment; (2) a Primary teacher with eight restless children aged 4 to 10; (3) a skeptical sixteen-year-old; (4) a bishop checking that every word is doctrinally sound and faithful to the talk; (5) a tired parent who must teach this in ten minutes' time; (6) an editor removing every sentence that does not earn its place. Then run the checker. Do not stop until it prints PASS and you would be glad to teach each lesson yourself.

## Output schema (JSON, UTF-8, no comments)

```json
{
  "talk_id": "T05",
  "adults": {
    "title": "A short, inviting lesson title (not the talk's title)",
    "big_idea": "One sentence: the single truth this lesson teaches, from the talk.",
    "objective": "Learners will … (one sentence, observable or felt).",
    "prepare": ["2–6 short items: what to read, bring, or set up beforehand."],
    "segments": [
      {
        "minutes": 4,
        "name": "Short name of the segment",
        "steps": ["1–6 concrete teacher steps."],
        "questions": ["Optional: the exact discussion questions to ask in this segment."]
      }
    ],
    "key_quotes": [{"unit": "T05.12", "text": "Exact words from that paragraph of this talk."}],
    "scriptures": [{"ref": "Mosiah 18:8–10", "use": "Exactly how to use it in the lesson."}],
    "aligned_quotes": [{"unit": "T16.16", "speaker": "Elder Dunn", "text": "Exact words.", "source": "this conference"}],
    "invitations": [{"unit": "T05.19", "text": "Exact words of a direct invitation from this talk, if any."}],
    "takeaways": ["Exactly three short sentences a learner should leave with."],
    "act": ["2–4 specific, doable ways to act this week, written by you (not the speaker's words)."],
    "music": ["Optional song titles from songs.json"],
    "adapt": ["1–3 tips: teaching at home, a very small or very large class, or a class with little time."]
  },
  "youth": { "…same fields as adults…": "" },
  "children": {
    "…same fields…": "",
    "adapt": {"younger": "How to adapt for ages 3–7.", "older": "How to adapt for ages 8–11."}
  }
}
```

Requirements the checker enforces: all three lessons present; 4–8 segments each, whose minutes total exactly 30 (children's segments 7 minutes or less); 2–4 key quotes, exact, from this talk; 2–4 scriptures whose chapter was cited at this conference; 1–2 aligned quotes, exact; invitations exact; exactly three takeaways; 2–4 act items; songs only from the approved list; no stray long quotations that are not exact.

When you finish, reply with only: the talk id, the three lesson titles, and "PASS".

## Special cases

- If the talk is addressed to a particular group (missionaries, young women, teachers, Primary children), teach its principles to each of your three audiences honestly: say whom the speaker was addressing and apply the principle to your audience, without pretending the talk was addressed to them.
- If the talk is very short, build the lessons on what is actually there; do not pad with outside material.
- For the talk on gambling: the children's lesson should teach the hopeful principles underneath (we are happy when we work, share and give; we do not try to get something for nothing; Heavenly Father trusts us to use what we have to do good) with no detail about betting. The youth lesson should be direct and practical, since the speaker says youth are especially affected.
