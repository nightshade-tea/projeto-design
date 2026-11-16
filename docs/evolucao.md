# Análise de evolução

Essa seção analisa o que aconteceria se tecnologias/integrações do sistema
precisassem ser substituídas. A análise foi feita com 2 possíveis mudanças.

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
