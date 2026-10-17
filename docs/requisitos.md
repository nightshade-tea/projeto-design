# Requisitos do sistema

## Contexto

Gestao de projetos de extensao considerando uma universidade federal,
possibilitando analise estatistica e geracao de certificados

alunos: 40k
professores: 2.5k
acessos simultaneos: 4k no pico



## Atores

### Administrador

Responsável pela administração da plataforma.

### Professor

Responsável pelo cadastro, gerenciamento e acompanhamento dos projetos de
extensão sob sua coordenação.

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


## ASRs

### ASR01 Escalabilidade e Disponibilidade

O sistema deverá suportar até 4.000 acessos simultâneos, garantindo a
disponibilidade de suas funcionalidades e mantendo níveis adequados de
desempenho mesmo durante períodos de alta demanda. A arquitetura deverá
permitir a expansão dos recursos computacionais conforme o crescimento da
utilização do sistema.

### ASR02 Integração Institucional

O sistema deverá integrar-se ao mecanismo de autenticação institucional
disponibilizado pela universidade, permitindo a identificação dos usuários por
meio de suas credenciais institucionais. A solução deverá utilizar os serviços
de autenticação existentes, sem a necessidade de implementar ou manter um
mecanismo próprio de gerenciamento de credenciais.

### ASR03 Manutenibilidade e Evolução

A arquitetura deverá facilitar a manutenção e a evolução do sistema, permitindo
a inclusão de novas funcionalidades, a alteração das regras de certificação e a
adaptação aos processos administrativos da universidade, minimizando o impacto
dessas mudanças sobre componentes não relacionados.

