# Sistema de Gestão de Projetos de Extensão

Sistema desenvolvido para gerenciar as etapas e operações de projetos de
extensão em uma universidade federal, desde o cadastro de projetos, atividades
e participantes até o registro de presenças, apuração automática de carga
horária e emissão de certificados em PDF.

Projetado para cerca de 42.500 usuários, com picos de até 4.000 acessos
simultâneos.

O repositório reúne a documentação, os diagramas, as decisões arquiteturais e
um protótipo funcional em Java.


## Principais funcionalidades

- Gestão de projetos e atividades: o professor cria o projeto e passa a ser
  o coordenador, cadastra as atividades e encerra o projeto (estados `ATIVO`
  e `ENCERRADO`)
- Participação e frequência: vínculo de alunos pela matrícula
  institucional, registro de presenças por atividade e cálculo da carga
  horária e do percentual de presença
- Certificação: o coordenador escolhe os critérios de aprovação (carga
  horária mínima e percentual mínimo de presença), e os certificados são
  emitidos ao encerrar o projeto
- Login institucional: a autenticação fica com o provedor de identidade da
  universidade, que também define o papel do usuário (`Aluno`, `Professor`
  ou `Administrador`)


## Visão geral da arquitetura

- Cliente-servidor + monólito modular + camadas (`controllers -> services
  -> domínio`), com as dependências apontando para o domínio
- O domínio é dividido em três módulos, com dependências em um único
  sentido (`certificacao -> projetos -> identidade`)
- As escritas são validadas na requisição e depois executadas por uma fila
  no próprio banco de dados, para absorver os picos de acesso sem um serviço
  de fila separado


## Documentação

- [Requisitos](docs/requisitos.md): contexto, atores, requisitos funcionais
  e não funcionais e regras de negócio
- [Domínio](docs/dominio.md): modelo de domínio e regras
- [Arquitetura](docs/arquitetura.md): organização, camadas, módulos,
  comunicação, persistência, integrações e API
- [Alternativas e trade-offs](docs/alternativas.md)
- Decisões arquiteturais (ADRs):
  - [ADR 001: Monólito modular](docs/adr/001-monolito-modular.md)
  - [ADR 002: Uso de camadas](docs/adr/002-camadas.md)
  - [ADR 003: Integração com o provedor de identidade](docs/adr/003-integracao-provedor-identidade.md)
- [Análise de evolução](docs/evolucao.md)

## Diagramas

- [Arquitetura](docs/diagramas/arquitetura.svg)
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

Os usuários e senhas do login institucional simulado estão em
[`usuarios.csv`](src/institucional/resources/usuarios.csv) (ex.: `carla` /
`sapato` é professora, `ana` / `sapato` é aluna).

### Organização do código

- `src/extensao/servidor`: o servidor, com os pacotes `controllers`,
  `services`, `dominio` (`identidade`, `projetos` e `certificacao`) e
  `infraestrutura`, como no [diagrama de pacotes](docs/diagramas/pacotes.svg)
- `src/extensao/cliente`: o cliente web, que só chama a API do servidor
- `src/institucional`: o login institucional simulado (sistema externo), um
  programa separado que o servidor acessa só por HTTP

### Fatia vertical implementada

- Casos de uso que modificam o estado: criar projeto, vincular aluno,
  cadastrar e editar atividades, registrar presença, definir critérios e
  encerrar o projeto com a emissão dos certificados
- Consultas: horas do aluno, horas dos participantes, projetos e
  certificados
- Fluxos alternativos e erros: token inválido (`401`), usuário sem permissão
  (`403`), matrícula ou projeto inexistente (`404`), presença de aluno não
  vinculado, matrícula que não é de aluno e alteração de projeto encerrado
  (`409`)
- Persistência: arquivos CSV na pasta `dados/`, atrás das interfaces
  `ProjetoRepository` e `CertificadoRepository`
- Dependência externa substituível: o login institucional, atrás de
  `ProvedorIdentidade` (`ProvedorIdentidadeInstitucional` no servidor e
  `ProvedorIdentidadeTeste` nos testes)

### Simplificações em relação à arquitetura documentada

A documentação descreve o sistema em produção. O protótipo mantém as mesmas
interfaces, camadas e módulos, mas:
- usa `ProjetoRepositoryCsv` e `CertificadoRepositoryCsv` no lugar do banco
  de dados (`...RepositorySql`)
- gera o certificado em texto (`GeradorTxt`) no lugar do PDF (`GeradorPdf`)
- executa as escritas na própria requisição, sem a fila. A resposta continua
  sendo `202 Accepted`, e a emissão dos certificados acontece junto com o
  encerramento
- o cliente web guarda o token em um cookie (rotas `/sessao` e `/sair`), além
  do cabeçalho `Authorization` da API

Trocar uma dessas implementações muda só a infraestrutura e a montagem em
[`ServidorExtensao`](src/extensao/servidor/java/extensao/ServidorExtensao.java).

## Licença

[GPL-3.0](LICENSE)
