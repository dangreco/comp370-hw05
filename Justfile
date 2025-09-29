project := "hw05"

[private]
_default:
    @just --list

[group("Python")]
run:
    @uv run "{{project}}"

[group("Python")]
sync:
    @uv sync
