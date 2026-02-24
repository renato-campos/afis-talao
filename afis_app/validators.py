from datetime import datetime
import re

from .constants import FIELD_LABELS

BOLETIM_PATTERN = re.compile(r"^([A-Z]{2})(\d{4})(?:-([1-9]\d?))?$")
BOLETIM_EXCEPTIONS = {"NÃO INFORMADO", "NAO INFORMADO"}


def _parse_date(value):
    """Converte string de data aceitando DD/MM/AAAA ou AAAA-MM-DD."""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError


def _normalize_and_validate_boletim(value):
    """Valida codificacao do boletim: AA0001..ZZ9999 com sufixo opcional -1..-99."""
    boletim = str(value or "").strip().upper()
    if boletim in BOLETIM_EXCEPTIONS:
        return "NÃO INFORMADO"
    match = BOLETIM_PATTERN.fullmatch(boletim)
    if not match:
        raise ValueError(
            "Campo Boletim inválido. Use o formato AA0001 até ZZ9999, com sufixo opcional -1 até -99."
        )
    numeracao = int(match.group(2))
    if numeracao < 1:
        raise ValueError(
            "Campo Boletim inválido. Use o formato AA0001 até ZZ9999, com sufixo opcional -1 até -99."
        )
    return boletim


def normalize_and_validate(data, required_fields):
    """Normaliza campos de data/hora e retorna lista de obrigatorios faltantes."""
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

    boletim = normalized.get("boletim")
    if boletim is not None and str(boletim).strip():
        normalized["boletim"] = _normalize_and_validate_boletim(boletim)

    missing = []
    for field in required_fields:
        if not str(normalized.get(field, "")).strip():
            missing.append(FIELD_LABELS[field])

    return normalized, missing
