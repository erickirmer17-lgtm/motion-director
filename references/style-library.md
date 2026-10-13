# Style library — visual languages to pitch from

Use this at Stage 2 to make concepts genuinely different. Each entry lists the look, the edit grammar and the
engine it suits. Combine freely; one organising idea per film.

## From our own projects (proven, with code)
| Style | Look | Grammar | Engine / files |
|---|---|---|---|
| **Engraving × Lime UI** (ai_editing_era) | white ground, B&W ink-extracted engravings + marble + carbon robot hands, lime UI (crop box, caret, playhead, highlight), terracotta spark | every transition is an edit; match cuts on points; serif→sans morphs; 3D timeline hero | canvas + Three.js; `examples/ai_editing_era` |
| **Lime robot-hands** (claude_motion_clone) | light grey ground, black carbon robot hand (gold seams), lime/green 3D bubbles and voxel tubes, bold grotesk | hand gestures drive type; orbiting particles; pixel trails | numpy `motion_clone_engine.py` |
| **Thermal / pixel / ink** (rise_fall, x_recreate) | grey paper + near-black, red accent, thermal gradient-mapped figures, pixel sprites voxel-extruded, ink scribbles boiled on twos, film finish | VO-synced typing with block→bar cursor; 1-frame flash frames; ring of sprites | numpy `rise_fall_core.py`; `examples/x_recreate_ANALYSIS.md` |
| **Engraving × terracotta** (Anthropic "Keep thinking" reference) | B&W public-domain engravings, terracotta painted marks, Copernicus-like serif | circle/spiral continuity element with 15 fps image flicker inside; ask→task word morphs | analysis in this session; don't copy, reinterpret |

## From promptsmotion.com (243 Claude-made motion pieces with prompts; inspiration, not copying)
Categories: Product UI (76), Charts (140), Kinetic Type (116), Music (44), Code (38), Characters (37),
Diagrams (32), Photos (25), Shapes (23), Particles (19), Phone (8). Pages are `promptsmotion.com/<handle>-<id>`.
WebFetch a page to read its brief when a concept needs a reference. Some useful directions:
- **Paper-style launch film** (`/ik-builds-b8bdcf`): marker notes on paper, a condensed display face for punch lines,
  handwriting drawn on with strokes, squash-and-stretch, one motion per cut, a new idea every 1.5–2 s, drums on dark hits, sub note on the logo.
- **Swiss-style showreel** (`/levabashidze-2d713a`): modernist grid, charts and kinetic type, maximal motion.
- **Easing & morphing showreel** (`/roundtablespace-d3a1be`): shape morphs and easing as the subject.
- **Risograph studio intro** (`/rneayan-474bcf`): riso colour separations, misregistration, halftone grain.
- **Oscilloscope-style motion graphic** (`/rneayan-ea6129`): phosphor vector lines, scope traces.
- **Shape morphing through UI states** (`/twoclipping-5cba86`), **Morphing UI states loop** (`/demonugc-4c5753`).
- **Poster breaking its frame** (`/pankajkumar-dev-0bee87`), **Infinite-zoom landscape loop** (`/koldo2k-5cff87`).
- **History of AI animated timeline** (`/kloss-xyz-b9b3f6`), **Pixel art LLM history** (`/pluginplay-3d4006`).
- **Engraving-style Claude ad** (`/lexnlin-038035`): the brief behind the reference we answered with ai_editing_era.
- **Cinetic** skill (`/lexnlin-6161a6`, `npx skills add Leonxlnx/cinetic`): a concept→launch-film skill to compare against.
- Also: stop-motion explainer, clay-style music video, ASCII visuals synced to a track, whiteboard explainers,
  shadow theatre, beat-synced 3D ball, Swiss editorial blue showreel, kinetic type self-portrait.

## Recipes for "historic → futuristic" (the user's favourite axis)
- Archival imagery (engravings, Muybridge, automata, marble) + one electric accent painted on top + a modern grotesk.
- A fused hero image: archival medium, futuristic subject (marble android, Encyclopédie robot arm).
- Old-tech sounds (typewriter, shutter, projector) handing over to soft modern UI sounds at the turn.
- The turn is a type event: a serif word rolls into a sans word; an archival title becomes your headline.
