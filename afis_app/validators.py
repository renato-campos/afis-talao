from datetime import datetime

from .constants import FIELD_LABELS


def _parse_date(value):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError


def normalize_and_validate(data, required_fields):
    normalized = dict(data)

    for key in ["data_solic", "data_bo"]:
        if normalized.get(key):
            try:
                normalized[key] = _parse_date(normalized[key]).strftime("%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(f"Campo {FIELD_LABELS[key]} inválido. Use DD/MM/YYYY.") from exc

    if normalized.get("hora_solic"):
        try:
            normalized["hora_solic"] = datetime.strptime(normalized["hora_solic"], "%H:%M").strftime("%H:%M")
        except ValueError as exc:
            raise ValueError("Campo Hora Solicitação inválido. Use HH:MM.") from exc

    missing = []
    for field in required_fields:
        if not str(normalized.get(field, "")).strip():
            missing.append(FIELD_LABELS[field])

    return normalized, missing
