# Use and verify FIVE 00s

## Setup and mission commands

Install Git and uv. The commands below use Python 3.14 with the committed lock.
The frozen `bond-api` protocol installs from the copy under `vendor/bond-api/`.

```bash
uv sync --locked --python 3.14 --extra dev
uv run --no-sync --python 3.14 python scripts/mission.py execute
uv run --no-sync --python 3.14 python scripts/z_generate_manuscript_variables.py
```

Use `brief`, `recon`, `plan`, or `debrief` in place of `execute` to inspect a
different mission phase. The `figures` subcommand generates the six concept
plots. The standalone manuscript generator reads the committed [mission and
experiment config](manuscript/config.yaml) and writes the variable map under
`output/data/`, images and their registry under `output/figures/`, and
resolved numbered sections under `output/manuscript/`.

## Native verification

```bash
uv run --no-sync --python 3.14 pytest tests/ --cov=src --cov-fail-under=90
uv run --no-sync --python 3.14 ruff check src/ scripts/ tests/
uv run --no-sync --python 3.14 ruff format --check src/ scripts/ tests/
uv run --no-sync --python 3.14 mypy src/ scripts/
uv run --no-sync --python 3.14 python scripts/vendor.py --check
```

The tests exercise the frozen protocol, generated variables, bibliography, and
byte-for-byte artifact regeneration. See the [testing guide](testing_philosophy.md).
Ruff reports existing repository-wide lint and formatting findings. Compare
its results against the base revision when changing code.

## Render the manuscript

Install Pandoc, a compatible pandoc-crossref filter, and XeLaTeX with Beamer.
Use Pandoc 3.14 and pandoc-crossref 0.3.26b (built against Pandoc 3.14)
for the Beamer filter's table-caption support. See the pinned [format guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/usage/output-formats.md)
for system requirements.

Start from a clean checkout of this repository. Put a detached copy inside the
pinned template checkout so its hydration subprocess can read the project.

```bash
project_root="$(pwd -P)"
verification_dir="$(mktemp -d)"
renderer="$verification_dir/template"
git clone https://github.com/docxology/template.git "$renderer"
git -C "$renderer" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$renderer/projects/working"
project_copy="$renderer/projects/working/bond-casino_royale_1967"
git clone --no-hardlinks "$project_root" "$project_copy"
git -C "$project_copy" checkout --detach "$(git -C "$project_root" rev-parse HEAD)"

cd "$project_copy"
uv sync --locked --python 3.14 --extra dev
cd "$renderer"
uv sync --locked --no-dev
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/bond-casino_royale_1967
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/bond-casino_royale_1967
```

Stage 03 runs the package's deterministic hydration step and renders PDF,
HTML, and Beamer slides. Open `output/pdf/bond-casino_royale_1967_combined.pdf`,
`output/web/index.html`, and the per-section PDFs under `output/slides/` in
`"$project_copy"`. Check the sections against the [manuscript index](manuscript/README.md)
and inspect the cited sources and the six figures in Results. Stage 04 writes
`output/reports/validation_report.json` and `output/reports/rendered_provenance.json`.
