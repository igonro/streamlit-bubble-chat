# Changelog

All notable changes to this project will be documented in this file.

The changelog is maintained with Commitizen and Conventional Commits.

## v0.1.3 (2026-04-14)

### Fix

- **examples**: Reset Filters now correctly resets all sidebar widgets
- bubble button and chat window survive rapid Streamlit reruns

## v0.1.2 (2026-04-14)

### Feat

- **examples**: add session-start system messages to chat
- **examples**: add pizza sales dashboard agent example

### Fix

- **ci**: update E2E tests to include Python version matrix
- restore window transition and backdrop fade animations
- move chat window and backdrop to document.body to prevent sidebar flicker
- raise stbc-root z-index above Streamlit sidebar
- **examples**: non-blocking chat, disable filters while waiting

## v0.1.1 - 2026-04-12

### Fixed

- Lazy component registration to support installed-package manifests.
- Bumped minimum Streamlit dependency to 1.53 (`isolate_styles` support).

## v0.1.0 - 2026-04-10

### Added

- Initial alpha release of the Streamlit Bubble Chat component.
