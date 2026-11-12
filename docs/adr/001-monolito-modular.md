# ADR 001: Monólito modular

## Status

Aceito

## Contexto

- O sistema gerencia projetos de extensão, frequência e certificados, com o
  domínio dividido em 3 partes: `identidade`, `projetos` e `certificacao`
- Deve suportar até 4.000 acessos simultâneos com disponibilidade de 99,5%
- As regras de certificação e os processos da universidade devem poder mudar
  sem afetar o resto do sistema
- A equipe de desenvolvimento é pequena
- A emissão de certificados usa dados de `projetos` e `identidade`, então os
  módulos conversam com frequência


## Alternativas consideradas

- **Monólito simples**: organização apenas em camadas, sem separação por módulos
- **Monólito modular**: divisão do sistema em módulos de domínio, com
  dependências num único sentido
- **Microsserviços**: um serviço por módulo, cada um com o próprio banco de
  dados, comunicando-se pela rede

## Decisão


Utilizar **monólito modular**: uma única aplicação dividida em com as seguintes
divisões e dependências: `certificacao` -> `projetos` -> `identidade`. Os
módulos conversam por chamadas de método.

## Consequências

### Positivas

- Uma única implantação e um único banco de dados, o que é mais adequado para
  uma equipe pequena
- Chamadas entre módulos sem custo de rede, o que ajuda no limite de 1s das
  consultas
- Mudanças ficam dentro de um módulo
- Um módulo pode virar um serviço separado no futuro, se for necessário
- Separar os módulos facilita a evolução e a escalabilidade

### Negativas, custos e riscos

- As fronteiras entre os módulos dependem da disciplina da equipe, pois nada
  impede que um módulo use outro diretamente
- Todos os módulos escalam juntos: não é possível dar mais recursos só à parte
  mais usada
- Uma falha grave na aplicação afeta todos os módulos, o que é reduzido rodando
  várias instâncias
