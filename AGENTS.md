## Dev Tips
- Use uv to do any Python related tasks - for example `uv run`
- Use uv add/remove Python packages instead of editing pyproject.toml directly
- The `quack` CLI version is installed using uv tool. To test the changes always reinstall it by,
  - uv tool uninstall quack
  - uv cache clean quack
  - uv tool install .

## Code Quality
- Static analysers available in the shell:
  - pyright
  - shellcheck
- Linters and formatters available in the shell
  - ruff
