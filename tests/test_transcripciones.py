"""Sample request bodies in transcripciones/ (spec: service-verification)."""

import json

import pytest
from pydantic import ValidationError

from app.routers.estimations import EstimationRequest
from helpers import REPO_ROOT

FILES = sorted((REPO_ROOT / "transcripciones").glob("*.json"))
EXPECTED = {"curso-landing.json", "tienda-vinos.json", "no-es-proyecto.json", "vacia.json", "inyeccion.json"}


def test_expected_files_present():
    assert {f.name for f in FILES} == EXPECTED


@pytest.mark.parametrize("path", FILES, ids=[f.name for f in FILES])
def test_file_is_a_valid_request_body(path):
    body = json.loads(path.read_text(encoding="utf-8"))
    assert set(body) == {"transcription"} and isinstance(body["transcription"], str)


@pytest.mark.parametrize("path", [f for f in FILES if f.name != "vacia.json"], ids=lambda p: p.name)
def test_non_empty_files_accepted_by_schema(path):
    EstimationRequest.model_validate_json(path.read_text(encoding="utf-8"))


def test_empty_file_rejected_by_schema():
    with pytest.raises(ValidationError):
        EstimationRequest.model_validate_json((REPO_ROOT / "transcripciones" / "vacia.json").read_text(encoding="utf-8"))
