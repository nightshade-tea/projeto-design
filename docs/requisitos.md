# Especificação de Requisitos

## Contexto

**Gestão de projetos de extensão**: Sistema interno para cadastrar projetos de
extensão, participantes e atividades, registrar participação e presença e
acompanhar horas e requisitos para certificação. Sistema para uma universidade
federal com as seguintes características:

- Alunos: ~40k
- Professores: ~2.5k
- Acessos simultaneos: ~4k (pico de acessos simultâneos)
- Equipe de desenvolvimento: ~4 pessoas

Picos ocorrem durante periodos específicos do semestre, perto dos prazos
definidos de submissão de projetos e horas de extensão.

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

**RF01 Gerenciar projetos** : O professor coordenador e o administrador podem
criar, editar, consultar e encerrar projetos.

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
ser alterados enquanto não houver certificado emitido no projeto.

**RF07 Emitir certificados** : Ao encerrar um projeto, ou quando o coordenador
solicitar, o sistema emite um certificado para cada participante que cumpre os
critérios definidos.

**RF08 Baixar certificados** : O aluno pode baixar os próprios certificados.

## Regras de negócio

**RN01**
: Só professores e administradores podem criar projetos. O professor que cria o
projeto passa a ser o seu coordenador.

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

### ASR01 Escalabilidade e Disponibilidade

O sistema deverá suportar até 4.000 acessos simultâneos, garantindo a
disponibilidade de suas funcionalidades e mantendo níveis adequados de
desempenho mesmo durante períodos de alta demanda. A arquitetura deverá permitir
a expansão dos recursos computacionais conforme o crescimento da utilização do
sistema.

O **ASR01** define questões como escalabilidade e disponibilidade que são
altamente limitados pela arquitetura e disponibilidade de recursos.

### ASR02 Integração Institucional

O sistema deverá integrar-se ao mecanismo de autenticação institucional
disponibilizado pela universidade, permitindo a identificação dos usuários por
meio de suas credenciais institucionais. A solução deverá utilizar os serviços
de autenticação existentes, sem a necessidade de implementar ou manter um
mecanismo próprio de gerenciamento de credenciais.

O **ASR02** define a necessidade de comunicação e integração com componentes
externos ao sistema em si, portanto é relevante em decisões arquiteturais

### ASR03 Manutenibilidade e Evolução

A arquitetura deverá facilitar a manutenção e a evolução do sistema, permitindo
a inclusão de novas funcionalidades, a alteração das regras de certificação e a
adaptação aos processos administrativos da universidade, minimizando o impacto
dessas mudanças sobre componentes não relacionados.

O **ASR03** leva em consideração que o sistema deve ser flexível o suficiente
para que possa incluir nova funcionalidades e regras. Especialmente no sistema
de gestão de extensão, o problema se liga a outros fatores como limitações
institucionais e uma questão de facilidade de modificar regras e estruturas do
sistema.

