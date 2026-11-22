"""Static few-shot examples: shape, coverage, structure and arithmetic (spec: estimation-examples)."""

import math
import re
import typing

import pytest

import app.context.examples as examples_module
from app.context.examples import ESTIMATION_EXAMPLES, EstimationExample

SECTIONS = ["Task Breakdown", "Totals", "Assumptions", "Out of Scope", "Risks", "Recommended Team", "Estimated Duration"]
RATE = 62.5
IDS = [f"example-{i}" for i in range(1, len(ESTIMATION_EXAMPLES) + 1)]


def money(text: str) -> float:
    return float(text.replace(",", ""))


def sections(estimation: str) -> dict[str, str]:
    return dict(zip(SECTIONS, re.split(r"^### .+$", estimation, flags=re.M)[1:]))


def task_rows(estimation: str) -> list[tuple[str, int, float]]:
    table = sections(estimation)["Task Breakdown"]
    return [(n, int(h), money(c)) for n, h, c in re.findall(r"^\| (?!Task \|)([^|]+?) \| (\d+) \| ([\d,]+) \|$", table, re.M)]


def totals(estimation: str) -> dict[str, tuple[int, float]]:
    found = re.findall(r"\*\*(Subtotal|Contingency \(15%\)|Total):\*\* (\d+) h, ([\d,]+) EUR", sections(estimation)["Totals"])
    return {k: (int(h), money(c)) for k, h, c in found}


def test_dataset_shape():
    assert len(ESTIMATION_EXAMPLES) == 7
    assert typing.get_type_hints(EstimationExample) == {"meeting_summary": str, "estimation": str}
    for example in ESTIMATION_EXAMPLES:
        assert set(example) == {"meeting_summary", "estimation"}
        assert all(isinstance(v, str) and v.strip() for v in example.values())


def test_module_is_data_only():
    own_functions = [
        name for name, value in vars(examples_module).items()
        if callable(value) and getattr(value, "__module__", "") == examples_module.__name__ and name != "EstimationExample"
    ]
    assert own_functions == []


def test_coverage_redsys_in_both_woocommerce_examples():
    shops = [e for e in ESTIMATION_EXAMPLES if "WooCommerce" in e["meeting_summary"]]
    assert len(shops) == 2
    for shop in shops:
        assert any("Redsys" in name for name, _, _ in task_rows(shop["estimation"]))


def test_corporate_site_lists_at_least_10_sections():
    corporate = next(e for e in ESTIMATION_EXAMPLES if "12 sections" in e["meeting_summary"])
    listed = corporate["meeting_summary"].split("12 sections:")[1].split(". They")[0]
    assert len(re.split(r",\s*(?:and\s+)?|\s+and\s+(?=[A-Z])", listed)) >= 10


@pytest.mark.parametrize("example", ESTIMATION_EXAMPLES, ids=IDS)
def test_english_and_structure(example):
    text = example["meeting_summary"] + example["estimation"]
    assert not re.search(r"[áéíóúñ¿¡]", text), "examples must be in English"
    assert example["estimation"].startswith("## ")
    assert re.findall(r"^### (.+)$", example["estimation"], re.M) == SECTIONS
    for name in ("Assumptions", "Out of Scope", "Risks"):
        assert len(re.findall(r"^- ", sections(example["estimation"])[name], re.M)) >= 3


@pytest.mark.parametrize("example", ESTIMATION_EXAMPLES, ids=IDS)
def test_arithmetic_is_consistent(example):
    estimation = example["estimation"]
    rows = task_rows(estimation)
    assert len(rows) >= 8
    for name, hours, cost in rows:
        assert hours % 2 == 0, f"odd hours: {name}"
        assert cost == hours * RATE, f"row cost: {name}"
    t = totals(estimation)
    (sub_h, sub_c), (cont_h, cont_c), (tot_h, tot_c) = t["Subtotal"], t["Contingency (15%)"], t["Total"]
    assert (sub_h, sub_c) == (sum(h for _, h, _ in rows), sum(c for _, _, c in rows))
    assert cont_h % 2 == 0 and abs(cont_h - 0.15 * sub_h) <= 1 and cont_c == cont_h * RATE
    assert (tot_h, tot_c) == (sub_h + cont_h, sub_c + cont_c)
    totals_text = sections(estimation)["Totals"]
    assert "62.5 EUR/h" in totals_text and "exclude VAT" in totals_text


@pytest.mark.parametrize("example", ESTIMATION_EXAMPLES, ids=IDS)
def test_duration_matches_hours_and_team(example):
    s = sections(example["estimation"])
    team_fte = sum(map(float, re.findall(r"\(([\d.]+) FTE\)", s["Recommended Team"])))
    match = re.search(r"\*\*(\d+) weeks\*\* with ([\d.]+) FTE", s["Estimated Duration"])
    assert match, "duration line not found"
    weeks, fte = int(match[1]), float(match[2])
    assert fte == team_fte
    assert weeks == math.ceil(totals(example["estimation"])["Total"][0] / (fte * 30))
