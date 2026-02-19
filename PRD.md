# Objetivo:
- criar um aplicativo desktop em python, base de dados sql server e interface gráfica tkinter e customtkinter que servirá como registro digital das solicitações de perícia AFIs, registrando um talão para cada solicitação, além de monitorar o preenchimento completo dos dados, conclusão das etapas obrigatórias do registro e servir como base permanente para consultas, relatórios e correições no futuro, dando fim ao registro manual em livros físicos.
# Contexto:
- rodará em ambiente Windows, com uso interno do CECOP, para usuários não técnicos e com execução local em rede interna.
# Funcionalidades:
1. cadastrar e monitorar os talões de solicitações de perícia AFIs
2. o cadastro dos talões deve conter na base de dados no mínimo os seguintes campos: data_solic, talao, hora_solic, delegacia, autoridade, solicitante, endereco, boletim, natureza, data_BO, vitimas, equipe, operador, status, observcao
3. Dicionário dos dados da tabela de talões:
   - talao: é o número do talão, deve ser único por ano, não se repete, autoincrementável e nunca nulo,
   - data_solic: data da solicitação e abertura do talão
   - hora_solic: hora da solicitação e abertura do talão
   - delegacia: delegacia que feza a solicitação de abertura do talão
   - autoridade: delegado que autorizou a solicitação
   - solicitante: quem entrou em contato solicitando o talão
   - endereco: endereço do local onde se realizará a perícia AFIs
   - boletim: Boletim que registrará a ocorrência do fato
   - natureza: é a qualificação do crime registrado no boletim
   - data_BO: data do registro do boletim de ocorrência
   - vitimas: vítimas registradas na ocorrência
   - equipe: é a equipe que realizou a perícia
   - operador: o policial do CECOP que recebeu a solicitação e registrou a abertura do talão
   - status: estado atual do talão, que pode ser monitorado, finalizado ou cancelado
   - observacao: são observações que o operador julgar necessário anotar no talão, como por exemplo por que o talão foi cancelado.
4. a numeração dos talões é subsequente, não há repetição, nem números vagos, porém é anual se reiniciando do 1 todo dia 01/01 de cada ano.
6. todo talão deve ser por padrão iniciado com o status monitorado
7. todo talão que tiver seu status monitorado deve ser inserido na tabela monitoramento, logo todo talão que tiver alterado o seu status de monitorado para finalizado ou cancelado deve ser removido do monitoramento
8. na base de dados deve ter outra tabela dedicada ao controle do monitoramento dos talões que estiverem sendo monitorados
9. periodicamente deve-se alertar o usuários sobre talões monitorados e se ações necessárias foram cumpridas para encerrar o monitoramento do talão.

# validaçoes:
1. os requisitos mínimos para a abertura de um novo registro de talão são os seguintes campos: talao, data_solic, hora_solic, delegacia, autoridade, solicitante, endereco, operador, status
2. dados de preenchimento obrigatório para possibilitar a finalização de um talão AFIs, tornando seu status finalizado e com isso sendo removido do monitoramento: todos exceto a observacao
3. dados de preenchimento obrigatório para possibilitar o cancelamento de um talão AFIs, tornando seu status cancelado e com isso sendo removido do monitoramento: talao, data_solic, hora_solic, delegacia, autoridade, solicitante, endereco, operador, status e observacao

# GUI
1. tomar como base a já disponível no main.py
2. complementar com os campos a mais
3. deve haver um botão para editar um talão permitindo a alteração de certos campos e preenchimento dos faltantes e alterar o status do monitoramento do talão
4. o preenchimento do status do talão deve ser uma caixa drop-down com as 3 opçoes possíveis: monitorado, finalizado, cancelado. Obviamente para que essa edição seja concluída deve ser aprovada na validação
5. a treeview deve mostrar inicialmente todos os talões a partir do dia anterior ao corrente além dos com status monitorado e no mínimo o último talão registrado independentemente do periódo e status.
6. na treeview devem ser mostradosos seguintes campos: talao, boletim, delegacia, natureza, status
   