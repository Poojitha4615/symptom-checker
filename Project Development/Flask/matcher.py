"""
Core matching logic for the Symptom Checker.
"""

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from rapidfuzz import fuzz, process

DATA_PATH = Path(__file__).parent / "data" / "dataset.csv"

SYNONYMS = {
    "tummy ache": "stomach pain",
    "tummy pain": "stomach pain",
    "belly ache": "stomach pain",
    "belly pain": "stomach pain",
    "throwing up": "vomiting",
    "throw up": "vomiting",
    "can't breathe": "difficulty breathing",
    "cant breathe": "difficulty breathing",
    "short of breath": "shortness of breath",
    "runny tummy": "diarrhea",
    "the runs": "diarrhea",
    "head hurts": "headache",
    "head is pounding": "headache",
    "feel dizzy": "dizziness",
    "feeling dizzy": "dizziness",
    "high temperature": "fever",
    "hot and cold": "chills",
    "cant sleep": "trouble sleeping",
    "can't sleep": "trouble sleeping",
    "no appetite": "loss of appetite",
    "worn out": "fatigue",
    "exhausted": "fatigue",
    "tired all the time": "fatigue",
}

URGENCY_ORDER = {"low": 0, "medium": 1, "high": 2, "emergency": 3}
URGENCY_LABEL = {
    "low": "Low — self-care is usually appropriate",
    "medium": "Medium — consider seeing a doctor soon",
    "high": "High — seek medical attention promptly",
    "emergency": "Emergency — seek immediate medical help",
}

FUZZY_THRESHOLD = 82


@dataclass
class Disease:
    name: str
    symptoms: list = field(default_factory=list)
    urgency: str = "low"
    advice: str = ""


@dataclass
class MatchResult:
    disease: Disease
    matched_symptoms: list
    score: float


def load_dataset(path: Path = DATA_PATH) -> list:
    diseases = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symptoms = [s.strip().lower() for s in row["symptoms"].split(",") if s.strip()]
            diseases.append(
                Disease(
                    name=row["disease"],
                    symptoms=symptoms,
                    urgency=row["urgency"].strip().lower(),
                    advice=row["advice"].strip(),
                )
            )
    return diseases


def build_symptom_vocabulary(diseases: list) -> list:
    vocab = set()
    for d in diseases:
        vocab.update(d.symptoms)
    return sorted(vocab)


def _apply_synonyms(text: str) -> str:
    text = text.lower()
    for lay_term, clinical_term in SYNONYMS.items():
        text = text.replace(lay_term, clinical_term)
    return text


def _split_into_phrases(text: str) -> list:
    text = re.sub(r"\b(and|also|plus)\b", ",", text, flags=re.IGNORECASE)
    parts = re.split(r"[,.;]", text)
    return [p.strip() for p in parts if p.strip()]


def extract_symptoms(user_text: str, vocabulary: list) -> list:
    normalized = _apply_synonyms(user_text)
    phrases = _split_into_phrases(normalized)

    found = set()
    for phrase in phrases:
        for symptom in vocabulary:
            if symptom in phrase:
                found.add(symptom)

        match = process.extractOne(phrase, vocabulary, scorer=fuzz.partial_ratio)
        if match and match[1] >= FUZZY_THRESHOLD:
            found.add(match[0])

    return sorted(found)


def match_diseases(user_symptoms: list, diseases: list, min_matches: int = 1) -> list:
    user_set = set(user_symptoms)
    results = []

    for disease in diseases:
        disease_set = set(disease.symptoms)
        overlap = user_set & disease_set
        if len(overlap) >= min_matches:
            score = len(overlap) / len(disease_set)
            results.append(MatchResult(disease=disease, matched_symptoms=sorted(overlap), score=score))

    results.sort(
        key=lambda r: (r.score, URGENCY_ORDER.get(r.disease.urgency, 0)),
        reverse=True,
    )
    return results


def check_symptoms(user_text: str, top_n: int = 5) -> dict:
    diseases = load_dataset()
    vocabulary = build_symptom_vocabulary(diseases)

    extracted = extract_symptoms(user_text, vocabulary)
    matches = match_diseases(extracted, diseases)[:top_n]

    highest_urgency = "low"
    if matches:
        highest_urgency = max(
            (m.disease.urgency for m in matches),
            key=lambda u: URGENCY_ORDER.get(u, 0),
        )

    return {
        "extracted_symptoms": extracted,
        "matches": matches,
        "highest_urgency": highest_urgency,
        "highest_urgency_label": URGENCY_LABEL.get(highest_urgency, highest_urgency),
    }