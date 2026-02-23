from __future__ import annotations

from datetime import datetime
from typing import Any

from .constants import (
    CANCEL_REQUIRED,
    CREATE_REQUIRED,
    EDITABLE_FIELDS,
    FINALIZE_REQUIRED,
    STATUS_CANCELADO,
    STATUS_FINALIZADO,
    STATUS_MONITORADO,
)
from .validators import normalize_and_validate


class TalaoService:
    """Centraliza regras de preparo e validacao de dados de talao."""

    def _required_fields_for_status(self, status: str) -> list[str]:
        """Retorna a lista de campos obrigatorios para o status informado."""
        normalized_status = str(status or "").strip().upper()
        if normalized_status == STATUS_FINALIZADO:
            return FINALIZE_REQUIRED
        if normalized_status == STATUS_CANCELADO:
            return CANCEL_REQUIRED
        return CREATE_REQUIRED

    def prepare_new_talao(
        self, form_data: dict[str, Any], now: datetime | None = None
    ) -> tuple[dict[str, Any], list[str], datetime]:
        """Monta payload de criacao com data/hora atuais e status monitorado."""
        current = now or datetime.now()
        data = dict(form_data)
        data["data_solic"] = current.strftime("%d/%m/%Y")
        data["hora_solic"] = current.strftime("%H:%M")
        data["status"] = STATUS_MONITORADO
        normalized, missing = normalize_and_validate(data, CREATE_REQUIRED)
        return normalized, missing, current

    def prepare_update_talao(
        self, form_data: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """Normaliza e valida um payload de edicao de talao."""
        data = dict(form_data)
        required = self._required_fields_for_status(str(data.get("status") or ""))
        return normalize_and_validate(data, required)

    def prepare_finalize_from_record(
        self, record: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """Converte um registro do banco em payload de finalizacao validado."""
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
    """Regras de negocio relacionadas a monitoramento e mensagens de alerta."""

    def is_edit_blocked_status(self, status: str) -> bool:
        """Indica se o status bloqueia edicao do talao."""
        normalized_status = str(status or "").strip().upper()
        return normalized_status in (STATUS_FINALIZADO, STATUS_CANCELADO)

    def is_monitorado(self, status: str) -> bool:
        """Valida se o status informado representa monitoramento ativo."""
        return str(status or "").strip().upper() == STATUS_MONITORADO

    def build_monitoring_question(self, ano: Any, talao: Any, boletim: Any) -> str:
        """Monta texto padrao da pergunta exibida no alerta periodico."""
        return (
            f"Talão {self._format_talao(ano, talao)} (Boletim: {boletim or 'sem boletim'}) segue monitorado.\n\n"
            "As ações necessárias para encerrar o monitoramento já foram cumpridas?"
        )

    def build_final_boletim_confirmation_question(self) -> str:
        """Retorna a pergunta obrigatoria antes de finalizar um talao."""
        return "Foi enviado o Boletim finalizado para o Grupo AFIS no zap?"

    def _format_talao(self, ano: Any, numero: Any) -> str:
        """Formata o numero do talao no padrao NNNN/AAAA."""
        try:
            return f"{int(numero):04d}/{int(ano)}"
        except (TypeError, ValueError):
            return f"{numero or '----'}/{ano or '----'}"
