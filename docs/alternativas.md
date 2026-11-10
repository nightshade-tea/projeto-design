# Alternativas e trade-offs

> Rascunho para revisão do grupo. Os valores da comparação são estimativas
> qualitativas e devem ser conferidos.

Além da solução escolhida (monólito modular, ver `arquitetura.md`), foram
analisadas duas alternativas. As três usam cliente-servidor, API REST e o
login institucional; a diferença está em como o servidor é dividido e
implantado.

## Alternativas

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
- Separar uma parte no futuro exige primeiro reorganizar o código

### B: Monólito modular (escolhida)

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
- Todos os módulos escalam juntos: não é possível dar mais recursos só à
  parte mais usada
- Uma falha grave na aplicação afeta todos os módulos

### C: Microsserviços

Um serviço por módulo (`identidade`, `projetos` e `certificacao`), cada um
com o próprio banco de dados, implantados separadamente e comunicando-se
pela rede (HTTP ou mensagens), com um gateway na frente.

**Vantagens**
- Cada serviço escala e é implantado de forma independente
- Uma falha em um serviço (ex.: certificação) não derruba os outros
- As fronteiras entre os módulos são garantidas pela própria divisão

**Desvantagens**
- Chamadas entre serviços passam pela rede, com mais latência e mais
  pontos de falha
- Consultas que cruzam módulos (ex.: emitir certificados a partir dos
  resumos de frequência) passam a exigir comunicação entre serviços e
  consistência eventual
- Exige infraestrutura a mais: gateway, descoberta de serviços,
  monitoramento distribuído, vários bancos de dados
- Custo de desenvolvimento e operação alto para uma equipe pequena

## Comparação

| Critério | A: Monólito simples | B: Monólito modular | C: Microsserviços |
|---|---|---|---|
| Modificabilidade | Baixa a média | Alta | Alta |
| Desempenho | Alto | Alto | Médio |
| Disponibilidade | Média | Média | Alta |
| Testabilidade | Média | Alta | Média |
| Complexidade | Baixa | Média | Alta |
| Implantação | Simples | Simples | Complexa |
| Escalabilidade | Média | Média a alta | Alta |
| Custo de desenvolvimento e operação | Baixo | Baixo a médio | Alto |

**Modificabilidade**
- A: sem fronteiras entre módulos, uma mudança pode se espalhar pelo código
- B: as mudanças ficam dentro de um módulo, e os outros dependem só das
  interfaces dele
- C: igual a B, mas mudanças que cruzam serviços exigem coordenar
  versões das APIs

**Desempenho**
- A e B: chamadas entre módulos são chamadas de método, sem custo de rede
- C: cada chamada entre serviços adiciona latência de rede; a emissão de
  certificados, por exemplo, depende de dados de `projetos` e `identidade`

**Disponibilidade**
- A e B: uma falha na aplicação afeta tudo; isso é reduzido rodando várias
  instâncias, o que é possível porque o servidor não guarda sessão
- C: falhas ficam isoladas por serviço, mas há mais componentes que podem
  falhar
- Nas três, se o provedor de identidade estiver indisponível, não é
  possível entrar no sistema

**Testabilidade**
- B: cada módulo pode ser testado isoladamente, com implementações de teste
  das interfaces (ex.: `ProvedorIdentidadeTeste`, `GeradorDocumentoTeste`)
- A: os testes tendem a depender de mais partes do sistema
- C: cada serviço é testável sozinho, mas os testes de integração exigem
  subir vários serviços

**Complexidade e implantação**
- A e B: uma aplicação e um banco de dados
- C: vários serviços, bancos e a infraestrutura entre eles

**Escalabilidade**
- A e B: escalam replicando a aplicação inteira atrás de um balanceador; a
  fila no banco de dados absorve os picos de escrita
- C: cada serviço escala separadamente, conforme a própria carga

**Custo de desenvolvimento e operação**
- A: o menor no início, mas cresce com a manutenção
- B: um pouco maior que A, pela organização em módulos
- C: o maior, pela infraestrutura e pela equipe necessária para operá-la

## Relação com os ASRs

**ASR01 Escalabilidade e Disponibilidade** (4.000 acessos simultâneos,
RNF01 e RNF02)
- A carga esperada não exige escalar partes do sistema separadamente; vale
  conferir essa suposição
- Em B, o servidor sem sessão pode rodar em várias instâncias, o que
  atende à escalabilidade e à disponibilidade de 99,5%
- As escritas assíncronas pela fila absorvem os picos de acesso
- C escalaria melhor por serviço, mas a rede entre os serviços dificulta o
  limite de 1 s das consultas

**ASR02 Integração Institucional**
- As três alternativas integram o login institucional da mesma forma
- Em B, a integração fica isolada atrás de `ProvedorIdentidade`, no módulo
  `identidade`

**ASR03 Manutenibilidade e Evolução**
- É o ASR que mais diferencia A de B
- Em B, as regras de certificação ficam em `CriterioCertificacao`, e novos
  critérios não alteram os outros módulos
- C também atende, mas com um custo de operação que não se justifica pelo
  tamanho do sistema

## Decisão

O monólito modular (B) foi escolhido por equilibrar os três ASRs:
- atende ao ASR01 com várias instâncias da mesma aplicação e com a fila de
  escritas, sem a latência e o custo de operação dos microsserviços
- atende ao ASR02 isolando o login institucional em uma interface
- atende ao ASR03 melhor que o monólito simples, pelas fronteiras entre os
  módulos
- mantém aberta a migração para microsserviços: um módulo pode ser separado
  se a carga ou a equipe crescerem
