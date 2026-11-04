# Modelo de Domínio e Responsabilidades

## Conceitos e responsabilidades

### Módulo `identidade`

**Usuario** (objeto)
- Atributos: `matricula`, `nome`, `papel`
- Responsabilidades:
  - informar o próprio papel (`ehAluno()`, `ehProfessor()`,
    `ehAdministrador()`)
  - responder se pode criar projetos (`podeCriarProjeto()`)

**Papel** (enumeração): `ALUNO`, `PROFESSOR`, `ADMINISTRADOR`. O valor é
derivado do vínculo informado pelo provedor de identidade.

**ProvedorIdentidade** (interface)
- `identificar(token): Usuario`: valida o token recebido do login
  institucional e devolve o usuário
- `buscarPorMatricula(matricula): Usuario`, usado para vincular alunos
- Implementações: `ProvedorIdentidadeInstitucional` e `ProvedorIdentidadeTeste`

### Módulo `projetos`

**Projeto** (objeto)
- Atributos: `titulo`, `descricao`, `coordenador`, `status`
  (`ATIVO` | `ENCERRADO`), `atividades`, `participacoes`, `criterios`
  (`CriteriosCertificacao`)
- Responsabilidades:
  - criar o projeto com um professor como coordenador
    (`new Projeto(titulo, descricao, coordenador): Projeto`)
  - editar e encerrar o projeto (`encerrar()`)
    - depois de encerrado, o projeto não aceita mais alterações
  - gerenciar atividades, participantes e critérios
    - remover uma atividade remove também as presenças dela
    - desvincular um aluno só encerra a participação
  - registrar e remover presenças, recusando alunos não vinculados na data
    da atividade (`vinculado(aluno, data)`)
  - informar a frequência de um aluno e os aprovados, inclusive os
    desvinculados (`resumoFrequencia(aluno)`, `aprovados()`), calculados por
    `Participacao` e `CriteriosCertificacao`

**Atividade** (objeto)
- Atributos: `titulo`, `descricao`, `data`, `cargaHoraria`, `presentes`
- Responsabilidades:
  - manter os próprios dados
  - registrar e remover a presença de um aluno
    (`registrarPresenca(aluno)`, `removerPresenca(aluno)`)
  - informar se um aluno esteve presente (`estevePresente(aluno)`)

**Participacao** (objeto)
- Atributos: `aluno`, `inicio`, `fim`
- Responsabilidades:
  - encerrar a participação (`encerrar()`)
  - informar se está ativa em uma data (`ativaEm(data)`)
  - apurar a própria frequência
    (`resumoFrequencia(projeto, atividades): ResumoFrequencia`)
    - soma a carga horária e conta as atividades e presenças, considerando
      só as atividades dentro do período da participação

**ResumoFrequencia** (objeto)
- Atributos: `aluno`, `projeto`, `horasCumpridas`, `qtdPresencas`,
  `qtdAtividades`
- Responsabilidades:
  - informar o percentual de presença (`percentualPresenca()`)
- É usado na consulta de horas e na emissão de certificados

**CriteriosCertificacao** (objeto)
- Atributos: `criterios` (lista de `CriterioCertificacao`)
- Responsabilidades:
  - substituir os critérios (`definir(criterios)`)
  - informar se um resumo atende a todos os critérios
    (`atende(resumo): boolean`)
    - sem critérios definidos, nenhum resumo atende

**CriterioCertificacao** (interface)
- `avaliar(resumo): boolean`
- Implementações disponibilizadas pelo sistema
  - `MinimoHoras(cargaHoraria)`
  - `PercentualMinimoPresenca(pct)`

### Módulo `certificacao`

**Certificado** (objeto)
- Atributos: `projeto`, `aluno`, `nomeAluno`, `tituloProjeto`,
  `cargaHoraria`, `emitidoEm`
- Responsabilidades:
  - ser criado a partir do resumo de frequência de um aluno aprovado
    (`new Certificado(resumo): Certificado`)
  - responder se pertence a um usuário (`pertenceA(usuario)`)
- Guarda uma cópia dos dados do momento da emissão, de modo que alterações
  posteriores no projeto não mudam um certificado já emitido

**GeradorDocumentoCertificado** (interface)
- `gerar(certificado): bytes`: produz o arquivo que o aluno baixa
- Implementações: `GeradorPdf` e `GeradorDocumentoTeste`

### Agregados

- `Projeto` (com `Atividade`, `Participacao` e `CriteriosCertificacao`)
- `Certificado`

Cada agregado é alterado e salvo como uma unidade

### Repositories

- `ProjetoRepository`
- `CertificadoRepository`

São interfaces, e as implementações ficam fora do domínio

## Justificativas GRASP

**Information Expert**
- Cada objeto responde com os dados que já possui: `Projeto.vinculado`,
  `Participacao.ativaEm`, `Participacao.resumoFrequencia`,
  `Atividade.estevePresente`, `CriteriosCertificacao.atende`,
  `ResumoFrequencia.percentualPresenca` e `Certificado.pertenceA`

**Creator**
- `Projeto` cria `Atividade`, `Participacao` e `CriteriosCertificacao`, pois
  as contém
- `Certificado` é criado a partir de um resumo em `projeto.aprovados()`, que
  tem o aluno, o projeto e as horas

**Pure Fabrication**
- Os repositories não são conceitos do domínio e existem para separar a
  persistência dos objetos de domínio

**Polymorphism e Protected Variations**
- `CriterioCertificacao`: permite adicionar critérios
- `ProvedorIdentidade`: isola o login institucional
- `GeradorDocumentoCertificado`: isola o formato do arquivo gerado

**Indirection**
- As interfaces `ProvedorIdentidade`, `GeradorDocumentoCertificado` e os
  repositories ficam entre o domínio e as suas implementações

## Coesão e acoplamento

**Coesão**
- Cada módulo trata de um único assunto: identidade, projetos e
  certificação
- `Certificado` só guarda os dados da emissão, e a geração do arquivo fica
  em `GeradorDocumentoCertificado`

**Acoplamento**
- Os módulos dependem em um único sentido: `certificacao` → `projetos` →
  `identidade`
- Sistemas externos e persistência são acessados só por interfaces

**Pontos de atenção**
- `Projeto` é a entrada para alterar atividades, participantes, presenças e
  critérios, o que é razoável já que ele garante que um projeto encerrado
  não seja alterado
  - os cálculos ficam em `Participacao` e `CriteriosCertificacao`, e
    `Projeto` só verifica as regras e repassa

## Princípios SOLID

**SRP (Single Responsibility Principle)**
- `Projeto` mantém as regras do projeto, `Participacao` apura a frequência,
  `CriteriosCertificacao` avalia os critérios, `Certificado` guarda os dados
  da emissão e `GeradorDocumentoCertificado` gera o arquivo

**OCP (Open/Closed Principle)**
- Novos critérios são novas implementações de `CriterioCertificacao`, sem
  alterar `Projeto` nem `CriteriosCertificacao`

**LSP (Liskov Substitution Principle)**
- As implementações de cada interface podem ser trocadas entre si

**ISP (Interface Segregation Principle)**
- As interfaces são pequenas e específicas para cada uso

**DIP (Dependency Inversion Principle)**
- O domínio define as interfaces (`ProvedorIdentidade`,
  `GeradorDocumentoCertificado` e repositories) e não depende das
  implementações
