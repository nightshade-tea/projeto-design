# Análise de evolução

Se uma das principais tecnologias ou integrações do sistema precisasse ser
substituída, quais partes seriam afetadas? Esta seção analisa três
mudanças possíveis

## 1. Banco de dados relacional → outro mecanismo de persistência

Ex.: trocar o banco relacional por um banco de documentos (como MongoDB)

**Elementos afetados**
- `ProjetoRepositorySql` e `CertificadoRepositorySql`, substituídos por
  novas implementações de `ProjetoRepository` e `CertificadoRepository`
- A cópia local dos usuários, guardada por `ProvedorIdentidadeInstitucional`
- A fila de escritas, que hoje é uma tabela no banco de dados: precisa de
  outro lugar para ficar (uma coleção no novo banco ou um serviço de fila)
- A garantia de que cada operação é salva em uma transação, se o novo
  mecanismo não tiver transações com a mesma garantia
- A montagem da aplicação, que escolhe as implementações

**Elementos inalterados**
- O domínio (`identidade`, `projetos` e `certificacao`), incluindo as
  interfaces dos repositories
- Os services e os controllers
- A API REST e o cliente web
- O provedor de identidade e a geração do certificado

**Decisões que ajudam**
- Repositories como interfaces no domínio, com as implementações na camada
  de infraestrutura: o domínio e os services não conhecem o banco
- Um repository por agregado, salvo como uma unidade: um agregado
  (`Projeto` com atividades, participações e critérios) vira um documento
  com naturalidade
- Cada módulo tem as próprias tabelas, sem acessar as de outro: os dados
  de cada módulo podem ser migrados separadamente
- Escritas idempotentes: a migração pode reprocessar operações sem duplicar
  dados

**Decisões que dificultam**
- A fila no próprio banco de dados: simplifica a operação, mas acopla a
  fila ao mecanismo de persistência, e ela precisa ser refeita junto
- Consultas que cruzam agregados (ex.: `listarPorAluno`, que busca os
  projetos de que o aluno participa) dependem de recursos do banco e
  precisam ser reescritas e testadas de novo

## 2. Login institucional → outro provedor de identidade

Ex.: a universidade troca o serviço de login único por um provedor OAuth
2.0/OpenID Connect, ou o sistema passa a aceitar o gov.br

**Elementos afetados**
- `ProvedorIdentidadeInstitucional`, substituído por uma nova implementação
  de `ProvedorIdentidade`
- O mapeamento do vínculo (aluno, professor, administrador) para a
  subclasse de `Usuario`, se o novo provedor informar o vínculo de outra
  forma
- A montagem da aplicação e a configuração (endereço do provedor,
  credenciais do sistema junto ao provedor)
- O cliente web, só se o fluxo de retorno do login mudar (ex.: receber um
  código e trocá-lo pelo token)

**Elementos inalterados**
- O domínio: o papel continua sendo a subclasse de `Usuario`, e a matrícula
  continua sendo a chave
- `AutenticacaoService` e os controllers, que só usam `urlLogin()` e
  `identificar(token)`
- Os services e as regras de permissão
- A persistência, os certificados e a API

**Decisões que ajudam**
- `ProvedorIdentidade` como interface no domínio, com três operações
  (`urlLogin`, `identificar` e `buscarPorMatricula`): é tudo o que o novo
  provedor precisa oferecer
- O servidor não guarda senhas nem sessão: não há credenciais para migrar
- O papel não vem do token, e sim da cópia local: mudar o formato do token
  não muda as permissões
- A cópia local dos usuários com a matrícula como chave: os usuários já
  conhecidos continuam com os mesmos projetos e certificados

**Decisões que dificultam**
- A matrícula como chave do usuário: se o novo provedor identificar as
  pessoas de outra forma (ex.: CPF no gov.br), é preciso uma tabela de
  correspondência ou migrar as referências a alunos em todos os módulos
- `buscarPorMatricula`, usada para vincular alunos: um provedor externo à
  universidade pode não oferecer busca de outras pessoas, e o vínculo
  passaria a depender só da cópia local
- Validar o token no provedor a cada requisição: um provedor mais lento
  ou com limite de requisições afeta todas as operações

## 3. Web → inclusão de um aplicativo mobile

Ex.: um aplicativo para o aluno consultar horas e baixar certificados, e
para o coordenador registrar presenças durante a atividade

**Elementos afetados**
- Um novo cliente (o aplicativo), que usa a mesma API
- O fluxo de login: o aplicativo abre o login institucional no navegador do
  sistema e precisa receber o token de volta (ex.: por um endereço próprio
  do aplicativo), o que depende do provedor aceitar esse retorno
- O download do certificado, se o aplicativo exibir o certificado em vez de
  baixar o PDF
- O registro de presenças, se ele precisar funcionar sem internet: o
  aplicativo guardaria as presenças e as enviaria depois

**Elementos inalterados**
- O servidor inteiro: domínio, services, controllers, persistência e
  integrações
- A API REST, que já é a única forma de acessar o sistema
- O cliente web, que continua funcionando ao lado do aplicativo

**Decisões que ajudam**
- Cliente-servidor com uma API REST em JSON: qualquer cliente que fale HTTP
  usa a mesma API, sem regras de negócio no cliente
- Servidor sem sessão, com o token em cada requisição: funciona igual para
  o navegador e para o aplicativo
- Erros devolvidos na própria requisição, com códigos HTTP padronizados
  (`401`, `403`, `404`, `409`): o aplicativo trata os erros do mesmo jeito
- Escritas idempotentes: o aplicativo pode reenviar uma presença em uma
  conexão instável sem registrá-la duas vezes
- O arquivo do certificado é gerado a cada download a partir dos dados
  salvos: dá para oferecer outro formato sem mudar o que é guardado

**Decisões que dificultam**
- O login por redirecionamento do navegador foi pensado para o cliente web;
  no aplicativo, o retorno com o token precisa de configuração no provedor
  institucional, que não é controlado pelo grupo
- A presença só é aceita se o aluno estava vinculado na data da atividade,
  verificada no envio: presenças enviadas depois, sem internet, podem ser
  recusadas se o vínculo mudou nesse meio-tempo
- Escritas respondem `202 Accepted` e são processadas pela fila: o
  aplicativo precisa consultar de novo para mostrar o estado atualizado
