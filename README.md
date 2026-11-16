# Sistema de Gestão de Projetos de Extensão

Sistema desenvolvido para gerenciar as etapas e operações de projetos de
extensão em uma universidade federal, desde o cadastro de projetos, atividades
e participantes até o registro de presenças, apuração automática de carga
horária e emissão de certificados em PDF.

Projetado para atender aproximadamente **~42.500 usuários** com suporte a
picos de até **4.000 acessos simultâneos**.

O repositório reúne a documentação, os diagramas, as decisões arquiteturais e
um protótipo funcional em Java.


## Principais Funcionalidades

- **Gestão de Projetos e Atividades:** Criação e administração de projetos de
  extensão por docentes coordenadores, com controle de estados (`ATIVO` /
  `ENCERRADO`) e cronograma de atividades.
- **Controle de Participação e Frequência:** Vínculo de discentes por matrícula
  institucional, registro de presenças por atividade e cálculo de carga horária
  e percentual de frequência.
- **Certificação Automatizada:** Definição flexível de critérios de aprovação
  (como carga horária mínima e/ou percentual mínimo de presença) e emissão
  assíncrona de certificados em PDF ao encerrar o projeto.
- **Integração Institucional:** Autenticação delegada ao provedor de identidade
  único da universidade, com atribuição automática de perfis (`Aluno`,
  `Professor` e `Administrador`).


## Visão Geral da Arquitetura

- **Estilo Arquitetural:** Cliente-servidor + Monólito Modular + camadas
  (`Controllers -> Services -> Domínio`), com dependências unidirecionais
  voltadas para o domínio.
- **Separação de Domínio:** Dividido em três módulos (`certificacao ->
  projetos -> identidade`) com isolamento lógico interno.
- **Processamento Assíncrono e Idempotência:** Operações de escrita são
  validadas de forma síncrona e enfileiradas no próprio banco de dados para
  absorver picos de acesso sem adicionar complexidade de infraestrutura
  distribuída.


## Documentação

- [Requisitos](docs/requisitos.md): contexto, atores, requisitos funcionais
  e não funcionais e regras de negócio
- [Domínio](docs/dominio.md): modelo de domínio e regras
- [Arquitetura](docs/arquitetura.md): organização, camadas, módulos,
  comunicação, persistência, integrações e API
- [Alternativas e trade-offs](docs/alternativas.md)
- [Decisões arquiteturais (ADRs)](docs/adr/README.md)
- [Análise de evolução](docs/evolucao.md)

## Diagramas

- [Arquitetura](docs/img/arquitetura.svg)
- [Classes](docs/diagramas/classes.svg)
- [Pacotes](docs/diagramas/pacotes.svg)
- [Componentes](docs/diagramas/componentes.svg)
- [Sequência](docs/diagramas/sequencia.svg), com um diagrama por caso de uso
  em [`sequencia/`](docs/diagramas/sequencia)
- [Comunicação](docs/diagramas/comunicacao.svg), com um diagrama por caso de
  uso em [`comunicacao/`](docs/diagramas/comunicacao)

Os diagramas são gerados pelos scripts em [`scripts/`](scripts).

## Protótipo

O código-fonte e os testes estão em [`src/`](src). É preciso só o JDK 21 ou
mais novo:

```
make run       # cliente web em http://localhost:8080
make test      # testes
make cenario   # reproduz o diagrama de sequência completo
```

## Licença

[GPL-3.0](LICENSE)
