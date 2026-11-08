#!/usr/bin/env python3
# Gera docs/diagramas/componentes.svg (diagrama de componentes, ver
# docs/arquitetura.md)
# Uso: python3 scripts/diagrama_componentes.py
#
# Notação UML 2:
# - componentes com a palavra-chave «component» e o ícone de componente;
#   o compartimento «realizations» lista as classes que realizam o componente
# - interfaces do domínio como conectores de montagem: soquete no componente
#   que requer a interface e bola no componente que a fornece
# - a API REST é fornecida por uma porta do Servidor, ligada aos controllers
#   por um conector de delegação
# - dependências tracejadas com seta aberta
from uml import (Componente, Svg, componente_conteiner, montagem, porta,
                 largura, sem_sobreposicao, H_CAB_COMP, PORTA, R_SOQUETE)

GV = 60      # comprimento das ligações verticais
GH = 100     # distância entre componentes ligados lado a lado
GA = 24      # distância entre os adaptadores empilhados
PAD = 36     # margem interna dos contêineres
MARGEM = 30

cliente = Componente("Cliente web")
controllers = Componente("Controllers", realizacoes=[
    "ProjetoController", "FrequenciaController", "CertificadoController",
    "AutenticacaoController"])
services = Componente("Services", realizacoes=[
    "ProjetoService", "EncerramentoService", "FrequenciaService",
    "CertificadoService", "AutenticacaoService"])
modulos = [Componente(n) for n in ["certificacao", "projetos", "identidade"]]
# (adaptador, interface do domínio que ele fornece)
ligacoes = [
    (Componente("ProjetoRepositorySql"), "ProjetoRepository"),
    (Componente("CertificadoRepositorySql"), "CertificadoRepository"),
    (Componente("ProvedorIdentidadeInstitucional"), "ProvedorIdentidade"),
    (Componente("GeradorPdf"), "GeradorDocumentoCertificado"),
]
adaptadores = [a for a, _ in ligacoes]
banco = Componente("Banco de dados")
provedor_ext = Componente("Provedor de identidade institucional")

# ------------------------------------------------------------------ layout

# Services com os adaptadores empilhados à direita
GM = max(largura(i, 12) for _, i in ligacoes) + 60   # largura da montagem
aw = max(a.w for a in adaptadores)
for a in adaptadores:
    a.w = aw
pilha_h = sum(a.h for a in adaptadores) + GA * (len(adaptadores) - 1)
services.h = max(services.h, pilha_h)
services.x, services.y = 0, 0
y = services.cy - pilha_h / 2
for a in adaptadores:
    a.x, a.y = services.dir + GM, y
    y = a.base + GA

# Controllers sobre Services
controllers.w = services.w = max(controllers.w, services.w)
controllers.x = services.x
controllers.y = services.topo - GV - controllers.h

# Dominio à esquerda de Services, com os módulos empilhados
mw = max(m.w for m in modulos)
for m in modulos:
    m.w = mw
dom_w = mw + 2 * PAD
dom_h = (H_CAB_COMP + PAD / 2 + sum(m.h for m in modulos)
         + GV * (len(modulos) - 1) + PAD)
dom_x = services.esq - GH - dom_w
dom_y = services.cy - dom_h / 2
y = dom_y + H_CAB_COMP + PAD / 2
for m in modulos:
    m.x, m.y = dom_x + PAD, y
    y = m.base + GV

internos = [controllers, services] + modulos + adaptadores
srv_x = min(dom_x, min(c.esq for c in internos)) - PAD
srv_y = controllers.topo - GV - 10
srv_dir = max(c.dir for c in internos) + PAD
srv_base = max(dom_y + dom_h, max(c.base for c in internos)) + PAD

# sistemas externos à direita do Servidor
ext_x = srv_dir + GH
r0, r1, idp = adaptadores[0], adaptadores[1], adaptadores[2]
banco.w = provedor_ext.w = max(banco.w, provedor_ext.w)
banco.x, banco.y = ext_x, r0.cy - 24
banco.h = r1.cy + 24 - banco.y
provedor_ext.x, provedor_ext.y = ext_x, idp.cy - provedor_ext.h / 2

# cliente acima da porta do Servidor
porta_x, porta_y = controllers.cx, srv_y
bola_y = porta_y - PORTA / 2 - 30
cliente.x = porta_x - cliente.w / 2
cliente.y = bola_y - R_SOQUETE - 30 - cliente.h

todos = internos + [cliente, banco, provedor_ext]
dx = MARGEM - min(srv_x, min(c.esq for c in todos))
dy = MARGEM - cliente.topo
for c in todos:
    c.mover(dx, dy)
srv_x, srv_dir, dom_x = srv_x + dx, srv_dir + dx, dom_x + dx
srv_y, srv_base, dom_y = srv_y + dy, srv_base + dy, dom_y + dy
porta_x, porta_y = porta_x + dx, porta_y + dy
W = max(c.dir for c in todos) + MARGEM
H = srv_base + MARGEM

sem_sobreposicao([(c.x, c.y, c.w, c.h, c.nome) for c in todos
                  if c not in modulos] +
                 [(dom_x, dom_y, dom_w, dom_h, "dominio")])

# --------------------------------------------------------------- desenho

svg = Svg()
componente_conteiner(svg, srv_x, srv_y, srv_dir - srv_x, srv_base - srv_y,
                     "Servidor")
componente_conteiner(svg, dom_x, dom_y, dom_w, dom_h, "dominio", fundo="#fff")
for c in todos:
    c.desenhar(svg)

# Cliente web requer a API REST fornecida pela porta do Servidor
montagem(svg, (porta_x, cliente.base), (porta_x, porta_y - PORTA / 2),
         "API REST")
porta(svg, porta_x, porta_y)
# delegação da porta para os controllers
svg.linha([(porta_x, porta_y + PORTA / 2), (porta_x, controllers.topo)],
          fim="seta")
svg.texto(porta_x + 8, (porta_y + controllers.topo) / 2 + 8, "«delegate»", 12)

# Controllers -> Services
svg.linha([(services.cx, controllers.base), (services.cx, services.topo)],
          tracejado=True, fim="seta")
# Services -> dominio
yd = services.topo + H_CAB_COMP / 2
svg.linha([(services.esq, yd), (dom_x + dom_w, yd)], tracejado=True,
          fim="seta")
# certificacao -> projetos -> identidade
for a, b in zip(modulos, modulos[1:]):
    svg.linha([(a.cx, a.base), (b.cx, b.topo)], tracejado=True, fim="seta")

# Services requer as interfaces do domínio fornecidas pelos adaptadores
for a, interface in ligacoes:
    montagem(svg, (services.dir, a.cy), (a.esq, a.cy), interface)

# adaptadores -> sistemas externos
for a, ext in [(r0, banco), (r1, banco), (idp, provedor_ext)]:
    svg.linha([(a.dir, a.cy), (ext.esq, a.cy)], tracejado=True, fim="seta")

svg.salvar("componentes.svg", W, H)
