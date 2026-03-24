"""
spaCy NER: extracts named entities from OCR text.
"""
import spacy
from app.core.config import settings

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(settings.SPACY_MODEL)
    return _nlp


ENTITY_LABELS = {
    "PERSON", "ORG", "GPE", "LOC", "DATE", "MONEY",
    "PRODUCT", "EVENT", "LAW", "PERCENT", "CARDINAL",
}


def extract_entities(text: str) -> list[dict]:
    nlp = _get_nlp()
    doc = nlp(text[:100_000])  # spaCy limit guard
    seen = set()
    entities = []
    for ent in doc.ents:
        if ent.label_ not in ENTITY_LABELS:
            continue
        key = (ent.text.strip(), ent.label_)
        if key in seen:
            continue
        seen.add(key)
        entities.append({
            "text": ent.text.strip(),
            "label": ent.label_,
            "description": spacy.explain(ent.label_) or ent.label_,
        })
    return entities
