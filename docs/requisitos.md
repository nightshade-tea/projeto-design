# Especificação de requisitos

## Contexto

**Gestão de projetos de extensão**: Sistema interno para cadastrar projetos de
extensão, participantes e atividades, registrar participação e presença e
acompanhar horas e requisitos para certificação. Sistema para uma universidade
federal com as seguintes características:

- Alunos: ~40k
- Professores: ~2.5k
- Acessos simultâneos: ~4k (pico de acessos simultâneos)
- Equipe de desenvolvimento: ~4 pessoas

Picos ocorrem no começo do semestre, quando a maioria dos projetos são
registrados, e no fim do semestre, quando os alunos consultam as horas de
extensão e baixam os certificados.

### Atores

**Aluno** : Participa de projetos. Consulta projetos e atividades, acompanha as
próprias horas e baixa os próprios certificados.

**Professor** : professor vinculado a um projeto como coordenador. Gerencia o
projeto, as atividades, os participantes, as presenças e os critérios de
certificação desse projeto.

**Administrador** : Tem acesso total ao sistema para manutenção.

**Provedor de identidade institucional** (sistema externo) : Serviço de login
único da universidade.

## Requisitos funcionais

**RF01 Gerenciar projetos** : O professor cria projetos. O coordenador do
projeto e o administrador podem editar, consultar e encerrar projetos.

**RF02 Gerenciar atividades** : O coordenador pode cadastrar, editar e remover
atividades de um projeto ativo.

**RF03 Gerenciar participantes** : O coordenador pode vincular alunos ao
projeto, buscando pela matrícula, e desvincular alunos. Desvincular encerra a
participação, mas mantém as presenças e horas já registradas.

**RF04 Registrar presença** : O coordenador registra a presença dos
participantes em uma atividade.

**RF05 Consultar horas** : O aluno consulta as próprias horas por projeto e no
total. O coordenador consulta as horas de todos os participantes do seu projeto.

**RF06 Definir critérios de certificação** : O coordenador define os critérios
de certificação de um projeto a partir de opções já disponibilizadas no sistema
(ex. mínimo de horas e percentual mínimo de presença). Os critérios só podem
ser alterados enquanto o projeto não for encerrado.

**RF07 Emitir certificados** : Ao encerrar um projeto, o sistema emite um
certificado para cada participante que cumpre os critérios definidos.

**RF08 Baixar certificados** : O aluno pode baixar os próprios certificados.

## Regras de negócio

**RN01**
: Só professores podem criar projetos. O professor que cria o projeto passa a
ser o seu coordenador.

**RN02**
: O professor só gerencia projetos em que é coordenador.

**RN03**
: O administrador pode gerenciar qualquer projeto.


## Requisitos não funcionais

**RNF01 Desempenho**
: Com 4.000 usuários simultâneos, 95% das consultas respondem em até 1 s e 95%
das operações de escrita em até 2 s.

**RNF02 Disponibilidade**
: Disponibilidade mensal de pelo menos 99,5% do tempo.

## Restrições

**RE01 Autenticação institucional**
: O login é feito exclusivamente pelo provedor de identidade da universidade.

**RE02 Papéis institucionais**
: O papel de cada usuário (aluno, professor, administrador) é derivado do
vínculo informado pelo provedor de identidade.

## Requisitos arquiteturalmente significativos (ASRs)

### ASR01 Escalabilidade e disponibilidade

O sistema deverá suportar até 4.000 acessos simultâneos nos picos de começo e
fim de semestre mantendo os limites do RNF01 (95% das consultas em até 1 s e
95% das escritas em até 2 s) e a disponibilidade do RNF02 (99,5% ao mês). Para
atender a uma carga maior, deve ser possível aumentar a capacidade adicionando
instâncias do servidor, sem alterar o código.

O **ASR01** influencia a arquitetura porque:
- rodar várias instâncias exige que o servidor não guarde sessão
- chamadas pela rede entre partes do sistema pesam no limite de 1 s das
  consultas, o que pesa contra dividir o sistema em serviços
- os picos de escrita precisam ser absorvidos sem perder o limite de 2 s, o
  que leva à fila de escritas

### ASR02 Integração institucional

O sistema deverá integrar-se ao mecanismo de autenticação institucional
disponibilizado pela universidade, permitindo a identificação dos usuários por
meio de suas credenciais institucionais. A solução deverá utilizar os serviços
de autenticação existentes, sem a necessidade de implementar ou manter um
mecanismo próprio de gerenciamento de credenciais. O sistema não guarda
senhas, e o papel de cada usuário vem do vínculo informado pelo provedor (RE01
e RE02). Trocar o provedor deve afetar só a implementação da integração, e os
testes devem rodar sem o provedor da universidade.

O **ASR02** define a necessidade de comunicação e integração com um sistema
externo, portanto influencia a arquitetura. Ele exige um ponto único de
integração isolado do domínio e define como cada requisição é autenticada e
o que acontece quando o provedor está indisponível.

### ASR03 Manutenibilidade e evolução

A arquitetura deverá facilitar a manutenção e a evolução do sistema, permitindo
a inclusão de novas funcionalidades, a alteração das regras de certificação e a
adaptação aos processos administrativos da universidade, minimizando o impacto
dessas mudanças sobre componentes não relacionados. Em particular:
- adicionar um novo tipo de critério de certificação (ex.: um número mínimo
  de presenças) deve exigir só uma nova classe, sem alterar `Projeto`, os
  services nem os outros módulos
- trocar o banco de dados, o provedor de identidade ou o formato do arquivo
  do certificado deve afetar só a implementação correspondente, sem alterar
  o domínio

O **ASR03** leva em consideração que o sistema deve ser flexível o suficiente
para incluir novas funcionalidades e regras. Especialmente no sistema de
gestão de extensão, as regras de certificação dependem de decisões
institucionais que mudam com o tempo. Por isso ele influencia a divisão do
sistema em módulos, o sentido das dependências entre eles e o uso de
interfaces entre o domínio e as tecnologias externas.

