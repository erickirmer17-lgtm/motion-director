# Assets — sourcing, prep, generation, costs

## Public-domain archives (free, the "historic" half of many ideas)
- **Wikimedia Commons** via `scripts/tools/commons_search.py` (API search, thumbnails, sizes).
  Rate limits are real: use a descriptive User-Agent (`AIEditingEraAd/1.0 (https://claude.ai/code; …)`)
  and sleep 6–8 s between downloads. **Request only standard thumbnail widths** (1920 or 3840:
  `/thumb/a/ab/Name.jpg/1920px-Name.jpg`, TIFF → `lossy-page1-1920px-Name.tif.jpg`) or the original if
  it's ≤1920. Non-standard sizes get 429/blocked. Never print or send the user's email in the UA.
- **Many archives at once:** `python3 System/tools/freeassets/freeassets.py img "<query>" [--category illustration]`
  searches Openverse across ~20 museum/library sources (Wikimedia, Met, Rijksmuseum, NYPL, Wellcome, Smithsonian units,
  Cleveland, Brooklyn, SMK, Science Museum, Europeana, NASA…), public domain only by default (`pdm,cc0`), downloads
  12 candidates (Wikimedia at standard thumb widths, 4 s apart) into `System/Resources/archive_images/<query>/` with
  `_credits.json` and a numbered `_sheet.jpg`. Read the sheet, pick, then prep. Slow (10–40 s per API page), 200
  requests/day anonymous. Thin for rare subjects: fall back to `commons_search.py` or the museum's own site.
- Met / AIC / LoC / Rijksmuseum / Wellcome (IIIF) are good alternatives (the Met API returned 410 in Oct 2026).
- Good veins for "history of X": Diderot *Encyclopédie* plates, Muybridge sheets (cells → animation),
  Marey, phenakistoscope discs (LoC), automata (Jaquet-Droz drawings, the Turk), Méliès, Metropolis (US PD),
  Dürer, Vesalius, Met marble heads (front/side/back = a turntable), patent drawings (NARA).

## Prep (`assets/prep.py` reads `assets/prep_spec.json`; example in `references/prep_spec_example.py`)
- `ink`: engraving → RGBA ink with alpha = darkness against the local paper level. Paper becomes transparent, so plates
  layer cleanly on white. Paper texture survives on very grainy scans; drop those or crop tight.
- `photo`: strict B&W with percentile levels; used rectangular or cover-fit in frames.
- `cut`: bg-removed RGBA, desaturated, cropped to content.
- Muybridge-style sheets: detect the cell grid from dark separators, then register each cell on the
  silhouette centroid (half-strength) so the subject gallops in place.
- Disc images: Hough circle → store cx, cy, cr in the manifest for clean circular clipping and rotation.
- Contact points: compute from alpha extremes (fingertip = leftmost opaque pixel) and store them in the manifest.

## Generation
- **GPT-Image-2** = Magnific `images_generate`, `mode: gpt-2`, `quality: high`, `resolution: 2k`, about 600 cr
  each (700 historically). For identity consistency upload the previous asset (`creations_request_upload`
  → curl PUT → `creations_finalize_upload visible:false`) and pass it as `{type:'image'}`. Prompt for a
  "pure seamless white background, soft even high-key studio light" to make cut-outs trivial.
  Fusions work well for historic-futuristic: "marble bust of an android", "Encyclopédie copperplate engraving of
  a robot arm splicing film".
- **Nano Banana** (`imagen-nano-banana-2-flash`): edits, text-preserving changes, cheaper iterations.
- **Background removal**: `images_remove_background` (3 cr), then `creations_wait`, then download within the token lifetime.
- Cheaper look-dev: `quality: medium` (~180 cr @2k).
- **Free 3D assets first**: Poly Haven (CC0, ~1,000 HDRIs, ~870 PBR textures, ~520 models) via
  `python3 System/tools/freeassets/freeassets.py ph search "<query>"` → `ph get <id> --res 2k`; cached in
  `System/Resources/polyhaven/`, `get` prints the Blender load line (`ph_blender.py`: new World / material / collection,
  never overwrites). Only pay Scenario for what Poly Haven lacks (a specific generated prop, a bespoke panorama).
- **3D beats in Blender** (Scenario extension, `references/scenario-blender.md`): PATINA PBR materials, 360 panorama →
  HDRI World, generated props, Blockout greybox. Each is priced exactly first (free estimate) and needs a yes. Stills
  stay on Magnific and video stays on Topview even though the extension offers both.

## Animation materials (free)
- **Lottie** (lottiefiles.com free animations, Lottie Simple License: commercial use OK, credit optional):
  icons, UI micro-animations, loaders. Render frame-exact in the engine (`references/motion-vocabulary.md` → Libraries).
- **GSAP** (all plugins free): only when a timeline is easier to author with it; drive it with `tl.totalTime(t)`.
- **Animista** names + keyframes for classic entrances/exits (data in `10_October/motion_refs/_research/tool_extracts/`).

## Moving footage (ask first, every batch)
- **Topview is the default** (installed `topview-browser` plugin; Wan 3.0 Prime ≈ 22.5 cr / 15 s 1080p). Magnific
  `video_generate`, fal (Seedance 2.5 `bytedance/seedance-2.5/...`) or Scenario Render Video only when the user picks
  them for that shot: Magnific credits are kept for stills. Write prompts with the seedance-2-0 / minimax-h3 skills.
- A Blender camera move as the motion guide: build it with Scenario `camera_path`, render the guide clip, then follow
  the 3D-guide → real-scale recipe on Topview.
- Before asking, show: the shots needed and why, the model, seconds, the cost estimate, and a fallback that skips video.

## Cost sheet to show at Stage 0 (update with live balances)
Balances: Magnific `account_balance`; ElevenLabs `python3 scripts/tools/elevenlabs.py quota` (scoped keys may 401, so check the dashboard); Topview via its plugin; Scenario CU in its web app (the extension only quotes per call).
| Item | Typical count | Cost |
|---|---|---|
| **Engine-only option** (type, shapes, archival images, library SFX) | — | **0 credits**. Always offer this |
| Openverse SFX gaps + Poly Haven HDRIs/textures/models | any | **0 credits** (CC BY sounds need the `freeassets credits` line in the post) |
| GPT-Image-2 hero/fusion stills | 4–8 | 600–700 cr each |
| Background removal | 5–15 | 3 cr each |
| ElevenLabs music candidates | 2–4 | small (account quota) |
| ElevenLabs SFX | 10–15 | small |
| Scenario (Blender beats: Blockout, PBR, HDRI, props) | 0–6 | exact CU quote per call |
| Video generation | 0–6 clips | ask per batch |
`ai_editing_era` spent ≈ 3,600 Magnific credits (6 GPT-Image-2 + 15 cut-outs) and 4 music + 14 SFX generations.
