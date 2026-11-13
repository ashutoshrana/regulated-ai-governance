"""Keep the installation quick start executable through the public API."""

from pathlib import Path


def test_readme_quickstart():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
    section = readme.split("## Quick start: an installed core guard", 1)[1]
    code = section.split("```python\n", 1)[1].split("```", 1)[0]
    exec(compile(code, "README.md", "exec"), {})


def test_api_reference_llamaindex_example_executes():
    reference = (Path(__file__).resolve().parents[1] / "docs" / "api-reference.md").read_text()
    section = reference.split("### LlamaIndex", 1)[1]
    code = section.split("```python\n", 1)[1].split("```", 1)[0]
    exec(compile(code, "docs/api-reference.md", "exec"), {})
