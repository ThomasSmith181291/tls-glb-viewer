# TLS GLB Model Viewer

A single-file, zero-install 3D viewer for `.glb` / `.gltf` models with
**snap-aware measurement** and **comments**. Reusable across BCDS, Nudura
BuildEase, Tremco Finish QS, and TLS Timber Frame.

## Use it
- **Local:** open `index.html` in any browser. Drag a `.glb` onto the page, or
  click **Open…**. The model never leaves your device.
- **Hosted / deep-link:** `index.html?model=https://host/path/model.glb` loads a
  remote GLB directly (handy for QR codes).

## Interaction (no modes to juggle)
- **Orbit + measure are unified.** **Drag** to rotate (right-drag/two-finger to
  pan, scroll/pinch to zoom); a **tap** (press with no drag) places a measure
  point. So you rotate and measure freely without switching tools.
- **Measure → conventional dimensions.** Tap two points and the viewer draws a
  proper dimension: **extension lines, a dimension line with arrowheads, and the
  value (mm + inches)**. Built as **real 3D geometry**, so it stays locked to the
  model as you orbit/zoom. Dimensions **persist** (each pair adds another).
  **Clear dimensions** removes them all.
  - **Choose the jog after picking** — after the 2nd point, pick **Vertical** or
    **Horizontal** to set which way the dimension line offsets. The value is the
    true point-to-point distance; the jog only changes presentation.
  - **Snapping:** hovering snaps to the nearest **vertex** (green) or **edge
    midpoint** (cyan) within ~16 px; else the free surface point (faint white).
    Vertices win ties.
- **⛓ Chain mode** — axis-locked running dimensions. Tap a sequence of points;
  each segment measures the distance **along the locked world axis** (cycle
  **Lock: X / Y / Z** — Y is vertical/height), drawn on a shared baseline with
  witness lines meeting it at 90°. **Finish chain** or **Esc** ends the chain;
  the axis can be re-cycled mid-chain to re-measure.
- **⚙ Sizes** — set **Text height** (default **150 mm**), **Arrowhead** (150 mm),
  and **Jog offset** (300 mm), all in model mm. Changes rebuild **all** existing
  dimensions and chains live. Dimension text is a **world-scale 3D billboard** —
  it sits at true model size (1:1) and scales with zoom like geometry, instead of
  staying a fixed pixel size.
- **Dimension types** — a **button group** (top-left of the toolbar, one icon per
  type) — click to select: **Aligned** (true point-to-point distance),
  **Linear** (horizontal/vertical projected), **Continuous** (running string),
  **Baseline** (all from one origin, stacked), **Angular** (vertex + two ends →
  degrees).
  - **Aligned / Linear:** tap two points, then pick **Vertical** or **Horizontal**.
  - **Continuous / Baseline:** tap a run of points → **individual orthogonal
    dimensions** projected to a **shared baseline** (witness lines at 90° — they
    measure the horizontal run or vertical rise, not the oblique point-to-point
    angle). Pick **Horizontal / Vertical** to set the orientation (live). Finish
    with **double-click last point**, **Finish**, or **Esc**. **Baseline** lines
    all share one offset (overlapping); their value text is **rotated 90° at the
    end** of each so the texts never collide.
- **📏 Dims** lists every dimension — click to focus, **✕** to delete one.
  **Right-click a dimension's value** in the 3D view to delete it directly.
- **Units** (in ⚙ Sizes) — switch readouts between **mm**, **"** (inches), or
  **both**; applies to all existing dimensions live.
- **📐 Views + Parallel** — one-click **Front / Rear / Left / Right / Top / Bottom
  / Iso**, framed to the model; standard views switch to **orthographic
  (parallel)** automatically (needed for true 2D views). The **◉ Perspective /
  ▱ Parallel** button toggles projection manually. **All views share standard
  Y-up**, so the orbit pivot never reorients (no need to Reset between views).
  **⟲ / ⟳ Rotate 90°** spins the current view in-plane about the vertical axis —
  handy to flip a Top/Bottom plan between portrait and landscape.
- **🎬 Scenes** — saved views (camera + projection + section). Every model starts
  with a fixed **Default** scene (the home view) — it's always the first tab and
  can't be edited or deleted; **click it to return to the original view**. **Save
  current view** adds a named scene; it becomes active and then **auto-updates as
  you change it** — no manual save. Orbiting/cutting while on Default simply
  *leaves* it (deselects the tab) without altering it. Scenes show as **tabs across
  the top** and in the 🎬 list (**Rename / ✕**). Persist per file in `localStorage`.
  (Per-scene dimension sets are a planned follow-up; dimensions are shared across
  scenes for now.)
- **✂ Section** — slice the model. Two modes:
  - **Plane** — one cutting plane: cycle the **axis**, drag **position**, **Flip**.
  - **Box** — a **clip box** (6 planes): X/Y/Z **min & max** sliders isolate a
    region. Shrink any face to crop the model to a slab or box.
  - **Show guide** hides the plane/box outline; **Cap faces** fills the cut with a
    solid surface (stencil-based — experimental, opt-in, may be slow on very heavy
    models); **Off** clears the cut. Clipping a model collapses its dialog via the
    **✂ Section** button **without turning the cut off** — only **Off** disables it.
    Clips the model **and its baked edges** (hidden edges disappear); dimensions/
    comments stay visible.
- **💬 Comment mode + 🗂 Comments** — tap (in comment mode) to drop a comment:
  a **3D anchor marker** at the point (rotates/zooms with the model, no drift)
  plus a numbered label. **Click any pin** to open a popup with the full text and
  **Reply** (as the designer), Focus, Edit, Delete. The **🗂 Comments** sidebar
  lists every comment with its **reply thread**, openable any time (not just in
  placement mode). Comments + replies **persist per file** in `localStorage`;
  **Export / Import** writes/reads a `*.comments.json` (replies included) so the
  thread travels with the model or to a teammate.

> Label anchoring uses `CSS2DObject.center` (not CSS `transform`, which the
> CSS2DRenderer overwrites each frame) — that's what keeps comment labels glued to
> their point. Dimension values are `THREE.Sprite`s sized in world units so they
> scale 1:1 with the model.

## Troubleshooting
- **Nothing happens / buttons dead:** you almost certainly opened `index.html`
  directly (`file://`). Browsers block ES-module scripts from `file://`. Serve the
  folder over http — `py -m http.server` in this folder, then open
  `http://localhost:8000/`. The viewer now shows a red banner if it detects this.
- Any load or runtime error is surfaced as an on-screen banner (and logged to the
  console) instead of failing silently.

Bounding-box dimensions (W × H × D, mm) are shown in the header on load.

## Engine
Built on **three.js 0.160** (not `<model-viewer>`) — direct mesh access is what
makes vertex/edge **snapping** and 3D-anchored comments possible. Pipeline:
`GLTFLoader` + `DRACOLoader` (so Draco-compressed GLBs load), `OrbitControls`,
`Raycaster` for picking/snapping, `CSS2DRenderer` for pins/labels,
`RoomEnvironment` for PBR lighting. All loaded from CDN via an ES-module importmap.

## Units
glTF geometry is in **metres**. Distances convert to mm (`×1000`) and inches
(`mm / 25.4`). SketchUp's glTF export writes metres — confirm any other exporter
does too, or the readout is off by the unit scale.

## Notes
- three.js + the Draco decoder load from CDN (unpkg + gstatic), so first load
  needs internet. For a fully offline factory-floor copy, vendor `three.module.js`,
  the `examples/jsm/` addons, and the Draco decoder locally and repoint the
  importmap / `setDecoderPath`.
- Snapping currently considers the hovered triangle's 3 vertices + 3 edge
  midpoints (cheap, no preprocessing). For very dense models, a BVH (three-mesh-bvh)
  would let snapping scan a wider neighbourhood without lag — see `TODO.md`.
