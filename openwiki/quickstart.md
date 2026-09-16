---
type: contributor quickstart
title: Quack Contributor Quickstart
description: A task-routing guide for safely changing Quack, from the Python 3.14 uv environment and public entry points to the workflow, contract, and verification pages that own each behavior.
tags: [contributing, quickstart, python, uv, testing, cli]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-16T14:26:49.981Z
sources:
  - id: openwiki-source-164e2da859b5277df81c7d94
    resource: repo://.github/workflows/ci.yml
  - id: openwiki-source-868b3402493aef58bb5db066
    resource: repo://.python-version
  - id: openwiki-source-8037e2358a2c4f9b2c722a11
    resource: repo://AGENTS.md
  - id: openwiki-source-05ccef8d4cf1698187f20464
    resource: repo://pyproject.toml
  - id: openwiki-source-61cb6484d86bb55677fb41b3
    resource: repo://quack/__init__.py
  - id: openwiki-source-15d347a6923a51f4b11e53e9
    resource: repo://quack/cli.py
  - id: openwiki-source-cb85e5d06b7e9f7f3a361526
    resource: repo://quack/core.py
  - id: openwiki-source-fc579c74fa4d4f7c4e7e1499
    resource: repo://quack/render.py
  - id: openwiki-source-9ec6473d05fcc2cd40915af2
    resource: repo://tests/test_cli.py
  - id: openwiki-source-63fdccb791696f475b33ce12
    resource: repo://tests/test_core.py
  - id: openwiki-source-6593c2766354dfa456f9117d
    resource: repo://tests/test_integration.py
  - id: openwiki-source-a2321074ad4c3a6b4fbcec2d
    resource: repo://tests/test_render.py
  - id: openwiki-source-bd37af7b4378e3d57fbec461
    resource: repo://tests/test_utils.py
generated: { by: "openwiki/0.5.2", at: "2026-09-16T14:26:49.981Z" }
---

## Start here

Quack is a Python package and a `quack` command for DuckDuckGo search and page-to-Markdown retrieval. Make changes from a Python **3.14** environment and use `uv` for environment management and every Python command. The repository pins the interpreter in `.python-version`; CI reads that file, performs a locked sync with all extras and development dependencies, then runs Ruff, pytest, and a build.

For a CI-equivalent contributor environment, run:

```bash
uv sync --locked --all-extras --dev
```

This deliberately includes the optional `render` capability, whose SeleniumBase dependency and browser prerequisites are heavier than the core search/fetch runtime. Use it when validating the full suite or a render change. For ordinary focused work, use `uv run ...` so commands run in the uv-managed environment. Do not edit dependency declarations by hand: use `uv add` or `uv remove`, and update the lock state as part of a dependency change.

## Choose the entry point before changing code

There are two public ways into the runtime:

- **Python caller:** `from quack import search, fetch`; `render` is conditionally exported when the render module imports. Library functions return data or raise validation/typed library exceptions.
- **Command user:** the packaged `quack = "quack.cli:main"` script parses arguments, calls the library functions, formats output or writes files, and turns failures into stderr diagnostics with exit status 1.

Start at [Runtime Domains and Public Surface](architecture/public-surface.md) when a change affects imports, `__all__`, package metadata, the console entry point, or optional-render behavior. That page establishes the boundary that the lightweight core must not acquire a mandatory SeleniumBase/browser dependency.

## Route the task to its owning behavior

| If you are changing… | Read first | Preserve or verify |
| --- | --- | --- |
| DuckDuckGo request parameters, challenge classification, parsing selectors, redirect cleanup, result shape, result ordering, or retry handling | [DuckDuckGo Search Pipeline](workflows/search-pipeline.md) | `search()` uses the impersonated HTML endpoint and returns non-empty normalized `title`/`href`/`body` records or a typed search failure. The live provider markup is an integration boundary. |
| HTTP page retrieval, Markdown conversion, JavaScript-rendered content, URL-scheme support, browser session setup, or retrieval output files | [Fetch and JavaScript Render Workflows](workflows/content-retrieval.md) | `fetch()` and optional `render()` acquire documents differently but converge on the shared HTML-to-Markdown helper. Keep the optional browser runtime isolated from normal fetch/search. |
| Validation, exception classes, retry eligibility, CLI stdout/stderr text, JSON, process status, or the difference between core normalization and `filter_results()` | [Input, Failure, and Output Contracts](concepts/failure-and-output-contracts.md) | Do not move CLI presentation into library code or silently change library exceptions into process exits. Only connection and timeout errors retry; challenges and semantic no-results do not. |
| Package exports, the `quack` command, CLI argument forwarding, new options, or render availability | [Runtime Domains and Public Surface](architecture/public-surface.md) | The package and CLI have separate guarded render imports. Preserve their independent behavior and the command adapter's ownership of formatting and output files. |
| Tests, a dependency/lockfile update, optional rendering, CI failures, release artifacts, or delivery validation | [Verification, Optional Dependencies, and Release Checks](testing/verification-and-delivery.md) | Match the focused test to the seam, then use the CI sequence before delivery. The suite includes both a live search integration test and a browser-backed render test. |

The linked pages are the detailed contracts. This page intentionally does not repeat their API reference or implementation walkthroughs.

## Work safely at the narrowest seam

1. **Classify the change.** Determine whether it belongs to search, static retrieval, optional rendering, public surface/CLI, or a pure helper. Follow the corresponding row above before editing.
2. **Keep the layers distinct.** `quack/__init__.py` is the package façade; `quack.cli` is the process-facing adapter; `quack.core` owns the search/fetch transport and conversion seam; `quack.render` owns browser execution. A change at one layer can affect another, but should not bypass its owner.
3. **Respect optional rendering.** The `render` extra supplies `seleniumbase`; the core install contains only `html2text`, `primp`, and `selectolax`. Do not introduce an unconditional browser import into a core path. To exercise rendering locally, install/sync the extra and account for browser/driver availability.
4. **Test the contract you changed.** Use mocks for deterministic core and CLI behavior; use the live DuckDuckGo and real-browser tests only for their integration signals. A passing CLI test does not replace a core retry/parser test, and a live test does not replace a focused unit test.
5. **Deliver through the project gates.** Run the focused test first, then the full test, lint, formatting check, and build. CI runs the same ordered quality path for pushes and pull requests targeting `main`.

## Focused validation commands

Use the smallest command that covers the modified boundary:

```bash
# Search/fetch transport, parsing, conversion, retries, and typed errors
uv run pytest tests/test_core.py

# Pure query and result utilities
uv run pytest tests/test_utils.py

# Argument parsing, formatting, output files, stderr, and exit behavior
uv run pytest tests/test_cli.py

# Optional browser-backed rendering path
uv sync --extra render --dev
uv run pytest tests/test_render.py

# Live DuckDuckGo compatibility signal
uv run pytest tests/test_integration.py
```

Before delivery, reproduce the repository's checks:

```bash
uv sync --locked --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

The complete `pytest` run is not fully hermetic: it includes a real DuckDuckGo search, and the rendering test uses SeleniumBase to render a local JavaScript fixture when its dependency is present. Diagnose those operational prerequisites separately from deterministic unit failures. `uv build` comes after the quality gates in CI and produces the distributable artifacts; it is not a publication command.

## Installing and checking the command boundary

The public installation examples use uv tools:

```bash
uv tool install git+https://github.com/corvuslee/quack.git
uv tool install "git+https://github.com/corvuslee/quack.git[render]"
```

After changing behavior intended for an installed `quack` command, test the installation boundary rather than relying only on `uv run`. Reinstall the tool so it points to the current checkout:

```bash
uv tool uninstall quack
uv cache clean quack
uv tool install .
```

Then smoke-test the relevant command shape, keeping network calls and browser availability in mind:

```bash
quack search "python programming" --json
quack fetch "https://www.python.org"
quack render "https://www.python.org"
```

For command-specific result format, output-file behavior, and failure presentation, return to [Input, Failure, and Output Contracts](concepts/failure-and-output-contracts.md). For the request paths behind those commands, use [DuckDuckGo Search Pipeline](workflows/search-pipeline.md) or [Fetch and JavaScript Render Workflows](workflows/content-retrieval.md).
