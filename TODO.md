# TLS GLB Model Viewer — TODO

## [ ] VISION: turn the viewer into a fast "3D → 2D views" platform

**Captured:** 2026-05-27. The direction: load a SketchUp model once, then rapidly
produce dimensioned 2D views (like SketchUp Scenes + LayOut, in the browser).
Technically all achievable in three.js — it's a scope jump from *viewer* to *app*.
Phased, with one gating dependency (tags must be embedded at export time).

- **[done] Parallel/orthographic projection** — required for true 2D views.
  Standard Views now switch to ortho; Perspective/Parallel toggle added.
- **[ ] Section planes** — three.js clipping planes (`renderer.localClippingEnabled`,
  `material.clippingPlanes`) with a draggable plane gizmo. **Capping** the cut
  (solid fill at the slice) needs the stencil-cap technique — the fiddly part.
- **[ ] Scenes** — named saved states: camera + projection + section plane(s) +
  layer/visibility state + which dimensions belong to the scene. Switch between
  them. This is "SketchUp Scenes" in the browser.
- **[ ] Per-scene model overrides** — each scene stores its own visibility set
  (and later colour/ghosting). Needs addressable parts → depends on tags below.
- **[ ] Layers / Tags from SketchUp — THE GATING DEPENDENCY.** glTF does NOT carry
  SketchUp tags natively. Fix on the EXPORT side: have `export_glbs.rb` write each
  entity's tag/layer (and name) into the glTF node `extras` (three.js surfaces
  these as `object.userData`). Then the viewer builds a Layers panel, toggles
  visibility per tag, and Scenes store per-tag state. Without this, we only have
  anonymous merged meshes. Ties into the converter task below.
- **[ ] Dimensions per scene** — tag each dimension def with a scene id; show/hide
  with the active scene (defs are already standalone 3D objects).
- **[ ] 2D output** — export the active ortho view + annotations. Easy: PNG of the
  canvas. Harder/better: project to **vector SVG/PDF** for crisp LayOut-style sheets.

**Honest scope:** this is a real application (weeks, not an afternoon), best run as
a proper GSD project/milestone. The tag pipeline is the lynchpin and is shared with
the converter work below.

## [ ] Built-in GLB converter: auto edge-bake + Draco on load

**Captured:** 2026-05-27

### Goal
Drag in a *raw* SketchUp-exported GLB → the viewer auto-runs our
presentation/lightweighting pipeline → presentable, lightweight model opens.
Today that pipeline is manual (run scripts, then view). Bring it inline so the
viewer does it on load.

### The pipeline to replicate (proven on BCDS Update Web models)
Reference scripts live next to the GLBs at
`C:\Users\Little Nineveh\BCDS Update Web\webapp\static\assets\3d\`:

1. **`export_glbs.rb`** — SketchUp Ruby Console. Classifies wall sub-groups
   (`W*`/`CR*` by name); for the *unpopulated* pass erases blocks+webs+other
   groups, for the *populated* pass erases envelope faces+edges; exports each via
   `model.export()`, then reverses each pass with `abort_operation`. Output → `raw/`.
   *(This is the SketchUp-side export; the viewer converter starts from its output.)*
2. **`bake_edges.py`** — Python + `pygltflib`. Adds `LINES` primitives per mesh
   (boundary + crease edges at a **30° threshold**), with **separate POSITION
   accessors** so Draco compresses them cleanly.
3. **Draco compression** — `npx -y gltf-pipeline -i raw/foo.glb -o foo.glb -d`
   (run from that folder). This is what shrinks **~32 MB → ~5.6 MB** on the
   populated model.
4. **Camera orbit** — NOT baked into the GLB. Set on the `<model-viewer>` element:
   `camera-orbit="119.13deg 70.37deg 53.929m"`,
   `camera-target="-0.288m 3.174m -1.031m"`, FOV 30°.

### Open design questions
- **Where does conversion run?** `pygltflib` (Python) and `gltf-pipeline` (Node)
  are not browser-native. Options:
  - (a) A small **local helper** (Python/Node) the viewer shells out to — only
    works for the desktop/local use case, not the hosted GH-Pages/QR case.
  - (b) Port edge-baking to **JS in-browser** (compute boundary + 30° crease
    edges, add LINES) and Draco-compress client-side via a WASM encoder
    (`draco_encoder`); fully client-side, works hosted too.
  - (c) Keep conversion **offline** (a `convert.py`/`convert.ps1` wrapper next to
    the viewer) and have the viewer just open the already-converted result —
    least work, but not "auto on load."
- Edge-baking is the presentation win (crease lines); Draco is the size win.
  Could ship them independently.
- Decide whether the converter targets the SketchUp `raw/` output specifically
  or any arbitrary dropped GLB.

### Notes
- Memory `reference_bcds_update_web_pa_deployment.md` lists the three script
  paths but not the end-to-end recipe — this file is the recipe of record.
- The scripts themselves remain the durable source for the exact logic.
