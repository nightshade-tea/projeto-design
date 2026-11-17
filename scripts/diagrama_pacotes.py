#!/usr/bin/env python3
# Gera docs/diagramas/pacotes.svg (diagrama de pacotes, ver
# docs/arquitetura.md e docs/dominio.md)
# Uso: python3 scripts/diagrama_pacotes.py
#
# Notação UML 2:
# - pacotes com os membros listados no corpo e o nome na aba
# - os módulos do domínio são subpacotes de dominio, desenhados dentro dele
# - dependências tracejadas com seta aberta, do pacote que depende para o
#   pacote de que depende
from uml import Pacote, Svg, sem_sobreposicao, pacote, ABA_H

GV = 60      # distância vertical entre as linhas de pacotes
GH = 100     # distância entre os módulos do domínio
PAD = 36     # margem interna de dominio
MARGEM = 30

controllers = Pacote("controllers", [
    "ProjetoController", "FrequenciaController", "CertificadoController",
    "AutenticacaoController"])
services = Pacote("services", [
    "ProjetoService", "EncerramentoService", "FrequenciaService",
    "CertificadoService", "AutenticacaoService"])
certificacao = Pacote("certificacao", [
    "Certificado", "CertificadoRepository", "GeradorDocumentoCertificado"])
projetos = Pacote("projetos", [
    "Projeto", "StatusProjeto", "Atividade", "Participacao",
    "ResumoFrequencia", "CriteriosCertificacao", "CriterioCertificacao",
    "MinimoHoras", "PercentualMinimoPresenca", "ProjetoRepository"])
identidade = Pacote("identidade", [
    "Usuario", "Aluno", "Professor", "Administrador", "ProvedorIdentidade"])
infraestrutura = Pacote("infraestrutura", [
    "ProjetoRepositorySql", "CertificadoRepositorySql",
    "ProvedorIdentidadeInstitucional", "GeradorPdf"])

modulos = [certificacao, projetos, identidade]
todos = [controllers, services] + modulos + [infraestrutura]

# mesma largura para todos (e o centro de cada um fica fora da aba, para as
# setas chegarem ao corpo). A altura de cada um vem dos membros
w = max(max(p.w for p in todos), 2 * max(p.aba_w for p in todos) + 60)
for p in todos:
    p.w = w

dom_w = len(modulos) * w + (len(modulos) - 1) * GH + 2 * PAD
dom_h = PAD + max(p.h for p in modulos) + PAD     # corpo
W = dom_w + 2 * MARGEM
cx = W / 2
y = MARGEM
for p in (controllers, services):
    p.x, p.y = cx - w / 2, y
    y = p.base + GV
dom_y = y
x = MARGEM + PAD
for p in modulos:
    p.x, p.y = x, dom_y + ABA_H + PAD
    x = p.dir + GH
dom_base = dom_y + ABA_H + dom_h
infraestrutura.x, infraestrutura.y = cx - w / 2, dom_base + GV
H = infraestrutura.base + MARGEM

sem_sobreposicao([(p.x, p.y, p.w, p.h, p.nome) for p in todos])

svg = Svg()
pacote(svg, MARGEM, dom_y, dom_w, dom_h, "dominio")
for p in todos:
    p.desenhar(svg)


def dep(pontos):
    svg.linha(pontos, tracejado=True, fim="seta")


# controllers -> services -> dominio
dep([(cx, controllers.base), (cx, services.topo_corpo)])
dep([(cx, services.base), (cx, dom_y + ABA_H)])
# infraestrutura -> dominio (implementa as interfaces do domínio)
dep([(cx, infraestrutura.topo_corpo), (cx, dom_base)])
# certificacao -> projetos -> identidade, na altura do menor corpo
yc = modulos[0].topo_corpo + (min(p.h for p in modulos) - ABA_H) / 2
for a, b in zip(modulos, modulos[1:]):
    dep([(a.dir, yc), (b.esq, yc)])
# certificacao -> identidade (Certificado usa Aluno e Usuario), por baixo
# de projetos
yb = dom_base - PAD / 2
dep([(certificacao.cx, certificacao.base), (certificacao.cx, yb),
     (identidade.cx, yb), (identidade.cx, identidade.base)])

svg.salvar("pacotes.svg", W, H)
