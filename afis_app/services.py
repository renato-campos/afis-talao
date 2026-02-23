from __future__ import annotations

from datetime import datetime
from typing import Any

from .constants import CANCEL_REQUIRED, CREATE_REQUIRED, EDITABLE_FIELDS, FINALIZE_REQUIRED, STATUS_CANCELADO, STATUS_FINALIZADO, STATUS_MONITORADO
from .validators import normalize_and_validate


class TalaoService:
    def _required_fields_for_status(self, status: str) -> list[str]:
        normalized_status = str(status or "").strip().upper()
        if normalized_status == STATUS_FINALIZADO:
            return FINALIZE_REQUIRED
        if normalized_status == STATUS_CANCELADO:
            return CANCEL_REQUIRED
        return CREATE_REQUIRED

    def prepare_new_talao(self, form_data: dict[str, Any], now: datetime | None = None) -> tuple[dict[str, Any], list[str], datetime]:
        current = now or datetime.now()
        data = dict(form_data)
        data["data_solic"] = current.strftime("%d/%m/%Y")
        data["hora_solic"] = current.strftime("%H:%M")
        data["status"] = STATUS_MONITORADO
        normalized, missing = normalize_and_validate(data, CREATE_REQUIRED)
        return normalized, missing, current

    def prepare_update_talao(self, form_data: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        data = dict(form_data)
        required = self._required_fields_for_status(str(data.get("status") or ""))
        return normalize_and_validate(data, required)

    def prepare_finalize_from_record(self, record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        data = {key: "" for key in EDITABLE_FIELDS}
        for key in EDITABLE_FIELDS:
            value = record.get(key)
            if value is None:
                data[key] = ""
            elif key == "data_bo":
                data[key] = value.strftime("%d/%m/%Y")
            else:
                data[key] = str(value)

        data_solic = record.get("data_solic")
        hora_solic = record.get("hora_solic")
        data["data_solic"] = data_solic.strftime("%d/%m/%Y") if data_solic else ""
        data["hora_solic"] = str(hora_solic)[:5] if hora_solic else ""
        data["status"] = STATUS_FINALIZADO
        return normalize_and_validate(data, FINALIZE_REQUIRED)


class AlertaService:
    def is_edit_blocked_status(self, status: str) -> bool:
        normalized_status = str(status or "").strip().upper()
        return normalized_status in (STATUS_FINALIZADO, STATUS_CANCELADO)

    def is_monitorado(self, status: str) -> bool:
        return str(status or "").strip().upper() == STATUS_MONITORADO

    def build_monitoring_question(self, ano: Any, talao: Any, boletim: Any) -> str:
        return (
            f"Talão {self._format_talao(ano, talao)} (Boletim: {boletim or 'sem boletim'}) segue monitorado.\n\n"
            "As ações necessárias para encerrar o monitoramento já foram cumpridas?"
        )

    def _format_talao(self, ano: Any, numero: Any) -> str:
        try:
            return f"{int(numero):04d}/{int(ano)}"
        except (TypeError, ValueError):
            return f"{numero or '----'}/{ano or '----'}"
