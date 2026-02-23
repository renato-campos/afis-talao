from __future__ import annotations

from datetime import date
from typing import Any, Protocol


class TalaoRepository(Protocol):
    """Contrato minimo de persistencia esperado pelas camadas de UI/servico."""

    def get_next_talao(self, ano: int) -> int:
        """Retorna o proximo numero de talao para o ano informado."""
        ...

    def insert_talao(self, data: dict[str, Any], intervalo_min: int) -> int:
        """Insere um novo talao e devolve a numeracao atribuida."""
        ...

    def update_talao(
        self,
        talao_id: int,
        data: dict[str, Any],
        intervalo_min: int,
        expected_updated_at: Any = None,
    ) -> None:
        """Atualiza um talao existente com opcao de controle de concorrencia."""
        ...

    def get_talao(self, talao_id: int) -> dict[str, Any] | None:
        """Retorna um talao por ID, ou None quando inexistente."""
        ...

    def list_initial_taloes(self) -> list[Any]:
        """Lista taloes exibidos inicialmente no dashboard."""
        ...

    def list_due_monitoring(self) -> list[Any]:
        """Lista monitoramentos com alerta vencido."""
        ...

    def list_taloes_by_period(self, data_inicio: date, data_fim: date) -> tuple[list[str], list[Any]]:
        """Retorna colunas e linhas de taloes dentro de um periodo."""
        ...

    def list_taloes_by_year(self, ano: int) -> tuple[list[str], list[Any]]:
        """Retorna colunas e linhas de taloes de um ano especifico."""
        ...

    def list_monitoramento_by_year(self, ano: int) -> tuple[list[str], list[Any]]:
        """Retorna colunas e linhas de monitoramento de um ano especifico."""
        ...

    def postpone_monitoring(self, talao_id: int, intervalo_min: int) -> None:
        """Posterga o proximo alerta de monitoramento de um talao."""
        ...
