# Gestão de projetos de extensão

Sistema interno de uma universidade federal para cadastrar projetos de
extensão, participantes e atividades, registrar presenças e acompanhar as
horas e os requisitos para a emissão de certificados.

O repositório reúne a documentação, os diagramas, as decisões
arquiteturais e um protótipo funcional em Java.

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
