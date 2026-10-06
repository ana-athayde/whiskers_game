# whiskers_game

Where's Whiskers? — interactive board for practicing place prepositions.

```bash
pip install -r requirements.txt
streamlit run aplicacao.py
```

- Each folder in `assets/` with a `background.png` becomes a map (tab).
  Its `furniture/` and `objects/` PNGs show up in the palette.
- Drag items from the palette onto the map (or click to add), then drag to move,
  use the square handle to resize and the round handle to rotate (Shift snaps 15°).
- Keyboard: arrows nudge, Delete removes, Ctrl+D duplicates, Esc deselects.
- Each map's arrangement is saved in the browser (localStorage).