# Manual do Usuario - Sistema AFIS Talao

## 1. Objetivo do sistema

O sistema substitui o registro manual em livro para controle de taloes AFIS, com:

- cadastro e acompanhamento de taloes;
- alertas de monitoramento;
- edicao de taloes em andamento;
- geracao de relatorios (CSV e Excel por modelo);
- geracao de backup SQL por ano.

## 2. Visao geral do fluxo de trabalho

Fluxo recomendado no dia a dia:

1. Abrir o sistema e confirmar conexao com banco.
2. Registrar novo talao na tela principal.
3. Acompanhar a lista de taloes visiveis e os alertas de monitoramento.
4. Editar talao quando houver atualizacao operacional.
5. Fechar/finalizar talao quando os campos obrigatorios estiverem completos.
6. Gerar relatorio por periodo para encaminhamento.
7. Gerar backup SQL periodico (por ano).

## 3. Inicio e configuracao

### 3.1 Arquivo de ambiente

As configuracoes do sistema ficam no arquivo:

- `assets/.env`

Exemplos de variaveis usadas:

- `DB_SERVER`
- `DB_NAME`
- `DB_USER` e `DB_PASSWORD` (quando nao usa trusted connection)
- `APP_ICON_PATH`
- `APP_WATERMARK_IMAGE_PATH` (opcional)

### 3.2 Inicializacao

Ao iniciar, o sistema:

1. carrega o `.env`;
2. tenta conectar no SQL Server;
3. valida existencia das tabelas principais;
4. abre a tela principal.

Se houver falha de conexao/esquema, uma mensagem de erro sera exibida.

## 4. Tela principal

## 4.1 Campos de abertura de talao

Na abertura, os principais campos operacionais sao:

- Delegacia
- Autoridade
- Solicitante
- Endereco
- Boletim
- Natureza
- Data BO
- Vitimas
- Equipe
- Operador
- Observacao

O sistema exibe tambem:

- proximo numero de talao do ano atual;
- intervalo de alerta (minutos).

## 4.2 Botoes da tela principal

Ordem atual:

1. `Salvar`
2. `Editar`
3. `Atualizar`
4. `Limpar`
5. `Relatorios`
6. `Backup`

## 4.3 Lista de taloes visiveis

A grade mostra:

- Talao
- Boletim
- Delegacia
- Natureza
- Status

Cores por status ajudam na leitura:

- monitorado - amarelo;
- finalizado - verde;
- cancelado  - vermelho.

## 5. Regras de status e obrigatoriedade

Os status do sistema sao:

- `MONITORADO`
- `FINALIZADO`
- `CANCELADO`

Campos obrigatorios variam conforme status:

- **Criacao/Monitorado**: data/hora solicitacao, delegacia, autoridade, solicitante, endereco, operador, status.
- **Finalizado**: exige os campos acima e tambem boletim, natureza, data BO, vitimas e equipe.
- **Cancelado**: exige os campos de criacao e observacao.

Observacoes:

- Data deve estar em formato `dd/mm/aaaa`.
- Hora deve estar em formato `HH:MM`.
- Taloes finalizados ou cancelados nao podem ser editados.

## 6. Janela de edicao

Ao clicar em `Editar`:

1. selecione um talao na grade;
2. abra a janela de edicao;
3. atualize os campos necessarios;
4. clique em `Salvar`.

Importante:

- o campo `Vitimas` aceita multilinha (Enter para separar por linha);
- o sistema faz validacoes antes de gravar;
- se outro terminal editar antes, o sistema pode sinalizar conflito de concorrencia.

## 7. Monitoramento e alertas

O sistema processa alertas automaticamente em ciclos.

Quando um talao monitorado vence o proximo alerta:

1. o sistema exibe popup de confirmacao;
2. se confirmar, tenta finalizar automaticamente;
3. se faltar campo obrigatorio, reabre o talao para complemento;
4. se negar, o monitoramento e postergado conforme intervalo.

## 8. Relatorios

A janela `Relatorios` permite informar:

- data inicio;
- data fim.

O periodo considera o campo:

- `data_solic` (data de solicitacao).

### 8.1 Exportacao CSV

Botao `CSV` gera um arquivo com os registros do periodo.

### 8.2 Exportacao Excel por modelo

Botao `Excel` gera um arquivo baseado no template:

- `assets/modelo.xlsx`

Preenchimento no modelo (a partir da linha 7):

- Data Solic.
- TALAO
- Data BO
- BO
- Delegacia
- Natureza
- Vitimas
- Equipe

Requisito:

- biblioteca `openpyxl` instalada no ambiente.

## 9. Backup

A janela `Backup` gera arquivo SQL por ano.

Fluxo:

1. informar ano de referencia;
2. clicar em `Backup SQL`;
3. escolher local de salvamento.

O arquivo inclui dados de:

- `dbo.taloes`;
- `dbo.monitoramento` do mesmo ano.

## 10. Boas praticas operacionais

- Preencher sempre campos essenciais no momento da abertura.
- Atualizar status conforme evolucao real do caso.
- Revisar alertas no tempo certo.
- Gerar relatorio periodico para supervisao.
- Gerar backup recorrente e guardar copia em local seguro.
- Nao compartilhar credenciais de banco no `.env`.

## 11. Solucao de problemas (rapido)

- **Erro ao iniciar**: conferir `assets/.env` e conectividade com SQL Server.
- **Erro de schema**: executar `schema.sql` no banco correto.
- **Sem icone/logo**: validar caminhos de assets no `.env`.
- **Excel nao gera**: instalar `openpyxl`.
- **Dados nao aparecem na grade**: usar `Atualizar` e checar filtro de visibilidade (ultimo, monitorados ou ultimas 24h).

## 12. Referencia de arquivos do sistema

- Entrada da aplicacao: `main.py`
- Configuracao: `afis_app/config.py`
- Interface: `afis_app/ui.py`
- Regras e labels: `afis_app/constants.py`
- Validacoes: `afis_app/validators.py`
- Acesso ao banco: `afis_app/repository.py`
- Template de relatorio: `assets/modelo.xlsx`
- Log de execucao: `afis_app.log`
