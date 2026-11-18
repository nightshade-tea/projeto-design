# Alternativas e trade-offs

A arquitetura escolhida neste trabalho foi o monólito modular
(`arquitetura.md`). Todas as alternativas comparadas são cliente-servidor
(cliente web + servidor) e usam o login institucional (sistema externo). A
diferença entre elas está na organização do servidor.


## Alternativas e arquitetura escolhida

### A: Monólito simples

Uma única aplicação organizada só em camadas (controllers, services,
domínio, implementações), sem separação por módulos do domínio.

**Vantagens**
- É a opção mais rápida de começar e a mais fácil de entender
- Uma única implantação, um único banco de dados e chamadas de método
  entre as partes

**Desvantagens**
- Sem fronteiras entre `identidade`, `projetos` e `certificacao`, qualquer
  classe pode usar qualquer outra, e o acoplamento cresce com o tempo
- Mudar as regras de certificação tende a afetar código de projetos e de
  frequência
- Separar uma parte ou adicionar novas funcionalidades no futuro exige
  primeiro reorganizar o código


### B: Monólito modular (arquitetura escolhida para o trabalho)

Uma única aplicação dividida nos módulos do domínio (`identidade`,
`projetos` e `certificacao`), com dependências em um único sentido e
camadas dentro do servidor. Descrita em `arquitetura.md`.

**Vantagens**
- Mantém a simplicidade de implantação do monólito
- Os módulos e as interfaces do domínio limitam o impacto das mudanças
- Um módulo pode virar um serviço separado no futuro, se for necessário

**Desvantagens**
- As fronteiras entre os módulos dependem de disciplina da equipe, pois o
  compilador não impede que um módulo use outro diretamente
- Todos os módulos escalam juntos, então não é possível dar mais recursos
  só à parte mais usada
- Uma falha grave na aplicação afeta todos os módulos


### C: Microsserviços

Um serviço por módulo (`identidade`, `projetos` e `certificacao`), cada um
com o próprio banco de dados, implantados separadamente e comunicando
pela rede (HTTP ou mensagens), com um gateway na frente.

**Vantagens**
- Cada serviço escala e é implantado de forma independente
- Uma falha em um serviço (como certificação) não derruba os outros
- As fronteiras entre os módulos são garantidas pela própria divisão

**Desvantagens**
- Chamadas entre serviços passam pela rede, com mais latência e mais
  pontos de falha
- Operações que cruzam módulos (como emitir certificados a partir dos
  resumos de frequência) passam a exigir comunicação entre serviços, por
  chamadas síncronas pela rede ou por eventos com consistência eventual
- Exige infraestrutura a mais: gateway, monitoramento distribuído, vários
  bancos de dados
- Custo de desenvolvimento e operação alto para uma equipe pequena (~4
  pessoas)

## Comparação

| Critério | A: Monólito simples | B: Monólito modular | C: Microsserviços |
|---|---|---|---|
| Modificabilidade | Baixa | Alta | Alta |
| Desempenho | Alto | Alto | Médio |
| Disponibilidade | Média | Média | Alta |
| Testabilidade | Baixa a Média | Alta | Média a Alta |
| Complexidade | Baixa | Média | Alta |
| Implantação | Simples | Simples | Complexa |
| Escalabilidade | Média | Média a Alta | Alta |
| Custo de desenvolvimento e operação | Baixo | Baixo a Médio | Alto |

**Modificabilidade**
- A: sem fronteiras entre módulos, uma mudança pode se espalhar pelo
  código
- B: as mudanças ficam dentro de um módulo, e os outros dependem só das
  interfaces dele
- C: igual a B, mas mudanças que cruzam serviços exigem coordenar
  versões das APIs

**Desempenho**
- A e B: chamadas entre módulos são chamadas de método, sem custo de rede
- C: cada chamada entre serviços adiciona latência de rede, a emissão de
  certificados, por exemplo, depende de dados de `projetos` e `identidade`

**Disponibilidade**
- A e B: uma falha na aplicação afeta tudo, isso é reduzido rodando várias
  instâncias, o que é possível porque o servidor não guarda sessão
- C: falhas ficam isoladas por serviço, mas há mais componentes que podem
  falhar
- Nas três, se o provedor de identidade estiver indisponível, não é
  possível entrar no sistema, pois é um sistema externo

**Testabilidade**
- A: os testes tendem a depender de mais partes do sistema
- B: cada módulo pode ser testado isoladamente, com implementações de teste
  das interfaces (ex.: `ProvedorIdentidadeTeste`, `GeradorDocumentoTeste`)
- C: cada serviço é testável sozinho, mas os testes de integração exigem
  subir vários serviços

**Complexidade e implantação**
- A: uma aplicação e um banco de dados
- B: uma aplicação e um banco de dados, com os módulos separados dentro do
  código e cada módulo com as próprias tabelas
- C: vários serviços, bancos e a infraestrutura entre eles

**Escalabilidade**
- A e B: escalam replicando a aplicação inteira atrás de um balanceador de
  carga, e a fila no banco de dados absorve os picos de escrita
- C: cada serviço escala separadamente, conforme a própria carga

**Custo de desenvolvimento e operação**
- A: o menor no início, mas a manutenção fica mais cara com o tempo
- B: um pouco maior que A, pela organização em módulos, mas a manutenção
  fica mais barata
- C: o maior, pela infraestrutura e pela equipe necessária para operar e
  manter os serviços

## Relação com os ASRs

**ASR01 Escalabilidade e disponibilidade** (4.000 acessos simultâneos,
RNF01 e RNF02)
- Em A e B, a carga esperada não exige escalar partes do sistema
  separadamente, e basta rodar várias instâncias do sistema inteiro
- Em B, o servidor sem sessão pode rodar em várias instâncias, o que
  atende à escalabilidade e à disponibilidade de 99,5%
- C escalaria melhor por serviço, mas a rede entre os serviços dificulta o
  limite de 1s das consultas
- As escritas assíncronas pela fila podem absorver os picos de acesso

**ASR02 Integração institucional**
- As três alternativas integram o login institucional da mesma forma
- Em B, a integração fica isolada atrás de `ProvedorIdentidade`, no módulo
  `identidade`

**ASR03 Manutenibilidade e evolução**
- É o ASR que mais diferencia A de B
- Em B, as regras de certificação ficam em `CriterioCertificacao`, e novos
  critérios não alteram os outros módulos
- C também atende, mas com um custo de operação que não se justifica pelo
  tamanho do sistema (com poucas funcionalidades)

## Decisão

O Monólito Modular (B) foi escolhido por equilibrar os três ASRs:
- Atende ao ASR01 com várias instâncias da mesma aplicação e com a fila de
  escritas, sem a latência e o custo de operação dos microsserviços
- Atende ao ASR02 isolando o login institucional atrás de uma interface do
  domínio (inversão de dependência)
- Atende ao ASR03 melhor que o monólito simples, pelas fronteiras entre os
  módulos, que limitam o impacto das mudanças e facilitam a evolução
- Mantém aberta a migração para microsserviços, já que um módulo pode ser
  separado se a carga ou a equipe crescerem
