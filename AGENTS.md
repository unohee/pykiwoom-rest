# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/pykiwoom_rest/` (core modules: `kiwoom_rest.py`, `stock_api.py`, `chart_api.py`, `account_api.py`, `order_api.py`, `ranking_api.py`, `sector_api.py`, `async_api.py`, `concurrent_api.py`)
- Tests: `tests/` (pytest; fixtures in `tests/conftest.py`)
- Docs: `README.md`, `API_DOCUMENTATION.md`, `docs/`, `api/`
- Examples: `examples/` (performance demos); Entry script: `main.py`

## Build, Test, and Development Commands
- Environment setup
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e .[dev]` or `pip install -r requirements.txt`
- Run tests
  - `python -m pytest tests -v`
  - Coverage (optional): `pytest --cov=src/pykiwoom_rest --cov-report=term-missing`
- Lint/format/type-check
  - `black .`
  - `flake8 src tests`
  - `mypy src/pykiwoom_rest`
- Local run/demo
  - `python main.py --info` | `python main.py --test` | `python main.py --demo`

## Coding Style & Naming Conventions
- Python 3.8+; 4-space indent; prefer type hints across public APIs.
- Files/functions/variables: `snake_case`; classes: `CamelCase`; constants: `UPPER_SNAKE`.
- Keep public method names stable; extend rather than break.
- Tools: Black (format), Flake8 (lint), MyPy (types). Run before pushing.

## Testing Guidelines
- Framework: pytest. Place tests under `tests/` as `test_*.py`.
- Use fixtures from `tests/conftest.py`; mock external HTTP (`requests.Session`) and environment variables.
- Add tests for new features and regressions; no strict coverage target, but cover critical paths.

## Commit & Pull Request Guidelines
- Commits: concise and scoped. Prefer Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`). If unsure, follow this style.
- PRs: include summary, rationale, test results (`pytest` output or screenshots), and notes on breaking changes. Link related issues.
- Update docs/examples when API changes affect users.

## Security & Configuration Tips
- Use `.env` for secrets (`KIWOOM_APPKEY`, `KIWOOM_APPSECRET`, `ACCOUNT_NO`); do not commit secrets.
- Handle rate limiting respectfully; avoid real API hits in tests—use mocks.

## Agent-Specific Instructions
- Make minimal, surgical changes; preserve API compatibility.
- Touch only necessary files; follow existing patterns in `src/pykiwoom_rest/`.
- Run lint/tests locally before proposing changes. Avoid destructive ops or network installs without confirmation.
