STATUS_MONITORADO = "MONITORADO"
STATUS_FINALIZADO = "FINALIZADO"
STATUS_CANCELADO = "CANCELADO"
STATUS_OPCOES = (STATUS_MONITORADO, STATUS_FINALIZADO, STATUS_CANCELADO)

CREATE_REQUIRED = [
    "data_solic",
    "hora_solic",
    "delegacia",
    "autoridade",
    "solicitante",
    "endereco",
    "operador",
    "status",
]

FINALIZE_REQUIRED = [
    "data_solic",
    "hora_solic",
    "delegacia",
    "autoridade",
    "solicitante",
    "endereco",
    "boletim",
    "natureza",
    "data_bo",
    "vitimas",
    "equipe",
    "operador",
    "status",
]

CANCEL_REQUIRED = [
    "data_solic",
    "hora_solic",
    "delegacia",
    "autoridade",
    "solicitante",
    "endereco",
    "operador",
    "status",
    "observacao",
]

FIELD_LABELS = {
    "data_solic": "Data Solicitação",
    "hora_solic": "Hora Solicitação (HH:MM)",
    "delegacia": "Delegacia",
    "autoridade": "Autoridade",
    "solicitante": "Solicitante",
    "endereco": "Endereço",
    "boletim": "Boletim",
    "natureza": "Natureza",
    "data_bo": "Data BO (DD/MM/AAAA)",
    "vitimas": "Vítimas",
    "equipe": "Equipe",
    "operador": "Operador",
    "status": "Status",
    "observacao": "Observação",
}

EDITABLE_FIELDS = [
    "delegacia",
    "autoridade",
    "solicitante",
    "endereco",
    "boletim",
    "natureza",
    "data_bo",
    "vitimas",
    "equipe",
    "operador",
    "status",
    "observacao",
]
