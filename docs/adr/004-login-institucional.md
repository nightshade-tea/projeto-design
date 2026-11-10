# ADR 004: Integração com o login institucional

> Rascunho para revisão do grupo.

**Status**: proposto

## Contexto

- O login é feito exclusivamente pelo provedor de identidade da
  universidade (RE01, ASR02)
- O papel do usuário (aluno, professor ou administrador) vem do vínculo
  informado pelo provedor (RE02)
- Professores vinculam alunos a projetos pela matrícula, inclusive alunos
  que nunca entraram no sistema
- O sistema deve rodar em várias instâncias para atender à carga e à
  disponibilidade (ASR01)

## Problema e forças

Como integrar o login institucional sem prender o sistema a ele?
- O sistema não deve guardar nem gerenciar senhas
- O provedor pode mudar, e os testes não devem depender dele
- Consultar o provedor a cada requisição aumenta a latência e a dependência
  dele
- Guardar a sessão no servidor dificulta rodar várias instâncias

## Alternativas consideradas

- **Login próprio**: o sistema guarda as credenciais dos usuários
  (descartada pela RE01)
- **Acesso direto ao provedor**: os services chamam o provedor diretamente,
  e o servidor guarda a sessão depois do login
- **Interface no domínio, sem sessão**: o provedor é acessado por uma
  interface, e cada requisição envia o token do login institucional

## Decisão

- O provedor é acessado pela interface **`ProvedorIdentidade`**, definida
  no módulo `identidade`, com as implementações
  `ProvedorIdentidadeInstitucional` e `ProvedorIdentidadeTeste`
- O servidor só **inicia o login**, redirecionando o navegador para o login
  institucional (`urlLogin()`), que gera o token e devolve o navegador ao
  cliente com ele
- O servidor **não guarda sessão**: cada requisição envia o token, validado
  por `identificar(token)`
- Os usuários obtidos do provedor são guardados em uma **cópia local**, com a
  matrícula como chave, e o papel é a subclasse de `Usuario`

## Consequências positivas

- O sistema não guarda senhas (ASR02)
- Trocar o provedor afeta só a implementação de `ProvedorIdentidade`
- Os testes usam `ProvedorIdentidadeTeste`, sem depender da universidade
- Sem sessão no servidor, qualquer instância atende qualquer requisição
  (ASR01)
- Alunos podem ser vinculados e consultados pela cópia local

## Consequências negativas, custos e riscos

- Se o provedor estiver indisponível, não é possível entrar no sistema nem
  vincular alunos que ainda não estão na cópia local
- Validar o token a cada requisição depende do provedor e adiciona latência;
  pode ser preciso guardar a validação por um tempo
- A cópia local pode ficar desatualizada (ex.: um aluno que mudou de
  vínculo), até o usuário entrar de novo
- O formato do token e a forma de validá-lo dependem do que a universidade
  oferece, e ainda precisam ser confirmados
