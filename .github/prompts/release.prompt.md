---
description: "Prepare and cut a release: analyze commits, decide bump type, confirm with user, then build → tag"
agent: agent
tools: [execute/runInTerminal, read/readFile, vscode/askQuestions]
---

Cut a release of `streamlit-bubble-chat` following the project's tag-driven release process.

## Steps

### 1. Verify the working tree is clean
Run `git status --short`. If there are uncommitted changes, ask the user to commit or stash them first (use tool `vscode/askQuestions`).

### 2. Determine the bump type from commits
Get the latest tag and the commits since then:
```bash
git describe --tags --abbrev=0
git log <latest-tag>..HEAD --oneline
```

Apply Conventional Commits rules to decide the bump type:
- **major** — any commit with `BREAKING CHANGE` in the footer, or a `!` suffix (e.g. `feat!:`, `fix!:`)
- **minor** — at least one `feat:` commit (no breaking changes)
- **patch** — only `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `chore:`, etc.

### 3. Present analysis and ask for confirmation
Create a file called `local_docs/release_analysis.md` (if it exists, overwrite it) to show the user:
- The detected bump type (patch / minor / major)
- The reasoning: list the commits that drove the decision, highlighting any `feat:` or breaking changes
- The current version and what the next version will be (get current from `pyproject.toml`)

Use tool `vscode/askQuestions` and ask two questions in the same call:
1. Whether the proposed bump type is correct (offer patch / minor / major as options)
2. Whether to proceed with the release

**Do not continue until the user confirms both questions.**
If the user selects a different bump type than detected, use their choice instead.

### 4. Run the full quality gate
```
make check
make test
```
If any step fails, stop and report the error. Do not proceed.

### 5. Build frontend + Python distributions
```
make build
```
Verify `streamlit_bubble_chat/frontend/build/` contains fresh `index-*.js` and `styles-*.css` files, and `dist/` contains `.tar.gz` and `.whl` artifacts.

### 6. Bump version, update CHANGELOG, create tag
Run the target matching the confirmed bump type:
- `patch` → `make release-patch`
- `minor` → `make release-minor`
- `major` → `make release-major`

This runs `uv run cz bump --increment <TYPE>`, which:
- Updates the version in `pyproject.toml`
- Appends a new section to [CHANGELOG.md](../../CHANGELOG.md)
- Creates a release commit (`bump: release vX.Y.Z`)
- Creates a git tag `vX.Y.Z`

Show the resulting tag name and the CHANGELOG entry added.

### 7. Remind to push
Show the user:
```bash
git push --tags
```
Pushing the tag triggers `.github/workflows/release.yml`, which publishes to PyPI and creates a GitHub Release. **Do not push automatically.**

## Notes
- See [docs/releasing.md](../../docs/releasing.md) for full release documentation and first-time PyPI setup.
- `make check` runs the full pre-commit hook suite; don't skip it.
- If the build step produces new hashed filenames, the release commit will include those — that is expected and correct.
