#!/usr/bin/env python3
# Gera docs/diagramas/classes.svg (diagrama de classes do domínio, ver docs/dominio.md)
# Uso: python3 scripts/diagrama_classes.py
#
# Notação UML 2:
# - tipos primitivos UML (String, Integer, Boolean, Real) e multiplicidade
#   entre colchetes no lugar de coleções (ex.: presentes : Aluno [0..*])
# - construtores marcados com «create»
# - uma propriedade aparece como atributo ou como ponta de associação, nunca
#   as duas; tipos de outro módulo aparecem como atributos e a dependência
#   entre os módulos é mostrada entre os pacotes
from uml import Classe, Svg, pacote, sem_sobreposicao, ABA_H

GV = 60      # comprimento das ligações verticais
GH = 80      # distância entre classes ligadas lado a lado
GL = 70      # distância entre classes vizinhas sem ligação
PAD = 36     # margem interna dos pacotes
GP = 80      # distância entre pacotes
MARGEM = 30

# ------------------------------------------------------------ certificacao

certificado_repo = Classe("CertificadoRepository", tipo="interface", operacoes=[
    "+ salvar(certificado : Certificado)",
    "+ buscarPorId(id : Integer) : Certificado",
    "+ listarPorAluno(aluno : Aluno) : Certificado [0..*]",
])
certificado = Classe("Certificado", atributos=[
    "- projeto : Projeto",
    "- aluno : Aluno",
    "- nomeAluno : String",
    "- tituloProjeto : String",
    "- nomeCoordenador : String",
    "- cargaHoraria : Integer",
    "- emitidoEm : DateTime",
], operacoes=[
    "«create» + Certificado(resumo : ResumoFrequencia)",
    "+ pertenceA(usuario : Usuario) : Boolean",
])
gerador = Classe("GeradorDocumentoCertificado", tipo="interface", operacoes=[
    "+ gerar(certificado : Certificado) : Byte [0..*]",
])

certificado_repo.x, certificado_repo.y = 0, 0
certificado.x, certificado.y = certificado_repo.dir + GH, 0
gerador.x, gerador.y = certificado.dir + GH, 0
mod_certificacao = [certificado_repo, certificado, gerador]

# ---------------------------------------------------------------- projetos

projeto_repo = Classe("ProjetoRepository", tipo="interface", operacoes=[
    "+ salvar(projeto : Projeto)",
    "+ buscarPorId(id : Integer) : Projeto",
    "+ listar() : Projeto [0..*]",
    "+ listarPorAluno(aluno : Aluno) : Projeto [0..*]",
])
projeto = Classe("Projeto", atributos=[
    "- titulo : String",
    "- descricao : String",
    "- coordenador : Professor",
    "- status : StatusProjeto",
], operacoes=[
    "«create» + Projeto(titulo : String, descricao : String, "
    "coordenador : Professor)",
    "+ editar(titulo : String, descricao : String)",
    "+ encerrar()",
    "+ adicionarAtividade(titulo : String, descricao : String, data : Date, "
    "cargaHoraria : Integer) : Atividade",
    "+ removerAtividade(atividade : Atividade)",
    "+ vincular(aluno : Aluno)",
    "+ desvincular(aluno : Aluno)",
    "+ definirCriterios(criterios : CriterioCertificacao [0..*])",
    "+ registrarPresenca(atividade : Atividade, aluno : Aluno)",
    "+ removerPresenca(atividade : Atividade, aluno : Aluno)",
    "+ vinculado(aluno : Aluno, data : Date) : Boolean",
    "+ resumoFrequencia(aluno : Aluno) : ResumoFrequencia",
    "+ aprovados() : ResumoFrequencia [0..*]",
])
status = Classe("StatusProjeto", tipo="enumeracao",
                literais=["ATIVO", "ENCERRADO"])
atividade = Classe("Atividade", atributos=[
    "- titulo : String",
    "- descricao : String",
    "- data : Date",
    "- cargaHoraria : Integer",
    "- presentes : Aluno [0..*]",
], operacoes=[
    "+ registrarPresenca(aluno : Aluno)",
    "+ removerPresenca(aluno : Aluno)",
    "+ estevePresente(aluno : Aluno) : Boolean",
])
participacao = Classe("Participacao", atributos=[
    "- aluno : Aluno",
    "- inicio : Date",
    "- fim : Date [0..1]",
], operacoes=[
    "+ encerrar()",
    "+ ativaEm(data : Date) : Boolean",
    "+ resumoFrequencia(projeto : Projeto, atividades : Atividade [0..*])"
    " : ResumoFrequencia",
])
criterios = Classe("CriteriosCertificacao", operacoes=[
    "+ definir(criterios : CriterioCertificacao [0..*])",
    "+ atende(resumo : ResumoFrequencia) : Boolean",
])
resumo = Classe("ResumoFrequencia", atributos=[
    "- aluno : Aluno",
    "- projeto : Projeto",
    "- horasCumpridas : Integer",
    "- qtdPresencas : Integer",
    "- qtdAtividades : Integer",
], operacoes=[
    "+ percentualPresenca() : Real",
])
criterio = Classe("CriterioCertificacao", tipo="interface", operacoes=[
    "+ avaliar(resumo : ResumoFrequencia) : Boolean",
])
minimo_horas = Classe("MinimoHoras", atributos=[
    "- cargaHoraria : Integer",
], operacoes=[
    "«create» + MinimoHoras(cargaHoraria : Integer)",
    "+ avaliar(resumo : ResumoFrequencia) : Boolean",
])
percentual = Classe("PercentualMinimoPresenca", atributos=[
    "- pct : Real",
], operacoes=[
    "«create» + PercentualMinimoPresenca(pct : Real)",
    "+ avaliar(resumo : ResumoFrequencia) : Boolean",
])

# linha das partes de Projeto
atividade.x = 0
participacao.x = atividade.dir + GL
criterios.x = participacao.dir + GL
# Projeto sobre Participacao, repository à esquerda, enumeração à direita
projeto.x, projeto.y = participacao.cx - projeto.w / 2, 0
projeto_repo.x, projeto_repo.y = projeto.esq - GH - projeto_repo.w, 0
status.x, status.y = projeto.dir + GL, 0
for c in (atividade, participacao, criterios):
    c.y = projeto.base + GV
# abaixo das partes
resumo.x, resumo.y = participacao.cx - resumo.w / 2, participacao.base + GV
criterio.x, criterio.y = criterios.cx - criterio.w / 2, criterios.base + GV
impl_y = criterio.base + GV
minimo_horas.y = percentual.y = impl_y
minimo_horas.x = criterio.esq
percentual.x = minimo_horas.dir + 40
mod_projetos = [projeto_repo, projeto, status, atividade, participacao,
                criterios, resumo, criterio, minimo_horas, percentual]

# -------------------------------------------------------------- identidade

provedor = Classe("ProvedorIdentidade", tipo="interface", operacoes=[
    "+ identificar(token : String) : Usuario",
    "+ buscarPorMatricula(matricula : String) : Usuario",
    "+ urlLogin() : String",
])
usuario = Classe("Usuario", tipo="abstrata", atributos=[
    "- matricula : String",
    "- nome : String",
], operacoes=[
    "+ getMatricula() : String",
    "+ setMatricula(matricula : String)",
    "+ getNome() : String",
    "+ setNome(nome : String)",
])
aluno = Classe("Aluno")
professor = Classe("Professor")
administrador = Classe("Administrador")
provedor.x, provedor.y = 0, 0
usuario.x, usuario.y = provedor.dir + GH, 0
papeis = [aluno, professor, administrador]
larg = sum(c.w for c in papeis) + 40 * (len(papeis) - 1)
x = usuario.cx - larg / 2
for c in papeis:
    c.x, c.y = x, usuario.base + GV
    x = c.dir + 40
mod_identidade = [provedor, usuario, aluno, professor, administrador]

# ------------------------------------------------- pacotes empilhados

modulos = [("certificacao", mod_certificacao), ("projetos", mod_projetos),
           ("identidade", mod_identidade)]


def caixa(cs):
    x0 = min(c.esq for c in cs)
    y0 = min(c.topo for c in cs)
    return x0, y0, max(c.dir for c in cs) - x0, max(c.base for c in cs) - y0


larg_pacote = max(caixa(cs)[2] for _, cs in modulos) + 2 * PAD
quadros = []
y = MARGEM
for nome, cs in modulos:
    x0, y0, w, h = caixa(cs)
    dx = MARGEM + (larg_pacote - w) / 2 - x0
    dy = y + ABA_H + PAD - y0
    for c in cs:
        c.mover(dx, dy)
    quadros.append((nome, y, h + 2 * PAD))
    y += ABA_H + h + 2 * PAD + GP

W = larg_pacote + 2 * MARGEM
H = y - GP + MARGEM
todas = [c for _, cs in modulos for c in cs]
sem_sobreposicao([(c.x, c.y, c.w, c.h, c.nome) for c in todas])

# --------------------------------------------------------------- desenho

svg = Svg()
for nome, y, h in quadros:
    pacote(svg, MARGEM, y, larg_pacote, h, nome)

# dependências entre pacotes: certificacao -> projetos -> identidade
for (_, y1, h1), (_, y2, _) in zip(quadros, quadros[1:]):
    svg.linha([(W / 2, y1 + ABA_H + h1), (W / 2, y2 + ABA_H)],
              tracejado=True, fim="seta")

for c in todas:
    c.desenhar(svg)


def dependencia_horizontal(origem, destino, rotulo=None):
    """origem e destino lado a lado, alinhados pelo topo"""
    y = min(origem.cy, destino.cy)
    if origem.dir < destino.esq:
        x1, x2 = origem.dir, destino.esq
    else:
        x1, x2 = origem.esq, destino.dir
    svg.linha([(x1, y), (x2, y)], tracejado=True, fim="seta")
    if rotulo:
        svg.texto((x1 + x2) / 2, y - 7, rotulo, 12, "middle")


def dependencia_vertical(origem, destino, rotulo=None):
    x = destino.cx
    svg.linha([(x, origem.base), (x, destino.topo)], tracejado=True,
              fim="seta")
    if rotulo:
        svg.texto(x + 8, (origem.base + destino.topo) / 2 + 4, rotulo, 12)


def rotulos_ponta(x, y, papel, mult):
    """papel à esquerda e multiplicidade à direita da linha, sobre a ponta"""
    svg.texto(x - 7, y - 7, papel, 12, "end")
    svg.texto(x + 7, y - 7, mult, 12)


def composicao(todo, parte, papel, mult):
    """losango no todo; reta se a parte está abaixo, senão sai pela lateral
    do todo e desce até a parte"""
    if todo.esq + 20 <= parte.cx <= todo.dir - 20:
        pontos = [(parte.cx, todo.base), (parte.cx, parte.topo)]
    else:
        y = todo.base - 24
        x = todo.esq if parte.cx < todo.esq else todo.dir
        pontos = [(x, y), (parte.cx, y), (parte.cx, parte.topo)]
    svg.linha(pontos, inicio="losango")
    rotulos_ponta(parte.cx, parte.topo, papel, mult)


def arvore(geral, especificas, tracejado=False):
    """generalização (ou realização, tracejada) com ramos que se juntam em
    uma única ponta de triângulo"""
    bus_y = geral.base + GV / 2
    for c in especificas:
        svg.linha([(c.cx, c.topo), (c.cx, bus_y), (geral.cx, bus_y),
                   (geral.cx, geral.base)], tracejado=tracejado,
                  fim="triangulo")


# certificacao
dependencia_horizontal(certificado_repo, certificado)
dependencia_horizontal(gerador, certificado)

# projetos
dependencia_horizontal(projeto_repo, projeto)
composicao(projeto, atividade, "atividades", "0..*")
composicao(projeto, participacao, "participacoes", "0..*")
composicao(projeto, criterios, "criterios", "1")
dependencia_vertical(participacao, resumo, "«create»")
composicao(criterios, criterio, "criterios", "0..*")
# realizações em árvore, com uma única ponta na interface
arvore(criterio, [minimo_horas, percentual], tracejado=True)

# identidade
dependencia_horizontal(provedor, usuario)
# generalizações em árvore, com uma única ponta na superclasse
arvore(usuario, papeis)

svg.salvar("classes.svg", W, H)
