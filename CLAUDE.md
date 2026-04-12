# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

"Nino's Tools" — a Blender addon (Python) providing modeling utilities: subdivision surface management, wireframe display, shrinkwrap refresh, image reload, smart delete, and texture group stamping. Lives in the N-panel under "Nino's Tools".

## Commands

- **Package for install:** `just package` — zips all `.py` files into `nino-tools.zip`
- **Lint:** `uv run ruff check .`
- **Format:** `uv run ruff format .`
- **Type check:** `uv run pyright`

There are no automated tests. The addon is tested manually inside Blender.

## Architecture

This is a standard Blender addon using the `bpy` API. All source files are in the repo root (no `src/` directory).

- `__init__.py` — Addon entry point. Registers all classes from submodules, sets up keyboard shortcuts (Cmd+1/2/3, Cmd+Shift+D, Backspace). Handles Blender's module reload protocol.
- `display.py` — `NinoToolsSettings` PropertyGroup (scene-level settings for all tools) and the wireframe auto-display depsgraph handler. Also owns `register()`/`unregister()` for the scene property and handler.
- `subd.py` — Subdivision surface operators (increase/decrease/set level, toggle visibility, toggle optimal display, cycle preview, subdivide selection via geometry nodes).
- `operators.py` — Standalone operators: shrinkwrap refresh, image reload, smart delete.
- `stamping.py` — Stamps `texture_group` custom properties on objects based on a hardcoded collection-name-to-group mapping.
- `ui.py` — All N-panel UI classes. Each feature section is a sub-panel under the main `NINO_PT_tools_panel`.

### Conventions

- Each module exports a `classes` tuple used by `__init__.py` for registration.
- Operator `bl_idname` uses the `nino.` prefix (e.g., `nino.decrease_subsurf_level`).
- Panel `bl_idname` uses the `NINO_PT_` prefix; operators use `NINO_OT_`.
- `OperatorReturnItems` is a Literal type alias defined in modules that have operators.
- `scripts.py` and `hello.py` are standalone utility scripts, not part of the addon.

### Blender API notes

- Type stubs come from `fake-bpy-module-latest` (dev dependency). Pyright uses these for type checking.
- The addon targets Blender 3.0+ (`bl_info`) / 4.2+ (`blender_manifest.toml`).
