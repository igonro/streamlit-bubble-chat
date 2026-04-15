# Changelog

All notable changes to this project will be documented in this file.

The changelog is maintained with Commitizen and Conventional Commits.

## v0.1.4 (2026-04-15)

### Feat

- implement best practices across the Python API, frontend, examples, and tests, including stricter validation, modularized frontend code, ARIA and keyboard support, safer example state patterns, and expanded unit/E2E coverage

### Fix

- sync the frontend package version and add `package.json` to Commitizen `version_files` so future version bumps stay aligned

### Docs

- add API reference, architecture, and customization guides, and expand the README and CONTRIBUTING docs with limitations, color validation, and frontend/testing workflow details
- use absolute GitHub URLs in the README so images and links render correctly on PyPI
- update the release process instructions to push tags with `git push --tags`

## v0.1.3 (2026-04-14)

### Fix

- **examples**: reset filters with a flag-and-rerun flow so all sidebar widgets return to their defaults without widget-state errors
- keep the bubble button and chat window alive during rapid Streamlit reruns by moving persistent UI and CSS to `document.body`, syncing state from the DOM, and covering the regression with a stress test

## v0.1.2 (2026-04-14)

### Feat

- **examples**: add session-start system messages to the chat examples
- **examples**: add a pizza sales dashboard agent example with LangChain/OpenAI integration, sample data, and an examples dependency group

### Fix

- **ci**: update the E2E suite to run across the Python version matrix
- restore the chat window transition and backdrop fade animations
- move the chat window and backdrop to `document.body` to prevent sidebar flicker
- raise the `stbc-root` z-index above the Streamlit sidebar so the maximized chat overlays correctly
- **examples**: make the dashboard chat non-blocking, disable filters while waiting, and surface unread replies when responses arrive with the chat closed

## v0.1.1 (2026-04-12)

### Fixed

- defer component registration until first use, improve installed-package manifest discovery, and support installed builds more reliably
- bump the minimum Streamlit dependency to 1.53 to require `isolate_styles` support

## v0.1.0 (2026-04-10)

### Added

- initial public release of the Streamlit Bubble Chat component.
