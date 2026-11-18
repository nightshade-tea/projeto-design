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
  feita de outra forma. Se o novo mecanismo não oferecer algo equivalente,
  um serviço de fila separado será necessário
- É preciso garantir que o novo mecanismo salve cada operação de forma
  atômica, como as transações de hoje
- O "deploy" da aplicação, garantindo o provisionamento do novo mecanismo

**Elementos inalterados**
- O domínio (`identidade`, `projetos` e `certificacao`)
- As interfaces dos repositories
- Os services e os controllers
- A API REST e o cliente web
- O provedor de identidade e a geração do certificado

**Decisões que ajudam**
- Uso de repositories como interfaces no domínio, desacoplando a tecnologia
  de persistência das regras de negócio
- Um repository por agregado, o que diminui o código a mudar e permite
  migrar um agregado de cada vez
- Como as escritas são idempotentes, reprocessar operações durante a
  migração não duplica dados

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
- Uso de `ProvedorIdentidade` como interface no domínio, então basta uma
  nova implementação
- A cópia local dos usuários usa a matrícula como chave e não depende do
  provedor, então não precisa ser migrada (a não ser que a chave mude)
- O papel do usuário fica nele mesmo e não no token recebido, então mudar o
  formato do token não muda as permissões dos usuários

**Decisões que dificultam**
- Dependendo da chave utilizada pelo novo provedor (ex. CPF pro gov.br), será
  necessário um mapeamento dessa chave para a matrícula ou alterar a chave
  utilizada
- Dependendo do rate limit de um provedor, a velocidade de todas as operações
  pode ser afetada, uma vez que validamos todas as requisições
