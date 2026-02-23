# Manual do Usuario - Sistema AFIS Talao

## 1. Para que serve o sistema

O sistema AFIS Talao e usado para registrar, acompanhar e encerrar taloes de forma digital.

Com ele, voce consegue:

- abrir novos taloes;
- acompanhar taloes em monitoramento;
- receber alertas periodicos;
- editar taloes em andamento;
- pesquisar taloes com filtros combinados;
- gerar mensagem padrao para envio no WhatsApp;
- gerar relatorios por periodo;
- gerar backup anual.

## 2. Fluxo rapido de uso (dia a dia)

Use esta sequencia como referencia:

1. Abra o sistema.
2. Preencha os dados do novo talao e clique em `Salvar`.
3. Acompanhe a lista de taloes na parte inferior da tela.
4. Quando houver atualizacao, selecione o talao e clique em `Editar`.
5. Responda os alertas quando aparecerem.
6. Gere relatorios quando precisar encaminhar resultados.
7. Gere backup periodico para seguranca dos dados.

## 3. Tela principal (o que cada parte faz)

### 3.1 Formulario de abertura

Na parte superior da tela voce informa os dados do atendimento:

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

Tambem aparecem:

- `Proximo Talao` do ano atual;
- `Alerta (min)` no topo, ao lado direito, para definir o intervalo do monitoramento.

### 3.2 Botoes principais

- `Salvar`: abre um novo talao com status monitorado.
- `Editar`: altera um talao selecionado na lista.
- `Atualizar`: recarrega a lista de taloes visiveis.
- `Limpar`: limpa o formulario para novo preenchimento.
- `Busca`: abre a janela de pesquisa no banco por filtros.
- `Relatorios`: abre a janela de exportacao por periodo.
- `Backup`: abre a janela de backup por ano.
- `Zap` (icone): gera uma mensagem pronta do talao selecionado para copiar e colar no WhatsApp.

### 3.3 Lista de taloes visiveis

A lista mostra:

- Talao
- Boletim
- Delegacia
- Natureza
- Status

Cores de apoio:

- monitorado: amarelo
- finalizado: verde
- cancelado: vermelho

## 4. Como abrir um novo talao

1. Preencha os campos do formulario.
2. Escolha o intervalo em `Alerta (min)` no topo da janela.
3. Clique em `Salvar`.

O sistema preenche automaticamente:

- data da solicitacao;
- hora da solicitacao;
- status inicial como `MONITORADO`;
- numero sequencial do talao no ano atual.

## 5. Como editar um talao

1. Selecione um talao na lista.
2. Clique em `Editar`.
3. Ajuste os campos necessarios.
4. Clique em `Salvar`.

Importante:

- taloes `FINALIZADO` e `CANCELADO` nao podem ser editados;
- se outro terminal tiver salvo alteracoes antes, o sistema pode avisar conflito.

## 6. Status do talao (quando usar cada um)

- `MONITORADO`: talao ainda em acompanhamento.
- `FINALIZADO`: atendimento encerrado com dados completos.
- `CANCELADO`: talao encerrado por cancelamento (com justificativa em observacao).

Campos obrigatorios por status:

- Monitorado: dados basicos de abertura + boletim.
- Finalizado: dados basicos + boletim + natureza + data BO + vitimas + equipe.
- Cancelado: dados basicos + boletim + observacao.

Padrao de preenchimento:

- data: `dd/mm/aaaa`
- hora: `HH:MM`
- boletim: `AA0001` ate `ZZ9999`, com sufixo opcional `-1` ate `-99` (ex.: `AB1234` ou `AB1234-2`)

## 7. Alertas de monitoramento (como responder)

Quando um talao monitorado atinge o horario de alerta, aparece uma pergunta de confirmacao:

- Se responder `Sim`: o sistema tenta finalizar automaticamente.
- Se faltar informacao obrigatoria para finalizar: o talao e aberto para complementar.
- Se responder `Nao`: o proximo alerta e adiado conforme o intervalo definido.

## 8. Busca de taloes (passo a passo)

1. Clique em `Busca`.
2. Preencha um ou mais filtros:
   - Talao (`NNNN` ou `NNNN/AAAA`)
   - Ano (`AAAA`)
   - Delegacia
   - Boletim
   - Data (`dd/mm/aaaa`)
   - Equipe
   - Operador
3. Clique em `Buscar`.
4. O resultado abre em um arquivo HTML com todas as informacoes dos registros encontrados.

Observacoes:

- quando mais de um campo e informado, a busca usa condicao `E`;
- o botao `Limpar` na janela de busca apaga todos os filtros.

## 9. Mensagem para WhatsApp (passo a passo)

1. Selecione um talao na lista principal.
2. Clique no icone `Zap`.
3. O sistema abre um arquivo `.txt` com a mensagem pronta.
4. Copie e cole no WhatsApp.

## 10. Relatorios (passo a passo)

1. Clique em `Relatorios`.
2. Informe `Data inicio` e `Data fim`.
3. Escolha:
   - `CSV` para planilha simples;
   - `Excel` para exportar no modelo padrao do setor.
4. Escolha a pasta e salve o arquivo.

Observacao:

- o periodo considera a data de solicitacao do talao.

## 11. Backup anual (passo a passo)

1. Clique em `Backup`.
2. Informe o ano de referencia.
3. Clique em `Backup SQL`.
4. Escolha onde salvar.

O arquivo gerado contem os registros daquele ano para restauracao futura e/ ou auditoria, se necessario.

## 12. Boas praticas de operacao

- Preencha os dados essenciais no momento da abertura.
- Nao deixe alerta acumulado sem resposta.
- Atualize o status de acordo com a situacao real.
- Gere relatorio com frequencia definida pela equipe.
- Gere backup regularmente e guarde copia em local seguro.

## 13. Duvidas comuns (solucao rapida)

- **Nao abre o sistema**: acione o suporte para validar conexao e configuracao.
- **Nao consigo salvar/finalizar**: revise campos obrigatorios e formato de data/hora/boletim.
- **Talao nao aparece na lista**: clique em `Atualizar`.
- **Conflito ao salvar edicao**: recarregue a lista e tente novamente.
- **Busca nao retornou dados**: revise filtros e lembre que multiplos campos usam condicao `E`.
- **Excel nao gera**: acione o suporte para validar componentes do ambiente.


