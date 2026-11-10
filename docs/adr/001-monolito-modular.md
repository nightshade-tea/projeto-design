# ADR 001: Monólito modular

> Rascunho para revisão do grupo.

**Status**: proposto

## Contexto

- O sistema gerencia projetos de extensão, frequência e certificados, com
  três assuntos de domínio: `identidade`, `projetos` e `certificacao`
- Deve suportar até 4.000 acessos simultâneos (ASR01, RNF01) com
  disponibilidade de 99,5% (RNF02)
- As regras de certificação e os processos da universidade devem poder
  mudar sem afetar o resto do sistema (ASR03)
- A equipe de desenvolvimento é pequena

## Problema e forças

Como dividir e implantar o servidor?
- Separar os módulos facilita a evolução e a escalabilidade
- Cada serviço a mais aumenta o custo de desenvolvimento, implantação e
  operação
- A emissão de certificados usa dados de `projetos` e `identidade`, então os
  módulos conversam com frequência

## Alternativas consideradas

- **Monólito simples**: uma aplicação organizada só em camadas, sem
  separação por módulos
- **Monólito modular**: uma aplicação dividida nos módulos do domínio, com
  dependências em um único sentido
- **Microsserviços**: um serviço por módulo, cada um com o próprio banco de
  dados, comunicando-se pela rede

## Decisão

O servidor é um **monólito modular**: uma única aplicação dividida em
`identidade`, `projetos` e `certificacao`, com dependências
`certificacao` → `projetos` → `identidade`. Os módulos conversam por
chamadas de método.

## Consequências positivas

- Uma única implantação e um único banco de dados, o que é simples para uma
  equipe pequena
- Chamadas entre módulos sem custo de rede, o que ajuda no limite de 1 s
  das consultas (RNF01)
- Mudanças ficam dentro de um módulo (ASR03)
- Um módulo pode virar um serviço separado no futuro, se for necessário

## Consequências negativas, custos e riscos

- As fronteiras entre os módulos dependem da disciplina da equipe, pois nada
  impede que um módulo use outro diretamente
- Todos os módulos escalam juntos: não é possível dar mais recursos só à
  parte mais usada
- Uma falha grave na aplicação afeta todos os módulos; isso é reduzido
  rodando várias instâncias (ver ADR 004)
