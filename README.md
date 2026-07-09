# Symptom Checker

A Flask web app that takes a free-text description of symptoms, matches it
against a dataset of common conditions, and returns likely conditions ranked
by symptom overlap — plus an urgency level.

**⚠️ Disclaimer:** Educational/portfolio project only, not a medical device.

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## Running tests

```bash
pytest tests/ -v
```