## Dev Tips
- Use uv to do any Python related tasks - for example `uv run`
- Use uv add/remove Python packages instead of editing pyproject.toml directly
- The `quack` CLI version is installed using uv tool. To test the changes always reinstall it by,
  - uv tool uninstall quack
  - uv cache clean quack
  - uv tool install .

## Code Quality
- Static analysers available in the shell:
  - ty
  - shellcheck
- Linters and formatters available in the shell
  - ruff

<!-- OPENWIKI:START -->

## OpenWiki

This repository has a generated `openwiki/` evidence index. It is optional just-in-time context, not required startup reading.

- Treat source code and tests as authoritative. A brief's unknowns and review items are verification gaps, not automatic requirements.
- Prefer the narrowest quiet validation that proves the changed behavior. Preserve complete failure output.

The scheduled OpenWiki GitHub Actions workflow refreshes the repository wiki. Do not hand-edit generated OpenWiki pages unless explicitly asked; prefer updating source code/docs and letting OpenWiki regenerate.

<!-- OPENWIKI:END -->
