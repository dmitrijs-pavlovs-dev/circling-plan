# Working in this repo

Read `README.md` first for the folder layout.

## Voice rules for anything public-facing

These were fought for over many rounds of feedback with Diana. Breaking them is
the fastest way to make copy that has to be rewritten.

- **No dashes as punctuation.** No em dashes, no en dashes, no " - ". Use
  commas, colons, or a new sentence. Dashes read as AI-written to this audience.
  (Interpuncts as separators in dates and venue lines are fine: `16:30 · Tallinn`.)
- **Never tell the reader what they feel or know.** "Most of us know the two
  extremes" was rejected for exactly this. Use "sometimes we…" or speak from
  the hosts' side instead.
- **Never prescribe how participants should behave.** "As a group, we give space
  and slowness" became "Our inspiration is to give space and slowness" for this
  reason. The hosts hold the conditions; nothing is asked of attendees.
- **No promises about outcomes.** Something can "become easier" or "come to
  feel"; it is never guaranteed.
- **Feelings are not ranked.** No draining-vs-filling framing that implies heavy
  feelings are the bad ones.
- **Emoji: few, and warm.** The approved set is 🌊 💜 🕯 🙏 plus 🗓 📍 for the
  date and venue lines. No faces.
- **Avoid facilitator jargon** where a plain phrase works. "Simple guidelines",
  not "agreements" or "container".
- Spell out "contact improvisation", not "CI", for a general audience.

## Fixed event facts

- Title: **Circling & Authentic Relating with Dmitrijs & Diana**
- Sunday, 16 August, 16:30, three hours
- Üks Maja, Valdeku 66, Tallinn
- Facebook event: https://www.facebook.com/events/1947390679313071
- Page: https://www.facebook.com/SoulFamilyEvents
- Hosts: Dmitrijs, circling facilitator and massage therapist. Diana,
  psychologist, somatic practitioner and contact improvisation dancer.
- Diana goes on the **left** in every cover, Dmitrijs on the right.

The canonical event description lives in
`events/2026-08-16-tallinn/event-copy.md`. Do not rewrite it from memory,
read it.

## Design conventions

- Palette: cream `#f3ece1`, burnt orange `#c2571f`, warm brown text `#45372c`,
  muted `#7a6a58`.
- Type: Playfair Display for titles and italic subtitles, Montserrat for the
  letterspaced kicker and detail lines.
- Covers are 1920×1005. Text block right, artwork left, gradient fade between.
- After rendering a design, **look at the PNG** before recommending it.
  Crop and overlap problems are invisible in the HTML.

## Session plans

`session-plan.md` at the root is always **the plan for the next session**,
whichever event that is. Right now it's the 16 August programme that came out of
the planning conversation. The arc is settled: arrive, principles, breath, body,
meeting, pairs, threes, circle. Eight items are still open at the bottom, so
don't present those as decided.

Things to keep straight:

- `app.js` fetches `session-plan.md` by that literal filename and
  `.github/workflows/deploy.yml` copies a fixed list of files into `_site`. If
  you rename the plan or add a file the live site needs, change both.
- `program.html` at the root is the designed read of the same programme, linked
  both ways with the app and published at `/program.html`. It duplicates the
  timings in `session-plan.md` deliberately. Change a timing in one and change
  it in the other, or the phone and the page will disagree during the session.
- The programs in `archive/` are from the **June 2026 Portugal event**,
  co-facilitated with Alina, about 100 minutes, built for a handful of people.
  They are an exercise library, not a template, and the planning conversation
  superseded them. In particular the **five guiding principles**, the **Wink**
  and the **Noticing Game** are not in the current evening. Never present
  archived material as the current plan.
- **Group size:** aiming for seven to twelve, the room holds about twelve, and
  the real number is not known until the day. Where a round's cost depends on
  headcount, give both branches rather than picking one.

## What is settled and what isn't

- **Settled, do not rewrite:** the event title, the event description in
  `events/2026-08-16-tallinn/event-copy.md`, and the published cover
  (`cover-25`). These went through many rounds with Diana.
- **Written but barely started:** the promotion plan.
- **Genuinely open:** the detail of the pair exercises, the consent frame for
  touch in the walking segment, and whether curiosity becomes a fifth principle.
