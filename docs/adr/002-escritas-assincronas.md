# ADR 002: Escritas assíncronas com fila no banco de dados

> Rascunho para revisão do grupo.

**Status**: proposto

## Contexto

- O sistema deve suportar até 4.000 acessos simultâneos, com 95% das
  escritas respondendo em até 2 s (ASR01, RNF01)
- Os acessos se concentram em picos, por exemplo no registro de presenças
  durante as atividades e no fim do semestre
- Encerrar um projeto emite um certificado para cada aluno aprovado, o que
  pode ser demorado

## Problema e forças

Como responder às escritas nos picos sem atrasar as outras requisições?
- O cliente precisa saber na hora se a escrita foi recusada (permissão ou
  regra de negócio)
- Processar todas as escritas na hora pode sobrecarregar o banco de dados
  nos picos
- Um serviço de mensageria separado é mais um componente para implantar e
  operar

## Alternativas consideradas

- **Escritas síncronas**: a escrita é salva durante a requisição
- **Fila em um serviço de mensageria** (ex.: RabbitMQ): a escrita é
  publicada em uma fila externa e processada depois
- **Fila em uma tabela do banco de dados**: a escrita é gravada em uma
  tabela e processada depois pela própria aplicação

## Decisão

- Consultas e autenticação são **síncronas**
- Escritas são **assíncronas**, por uma **fila em uma tabela do banco de
  dados**:
  - a autenticação, a permissão e as regras são verificadas na hora, e os
    erros são devolvidos na própria requisição
  - se a escrita for aceita, ela entra na fila e a resposta é
    `202 Accepted`
  - a própria aplicação lê a fila e chama os services
- A emissão dos certificados é uma operação separada do encerramento do
  projeto

## Consequências positivas

- A fila absorve os picos de escrita, e as respostas ficam rápidas (RNF01)
- O cliente não precisa consultar o resultado depois, pois os erros já
  foram devolvidos
- Sem um serviço a mais para operar
- A emissão dos certificados não atrasa as outras operações da fila

## Consequências negativas, custos e riscos

- Há um intervalo entre a resposta e a escrita ser salva: uma consulta logo
  depois pode ainda não mostrar a alteração
- O estado pode mudar antes da execução (ex.: o projeto ser encerrado nesse
  meio-tempo), por isso as regras são verificadas de novo e a escrita pode
  ser descartada
- Operações que falham são tentadas de novo, então todas as escritas
  precisam ser idempotentes
- A fila usa o mesmo banco de dados que o resto do sistema e disputa
  recursos com ele; se a carga crescer muito, pode ser preciso trocar por
  um serviço de mensageria
