# Scenario for Blender — AI generation and agent tools inside the 3D scene

[scenario-labs/blender-plugin](https://github.com/scenario-labs/blender-plugin): a Blender 5.0+ extension
(GPL-3.0, experimental) that puts Scenario's image, video, 3D, PBR, audio and 360-environment models into
Blender, plus a **local MCP server** (`scenario-blender`) that gives an agent the open scene. Use it when a
beat is built in Blender (see Tool choice in SKILL.md); the canvas engine doesn't need it.
Docs: the [user guide](https://github.com/scenario-labs/blender-plugin/blob/main/docs/USER_GUIDE.md),
[MCP reference](https://github.com/scenario-labs/blender-plugin/blob/main/docs/MCP.md) and
[known limitations](https://github.com/scenario-labs/blender-plugin/blob/main/docs/KNOWN_LIMITATIONS.md).

## Setup (the user does the account steps)
1. A Scenario account with API access, plus an API key and secret (Scenario > Organization settings > API Keys).
   Generation spends Creative Units (CU).
2. Blender: Edit > Preferences > System > Network > **Allow Online Access** on. Then Get Extensions >
   Repositories > Add Remote Repository `https://blender.scenario.com/repo/index.json`, and install "Scenario".
   (It isn't on extensions.blender.org because it needs an external account.)
3. Preferences > Add-ons > Scenario: paste the key and secret, **Test connection**, choose an Output Folder.
4. Connect the agent: **Scenario > Agents (MCP) > Connect** (Claude Code), or
   `claude mcp add --transport http scenario-blender http://127.0.0.1:<port>/mcp`. Reload the client.
   The server runs while Blender has Allow Online Access on. Headless: `blender --background f.blend --command scenario_blender`.

**Port clash:** Blender Lab's MCP extension (the generic Blender MCP) also defaults to 9876. Then Scenario's panel
says "Port 9876 on 127.0.0.1 is in use" and HTTP calls to 9876 hang, because they reach the other server's raw
socket. Set Scenario's **MCP Port** to 9877 (Add-ons > Scenario > MCP server (agents)), press **Start MCP server**,
then **Connect > Claude Code** so the config gets the new URL.

It sits beside the generic Blender MCP (`execute_blender_code` etc.). Keep Scenario's **Allow connected agents
to run Python** off and use the generic Blender MCP for bpy work. The Scenario server has no auth: any program on
the machine can call it, including paid tools, so press **Stop MCP server** when you aren't using it.

## Free tools (no CU) worth using in every Blender beat
| Tool | Use in motion-director |
|---|---|
| `camera_path` | Build the shot camera from a description (`"slow ellipse 2, 8 s, 35mm, hold 2 s"`), a preset (orbits, ellipses, dolly/truck, crane/arc, pan, flyover) or explicit waypoints. Animates `Scenario Shot Camera`, saved in the .blend, so it's deterministic and re-renderable. Retime it to the beat table's frames afterwards. |
| `capture_views` | One labelled contact sheet of several angles or frames, rendered offscreen: the Blender equivalent of `sheet.py` for checking a placement, a model or a camera move before a real render. |
| `render_still`, `screenshot_viewport` | Quick OpenGL stills for style frames and gate reviews (GUI session only). |
| `scene_summary`, `object_detail`, `datablocks_summary`, `set_frame`, `select_objects`, `blender_api_help` | Inspect before changing anything. |
| Film export (`prepare_film_export` → `render_film_export`) | Renders a built review scene to a new MP4 inside the Output Folder without spending anything. |

## Paid lanes and where they fit
| Lane | Fit | Notes |
|---|---|---|
| **Blockout** | Stage 3 previs for a 3D beat: a description becomes a greybox layout (a `Blockout` collection, colour-coded floor/wall/prop…) to place the camera and timing against. Then swap the blocks for real assets. | Design and refinement are priced separately. Rebuild wipes manual edits inside the `Blockout` collection, so keep your objects outside it. |
| **Materials** (PATINA) | Seamless PBR sets (base colour, normal, roughness, metalness, height) from a prompt or a photo, for hero objects that need a real material (marble, brass, carbon, paper). | Applies to one chosen material slot of a UV'd mesh. **Not undoable**: save the .blend first. |
| **Environment** | 360 panorama → World, HDRI (EXR) conversion, 2× upscale. Gives glossy Cycles/EEVEE objects real reflections and light. | Check seams and light yourself; the extension doesn't measure them. |
| **3D** | Generate props, or remesh / retexture / rig / animate a selected mesh. | Compare price and quality with Magnific `models3d_generate`. |
| Render Image | Scene capture + a look → a finished still (GPT Image 2 by default). | **Off by default here: images run on Magnific GPT 2.5** (the author's standing rule). Use `render_still` → Magnific with the capture as a reference instead, unless the user overrides it for that shot. |
| Video / Render Video | Playblast → video-to-video (Seedance, Minimax, Runway Aleph …). | **Off by default here: video runs on Topview.** Use Scenario for the *guide* only: `camera_path` + a camera clip render, then the 3D-guide → real-scale recipe on Topview (`auto` mode, GPT anchor first frame, last-frame chaining). Override per shot only when the user says so. |
| Audio | Speech, music, SFX. | The SFX library + ElevenLabs direct stay the default (see sound-design.md). |
| Film tasks | JSON recipe → shots → timeline → composition → review scene → MP4 → case-study ZIP. | Experimental, one approval per step. Worth it only for a multi-shot 3D previs; the canvas engine owns the edit otherwise. |

## Camera guide → Seedance (precise direction)
Blender sets the camera and the blocking; Seedance makes it real. Validated on the tea-house demo (2026-10-20):
1. Plan the move with `camera_path` (waypoints + a placed `Shot Target`), at about 3 beats per clip and 8–12 s.
   Slower than feels natural reads as real scale.
2. Render the guide headless, **all clay** (`view_layer.material_override`), 1280×720 → `guide_clay.mp4`. Clay
   tells Seedance "layout and motion only"; CG materials in the guide leak into the result.
3. Make **Image1 from the guide's exact first frame**: Render Image of the same camera at frame 1 (12 CU). An
   outpainted or re-framed anchor makes the opening jump.
4. Topview `topview_generate_video`: `taskType omni_reference`, `model "Seedance 2.5"`, `omniReferenceTaskType auto`
   (`edit` copies the clay look), `inputImages [{fileId, name:"Image1"}]`, `inputVideos [{fileId, name:"Video1"}]`,
   uploads via `ta_upload_credential` → PUT → `ta_upload_check_file`. Prompt in the structured format: Image1 = FIRST
   FRAME + look; Video1 = "ONLY the CAMERA MOVE and where objects stand… NOT inherited"; decimal ACTION TIMING that
   mirrors the guide; POSITIVE LOCKS for the geography. About 1.8 cr/s at 720p.
5. Check with a side-by-side (guide | result) before using it; chain longer moves with the last frame as the next Image1.

## Money rules inside Scenario
- Add the Scenario CU balance to the Stage 0 cost sheet when a Blender beat is planned.
- Every paid call goes estimate → user yes → submit: `estimate_cost` / `estimate_blockout` / `estimate_workflow`
  (free, exact `cu_cost_exact`), show it, then `generate` / `approve_blockout` / `run_workflow` with
  `approved_cost` set to the unchanged string. Video gens are still asked per batch, like everywhere else.
- An empty look in Render Image/Video triggers Prompt Spark, which has its own price. Turn Spark off or write the look.
- If a submission times out or the outcome is uncertain, **never submit again**: `list_local_jobs`, then `job_status`
  or `recover_local_job`. Client timeouts don't cancel remote work.

## Gotchas
Learned on the first real run (Isfahan tea-house demo, 2026-10-20, `10_October/scenario_demo/`):
- **Blockout boxes share one primitive mesh and have no UVs.** Before applying a PATINA material: copy the mesh
  (`o.data = o.data.copy()`), add UVs (world-scale box projection, about 1.2 m per repeat), make the object active,
  then `prepare_result_application(purpose=material)`. Give other objects the same material directly; it's free.
- **`camera_path` aims via a Track-To on a `Shot Target` empty parked at the scene centre.** Waypoint rotations are
  ignored, and a path that passes the centre turns around. Move `Shot Target` onto the subject after every
  `camera_path` call (each call resets it). Description mode picks a generic preset (it chose dolly_in and ignored
  "crane up"); waypoints + a placed target give real control. Always check with `capture_views(mode=frames)`.
- **Render Image (GPT Image 2.5) returned 1672×941 (16:9) even from a 9:16 capture.** Plan 16:9 or test first.
  It keeps the layout remarkably well: object positions, the applied PATINA tile, even the samovar's table.
- `import` with `target_size_m` needs the GLB's `asset_id`; it lands bottom-centre on the 3D cursor.
- An `uncertain` job with no cloud match was never charged, but the extension blocks an identical resubmit until a
  human presses **Mark reviewed** in Jobs (deliberately native-only). Submit paid jobs one at a time.
- Headless renders: `blender -b --factory-startup file.blend -P script.py` (the extension doesn't load there, so read
  `bpy.data.collections["Blockout"]` rather than `scene.scenario_blockout`). Eevee about 0.4 s per 1080p frame on an M4 Pro.
- Costs seen: Blockout 0.5 CU, Rodin Gen-2.5 Medium 60, PATINA 17, Skybox Flux ×1 14, Render Image GPT 2.5 Flare 12.
- Captures are silent 1280×720 MP4s of the preview (or scene) range, fixed once uploaded: set the range first.
- Seedance 2.5, 2.0 Fast/Mini, Minimax H3 and Wan 3.0 can't take a first frame and a clip together; there the
  image only guides the opening look.
- Film capture files expire with the Blender session: upload or copy them first. Film video capture needs ffmpeg
  and ffprobe on PATH (`System/tools/bin` in this workspace).
- Results never land in the scene by themselves: `prepare_result_application` → user approves → `apply_result_application`.
- For the final picture, render frames from Blender as a PNG sequence into `render/` and composite them in the
  engine or ffmpeg, same as any other Blender beat.
