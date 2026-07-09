import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from matcher import (
    build_symptom_vocabulary,
    check_symptoms,
    extract_symptoms,
    load_dataset,
    match_diseases,
)


def test_load_dataset_returns_diseases():
    diseases = load_dataset()
    assert len(diseases) > 0
    assert all(d.symptoms for d in diseases)


def test_vocabulary_is_deduplicated_and_sorted():
    diseases = load_dataset()
    vocab = build_symptom_vocabulary(diseases)
    assert vocab == sorted(set(vocab))


def test_extract_symptoms_direct_match():
    diseases = load_dataset()
    vocab = build_symptom_vocabulary(diseases)
    found = extract_symptoms("I have a fever and a cough", vocab)
    assert "fever" in found
    assert "cough" in found


def test_extract_symptoms_synonym_match():
    diseases = load_dataset()
    vocab = build_symptom_vocabulary(diseases)
    found = extract_symptoms("bad tummy ache and throwing up", vocab)
    assert "stomach pain" in found
    assert "vomiting" in found


def test_match_diseases_ranks_by_overlap():
    diseases = load_dataset()
    results = match_diseases(["fever", "cough", "chills", "muscle aches"], diseases)
    assert len(results) > 0
    names = [r.disease.name for r in results]
    assert "Influenza" in names


def test_emergency_symptoms_flagged_correctly():
    result = check_symptoms("crushing chest pain radiating to my arm and cold sweat")
    assert result["highest_urgency"] == "emergency"


def test_check_symptoms_handles_gibberish_gracefully():
    result = check_symptoms("asdkfjaslkdfj qqqqq")
    assert isinstance(result["matches"], list)