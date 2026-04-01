# python_in_the_browser

Demos for my Python-in-the-browser Meetup talk.

## PyScript Weather Demo

This repo now includes a small browser-only Python app in
`pyscript_panel_plotly_demo/`.

It demonstrates:

- modern `PyScript` and `Pyodide`
- `Panel` widgets and layout
- `Panel`'s Plotly pane
- browser-side CSV fetching with `pyscript.fetch`
- reactive filtering without a backend

Run it locally with:

```bash
uv run serve_demo.py --directory pyscript_panel_plotly_demo
```

Then open `http://127.0.0.1:8000/`.
