# ADR 003: Integração com o provedor de identidade

## Contexto

- O login é feito exclusivamente pelo provedor de identidade da universidade
  (RE01, ASR02), então o sistema não guarda credenciais
- O papel do usuário (aluno, professor ou administrador) vem do vínculo
  informado pelo provedor (RE02)
- Professores vinculam alunos a projetos pela matrícula, inclusive alunos que
  nunca entraram no sistema
- O sistema roda em várias instâncias para atender a 4.000 acessos
  simultâneos com 99,5% de disponibilidade (RNF01, RNF02)

## Problema e forças

O provedor é obrigatório, mas é um sistema externo, fora do controle da
equipe. É preciso decidir como o sistema se integra a ele:
- o domínio não deve depender da tecnologia do provedor, e os testes não
  devem depender da universidade
- uma indisponibilidade do provedor não deve parar mais do que o necessário
- cada chamada ao provedor adiciona latência às requisições, que devem
  responder em até 1 s (consultas) ou 2 s (escritas)
- qualquer instância deve poder atender qualquer requisição
- o formato do token e a forma de validá-lo dependem do que a universidade
  oferece

## Alternativas consideradas

- **Chamada direta**: controllers e services chamam a API do provedor
  diretamente, e o servidor guarda a sessão depois do login
- **Interface, consultando o provedor sempre**: o provedor é acessado por uma
  interface do domínio, e todo dado de usuário (papel, nome, busca por
  matrícula) é pedido ao provedor quando é usado
- **Importação periódica**: os usuários da universidade são importados em
  lote para o banco, e o sistema só consulta a cópia
- **Interface com cópia local sob demanda**: o provedor é acessado por uma
  interface do domínio, o token é validado a cada requisição, e os usuários
  obtidos do provedor ficam numa cópia local

## Decisão

Utilizar uma **interface com cópia local sob demanda**:
- O provedor é acessado pela interface **`ProvedorIdentidade`**, definida no
  módulo `identidade`, com as implementações `ProvedorIdentidadeInstitucional`
  e `ProvedorIdentidadeTeste`
- O servidor só **inicia o login**, redirecionando o navegador para o login
  institucional (`urlLogin()`), que gera o token e devolve o navegador ao
  cliente com ele
- O servidor **não guarda sessão**: cada requisição envia o token, validado
  por `identificar(token)`
- Os usuários obtidos do provedor (no login ou em
  `buscarPorMatricula(matricula)`) são guardados em uma **cópia local**, com a
  matrícula como chave, e o papel é a subclasse de `Usuario`

## Consequências

### Positivas

- O domínio não conhece a tecnologia do provedor: trocá-lo afeta só a
  implementação de `ProvedorIdentidade`
- Os testes usam `ProvedorIdentidadeTeste`, sem depender da universidade
- Sem sessão no servidor, qualquer instância atende qualquer requisição
- Alunos já obtidos podem ser vinculados e consultados pela cópia local, sem
  chamar o provedor
- Só os usuários que usam o sistema ou são vinculados ficam na cópia, sem
  importar toda a base da universidade

### Negativas, custos e riscos

- Se o provedor estiver indisponível, não é possível entrar no sistema nem
  vincular alunos que ainda não estão na cópia local
- Validar o token a cada requisição depende do provedor e adiciona latência
- A cópia local pode ficar desatualizada (ex.: um aluno que mudou de vínculo),
  até o usuário entrar de novo
- O formato do token e a forma de validá-lo ainda precisam ser confirmados
  com a universidade
