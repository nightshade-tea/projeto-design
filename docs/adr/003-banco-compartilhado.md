# ADR 003: Banco de dados compartilhado, com tabelas por módulo

> Rascunho para revisão do grupo.

**Status**: proposto

## Contexto

- O servidor é um monólito modular, com os módulos `identidade`, `projetos`
  e `certificacao` (ADR 001)
- O domínio tem dois agregados, `Projeto` e `Certificado`, cada um com um
  repository
- O certificado é criado a partir do resumo de frequência de um projeto, e
  o encerramento e a emissão precisam ser consistentes

## Problema e forças

Como guardar os dados dos módulos?
- Bancos separados isolam os módulos, mas complicam operações que envolvem
  mais de um módulo
- Um banco único é mais simples, mas permite que um módulo dependa das
  tabelas de outro
- Os dados devem poder ser separados se um módulo virar um serviço no
  futuro

## Alternativas consideradas

- **Um banco por módulo**: cada módulo tem o próprio banco de dados
- **Banco compartilhado sem regras**: todos os módulos usam as mesmas
  tabelas livremente
- **Banco compartilhado, com tabelas por módulo**: um único banco, e cada
  módulo só acessa as próprias tabelas

## Decisão

- Um único **banco de dados compartilhado** pelos módulos
- Cada módulo tem as **próprias tabelas**, e um módulo não acessa as
  tabelas de outro
- O acesso é feito pelos repositories (`ProjetoRepository` e
  `CertificadoRepository`), um por agregado, e cada agregado é salvo em uma
  transação
- O arquivo do certificado não é guardado: ele é gerado a cada download a
  partir dos dados de `Certificado`

## Consequências positivas

- Um único banco para implantar, fazer backup e operar
- Transações locais, sem consistência eventual entre módulos
- As fronteiras entre as tabelas facilitam separar um módulo no futuro
  (ASR03)
- O domínio não depende do banco, só das interfaces dos repositories

## Consequências negativas, custos e riscos

- A separação das tabelas é uma convenção, e nada impede uma consulta que
  cruze os módulos
- O banco é um ponto único de falha e pode virar o gargalo com a carga
  máxima (ASR01); pode ser preciso usar réplicas de leitura
- A fila de escritas (ADR 002) também usa esse banco, o que aumenta a carga
  sobre ele
- Gerar o arquivo a cada download usa mais processamento do que guardá-lo
