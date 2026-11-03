# scripts/ — thin CLI wrappers

`mission.py` and `z_generate_manuscript_variables.py`.

## Rules

- **Thin orchestrators.** Each script does a `sys.path` bootstrap (with `# noqa: E402` on the lines
  after it) and forwards `argv`; the work happens in `src/casino_royale_1967/`.
- **`z_generate_manuscript_variables.py` is the manuscript generator** and it is last by name on
  purpose. It writes tokens, prose and figures, and it exits 1 on an unresolved `{{TOKEN}}` or a
  malformed single-brace `{TOKEN}` — do not weaken that exit.
- **Exit 0 iff the phase succeeded.** A wrapper that swallows a failure makes a broken run look
  finished.
- **Never hand-author a manuscript number.** Values arrive through `manuscript/config.yaml` and
  `src/casino_royale_1967/manuscript_variables.py`; a figure or token typed into prose defeats the
  determinism the suite is built around.
- **No sibling writes.** Scope is this package directory: do not touch `../bond-api`, the bond root or
  the template repository from a script here.
