from __future__ import annotations

from datetime import date
from typing import Any, Protocol


class TalaoRepository(Protocol):
    def get_next_talao(self, ano: int) -> int:
        ...

    def insert_talao(self, data: dict[str, Any], intervalo_min: int) -> int:
        ...

    def update_talao(
        self,
        talao_id: int,
        data: dict[str, Any],
        intervalo_min: int,
        expected_updated_at: Any = None,
    ) -> None:
        ...

    def get_talao(self, talao_id: int) -> dict[str, Any] | None:
        ...

    def list_initial_taloes(self) -> list[Any]:
        ...

    def list_due_monitoring(self) -> list[Any]:
        ...

    def list_taloes_by_period(self, data_inicio: date, data_fim: date) -> tuple[list[str], list[Any]]:
        ...

    def list_taloes_by_year(self, ano: int) -> tuple[list[str], list[Any]]:
        ...

    def list_monitoramento_by_year(self, ano: int) -> tuple[list[str], list[Any]]:
        ...

    def postpone_monitoring(self, talao_id: int, intervalo_min: int) -> None:
        ...
