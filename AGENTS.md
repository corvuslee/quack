## Dev Tips
- This project uses Python managed by uv
- To install or uninstall files, use the CLI instead of updating the pyproject.toml file
- The CLI version is installed using uv tool. To test the changes always reinstall it by,
  - uv tool uninstall <package name>
  - uv cache clean <package name>
  - uv tool install .