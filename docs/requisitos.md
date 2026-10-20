# Requisitos do Sistema

## Contexto

**Gestão de projetos de extensão** — Sistema interno para cadastrar projetos de extensão, participantes e atividades, registrar participação e presença e acompanhar horas e requisitos para certificação. Sistema para uma universidade federal com as seguintes características:

- Alunos: ~40k
- Professores: ~2.5k
- Acessos simultaneos: ~4k (pico de acessos simultâneos)
- Equipe de desenvolvimento especializada de porte medio (~15 pessoas)

Picos ocorrem durante periodos específicos do semestre, perto dos prazos definidos de submissão de projetos e horas de extensão.



## Atores

### Administrador

Majoritariamente composta por desenvolvedores. Responsável pela administração, manutenção e gerenciamento das funcionalidades da plataforma.

### Professor

Responsável pelo cadastro, gerenciamento e acompanhamento dos projetos de extensão sob sua coordenação.

### Aluno

Responsável por consultar os projetos disponíveis, acompanhar suas horas e
emitir seus certificados.



## Funcionais

### RF01 Cadastro de Projetos

O sistema deverá permitir o cadastro, a edição, a consulta e o encerramento de
projetos de extensão.

### RF02 Gerenciamento de Atividades

O sistema deverá permitir o cadastro e o gerenciamento das atividades
vinculadas a cada projeto.

### RF03 Gerenciamento de Participantes

O sistema deverá permitir o registro e o gerenciamento dos alunos participantes
de cada projeto.

### RF04 Registro de Presença

O sistema deverá permitir o registro e a consulta da presença dos alunos nas
atividades dos projetos.

### RF05 Controle de Horas

O sistema deverá contabilizar e disponibilizar as horas de participação de cada
aluno nos projetos e atividades.

### RF06 Definição de requisitos de certificação

O sistema deverá permitir a definição dos critérios necessários para a obtenção
de certificados, considerando cada projeto ou atividade.

### RF07 Geração de certificados

O sistema deverá gerar certificados para os alunos que atenderem aos critérios
de certificação definidos.

### RF08 Download de certificados

O sistema deverá permitir que os alunos consultem e realizem o download dos
certificados emitidos.



## Restricoes

### RE01 Autenticação Institucional

O acesso ao sistema deverá ser realizado exclusivamente por meio do mecanismo
de login institucional disponibilizado pela universidade.

### RE02 Papéis Institucionais

Diferentes níveis de accesso ao sistema, como administradores, docentes,
discentes, devem ser baseados no perfil institucional.

## Regras de Negócio

### RN01 Criação de Projetos

Apenas usuários com perfil Docente ou Administrador podem criar novos projetos de extensão.

### RN02 Escopo de Gestão de Docente

Um Docente só pode gerenciar, atualizar e cadastrar atividades/participantes em projetos nos quais esteja vinculado como Coordenador (ou responsável).

### RN03 Acesso Administrativo

Usuários com perfil Administrador possuem permissão total para gerenciar qualquer projeto, atividade, participante, carga horária e regra de certificação no sistema.


## ASRs

### ASR01 Escalabilidade e Disponibilidade

O sistema deverá suportar até 4.000 acessos simultâneos, garantindo a
disponibilidade de suas funcionalidades e mantendo níveis adequados de
desempenho mesmo durante períodos de alta demanda. A arquitetura deverá
permitir a expansão dos recursos computacionais conforme o crescimento da
utilização do sistema.

O **ASR01** define questões como escalabilidade e disponibilidade que são altamente limitados pela arquitetura e disponibilidade de recursos.

### ASR02 Integração Institucional

O sistema deverá integrar-se ao mecanismo de autenticação institucional
disponibilizado pela universidade, permitindo a identificação dos usuários por
meio de suas credenciais institucionais. A solução deverá utilizar os serviços
de autenticação existentes, sem a necessidade de implementar ou manter um
mecanismo próprio de gerenciamento de credenciais.

O **ASR02** define a necessidade de comunicação e integração com componentes externos ao sistema em si, portanto é relevante em decisões arquiteturais

### ASR03 Manutenibilidade e Evolução

A arquitetura deverá facilitar a manutenção e a evolução do sistema, permitindo
a inclusão de novas funcionalidades, a alteração das regras de certificação e a
adaptação aos processos administrativos da universidade, minimizando o impacto
dessas mudanças sobre componentes não relacionados.

O **ASR03** leva em consideração que o sistema deve ser flexível o suficiente para que possa incluir nova funcionalidades e regras. Especialmente no sistema de gestão de extensão, o problema se liga a outros fatores como limitações institucionais e uma questão de facilidade de modificar regras e estruturas do sistema.

