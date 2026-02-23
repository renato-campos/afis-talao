# Manual do Usuario - Sistema AFIS Talao

## 1. Para que serve o sistema

O sistema AFIS Talao e usado para registrar, acompanhar e encerrar taloes de forma digital.

Com ele, voce consegue:

- abrir novos taloes;
- acompanhar taloes em monitoramento;
- receber alertas periodicos;
- editar taloes em andamento;
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
- `Alerta (min)` para definir o intervalo do monitoramento.

### 3.2 Botoes principais

- `Salvar`: abre um novo talao com status monitorado.
- `Editar`: altera um talao selecionado na lista.
- `Atualizar`: recarrega a lista de taloes visiveis.
- `Limpar`: limpa o formulario para novo preenchimento.
- `Relatorios`: abre a janela de exportacao por periodo.
- `Backup`: abre a janela de backup por ano.

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
2. Escolha o intervalo em `Alerta (min)`.
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

- Monitorado: dados basicos de abertura.
- Finalizado: dados basicos + boletim + natureza + data BO + vitimas + equipe.
- Cancelado: dados basicos + observacao.

Padrao de preenchimento:

- data: `dd/mm/aaaa`
- hora: `HH:MM`

## 7. Alertas de monitoramento (como responder)

Quando um talao monitorado atinge o horario de alerta, aparece uma pergunta de confirmacao:

- Se responder `Sim`: o sistema tenta finalizar automaticamente.
- Se faltar informacao obrigatoria para finalizar: o talao e aberto para complementar.
- Se responder `Nao`: o proximo alerta e adiado conforme o intervalo definido.

## 8. Relatorios (passo a passo)

1. Clique em `Relatorios`.
2. Informe `Data inicio` e `Data fim`.
3. Escolha:
   - `CSV` para planilha simples;
   - `Excel` para exportar no modelo padrao do setor.
4. Escolha a pasta e salve o arquivo.

Observacao:

- o periodo considera a data de solicitacao do talao.

## 9. Backup anual (passo a passo)

1. Clique em `Backup`.
2. Informe o ano de referencia.
3. Clique em `Backup SQL`.
4. Escolha onde salvar.

O arquivo gerado contem os registros daquele ano para restauracao futura e/ ou auditoria, se necessario.

## 10. Boas praticas de operacao

- Preencha os dados essenciais no momento da abertura.
- Nao deixe alerta acumulado sem resposta.
- Atualize o status de acordo com a situacao real.
- Gere relatorio com frequencia definida pela equipe.
- Gere backup regularmente e guarde copia em local seguro.

## 11. Duvidas comuns (solucao rapida)

- **Nao abre o sistema**: acione o suporte para validar conexao e configuracao.
- **Nao consigo salvar/finalizar**: revise campos obrigatorios e formato de data/hora.
- **Talao nao aparece na lista**: clique em `Atualizar`.
- **Conflito ao salvar edicao**: recarregue a lista e tente novamente.
- **Excel nao gera**: acione o suporte para validar componentes do ambiente.


