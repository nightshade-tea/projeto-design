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
  (`ATIVO` | `ENCERRADO`), `atividades`, `participacoes`
- Responsabilidades:
  - criar o projeto com um professor como coordenador
    (`new Projeto(titulo, descricao, coordenador): Projeto`)
  - informar se um usuário pode gerenciar o projeto, sendo o coordenador
    ou um administrador (`podeGerenciar(usuario)`)
  - editar os próprios dados (`editarTitulo(titulo)`, etc.)
  - encerrar o projeto (`encerrar()`)
    - depois de encerrado, o projeto não aceita mais alterações
  - criar, editar e remover atividades
  - publicar o evento `AtividadeRemovida` ao remover uma atividade
  - vincular e desvincular alunos
    (`vincular(aluno)`, `desvincular(aluno)`)
    - desvincular só encerra a participação, sem apagar o registro
  - informar se um aluno estava vinculado em uma data
    (`vinculado(aluno, data)`)
  - publicar o evento `ProjetoEncerrado` ao ser encerrado

**Atividade** (objeto)
- Atributos: `titulo`, `descricao`, `data`, `cargaHoraria`
- Responsabilidade:
  - manter os próprios dados

**Participacao** (objeto)
- Atributos: `aluno`, `inicio`, `fim`
- Responsabilidades:
  - encerrar a participação (`encerrar()`)
  - informar se está ativa em uma data (`ativaEm(data)`)

**ProjetoEncerrado** (evento de domínio): `projeto`. Permite que
`certificacao` reaja ao encerramento sem que `projetos` dependa dela.

**AtividadeRemovida** (evento de domínio): `atividade`. Permite que
`frequencia` exclua a lista de presença da atividade removida.

### Módulo `frequencia`

**ListaPresenca** (objeto)
- Uma por atividade
- Atributos: `atividade`, `projeto`, `presentes` (alunos presentes)
- Responsabilidades:
  - registrar a presença de um participante
    (`registrar(aluno)`)
    - recusa alterações se o projeto estiver encerrado ou para
      alunos não vinculados na data da atividade
  - remover uma presença registrada por engano (`remover(aluno)`)
  - informar se um aluno esteve presente (`estevePresente(aluno)`)

**ApuracaoFrequencia** (serviço de domínio)
- `apurar(participacao, atividades, listas): ResumoFrequencia`
- Soma a carga horária das atividades em que o aluno esteve presente
- Conta as atividades realizadas no projeto e as presenças do aluno,
  considerando só as atividades dentro do período da participação

**ResumoFrequencia** (objeto)
- Atributos: `aluno`, `projeto`, `horasCumpridas`, `qtdPresencas`,
  `qtdAtividades`
- Responsabilidades:
  - informar o percentual de presença (`percentualPresenca()`)
- É usado na consulta de horas e na avaliação de certificação

### Módulo `certificacao`

**PoliticaCertificacao** (objeto)
- Atributos: `projeto`, `criterios` (lista de `CriterioCertificacao`),
  `bloqueada`
- Responsabilidades:
  - definir os critérios, recusando a alteração se `bloqueada`
    (`definirCriterios(criterios)`)
  - avaliar o resumo de frequência de um aluno e informar se atende a
    todos os critérios (`avaliar(resumo): boolean`)
  - emitir o certificado de quem atende os critérios
    (`emitir(resumo): Certificado`)
  - bloquear os critérios quando o projeto é encerrado (`bloquear()`)

**CriterioCertificacao** (interface)
- `avaliar(resumo): boolean`
- Implementações disponibilizadas pelo sistema
  - `MinimoHoras(cargaHoraria)`
  - `PercentualMinimoPresenca(pct)`

**Certificado** (objeto)
- Atributos: `projeto`, `aluno`, `nomeAluno`, `tituloProjeto`,
  `cargaHoraria`, `emitidoEm`
- Responsabilidade:
  - responder se pertence a um usuário (`pertenceA(usuario)`)
- Guarda uma cópia dos dados do momento da emissão, de modo que alterações
  posteriores no projeto não mudam um certificado já emitido

**GeradorDocumentoCertificado** (interface)
- `gerar(certificado): bytes`: produz o arquivo que o aluno baixa
- Implementações: `GeradorPdf` e `GeradorDocumentoTeste`

**EmissaoCertificados** (serviço de domínio)
- `emitirCertificados(projeto): Certificado[]`
- Para cada participante, inclusive os desvinculados, apura a frequência,
  avalia pela política e emite o certificado de quem atende os critérios
- Acionado pelo evento `ProjetoEncerrado`, que também bloqueia a política
- Não emite certificados para projetos sem critérios definidos

### Agregados

- `Projeto` (com `Atividade` e `Participacao`)
- `ListaPresenca`
- `PoliticaCertificacao`
- `Certificado`

Cada agregado é alterado e salvo como uma unidade

### Repositórios

- `ProjetoRepositorio`
- `ListaPresencaRepositorio`
- `PoliticaCertificacaoRepositorio`
- `CertificadoRepositorio`

São interfaces, e as implementações ficam fora do domínio

## Justificativas GRASP

**Information Expert**
- Cada objeto responde com os dados que já possui: `Projeto.podeGerenciar`,
  `Projeto.vinculado`, `Participacao.ativaEm`, `ListaPresenca.estevePresente`,
  `ResumoFrequencia.percentualPresenca` e `Certificado.pertenceA`

**Creator**
- `Projeto` cria `Atividade` e `Participacao`, pois as contém
- `PoliticaCertificacao` cria `Certificado`, pois recebe o resumo de
  frequência, que tem o aluno, o projeto e as horas, e só emite para quem
  atende os critérios

**Pure Fabrication**
- `ApuracaoFrequencia` e `EmissaoCertificados` usam dados de mais de um
  agregado e não pertencem a nenhum deles
- Os repositórios separam a persistência dos objetos de domínio

**Polymorphism e Protected Variations**
- `CriterioCertificacao`: permite adicionar critérios
- `ProvedorIdentidade`: isola o login institucional
- `GeradorDocumentoCertificado`: isola o formato do arquivo gerado

**Indirection**
- Os eventos `ProjetoEncerrado` e `AtividadeRemovida` ligam os módulos sem
  que `projetos` dependa de `frequencia` ou `certificacao`

## Coesão e acoplamento

**Coesão**
- Cada módulo trata de um único assunto: identidade, projetos, frequência e
  certificação
- Apuração, avaliação e geração do arquivo do certificado ficam em classes
  separadas

**Acoplamento**
- As dependências seguem um único sentido: `certificacao` → `frequencia` →
  `projetos` → `identidade`
- Os eventos de domínio evitam dependências no sentido contrário
- Sistemas externos são acessados só por interfaces

**Pontos de atenção**
- `Projeto` concentra muitas responsabilidades, o que é razoável já que ele
  garante que um projeto encerrado não seja alterado
- `ListaPresenca` consulta `Projeto` para validar o registro de presença
- `EmissaoCertificados` usa `projetos`, `frequencia` e `certificacao` e é o
  ponto de maior acoplamento, mantido isolado no serviço

## Princípios SOLID

**SRP (Single Responsibility Principle)**
- `ApuracaoFrequencia` apura, `PoliticaCertificacao` avalia e
  `GeradorDocumentoCertificado` gera o arquivo

**OCP (Open/Closed Principle)**
- Novos critérios são novas implementações de `CriterioCertificacao`, sem
  alterar `PoliticaCertificacao`

**LSP (Liskov Substitution Principle)**
- As implementações de cada interface podem ser trocadas entre si

**ISP (Interface Segregation Principle)**
- As interfaces são pequenas e específicas para cada uso

**DIP (Dependency Inversion Principle)**
- O domínio depende de interfaces (`ProvedorIdentidade`,
  `GeradorDocumentoCertificado` e repositórios), e as implementações ficam
  fora dele
