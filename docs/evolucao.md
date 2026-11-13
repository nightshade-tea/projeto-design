# Análise de evolução

Essa seção analisa o que aconteceria se tecnologias/integrações do sistema
precisassem ser substituídas. A análise foi feita com 3 possíveis mudanças.

## 1. Alteração no mecanismo de persistência

Por exemplo, trocar o banco relacional por um banco de documentos (ex. MongoDB)

**Elementos afetados**
- `ProjetoRepositorySql` e `CertificadoRepositorySql`, substituídos por
  novas implementações de `ProjetoRepository` e `CertificadoRepository`
- A cópia local dos usuários, guardada por `ProvedorIdentidadeInstitucional`
- A fila de escritas, que hoje é uma tabela no banco de dados, precisa ser
  feita de outra forma. Dependendo do mecanismo escolhido (caso não implemente),
  um novo serviço de fila será necessário
- Preciso garantir que o novo mecanismo salve operações como transações
- O "deploy" da aplicação, garantindo o provisionamento do novo mecanismo

**Elementos inalterados**
- O domínio (`identidade`, `projetos` e `certificacao`)
- As interfaces dos repositories
- Os services e os controllers
- A API REST e o cliente web
- O provedor de identidade e a geração do certificado

**Decisões que ajudam**
- Uso de Repositories como interfaces no domínio, desacoplando qualquer
  tecnologia de persistência de como o sistema opera em alto nível
- Um repository por "recurso", diminuindo a abrangência da mudança de código
  a ser feita e separando a eventual migração
- Pelas escritas serem idempotentes, a migração não precisa ter "medo" de
  duplicar dados ao reprocessar as operações

**Decisões que dificultam**
- Ter a fila no próprio banco (acoplamento). Simplifica as operações mas também
  precisa ser refeita junto com o banco
- Consultas entre recursos (ex. `listarPorAluno`) dependem do mecanismo de
  persistência e precisam ser reescritas e testadas

## 2. Alteração no provedor de identidade

Por exemplo, troca do login único por OAuth, ou usar autenticação do gov.br

**Elementos afetados**
- `ProvedorIdentidadeInstitucional` é substituído por uma nova implementação
  de `ProvedorIdentidade`
- Se o novo provedor mudar a maneira de enviar o tipo de vínculo com a
  universidade, será necessário alterar esse mapeamento
- A configuração da conexão com o provedor novo (endereço e credenciais)
- O cliente web, só se o mecanismo de retorno do login mudar

**Elementos inalterados**
- O domínio (`Usuario`)
- `AutenticacaoService` e os controllers, que só usam `urlLogin()` e
  `identificar(token)`
- Os services e as regras de permissão
- A persistência, os certificados e a API

**Decisões que ajudam**
- Uso de `ProvedorIdentidade` como interface no domínio, apenas precisará
  de novas implementações
- Não existe persistência nessa parte e, portanto, não precisa migrar nada
- O papel do usuário fica nele mesmo e não no token recebido, então mudar o
  formato do token não muda as permissões dos usuários

**Decisões que dificultam**
- Dependendo da chave utilizada pelo novo provedor (ex. CPF pro gov.br), será
  necessário um mapeamento dessa chave para a matrícula ou alterar a chave
  utilizada
- Dependendo do rate limit de um provedor, a velocidade de todas as operações
  pode ser afetada, uma vez que validamos todas as requisições

## 3. Adicionando um aplicativo mobile

Por exemplo, surgiu a necessidade de ter um aplicativo de celular para essa
aplicação.

**Elementos afetados**
- Um novo cliente, que usa a mesma API
- O fluxo de login, necessitando autenticação nativa ou abrir abas no navegador
- O registro de presenças, caso ele precise funcionar sem internet; acumulando
  localmente e enviando depois

**Elementos inalterados**
- O sistema inteiro, seria apenas uma expansão que utiliza das interfaces já
  existentes

**Decisões que ajudam**
- Cliente-servidor com uma API REST em JSON, já que qualquer cliente que fale
  HTTP usa a mesma API
- Token verificado em cada requisição: funciona igual para o navegador e para
  o aplicativo
- Erros são devolvidos na própria requisição, então o aplicativo trata os erros
  do mesmo jeito
- Escritas idempotentes: o aplicativo pode reenviar uma presença em uma
  conexão instável sem registrá-la duas vezes
- Já que o certificado é gerado a cada download, outros formatos podem ser
  oferecidos sem mudar como é guardado

**Decisões que dificultam**
- O login por redirecionamento do navegador foi pensado para o cliente web. No
  aplicativo isso provavelmente precisará ser revisto e, talvez, atualizado
- O "buffering" de presenças caso sem internet precisará ser testado pois
  casos de borda podem aparecer se estados do servidor mudam antes do envio
  pelo cliente
