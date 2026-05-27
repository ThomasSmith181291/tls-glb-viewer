# Deploying the TLS GLB Model Viewer to GitHub Pages

Static site — no build step. These files are all that's served:

- `index.html` — the viewer
- `sheet_a3.svg` — the A3 sheet template
- `sample.glb` — the model that auto-loads
- `sample.annot.json` *(optional)* — dimensions/comments/scenes/sheets that load automatically
- `.nojekyll` — tells GitHub Pages not to run Jekyll

## One-time setup

```bash
# from this folder, with a GitHub repo already created (e.g. "tls-glb-viewer")
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save**.

Live at: `https://<you>.github.io/<repo>/` (first deploy can take a minute or two).

## Sharing your dimensions with the link

In the viewer, click **💾 Save annotations**, then drop the downloaded `sample.annot.json`
into this folder next to `sample.glb`, commit, and push. Anyone opening the link sees the
dimensions on their correct scenes/sheets automatically.

## Updating later

```bash
git add -A
git commit -m "Update viewer"
git push
```

## Notes

- three.js + the Draco decoder load from CDN, so viewers need internet on first load.
- Each visitor's edits save to *their* browser only. To exchange work, use
  **💾 Save annotations** / **📂 Load annotations**.
- To share a different model: host its `.glb` and open
  `…github.io/<repo>/?model=https://host/path/model.glb`.
