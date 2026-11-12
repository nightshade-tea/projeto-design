# ADR 003: Integração com o login institucional

## Status

Aceito

## Contexto

- O login é feito apenas pelo provedor de identidade da universidade
- O papel do usuário (aluno, professor ou administrador) vem do vínculo
  informado pelo provedor
- Professores vinculam alunos a projetos pela matrícula, inclusive alunos que
  nunca entraram no sistema
- O sistema deve rodar em várias instâncias para atender à carga e à
  disponibilidade

## Alternativas consideradas

- **Login próprio**: o sistema guarda as credenciais dos usuários
- **Acesso direto ao provedor**: os services chamam o provedor diretamente, e o
  servidor guarda a sessão depois do login
- **Interface no domínio, sem sessão**: o provedor é acessado por uma
  interface, e cada requisição envia o token do login institucional

## Decisão

- O provedor é acessado pela interface **`ProvedorIdentidade`**, definida no
  módulo `identidade`, com as implementações `ProvedorIdentidadeInstitucional`
  e `ProvedorIdentidadeTeste`
- O servidor só **inicia o login**, redirecionando o navegador para o login
  institucional (`urlLogin()`), que gera o token e devolve o navegador ao
  cliente com ele
- O servidor **não guarda sessão**: cada requisição envia o token, validado
  por `identificar(token)`
- Os usuários obtidos do provedor são guardados em uma **cópia local**, com a
  matrícula como chave, e o papel é a subclasse de `Usuario`


## Consequências

### Positivas

- O sistema não guarda senhas
- Trocar o provedor afeta só a implementação de `ProvedorIdentidade`
- Os testes usam `ProvedorIdentidadeTeste`, sem depender da universidade
- Sem sessão no servidor, qualquer instância atende qualquer requisição
- Alunos podem ser vinculados e consultados pela cópia local

### Negativas, custos e riscos

- Se o provedor estiver indisponível, não é possível entrar no sistema nem
  vincular alunos que ainda não estão na cópia local
- Validar o token a cada requisição depende do provedor e adiciona latência
- A cópia local pode ficar desatualizada (ex.: um aluno que mudou de vínculo),
  até o usuário entrar de novo
- O formato do token e a forma de validá-lo dependem do que a universidade
  oferece, e ainda precisam ser confirmados
