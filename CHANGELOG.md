# Changelog

All notable changes to this project will be documented in this file.

## [unreleased] — Claude Code 2.1.178 compatibility

### Changed

- Reviewed the plugin against the Claude Code 2.1.139–2.1.178 changelog. No
  deprecated features are used: confirmed zero references to `/simplify`
  (renamed `/code-review`) or `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE`, and no
  other removed APIs. No source changes were required.
- Hooks left on the shell `command` form deliberately. The Stop hook
  (`cd ${CLAUDE_PLUGIN_ROOT}/scripts && python3 -m amoa_stop_check.main`) relies
  on `cd` to set the working directory for `-m` package resolution; the new
  `args: string[]` exec form (2.1.139) runs without a shell, so `cd`/`&&` are
  unavailable and the conversion would not be lossless. The other three hooks
  are single shell-less commands that work correctly and are not exercised by
  the hook tests in their wired form, so converting them was skipped as an
  unverified, no-benefit change.

    ## [1.8.2] - 2026-06-15

### Features

- Adopt global janitor 3-scope memory; remove per-plugin skills (orch #14)    


