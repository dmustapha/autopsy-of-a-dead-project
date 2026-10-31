"""
Static assertion that app/static/app.js surfaces the new certificate fields.
No DOM execution — this is a source-level wiring check.
The visual/interactive check is deferred to Task 8 (Chrome run against live box).
"""
import pathlib

APP_JS = pathlib.Path(__file__).parent.parent / "app" / "static" / "app.js"


def _src() -> str:
    return APP_JS.read_text(encoding="utf-8")


def test_appjs_surfaces_summary_and_content_badge():
    src = _src()

    # (a) references project_summary
    assert "project_summary" in src, \
        "app.js must reference d.project_summary to surface the What-this-project-was block"

    # (b) contains the label text
    assert "What this project was" in src, \
        "app.js must emit the label 'What this project was' inside the render() template"

    # (c) emits a content-read badge — references narration_engine AND "evidence read by" or "read by"
    assert "narration_engine" in src, \
        "app.js must reference d.narration_engine for the content-read badge"
    assert ("evidence read by" in src or "read by" in src), \
        "app.js must emit 'evidence read by' (or 'read by') text in the content-read badge"

    # (d) null-guards project_summary with a truthy ternary
    assert "d.project_summary ?" in src, \
        "app.js must null-guard d.project_summary with a ternary (d.project_summary ? ...) for old-shape results"
