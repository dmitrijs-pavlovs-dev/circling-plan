# Soulful Events — circling & authentic relating

Everything for running and promoting circling events in Tallinn, hosted by
Dmitrijs and Diana under the [Soulful events](https://www.facebook.com/SoulFamilyEvents)
page.

This repo used to be two separate projects: `circling-plan` (the session
runner app) and `circling-tallinn` (the Facebook cover and logo design work).
They are merged here. The repo name and the live URL stay `circling-plan`
so the GitHub Pages link keeps working.

**Live session app:** https://dmitrijs-pavlovs-dev.github.io/circling-plan/

---

## Folders

| Path | What's in it |
|---|---|
| `index.html`, `app.js`, `styles.css` | The session-runner web app. Renders the session plan on your phone and adds a live clock, a focus timer and a music player. Must stay at the repo root, that's what GitHub Pages serves. |
| `session-plan.md` | **The plan for the next session,** the version you read on the phone while running it. The app fetches this file by this literal name and the deploy workflow copies it into the published site, so edit it in place. Push to `main` and the live site re-renders. After an event, copy the plan into `events/<date>/` and start the next one here. |
| `program.html` | **The designed read of the same programme:** the four principles written out in full, the run of show, and what is still open. Self-contained, print friendly, and published at `/program.html`. The app links to it and it links back. Two files hold the same programme on purpose, one to run from and one to read and share, so **when you change a timing in one, change it in the other.** |
| `research.md` | Background research on circling and authentic relating formats: exercise tiers, prompts by intensity, session timings including the three-hour format. Reference material for designing sessions. |
| `brand/` | All visual assets. See below. |
| `events/<date>-<city>/` | One folder per event: the copy, the promotion plan, and the exact assets that were published. `2026-08-16-tallinn` is the current one. |
| `archive/` | Superseded work, nothing live: the June 2026 Portugal session programs, and the second round of Facebook cover exploration. See `archive/README.md`. |
| `render.sh` | Renders the HTML design templates to PNG with headless Chrome. |
| `.claude/agents/` | Subagent definitions for working on this repo. See below. |

### `brand/`

| Path | What's in it |
|---|---|
| `brand/covers/` | 25 Facebook cover designs as hand-written HTML (`cover-01.html` … `cover-25.html`) plus the shared `base.css`. Each is a self-contained 1920×1005 layout. **Covers 12 to 25 are the current round**; 25 is published on the event, and 23 and 24 are the other two finalists. The rest of that range are live alternates worth reusing as ad creatives rather than dead drafts. Round two is in `archive/`; round one was deleted as superseded twice over. |
| `brand/social/` | Instagram formats built on the same design language: `ig-square.html` (1080×1080 feed) and `ig-story.html` (1080×1920 story) on `base-social.css`, plus the ad creatives, `ad-01` to `ad-22` (square) and `story-01` to `story-04` (vertical), on `base-ad.css`, `base-ad-bold.css`, `base-ad-circle.css` and `base-story.css`. `brand/covers/ad-wide-01.html` is the one wide ad. |
| `brand/bg/` | Background plates, 16 of them. `11`–`16` are the current watercolor set (two circles, enso ring, three circles, ripples, people ring, people top view). AI-generated and not reproducible, so they are committed. |
| `brand/logos/` | 16 logo concepts for the Soulful events page, plus `preview.html` which mocks them through Facebook's circular profile crop. `logo-15-flame-badge` and `logo-12-heart-badge` are the two that survive the crop with the wordmark intact. |
| `brand/avatars/` | Host portraits used in the covers. |
| `brand/out/` | Rendered PNGs. **Git-ignored** — regenerate with `./render.sh`. |

## Rendering

```bash
./render.sh          # every cover + both Instagram formats → brand/out/
./render.sh 24 25    # just covers 24 and 25
./render.sh social   # just the Instagram formats
./render.sh ads      # just the ad creatives (squares, stories, the wide one)
```

Needs Google Chrome at the standard macOS path. The templates load Google Fonts
over the network, so be online when rendering.

To make a new design, copy the closest existing template, edit the text and the
`background-image`, and render it. Paths inside `brand/covers/` and
`brand/social/` are relative (`../bg/`, `../avatars/`), so both folders sit as
siblings of `bg/` and `avatars/` on purpose.

## Agents

Defined in `.claude/agents/`, each scoped to one part of the work:

- **event-copywriter** — event descriptions, posts, captions, ad copy. Holds the
  voice rules (no dashes, sparse emoji, nothing prescriptive about how
  participants should feel).
- **cover-designer** — new covers and social formats from the HTML templates,
  renders and visually checks them.
- **session-designer** — the facilitation program: exercises, timing, arc.
- **promo-strategist** — outreach planning, channel choices, paid ads, tracking.

See `CLAUDE.md` for the conventions all of them follow.

## Where things stand

- The **event copy and cover are done and published.** Don't rewrite them.
- The **promotion plan** is written and dated but barely started. The three
  free Facebook levers in it (co-host, invites, posting inside the event) are
  the first thing to do.
- The **session programme now has a settled arc** out of the planning
  conversation: arrive, principles, breath, body, meeting, pairs, threes,
  circle. Eight items are still open at the end of `session-plan.md`, the two
  that matter being the detail of the pair exercises and the consent frame for
  touch.
