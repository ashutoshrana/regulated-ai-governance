"""Keep the installation quick start executable through the public API."""

from pathlib import Path


def test_readme_quickstart():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
    section = readme.split("## Quick start: an installed core guard", 1)[1]
    code = section.split("```python\n", 1)[1].split("```", 1)[0]
    exec(compile(code, "README.md", "exec"), {})
