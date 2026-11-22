"""Folder structure required by the course (spec: project-structure, ci-pipeline)."""

import shutil
import subprocess

import pytest

from helpers import REPO_ROOT

REQUIRED_PATHS = [
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/routers/__init__.py",
    "app/routers/estimations.py",
    "app/services/__init__.py",
    "app/services/llm_service.py",
    "app/context/__init__.py",
    "app/context/examples.py",
    ".env.example",
    ".gitignore",
    "pyproject.toml",
    "uv.lock",
    "README.md",
]

PACKAGES = ["app", "app/routers", "app/services", "app/context"]


@pytest.mark.parametrize("path", REQUIRED_PATHS)
def test_required_path_exists(path):
    assert (REPO_ROOT / path).is_file(), f"missing required file: {path}"


@pytest.mark.parametrize("package", PACKAGES)
def test_every_package_has_init(package):
    assert (REPO_ROOT / package / "__init__.py").is_file(), f"package without __init__.py: {package}"


def test_required_modules_import():
    import app.config  # noqa: F401
    import app.context.examples  # noqa: F401
    import app.main  # noqa: F401
    import app.routers.estimations  # noqa: F401
    import app.services.llm_service  # noqa: F401


def test_requires_python_311():
    assert 'requires-python = ">=3.11"' in (REPO_ROOT / "pyproject.toml").read_text()


@pytest.mark.skipif(shutil.which("git") is None or not (REPO_ROOT / ".git").exists(), reason="needs git and a git checkout")
def test_env_file_is_gitignored():
    result = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=REPO_ROOT)
    assert result.returncode == 0, ".env is not ignored by git"


def test_env_example_has_only_empty_values():
    expected = {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER", "LLM_MODEL", "APP_ENV", "LOG_LEVEL"}
    found = {}
    for line in (REPO_ROOT / ".env.example").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            found[key.strip()] = value.strip()
    assert set(found) == expected
    assert all(value == "" for value in found.values()), f"non-empty values in .env.example: {found}"


def test_extra_folders_do_not_break_structure():
    # Additions outside the course layout are allowed (e.g. transcripciones/, openspec/, tests/).
    assert (REPO_ROOT / "transcripciones").is_dir()
    for path in REQUIRED_PATHS:
        assert (REPO_ROOT / path).is_file()
