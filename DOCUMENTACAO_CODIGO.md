# Documentacao Tecnica do Codigo - AFIS Talao

## 1. Objetivo deste documento

Este arquivo descreve a estrutura atual do codigo, regras de negocio, fluxo operacional, pontos de integracao e orientacoes de manutencao.

Publico alvo:

- desenvolvedores que vao manter o projeto;
- equipe de suporte tecnico;
- revisores de arquitetura e qualidade.

## 2. Visao geral da arquitetura

O projeto segue uma arquitetura em camadas simples, com separacao por responsabilidade:

1. `main.py`:
- ponto de entrada da aplicacao;
- carrega configuracao;
- cria a janela principal;
- injeta repositorio na UI.

2. `afis_app/ui.py`:
- camada de interface (Tkinter/CustomTkinter);
- orquestra interacao do usuario;
- chama servicos de negocio;
- chama repositorio para persistencia.

3. `afis_app/services.py`:
- camada de regras de negocio (use cases locais);
- encapsula validacao e decisao por status;
- encapsula regras de alerta.

4. `afis_app/repository.py`:
- acesso ao SQL Server (`pyodbc`);
- queries, insert, update, listagens e sincronizacao de monitoramento.

5. `afis_app/validators.py`:
- normalizacao de data/hora;
- validacao de campos obrigatorios;
- validacao de formato do boletim.

6. `afis_app/constants.py`:
- status, listas de campos obrigatorios e labels.

7. `afis_app/interfaces.py`:
- contrato (`Protocol`) esperado para o repositorio;
- permite desacoplamento entre UI e implementacao concreta.

## 3. Estrutura de pastas e arquivos

- `main.py`: entrada da aplicacao.
- `afis_app/config.py`: carga de ambiente (`assets/.env`).
- `afis_app/constants.py`: constantes de dominio e labels.
- `afis_app/interfaces.py`: contrato `TalaoRepository`.
- `afis_app/services.py`: `TalaoService` e `AlertaService`.
- `afis_app/validators.py`: parse/validacao.
- `afis_app/repository.py`: implementacao `SQLServerRepository`.
- `afis_app/ui.py`: janelas e dashboard principal.
- `bd_scripts/schema_afis.sql`: script de schema.
- `tests/test_services.py`: testes unitarios dos servicos.

## 4. Fluxos principais de negocio

## 4.1 Inicializacao da aplicacao

Fluxo:

1. `main()` chama `load_env_file()`.
2. Configura logging.
3. Cria root via `build_root()`.
4. Instancia `SQLServerRepository` tipado como `TalaoRepository`.
5. Instancia `AFISDashboard`.
6. Inicia loop Tk (`mainloop`).

Pontos de falha:

- ausencia de `pyodbc`;
- credenciais/servidor invalidos;
- tabelas nao existentes no banco.

## 4.2 Criacao de talao

Fluxo:

1. UI coleta campos (`AFISDashboard._collect_form_data`).
2. `TalaoService.prepare_new_talao`:
- injeta data/hora atuais;
- fixa status em `MONITORADO`;
- valida obrigatorios de criacao.
3. UI chama `repo.insert_talao(normalized, intervalo)`.
4. Repositorio:
- calcula proximo numero por ano com lock;
- grava em `dbo.taloes`;
- sincroniza `dbo.monitoramento`.

## 4.3 Edicao de talao

Fluxo:

1. Usuario seleciona item no grid e abre `TalaoEditor`.
2. `TalaoEditor.save()`:
- coleta dados;
- chama `TalaoService.prepare_update_talao`.
3. Regra adicional de finalizacao:
- se status desejado for `FINALIZADO`, pergunta se o boletim finalizado foi enviado ao grupo AFIS no zap;
- se resposta for `Nao`, status e forçado para `MONITORADO`.
4. UI chama `repo.update_talao(...)`.

Regra de bloqueio:

- status `FINALIZADO` e `CANCELADO` nao pode ser editado.

## 4.4 Alertas de monitoramento

Fluxo:

1. Scheduler (`after`) chama `processar_alertas`.
2. Se houver modal aberta, adia ciclo.
3. Busca vencidos via `repo.list_due_monitoring`.
4. Processa 1 alerta por ciclo.
5. Pergunta se acao de encerramento foi cumprida.
6. Se `Nao`: chama `repo.postpone_monitoring`.
7. Se `Sim`: tenta finalizar via `_tentar_finalizar_por_alerta`.

Finalizacao por alerta:

1. Carrega registro.
2. `TalaoService.prepare_finalize_from_record`.
3. Se faltar campo: reabre `TalaoEditor`.
4. Confirmacao obrigatoria do envio do boletim finalizado:
- se `Nao`, mantem monitorado e posterga alerta;
- se `Sim`, chama `repo.update_talao` com status finalizado.

## 4.5 Relatorios

Fluxo:

1. Usuario informa periodo.
2. UI valida datas.
3. Busca dados por periodo em `repo.list_taloes_by_period`.
4. Exporta:
- CSV (`gerar_csv`);
- XLSX por template `assets/modelo.xlsx` (`gerar_modelo_xlsx`).

## 4.6 Busca de taloes (filtros combinados)

Fluxo:

1. Usuario clica em `Busca` no dashboard.
2. Abre `BuscaTaloesWindow` com filtros:
- talao;
- ano;
- delegacia;
- boletim;
- data;
- equipe;
- operador.
3. Janela converte e valida filtros:
- talao aceita `NNNN` ou `NNNN/AAAA`;
- ano exige 4 digitos;
- data aceita `DD/MM/AAAA` e `AAAA-MM-DD`.
4. UI chama `repo.search_taloes(filters)`.
5. Repositorio monta SQL dinamico com `AND` entre filtros.
6. UI gera HTML temporario com todas as colunas retornadas e abre no navegador.

## 4.7 Mensagem WhatsApp (template manual)

Fluxo:

1. Usuario seleciona um talao na grade.
2. Usuario clica no icone `Zap`.
3. UI busca o registro por `id` (`repo.get_talao`).
4. UI monta mensagem padrao (`_build_whatsapp_message`).
5. UI grava arquivo `.txt` temporario e abre no app padrao para copia/cola.

## 4.8 Backup anual

Fluxo:

1. Usuario informa ano.
2. UI busca dados:
- `repo.list_taloes_by_year`;
- `repo.list_monitoramento_by_year`.
3. Gera arquivo SQL com inserts (inclui `IDENTITY_INSERT`).

## 5. Modelo de dados (SQL Server)

Tabela `dbo.taloes`:

- chave primaria `id`;
- unicidade `ano + talao`;
- campos operacionais (delegacia, autoridade, boletim etc);
- `status` com `CHECK`:
  `MONITORADO`, `FINALIZADO`, `CANCELADO`;
- timestamps `criado_em` e `atualizado_em` em UTC.

Tabela `dbo.monitoramento`:

- referencia 1:1 por `talao_id`;
- `proximo_alerta` e `intervalo_min`;
- `ON DELETE CASCADE` para remover monitoramento junto com talao.

## 6. Catalogo de classes, funcoes e metodos

## 6.1 `main.py`

- `_resolve_asset_path(path_value)`: resolve caminhos relativos/absolutos para assets.
- `_configure_app_icon(root)`: aplica icone da aplicacao.
- `main()`: fluxo de boot e injecao de dependencias.

## 6.2 `afis_app/config.py`

- `load_env_file()`: carrega `assets/.env` se existir.
- `get_env(key, default=None)`: leitura de variavel com fallback.

## 6.3 `afis_app/interfaces.py`

- `class TalaoRepository(Protocol)`:
- `get_next_talao`
- `insert_talao`
- `update_talao`
- `get_talao`
- `list_initial_taloes`
- `list_due_monitoring`
- `get_monitoring_interval`
- `list_taloes_by_period`
- `search_taloes`
- `list_taloes_by_year`
- `list_monitoramento_by_year`
- `postpone_monitoring`

## 6.4 `afis_app/validators.py`

- `_parse_date(value)`: parse `dd/mm/yyyy` ou `yyyy-mm-dd`.
- `_normalize_and_validate_boletim(value)`: valida padrao `AA0001..ZZ9999` com sufixo opcional `-1..-99`.
- `normalize_and_validate(data, required_fields)`:
- normaliza datas e hora para formato persistivel;
- normaliza e valida boletim quando informado;
- retorna `(normalized, missing)`.

## 6.5 `afis_app/services.py`

`class TalaoService`:

- `_required_fields_for_status(status)`: resolve lista de obrigatorios por status.
- `prepare_new_talao(form_data, now=None)`: prepara payload de criacao.
- `prepare_update_talao(form_data)`: prepara payload de edicao.
- `prepare_finalize_from_record(record)`: prepara payload de finalizacao.

`class AlertaService`:

- `is_edit_blocked_status(status)`: bloqueio de edicao.
- `is_monitorado(status)`: confirma status monitorado.
- `build_monitoring_question(ano, talao, boletim)`: texto do alerta periodico.
- `build_final_boletim_confirmation_question()`: texto da confirmacao obrigatoria para finalizar.
- `_format_talao(ano, numero)`: formata numero de talao.

## 6.6 `afis_app/repository.py`

Excecoes:

- `DatabaseError`
- `ConcurrencyError`
- `DuplicateTalaoError`

`class SQLServerRepository`:

- `__init__`
- `_build_connection_string`
- `_to_yes_no`
- `_connect`
- `ensure_schema_is_ready`
- `get_next_talao`
- `_to_int`
- `_parse_required_date`
- `_parse_optional_date`
- `_parse_required_time`
- `_nullable_text`
- `_build_db_payload`
- `insert_talao`
- `update_talao`
- `_is_unique_key_violation`
- `_sync_monitoramento`
- `get_talao`
- `list_initial_taloes`
- `list_due_monitoring`
- `list_taloes_by_period`
- `list_taloes_by_year`
- `list_monitoramento_by_year`
- `postpone_monitoring`

## 6.7 `afis_app/ui.py`

Funcoes utilitarias de modulo:

- `format_talao`
- `_normalize_user_text`
- `_apply_toplevel_theme`
- `_build_button`
- `_center_toplevel_on_parent`
- `build_root`

Classes:

`class TalaoEditor(tk.Toplevel)`:

- `__init__`
- `_collect`
- `_set_entry_text_color`
- `_bind_data_bo_placeholder`
- `_set_data_bo_placeholder`
- `_on_data_bo_focus_in`
- `_on_data_bo_focus_out`
- `_on_data_bo_key_press`
- `save`

`class RelatorioPeriodoWindow(tk.Toplevel)`:

- `__init__`
- `_parse_periodo`
- `_set_entry_text_color`
- `_bind_date_placeholder`
- `_set_date_placeholder`
- `_on_date_focus_in`
- `_on_date_focus_out`
- `_on_date_key_press`
- `_get_date_value`
- `_load_report_rows`
- `_resolve_modelo_path`
- `_format_excel_date`
- `gerar_csv`
- `gerar_modelo_xlsx`

`class BackupAnoWindow(tk.Toplevel)`:

- `__init__`
- `_sql_literal`
- `_build_insert_block`
- `gerar_backup`

`class BuscaTaloesWindow(tk.Toplevel)`:

- `__init__`
- `_parse_filters`
- `_format_html_value`
- `_build_result_html`
- `buscar`
- `limpar_campos`

`class AFISDashboard`:

- `__init__`
- `_apply_theme`
- `_build_button`
- `_build_layout`
- `_set_defaults`
- `_resolve_asset_path`
- `_load_watermark_image`
- `_setup_watermark`
- `_collect_form_data`
- `_bind_data_bo_placeholder`
- `_set_data_bo_placeholder`
- `_on_data_bo_focus_in`
- `_on_data_bo_focus_out`
- `_on_data_bo_key_press`
- `_refresh_proximo_talao`
- `criar_talao`
- `editar_selecionado`
- `abrir_relatorios`
- `abrir_busca`
- `abrir_backup`
- `gerar_mensagem_whatsapp_selecionado`
- `refresh_tree`
- `_auto_refresh`
- `_has_active_modal`
- `processar_alertas`
- `_tentar_finalizar_por_alerta`

## 7. Regras de negocio consolidadas

Status:

- `MONITORADO`: estado inicial e estado de continuidade.
- `FINALIZADO`: exige campos adicionais.
- `CANCELADO`: exige observacao.

Obrigatoriedade:

- criacao: `CREATE_REQUIRED`;
- finalizacao: `FINALIZE_REQUIRED`;
- cancelamento: `CANCEL_REQUIRED`.

Boletim:

- obrigatorio em criacao, finalizacao e cancelamento;
- formato aceito: `AA0001` ate `ZZ9999`;
- sufixo opcional: `-1` ate `-99` (ex.: `AB1234-2`).

Regra adicional de finalizacao:

- para finalizar, usuario deve confirmar envio do boletim finalizado ao grupo AFIS no zap;
- sem confirmacao, status nao pode virar `FINALIZADO`.

## 8. Concorrencia e consistencia

Pontos implementados:

- lock de sequencia no insert (`UPDLOCK`, `HOLDLOCK`);
- controle de conflito por `expected_updated_at`;
- erro dedicado para conflito de edicao (`ConcurrencyError`);
- tratamento de chave unica para concorrencia de numeracao (`DuplicateTalaoError`).

Risco conhecido:

- mistura de funcoes de data local e UTC em consultas/listagens pode gerar diferencas de borda de horario.

## 9. Tratamento de erros

Padrao atual:

- camada de repositorio levanta excecoes de dominio tecnico;
- camada de UI captura e traduz para mensagens do usuario;
- logging em `afis_app.log`.

Ponto de atencao:

- ha varios `except Exception` na UI (bom para resiliencia, mas pode mascarar classe de erro se nao houver log detalhado).

## 10. Testes automatizados

Arquivo:

- `tests/test_services.py`

Cobertura atual:

- `TalaoService`:
- preparacao de criacao;
- obrigatoriedade por status em edicao;
- validacao de formato de boletim;
- preparacao de finalizacao.
- `AlertaService`:
- bloqueio de edicao por status;
- deteccao de monitorado;
- texto do alerta.

Executar testes:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## 11. Guia de manutencao futura

Checklist antes de mudar regra de negocio:

1. Alterar primeiro em `services.py`.
2. Atualizar UI apenas para consumir servico.
3. Cobrir regra nova com teste em `tests/test_services.py`.
4. Rodar compilacao + testes.

Checklist para mudancas de banco:

1. Ajustar `bd_scripts/schema_afis.sql`.
2. Ajustar `repository.py`.
3. Revisar impacto em exportacao/backup.
4. Validar mensagens de erro e manual do usuario.

Checklist para mudancas de UI:

1. Evitar colocar regra de negocio em widget/evento.
2. Reusar servicos.
3. Garantir comportamento modal (`transient` + `grab_set`).
4. Testar cenarios de alerta com janela aberta.

## 12. Dividas tecnicas e proximos passos recomendados

1. Cobrir `repository.py` com testes de integracao (ambiente SQL de teste).
2. Criar testes para fluxos criticos da UI (ao menos smoke tests).
3. Padronizar toda logica temporal em UTC ou local com estrategia unica.
4. Extrair exportacao/backup para modulo dedicado, reduzindo tamanho de `ui.py`.
5. Criar changelog tecnico para regras de negocio (especialmente status/finalizacao).

