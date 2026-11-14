# Arquitetura

## Organização arquitetural

```
Cliente-servidor
+
Monólito modular
+
Organização em camadas
```

- **Cliente-servidor**: o cliente (navegador) acessa o servidor por REST/HTTPS
- **Monólito modular**: o servidor é implantado como uma única aplicação,
  dividida nos módulos do domínio (`identidade`, `projetos` e
  `certificacao`)
- **Camadas**: o código é organizado em camadas, e as dependências apontam
  para o domínio

Com uma equipe pequena e a carga esperada, um monólito modular é mais simples
de manter do que serviços separados. Os módulos e as interfaces do domínio
permitem separar um módulo no futuro, se for necessário, o que mantém o
sistema escalável

## Diagrama

![Diagrama da arquitetura](img/arquitetura.svg)


## Camadas

- **Controllers** (`...Controller`): recebem as requisições do cliente,
  identificam o usuário e chamam um service ou colocam a escrita na fila
- **Services** (`...Service`): executam os casos de uso; buscam os objetos no
  repository, chamam o domínio e salvam o resultado
- **Domínio**: objetos e regras de negócio, descritos em
  `dominio.md`
- **Interfaces e Implementações**: interfaces e implementações dos
  repositories, do login institucional e da geração do arquivo do
  certificado

### Controllers

Todos recebem as requisições do cliente e identificam o usuário com
`AutenticacaoService`, sem regras de negócio
- consultas chamam o service e respondem na hora
- escritas chamam o service, que verifica permissão e regras na hora, se a
  escrita for aceita, ela entra na fila e a resposta é `202 Accepted`

**ProjetoController**
- requisições sobre projetos, atividades, participantes e critérios
  - chama `ProjetoService`
- requisição de encerramento do projeto
  - chama `EncerramentoService`

**FrequenciaController**
- requisições de registro e remoção de presenças e de consulta de horas
  - chama `FrequenciaService`

**CertificadoController**
- requisições de listagem e download de certificados
  - chama `CertificadoService`

**AutenticacaoController**
- início do login, que redireciona o navegador para o login institucional
- requisição de consulta do usuário logado, com nome e papel
  - chama `AutenticacaoService`

### Services

**ProjetoService**
- criar, editar e consultar projetos
- gerenciar atividades, participantes e critérios
  - busca o aluno a vincular com `ProvedorIdentidade.buscarPorMatricula`
- recusa (`409`) a vinculação de uma matrícula que não é de um `Aluno`
- só aceita a criação de projetos por um `Professor` ou `Administrador`
- só aceita alterações do coordenador do projeto ou de um administrador
  (`projeto.podeGerenciar(usuario)`)

**EncerramentoService**
- encerrar o projeto e emitir os certificados, em duas operações da fila
  - a primeira encerra e salva o projeto, e coloca a emissão na fila
  - a emissão cria e salva um `Certificado` para cada resumo em
    `projeto.aprovados()` que ainda não tem certificado
    (`CertificadoRepository.existe(projeto, aluno)`)
- só aceita o coordenador do projeto ou um administrador
  (`projeto.podeGerenciar(usuario)`)

**FrequenciaService**
- registrar e remover presenças
  - busca o aluno com `ProvedorIdentidade.buscarPorMatricula` e a
    atividade com `projeto.atividade(atividadeId)`
  - recusa (`409`) uma matrícula que não é de um `Aluno`
- consultar as horas do aluno, por projeto (`projeto.resumoFrequencia`) e
  no total (soma das horas dos resumos), e as horas de todos os
  participantes para o coordenador (`projeto.resumos()`)
- só o coordenador do projeto ou um administrador registra presenças e
  consulta as horas de todos os participantes
  (`projeto.podeGerenciar(usuario)`)

**CertificadoService**
- listar os certificados do aluno
- gerar o arquivo para download com `GeradorDocumentoCertificado`
  - só entrega certificados que pertencem ao usuário (`pertenceA(usuario)`),
    e responde `404` se o certificado não existe e `403` se não pertence

**AutenticacaoService**
- obter o endereço do login institucional, com
  `ProvedorIdentidade.urlLogin()`
- identificar o usuário a partir do token, com
  `ProvedorIdentidade.identificar(token)`
  - usado por todos os controllers no início de cada requisição
- recusar tokens ausentes ou inválidos (`401`), e o cliente então direciona
  o usuário para o login institucional

### Implementações

- `ProjetoRepositorySql` e `CertificadoRepositorySql`, implementações dos
  repositories, que acessam o banco de dados
- `ProvedorIdentidadeInstitucional`, que acessa o login da universidade e
  guarda a cópia local dos usuários
- `GeradorPdf`, que gera o arquivo do certificado

## Módulos no Domínio

- **`identidade`**: usuários (`Aluno`, `Professor` e `Administrador`),
  obtidos do provedor de identidade
- **`projetos`**: projetos, atividades, participantes, presenças, critérios
  de certificação e apuração da frequência
- **`certificacao`**: certificados emitidos e geração do arquivo para
  download

## Dependências

- Entre camadas: controllers → services → domínio
- Entre implementações e domínio: as implementações dependem das
  interfaces definidas no domínio
- Entre módulos: `certificacao` -> `projetos` -> `identidade`, e
  `certificacao` -> `identidade` (`Certificado` usa `Aluno` e `Usuario`).

## Interfaces relevantes

- `ProvedorIdentidade`: identificação dos usuários pelo login institucional
  - implementações: `ProvedorIdentidadeInstitucional` e
    `ProvedorIdentidadeTeste`
- `ProjetoRepository` e `CertificadoRepository`: salvar e buscar os
  agregados
  - implementações: `ProjetoRepositorySql` e `CertificadoRepositorySql`
- `GeradorDocumentoCertificado`: geração do arquivo do certificado
  - implementações: `GeradorPdf` e `GeradorDocumentoTeste`
- `CriterioCertificacao`: critérios de certificação, usada só dentro do
  domínio

## Comunicação

**Mecanismos**
- Cliente → servidor: requisições HTTPS para uma API REST, com dados em JSON
  - o arquivo do certificado é devolvido em PDF
- Dentro do servidor: chamadas de método entre camadas e módulos, na mesma
  aplicação
- Servidor → banco de dados: pelas implementações dos repositories e de
  `ProvedorIdentidade` (cópia local dos usuários)
- Servidor → provedor de identidade: pela implementação de
  `ProvedorIdentidade`
- Fila: uma tabela no banco de dados, lida da mesma aplicação,
  que chamam os services

**Decisões**
- A comunicação entre módulos não precisa de eventos, por ser um monólito
- A autenticação é síncrona, pois o restante da requisição depende dela
- Consultas são síncronas
- Escritas são assíncronas: depois da autenticação e da verificação de
  permissão e regras, entram na fila e são processadas, o que
  absorve os picos de acesso
  - como os erros são devolvidos antes de a escrita entrar na fila, o
    cliente não precisa consultar o resultado depois
  - se o estado mudar antes da execução (ex.: o projeto ser encerrado nesse
    meio-tempo), são verificadas as regras de novo e descarta a escrita
  - a fila fica no próprio banco de dados, sem um serviço a mais para
    operar
  - uma operação que falha é tentada de novo, por isso as escritas são
    idempotentes (ver Persistência)
- A emissão dos certificados é uma operação separada do encerramento, para
  não atrasar as outras operações da fila
- O servidor não guarda sessão, cada requisição envia o token do login
  institucional, validado pelo `AutenticacaoService`
- O cliente só conversa com os controllers, e nunca com o banco de dados ou
  o provedor de identidade, o servidor só inicia o login, redirecionando o
  navegador para a página de login institucional

## Persistência

- Banco de dados, compartilhado pelos módulos
  - cada módulo tem as próprias tabelas, e um módulo não acessa as tabelas
    de outro
- Um repository por agregado, e cada agregado é salvo como uma unidade
- Cada operação salva os dados em uma transação
  - ao encerrar um projeto, o projeto é salvo primeiro, e os certificados
    são emitidos em outra operação, se a emissão falhar, ela é tentada de
    novo sem duplicar certificados
- O arquivo do certificado não é guardado, ele é gerado a cada download a
  partir dos dados salvos em `Certificado`
- Usuários vem do provedor de identidade


**Idempotência**
- A matrícula é a chave do usuário: salvar um usuário que já existe atualiza
  a cópia em vez de criar outra, então repetir um login ou uma busca não
  duplica dados
- Escritas que podem ser repetidas (pela fila ou pelo cliente reenviando a
  requisição) não têm efeito duplicado
  - registrar uma presença já registrada não cria outra
  - encerrar um projeto já encerrado é recusado, e há no máximo um
    certificado por aluno e projeto

## Integrações externas

**Provedor de identidade institucional**
- O servidor redireciona o navegador para o serviço de login único da
  universidade (`urlLogin()`), depois do login, o serviço gera o token e
  devolve o navegador ao cliente com ele
- O servidor valida o token a cada requisição (`identificar(token)`), só
  para confirmar a sessão e saber de qual usuário ela é
- O papel do usuário não vem do token: é a subclasse de `Usuario` (`Aluno`,
  `Professor` ou `Administrador`), definida pelo vínculo quando o usuário é
  obtido do provedor e guardada na cópia local
- O servidor busca alunos pela matrícula para vinculá-los a projetos
  (`buscarPorMatricula(matricula)`)
- Se o provedor estiver indisponível, não é possível entrar no sistema nem
  vincular alunos que ainda não estão na cópia local
- Nos diagramas de sequência e de comunicação, a validação do token no
  login institucional (`validar(token)`) e a resposta `401` aparecem só no
  login e no cenário completo; nos diagramas por caso de uso,
  `identificar(token)` é mostrado devolvendo o usuário, para não repetir
  esse trecho em todos eles

## API

Todas as rotas, exceto `GET /login`, exigem o token no cabeçalho
`Authorization: Bearer <token>`. Consultas (`GET`) respondem com os dados,
escritas respondem `202 Accepted` depois de verificadas, e são salvas em
seguida pela fila.

**Projetos** (`ProjetoController`)
- `GET` e `POST /projetos`: listar e criar projetos
- `GET` e `PUT /projetos/{id}`: consultar e editar um projeto
- `POST /projetos/{id}/encerramento`: encerrar o projeto e emitir os
  certificados
- `POST /projetos/{id}/atividades`: cadastrar uma atividade
- `PUT` e `DELETE /projetos/{id}/atividades/{atividadeId}`: editar e remover
  uma atividade
- `POST /projetos/{id}/participantes`: vincular um aluno pela matrícula
- `DELETE /projetos/{id}/participantes/{matricula}`: desvincular um aluno
- `PUT /projetos/{id}/criterios`: definir os critérios de certificação

**Frequência** (`FrequenciaController`)
- `POST /projetos/{id}/atividades/{atividadeId}/presencas`: registrar
  presença pela matrícula
- `DELETE /projetos/{id}/atividades/{atividadeId}/presencas/{matricula}`:
  remover uma presença
- `GET /projetos/{id}/horas` e `GET /me/horas`: horas dos participantes, para
  o coordenador, e as do próprio aluno

**Certificados** (`CertificadoController`)
- `GET /me/certificados`: listar os certificados do aluno
- `GET /certificados/{id}/arquivo`: baixar o certificado em PDF

**Usuário** (`AutenticacaoController`)
- `GET /login`: redireciona (`302`) para o login institucional
- `GET /me`: usuário logado, com nome e papel

**Erros**
- `401` token ausente ou inválido, `403` sem permissão, `404` não
  encontrado e `409` recusado por uma regra de negócio (ex.: alterar um
  projeto encerrado)
- Todos os erros são devolvidos na própria requisição, antes de a escrita
  entrar na fila
