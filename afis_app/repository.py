from datetime import datetime
import logging

try:
    import pyodbc
except ImportError:
    pyodbc = None

from .constants import STATUS_CANCELADO, STATUS_FINALIZADO, STATUS_MONITORADO
from .config import get_env

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class ConcurrencyError(DatabaseError):
    pass


class DuplicateTalaoError(DatabaseError):
    pass


class SQLServerRepository:
    def __init__(self):
        self.connection_string = self._build_connection_string()
        self.ensure_schema_is_ready()

    def _build_connection_string(self):
        driver = get_env("DB_DRIVER", default="ODBC Driver 18 for SQL Server")
        driver = str(driver).strip("{}")
        server = get_env("DB_SERVER")
        database = get_env("DB_NAME")
        user = get_env("DB_USER")
        password = get_env("DB_PASSWORD")
        trusted = get_env("DB_TRUSTED", default="1")
        encrypt = self._to_yes_no(get_env("DB_ENCRYPT", default="yes"))
        trust_server_certificate = self._to_yes_no(get_env("DB_TRUST_SERVER_CERT", default="no"))

        if not server:
            raise DatabaseError("Variável DB_SERVER não configurada no arquivo .env.")
        if not database:
            raise DatabaseError("Variável DB_NAME não configurada no arquivo .env.")
        if user and not password:
            raise DatabaseError("DB_USER configurado sem DB_PASSWORD no arquivo .env.")
        if password and not user:
            raise DatabaseError("DB_PASSWORD configurado sem DB_USER no arquivo .env.")

        if user and password:
            return (
                f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
                f"UID={user};PWD={password};Encrypt={encrypt};"
                f"TrustServerCertificate={trust_server_certificate};"
            )

        trusted_mode = "yes" if trusted == "1" else "no"
        return (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            f"Trusted_Connection={trusted_mode};Encrypt={encrypt};"
            f"TrustServerCertificate={trust_server_certificate};"
        )

    def _to_yes_no(self, value):
        normalized = str(value).strip().lower()
        if normalized in ("1", "true", "yes", "y", "on"):
            return "yes"
        if normalized in ("0", "false", "no", "n", "off"):
            return "no"
        logger.warning("Valor inválido para flag booleana (%r). Usando 'no'.", value)
        return "no"

    def _connect(self):
        if pyodbc is None:
            raise DatabaseError("pyodbc não está instalado.")
        return pyodbc.connect(self.connection_string, autocommit=False)

    def ensure_schema_is_ready(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT t.name
                FROM sys.tables t
                INNER JOIN sys.schemas s ON s.schema_id = t.schema_id
                WHERE s.name = 'dbo' AND t.name IN ('taloes', 'monitoramento')
                """
            )
            names = {row[0] for row in cur.fetchall()}
            missing = {"taloes", "monitoramento"} - names
            if missing:
                missing_sorted = ", ".join(sorted(missing))
                raise DatabaseError(
                    "Schema ausente no banco. Execute o arquivo bd_scripts/schema_afis.sql antes de iniciar o app. "
                    f"Tabelas faltantes: {missing_sorted}."
                )

    def get_next_talao(self, ano):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT ISNULL(MAX(talao), 0) + 1 FROM dbo.taloes WHERE ano = ?", ano)
            row = cur.fetchone()
            return self._to_int(row[0] if row else None, "próximo talão")

    def _to_int(self, value, context):
        if value is None:
            raise DatabaseError(f"Valor nulo retornado para {context}.")
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise DatabaseError(f"Valor inválido para {context}: {value!r}") from exc

    def _parse_required_date(self, value, field_name):
        if value is None or str(value).strip() == "":
            raise DatabaseError(f"Campo {field_name} vazio.")
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    def _parse_optional_date(self, value):
        if value is None or str(value).strip() == "":
            return None
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    def _parse_required_time(self, value, field_name):
        if value is None or str(value).strip() == "":
            raise DatabaseError(f"Campo {field_name} vazio.")
        return datetime.strptime(str(value), "%H:%M").time()

    def _nullable_text(self, value):
        if value is None:
            return None
        txt = str(value).strip()
        return txt if txt else None

    def _build_db_payload(self, data):
        data_solic = self._parse_required_date(data.get("data_solic"), "data_solic")
        hora_solic = self._parse_required_time(data.get("hora_solic"), "hora_solic")
        return {
            "ano": data_solic.year,
            "data_solic": data_solic,
            "hora_solic": hora_solic,
            "delegacia": str(data["delegacia"]).strip(),
            "autoridade": str(data["autoridade"]).strip(),
            "solicitante": str(data["solicitante"]).strip(),
            "endereco": str(data["endereco"]).strip(),
            "boletim": self._nullable_text(data.get("boletim")),
            "natureza": self._nullable_text(data.get("natureza")),
            "data_bo": self._parse_optional_date(data.get("data_bo")),
            "vitimas": self._nullable_text(data.get("vitimas")),
            "equipe": self._nullable_text(data.get("equipe")),
            "operador": str(data["operador"]).strip(),
            "status": str(data["status"]).strip(),
            "observacao": self._nullable_text(data.get("observacao")),
        }

    def insert_talao(self, data, intervalo_min):
        payload = self._build_db_payload(data)
        ano = payload["ano"]

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT ISNULL(MAX(talao), 0) + 1 FROM dbo.taloes WITH (UPDLOCK, HOLDLOCK) WHERE ano = ?",
                ano,
            )
            row = cur.fetchone()
            proximo_talao = self._to_int(row[0] if row else None, "sequencia do talao")

            try:
                cur.execute(
                    """
                    INSERT INTO dbo.taloes (
                        ano, talao, data_solic, hora_solic, delegacia, autoridade, solicitante,
                        endereco, boletim, natureza, data_bo, vitimas, equipe, operador, status, observacao, atualizado_em
                    )
                    OUTPUT INSERTED.id
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, SYSUTCDATETIME())
                    """,
                    ano,
                    proximo_talao,
                    payload["data_solic"],
                    payload["hora_solic"],
                    payload["delegacia"],
                    payload["autoridade"],
                    payload["solicitante"],
                    payload["endereco"],
                    payload["boletim"],
                    payload["natureza"],
                    payload["data_bo"],
                    payload["vitimas"],
                    payload["equipe"],
                    payload["operador"],
                    payload["status"],
                    payload["observacao"],
                )
            except Exception as exc:
                if self._is_unique_key_violation(exc):
                    raise DuplicateTalaoError(
                        "Outro terminal inseriu este número de talão antes. Atualize a tela e tente novamente."
                    ) from exc
                raise
            row = cur.fetchone()
            talao_id = self._to_int(row[0] if row else None, "id do talão inserido")

            self._sync_monitoramento(cur, talao_id, payload["status"], intervalo_min)
            conn.commit()
            return proximo_talao

    def update_talao(self, talao_id, data, intervalo_min, expected_updated_at=None):
        payload = self._build_db_payload(data)
        novo_ano = payload["ano"]

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT ano, status FROM dbo.taloes WHERE id = ?", talao_id)
            row = cur.fetchone()
            if not row:
                raise DatabaseError("Talão não encontrado para atualização.")
            ano_atual = self._to_int(row[0], "ano atual do talão")
            status_atual = str(row[1]).strip().upper() if len(row) > 1 and row[1] is not None else ""
            if status_atual in (STATUS_FINALIZADO, STATUS_CANCELADO):
                raise DatabaseError("Talões finalizados ou cancelados não podem ser editados.")
            if novo_ano != ano_atual:
                raise DatabaseError("Não é permitido alterar o ano do talão na edição.")

            params = [
                payload["data_solic"],
                payload["hora_solic"],
                payload["delegacia"],
                payload["autoridade"],
                payload["solicitante"],
                payload["endereco"],
                payload["boletim"],
                payload["natureza"],
                payload["data_bo"],
                payload["vitimas"],
                payload["equipe"],
                payload["operador"],
                payload["status"],
                payload["observacao"],
                talao_id,
            ]
            where_clause = "WHERE id = ?"
            if expected_updated_at is not None:
                where_clause += " AND ABS(DATEDIFF_BIG(NANOSECOND, atualizado_em, ?)) <= 1000"
                params.append(expected_updated_at)

            cur.execute(
                f"""
                UPDATE dbo.taloes
                SET data_solic = ?,
                    hora_solic = ?,
                    delegacia = ?,
                    autoridade = ?,
                    solicitante = ?,
                    endereco = ?,
                    boletim = ?,
                    natureza = ?,
                    data_bo = ?,
                    vitimas = ?,
                    equipe = ?,
                    operador = ?,
                    status = ?,
                    observacao = ?,
                    atualizado_em = SYSUTCDATETIME()
                {where_clause}
                """,
                *params,
            )
            if cur.rowcount == 0:
                raise ConcurrencyError("Talão alterado em outro terminal. Recarregue e tente novamente.")
            self._sync_monitoramento(cur, talao_id, payload["status"], intervalo_min)
            conn.commit()

    def _is_unique_key_violation(self, exc):
        message = str(exc).lower()
        return "uq_taloes_ano_talao" in message or "unique" in message or "2601" in message or "2627" in message

    def _sync_monitoramento(self, cur, talao_id, status, intervalo_min):
        if status == STATUS_MONITORADO:
            cur.execute(
                """
                MERGE dbo.monitoramento AS destino
                USING (SELECT ? AS talao_id) AS origem
                ON destino.talao_id = origem.talao_id
                WHEN MATCHED THEN
                    UPDATE SET proximo_alerta = DATEADD(MINUTE, ?, SYSUTCDATETIME()), intervalo_min = ?
                WHEN NOT MATCHED THEN
                    INSERT (talao_id, proximo_alerta, intervalo_min)
                    VALUES (?, DATEADD(MINUTE, ?, SYSUTCDATETIME()), ?);
                """,
                talao_id,
                intervalo_min,
                intervalo_min,
                talao_id,
                intervalo_min,
                intervalo_min,
            )
        else:
            cur.execute("DELETE FROM dbo.monitoramento WHERE talao_id = ?", talao_id)

    def get_talao(self, talao_id):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM dbo.taloes WHERE id = ?", talao_id)
            row = cur.fetchone()
            if not row:
                return None
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))

    def list_initial_taloes(self):
        query = """
        WITH ultimo AS (
            SELECT TOP 1 id
            FROM dbo.taloes
            ORDER BY ano DESC, talao DESC, id DESC
        ),
        limite AS (
            SELECT CAST(DATEADD(DAY, -1, CAST(GETDATE() AS DATE)) AS DATE) AS data_limite
        )
        SELECT t.id, t.ano, t.talao, t.boletim, t.delegacia, t.natureza, t.status
        FROM dbo.taloes t
        WHERE t.id IN (SELECT id FROM ultimo)
           OR LOWER(LTRIM(RTRIM(ISNULL(t.status, '')))) = ?
           OR t.data_solic >= (SELECT data_limite FROM limite)
        ORDER BY t.ano DESC, t.talao DESC;
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query, STATUS_MONITORADO)
            return cur.fetchall()

    def list_due_monitoring(self):
        query = """
        SELECT m.talao_id, m.intervalo_min, t.ano, t.talao, t.boletim, t.status
        FROM dbo.monitoramento m
        INNER JOIN dbo.taloes t ON t.id = m.talao_id
        WHERE m.proximo_alerta <= SYSUTCDATETIME()
          AND t.status = 'MONITORADO'
        ORDER BY m.proximo_alerta ASC;
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query)
            return cur.fetchall()

    def list_taloes_by_period(self, data_inicio, data_fim):
        query = """
        SELECT
            t.id,
            t.ano,
            t.talao,
            t.data_solic,
            t.hora_solic,
            t.delegacia,
            t.autoridade,
            t.solicitante,
            t.endereco,
            t.boletim,
            t.natureza,
            t.data_bo,
            t.vitimas,
            t.equipe,
            t.operador,
            t.status,
            t.observacao,
            t.criado_em,
            t.atualizado_em
        FROM dbo.taloes t
        WHERE t.data_solic BETWEEN ? AND ?
        ORDER BY t.data_solic ASC, t.hora_solic ASC, t.id ASC;
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query, data_inicio, data_fim)
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
            return columns, rows

    def list_taloes_by_year(self, ano):
        query = """
        SELECT *
        FROM dbo.taloes
        WHERE ano = ?
        ORDER BY id ASC;
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query, ano)
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
            return columns, rows

    def list_monitoramento_by_year(self, ano):
        query = """
        SELECT m.*
        FROM dbo.monitoramento m
        INNER JOIN dbo.taloes t ON t.id = m.talao_id
        WHERE t.ano = ?
        ORDER BY m.id ASC;
        """
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query, ano)
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description]
            return columns, rows

    def postpone_monitoring(self, talao_id, intervalo_min):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE dbo.monitoramento
                SET proximo_alerta = DATEADD(MINUTE, ?, SYSUTCDATETIME()),
                    intervalo_min = ?
                WHERE talao_id = ?
                """,
                intervalo_min,
                intervalo_min,
                talao_id,
            )
            conn.commit()
