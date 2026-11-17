# ADR 001: Monólito modular

## Contexto

- O sistema gerencia projetos de extensão, frequência e certificados, com o
  domínio dividido em 3 partes: `identidade`, `projetos` e `certificacao`
- Deve suportar até 4.000 acessos simultâneos com disponibilidade de 99,5%
- A equipe de desenvolvimento é pequena

## Problemas envolvidos

É preciso decidir como dividir o sistema em unidades de implantação:
- as regras de certificação e os processos da universidade devem poder mudar
  sem afetar o resto do sistema
- a emissão de certificados usa dados de `projetos` e `identidade`, então os
  módulos conversam com frequência, e chamadas pela rede pesam no limite de
  1 s das consultas
- o sistema precisa escalar e continuar disponível nos picos de acesso
- cada unidade a mais precisa ser implantada, monitorada e operada pela
  mesma equipe pequena

## Alternativas consideradas

- **Monólito simples**: organização apenas em camadas, sem separação por módulos
- **Monólito modular**: divisão do sistema em módulos de domínio, com
  dependências num único sentido
- **Microsserviços**: um serviço por módulo, cada um com o próprio banco de
  dados, comunicando-se pela rede

## Decisão

Utilizar **monólito modular**: uma única aplicação dividida nos módulos
`certificacao`, `projetos` e `identidade`, com as dependências
`certificacao` -> `projetos` -> `identidade`. Os módulos conversam por
chamadas de método.

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
