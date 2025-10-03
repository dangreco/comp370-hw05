root := `git rev-parse --show-toplevel`

[private]
_default:
    @just --list
    echo "{{root}}"

@setup:
    #!/usr/bin/env bash
    set -euo pipefail

    TMP=$(mktemp -d)

    cleanup() {
        rm -rf "$TMP"
    }

    trap cleanup EXIT SIGINT SIGTERM

@clean:
    # rm -rf "{{root}}/.in"
    rm -rf "{{root}}/.out"


@bundle:
    #!/usr/bin/env bash
    set -euo pipefail

    TMP=$(mktemp -d)

    cleanup() {
        rm -rf "$TMP"
    }

    trap cleanup EXIT SIGINT SIGTERM

    just clean
    just setup

    mkdir -p "{{root}}/.out/bundle"

    cp "{{root}}/scripts/borough_complaints.py" "{{root}}/.out/bundle/borough_complaints.py"
    cp "{{root}}/md/Task3.md" "{{root}}/.out/bundle/complaint_type_analysis.md"

    # clean up source code
    mkdir -p "$TMP/Bokeh"
    cp "{{root}}/.python-version" "$TMP/Bokeh/.python-version"
    cp "{{root}}/.gitignore" "$TMP/Bokeh/.gitignore"
    cp "{{root}}/pyproject.toml" "$TMP/Bokeh/pyproject.toml"
    cp -r "{{root}}/src" "$TMP/Bokeh/src"
    find "$TMP/Bokeh/src" -type d -name "__pycache__" -exec rm -rf {} +
    tar -czf "{{root}}/.out/bundle/Bokeh.tgz" -C "$TMP" "Bokeh"

    (cd "{{root}}/.out/bundle" && zip -r "../bundle.zip" .)
