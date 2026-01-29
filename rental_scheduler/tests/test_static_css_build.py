from pathlib import Path


def test_static_css_has_no_apply_directives():
    css_dir = Path(__file__).resolve().parents[1] / "static" / "rental_scheduler" / "css"
    assert css_dir.exists(), f"Missing static CSS directory: {css_dir}"

    css_files = sorted(css_dir.glob("*.css"))
    assert css_files, f"No CSS files found in {css_dir}"

    offenders = []
    for css_file in css_files:
        if "@apply" in css_file.read_text(encoding="utf-8"):
            offenders.append(css_file.name)

    assert not offenders, f"Found @apply in built CSS: {', '.join(offenders)}"
