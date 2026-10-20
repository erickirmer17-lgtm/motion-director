# Review — the critic loop (Stage 5 and 6)

A film is done when the evidence says it works, not when the last command exits. The critic judges
**only rendered frames and the rendered mix**, never the intent in `scene.js` or `DIRECTION.md`.

## 1. Evidence pack (≈1 min, all local)
Build it in `reviews/rNN/` (r01 = first rough cut, r02 = after fixes, …):
- `beats.jpg`: one frame per beat (the frame where the beat reads best) plus the first and last frame:
  `capture.js --list 0,40,…,LAST --out ../reviews/r01/beats` then `sheet.py reviews/r01/beats reviews/r01/beats.jpg`.
- `transitions_*.jpg`: the 6–10 frames around each fast transition (`--from --to`, `--crop` for a morph).
- `safe.jpg`: the beat frames again with `--safe`. Copy, logo or a key subject in red is a defect.
- `phone.jpg`: beat frames with `--width 390 --cols 4`, about phone-in-hand size. Read every word at that size.
- `pop_detect.py` output: every spike is a planned cut or a fast move.
- `strip_*.jpg`: every frame of the fastest move (12 consecutive frames) and the cue frames at −2/0/+2 for the
  biggest sync points; `--crop` for full-resolution detail on faces, logos and small type.
- `flow_check.py` on a 30 fps preview (`--glide a:b` for every move that should be one steady glide): no DIP,
  REVERSE or unplanned STALL/POP. Camera glides and zoom-outs are where generated films stutter.
- Looping films: the last frame matches the first, cursor velocity included; play the clip twice back to back.
- Measured recreations: the per-frame error plot against the source (`references/measured-recreation.md` §4).
- `seek_check.py engine/`: PASS (renders the same in any order; also proves a section can be re-rendered alone).
- Sound: `earshot timeline` with `mix.cues.json`, `earshot sheet` (open it), `earshot critique` (see sound-design.md).
- Per variant (9:16 / 16:9 / 1:1): its own `beats.jpg` and `safe.jpg`. A variant isn't checked because it encoded.

## 2. Checklist (all must hold)
- [ ] First 2 s contain a real hook, not a logo, a fade from black or a title card
- [ ] Every message word readable in `phone.jpg`, and on screen long enough to read: no faster than about
      20 characters per second, counted from when its first word appears (montage words that are texture are exempt)
- [ ] Nothing important outside the safe area, in every variant
- [ ] Real product assets only: the logo is the supplied file, screens are real captures, no invented numbers
- [ ] Same type, colour and grade in every beat (compare `beats.jpg` tiles side by side)
- [ ] No awkward mid-transition frames (half-drawn letters, double images, a stray dot)
- [ ] After every move the eye knows where to go: one focal point per beat, the rest quieter
- [ ] Each cut and visible event has its sound on the frame (earshot sync), and the mix has shape with eyes closed
- [ ] The last frame works as a poster (it ships as `_poster.png`)
- [ ] It doesn't look like the default demo (centred big text on a gradient, everything fading in, logo at the end)
      unless the brief asked for exactly that

## 3. Scorecard (1–5 each, write it to `reviews/rNN/REVIEW.md`)
| hook | readability | continuity | motion | sound sync | brand/facts |
|---|---|---|---|---|---|
Anything under 4 must appear in the defect list.

## 4. Three-defect repair loop
Write the **three largest defects**, each as:
```
D1  f212–f226 (3.53–3.77 s)   evidence: transitions_paste.jpg tiles 214–218 — "e" doubles while the caret moves
    cause: glyph swap at FR 216 but the caret's spring is still at 40 %    local fix: start the swap at 219
```
For launch-critical films, have a second agent try to refute each serious defect (and look for ones you missed)
with a default stance of *reject*, before you spend time fixing; one critic per lens (motion, design, sound/sync)
works better than one generalist.
Patch only those sections, re-render only the affected frame ranges, rebuild only the affected sheets, then
re-score. Repeat until the checklist holds and no score is under 4, or until you've done 3 rounds; then send
the cut and list what's still open. Rank by impact on the viewer, not by ease of fixing. Don't "fix"
things the evidence doesn't show.

## 5. Delivery note (with the final MP4)
2–4 lines: what's in it, format/length per variant, and **what still needs a human eye**: brand sign-off,
claims or numbers to verify, licences (music, archival images), anything the critic scored 4 rather than 5.
