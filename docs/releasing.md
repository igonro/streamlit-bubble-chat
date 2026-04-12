# Releasing To PyPI

This repository is set up for tag-driven releases with GitHub Actions, `uv`,
and PyPI trusted publishing.

## What gets automated

- `Commitizen` bumps the version and creates a git tag.
- GitHub Actions builds the frontend and Python distributions.
- PyPI trusted publishing uploads the release without a long-lived API token.
- GitHub Actions creates a GitHub Release and attaches the built artifacts.

## First-time setup

### 1. Create the project accounts

- Create a PyPI account.
- Create or select the GitHub repository `igonro/streamlit-bubble-chat`.

### 2. Configure the GitHub environment

Create a GitHub Actions environment named `pypi`.

This is optional from PyPI's perspective, but recommended because it lets you
protect publishing with reviewers or branch restrictions later.

The Python Packaging User Guide recommends requiring manual approval on the
`pypi` environment for extra safety.

### 3. Add the trusted publisher in PyPI

In PyPI, go to `https://pypi.org/manage/account/publishing/` and configure a
pending trusted publisher for this project using:

- PyPI project name: `streamlit-bubble-chat`
- Repository owner: `igonro`
- Repository name: `streamlit-bubble-chat`
- Workflow file: `.github/workflows/release.yml`
- Environment: `pypi`

On the first successful release, PyPI will create the project automatically from
that pending publisher. No long-lived PyPI token is required.

If you want a dry run first, repeat the same setup in TestPyPI with a separate
workflow or temporary `repository-url` override.

## Local release flow

### Preview the next version

```bash
make release-dry-run
```

### Create the release commit and tag

```bash
make release-patch
# or: make release-minor
# or: make release-major
```

That command updates the version, updates the changelog, creates a release
commit, and creates a tag like `v0.2.0`.

### Push the release

```bash
git push --follow-tags
```

Pushing the tag triggers `.github/workflows/release.yml`, which publishes the
package to PyPI and creates a GitHub Release.

## Important note about pip

You do not upload a package "to pip". You publish a distribution to PyPI,
and then users install it with `pip install ...` or `uv add ...`.

## Recommended first public release checklist

- Create the initial tag: `git tag v0.1.0 && git push --tags`.
- Confirm that the trusted publisher points to `igonro/streamlit-bubble-chat`.
- Verify the README renders correctly on GitHub.
- Run `make check`.
- Run `make build`.
- Perform one test release against TestPyPI (see below).

## Testing with TestPyPI

TestPyPI is useful for verifying the full packaging pipeline before the first
real release and whenever you change something structural (build backend, asset
layout, entry points).

### One-time TestPyPI setup

1. Create an account at https://test.pypi.org.
2. Add a trusted publisher at https://test.pypi.org/manage/account/publishing/:
   - PyPI project name: `streamlit-bubble-chat`
   - Repository owner: `igonro`
   - Repository name: `streamlit-bubble-chat`
   - Workflow file: `.github/workflows/release.yml`
   - Environment: `testpypi`
3. In GitHub, create an environment called `testpypi`.

### Manual publish to TestPyPI

```bash
make build
uv publish --publish-url https://test.pypi.org/legacy/ --token <your-testpypi-token>
```

### Verify the install from TestPyPI

```bash
uv run --isolated --no-project \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  --with streamlit-bubble-chat \
  -- python -c "from streamlit_bubble_chat import bubble_chat; print('OK')"
```

The `--extra-index-url` fallback to real PyPI is needed because TestPyPI does
not host `streamlit` and other dependencies.

### When to use TestPyPI

- **First release:** Always. Verify trusted publishing, metadata rendering, and
  that the installed package imports correctly.
- **Regular releases:** Not needed. The CI pipeline builds and tests the
  artifacts before publishing.
- **Packaging changes:** Use it again if you change the build backend, asset
  layout, or anything that affects the wheel contents.
