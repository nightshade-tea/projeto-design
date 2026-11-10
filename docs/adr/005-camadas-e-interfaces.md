# ADR 005: Camadas com interfaces no domínio

> Rascunho para revisão do grupo.

**Status**: proposto

## Contexto

- O sistema depende de partes que podem mudar: o banco de dados, o login
  institucional e o formato do arquivo do certificado
- As regras de certificação devem poder mudar e crescer (ASR03)
- O domínio deve ser testável sem o banco e sem o provedor de identidade

## Problema e forças

Como organizar o código dentro do servidor?
- O domínio não deve depender de banco, HTTP ou serviços externos
- Arquiteturas como Hexagonal, Onion e Clean isolam bem o domínio, mas
  trazem mais camadas e conceitos
- A equipe é pequena e o sistema é de porte médio

## Alternativas consideradas

- **Camadas tradicionais**: controllers → services → acesso a dados, e o
  domínio depende da persistência
- **Arquitetura Hexagonal ou Clean completa**: portas de entrada e saída,
  casos de uso e adaptadores separados para tudo
- **Camadas com interfaces no domínio**: controllers → services → domínio,
  e o domínio define as interfaces que as implementações seguem

## Decisão

O código é organizado em **camadas**, e as dependências apontam para o
domínio:
- **Controllers** recebem as requisições e identificam o usuário, sem
  regras de negócio
- **Services** executam os casos de uso
- **Domínio** tem os objetos, as regras e as interfaces
  (`ProvedorIdentidade`, `GeradorDocumentoCertificado`, `ProjetoRepository`,
  `CertificadoRepository`)
- **Implementações** (`ProjetoRepositorySql`, `CertificadoRepositorySql`,
  `ProvedorIdentidadeInstitucional`, `GeradorPdf`) dependem das interfaces
  do domínio

As regras de certificação são implementações de `CriterioCertificacao`,
dentro do domínio.

## Consequências positivas

- O domínio não depende do banco, do provedor nem do formato do arquivo
  (inversão de dependência)
- As implementações podem ser trocadas, e os testes usam implementações de
  teste (`ProvedorIdentidadeTeste`, `GeradorDocumentoTeste`)
- Novos critérios de certificação não alteram `Projeto` nem
  `CriteriosCertificacao` (ASR03)
- Menos camadas e conceitos que uma arquitetura Hexagonal ou Clean completa

## Consequências negativas, custos e riscos

- Mais interfaces e classes do que em camadas tradicionais
- Os controllers e services não têm interfaces próprias, então trocar a
  forma de acesso (ex.: outra API além de REST) exige mais mudanças do que
  na arquitetura Hexagonal
- Manter as dependências no sentido certo depende da disciplina da equipe
