# Assets — sourcing, prep, generation, costs

## Public-domain archives (free, the "historic" half of many ideas)
- **Wikimedia Commons** via `scripts/tools/commons_search.py` (API search, thumbnails, sizes).
  Rate limits are real: use a descriptive User-Agent (`AIEditingEraAd/1.0 (https://claude.ai/code; …)`)
  and sleep 6–8 s between downloads. **Request only standard thumbnail widths** (1920 or 3840:
  `/thumb/a/ab/Name.jpg/1920px-Name.jpg`, TIFF → `lossy-page1-1920px-Name.tif.jpg`) or the original if
  it's ≤1920. Non-standard sizes get 429/blocked. Never print or send the user's email in the UA.
- Met / AIC / LoC / Rijksmuseum / Wellcome (IIIF) are good alternatives (the Met API returned 410 in Oct 2026).
- Good veins for "history of X": Diderot *Encyclopédie* plates, Muybridge sheets (cells → animation),
  Marey, phenakistoscope discs (LoC), automata (Jaquet-Droz drawings, the Turk), Méliès, Metropolis (US PD),
  Dürer, Vesalius, Met marble heads (front/side/back = a turntable), patent drawings (NARA).

## Prep (`scripts/tools/prep_assets.py`, edit the SPEC dict)
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

## Moving footage (ask first, every batch)
- Topview (installed `topview-browser` plugin; Wan 3.0 Prime ≈ 22.5 cr / 15 s 1080p), Magnific `video_generate`,
  fal (Seedance 2.5 `bytedance/seedance-2.5/...`). Write prompts with the seedance-2-0 / minimax-h3 skills.
- Before asking, show: the shots needed and why, the model, seconds, the cost estimate, and a fallback that skips video.

## Cost sheet to show at Stage 0 (update with live balances)
| Item | Typical count | Cost |
|---|---|---|
| GPT-Image-2 hero/fusion stills | 4–8 | 600–700 cr each |
| Background removal | 5–15 | 3 cr each |
| ElevenLabs music candidates | 2–4 | small (account quota) |
| ElevenLabs SFX | 10–15 | small |
| Video generation | 0–6 clips | ask per batch |
`ai_editing_era` spent ≈ 3,600 Magnific credits (6 GPT-Image-2 + 15 cut-outs) and 4 music + 14 SFX generations.
