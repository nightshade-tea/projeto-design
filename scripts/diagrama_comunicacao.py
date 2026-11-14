#!/usr/bin/env python3
# Gera os diagramas de comunicação (os mesmos de scripts/diagrama_sequencia.py):
# - docs/diagramas/comunicacao.svg: cenário completo, com autenticação: o
#   professor faz login pelo login institucional, cria um projeto e vincula
#   um aluno; notas indicam os fluxos de exceção (401, 403 e 409)
# e um diagrama por caso de uso, começando pela identificação do usuário:
# - docs/diagramas/comunicacao/login.svg
# - docs/diagramas/comunicacao/criar_projeto.svg (RF01)
# - docs/diagramas/comunicacao/vincular_aluno.svg (RF03)
# - docs/diagramas/comunicacao/registrar_presenca.svg (RF04)
# - docs/diagramas/comunicacao/consultar_horas.svg (RF05, horas do aluno)
# - docs/diagramas/comunicacao/consultar_horas_projeto.svg (RF05, horas dos
#   participantes, para o coordenador)
# - docs/diagramas/comunicacao/encerrar_projeto.svg (RF07)
# - docs/diagramas/comunicacao/baixar_certificado.svg (RF08)
# Uso: python3 scripts/diagrama_comunicacao.py
#
# Como nos diagramas de sequência, a validação do token no login
# institucional e o 401 só aparecem no login e no cenário completo. As
# recusas (403, 404 e 409) ficam em uma nota abaixo da interação.
#
# Notação UML 2:
# - linhas de vida "nome : Tipo", sem sublinhado, ligadas por links
# - mensagens com número de sequência aninhado (1, 1.1, 1.1.1...) e seta
#   no sentido do envio; o resultado aparece como "var := operacao(...)"
# - repetição indicada por "*[guarda]" e condição por "[guarda]" depois do
#   número de sequência
from uml import Objeto, Svg, ligacao, bloco_mensagens, salvar_interacao, nota, \
    ligacao_rota

GMIN = 80    # comprimento mínimo de um link


def gap_h(msgs):
    return max(GMIN, bloco_mensagens(msgs)[0] + 40) if msgs else GMIN


def gap_v(msgs):
    return max(GMIN, bloco_mensagens(msgs)[1] + 50) if msgs else GMIN


def por_cima(a, b, msgs_abaixo, folga=50):
    """rota de a até b passando acima da linha, sobre as mensagens dos links
    dessa linha"""
    y = min(a.topo, b.topo) - max(bloco_mensagens(m)[1]
                                  for m in msgs_abaixo) - folga
    return [(a.cx, a.topo), (a.cx, y), (b.cx, y), (b.cx, b.topo)]


def lado_a_lado(a, b, msgs):
    """b à direita de a, mesma linha"""
    b.x, b.y = a.dir + gap_h(msgs), a.cy - b.h / 2


def abaixo(a, b, msgs):
    b.x, b.y = a.cx - b.w / 2, a.base + gap_v(msgs)


def acima(a, b, msgs):
    b.x, b.y = a.cx - b.w / 2, a.topo - gap_v(msgs) - b.h


def excecoes(objetos, linhas, alvo=None):
    """nota com os fluxos de exceção, abaixo de todos os objetos e alinhada
    à esquerda deles"""
    x = min(o.esq for o in objetos)
    y = max(o.base for o in objetos) + 60
    return (x, y, linhas, alvo)


def desenhar(nome, arquivo, objetos, links, notas=(), rotas=()):
    svg = Svg()
    caixas = [(o.esq, o.topo, o.dir, o.base) for o in objetos]
    for pontos, msgs, lado in rotas:
        caixas.append(ligacao_rota(svg, pontos, msgs, lado))
    for x, y, linhas, alvo in notas:
        caixas.append(nota(svg, x, y, linhas, alvo))
    for a, b, msgs, lado, *x in links:
        c = ligacao(svg, a, b, msgs, lado, x=x[0] if x else None)
        if c:
            caixas.append(c)
    for o in objetos:
        o.desenhar(svg)
    salvar_interacao(svg, caixas, nome, arquivo)


EXC_GERENCIAR = [
    "[não pode]: o controller responde 403 Forbidden e a interação termina",
    "[projeto encerrado]: o controller responde 409 Conflict e a interação"
    " termina"]
EXC_ALUNO = [
    "[matricula não é de um Aluno]: o controller responde 409 Conflict e a",
    "interação termina"]

M_AUTH = ["1.1: usuario := identificar(token)"]
M_IDP = ["1.1.1: usuario := identificar(token)"]


def autenticacao(ctrl):
    """AutenticacaoService abaixo do controller e ProvedorIdentidade
    abaixo dele; devolve os objetos e os links"""
    auth = Objeto(": AutenticacaoService")
    idp = Objeto(": ProvedorIdentidade")
    abaixo(ctrl, auth, M_AUTH)
    abaixo(auth, idp, M_IDP)
    return auth, idp, [(ctrl, auth, M_AUTH, 1), (auth, idp, M_IDP, 1)]


def autenticacao_lado(ctrl, svc, m_idp):
    """para os casos em que o service também usa ProvedorIdentidade:
    AutenticacaoService abaixo do controller e ProvedorIdentidade abaixo do
    service, na mesma linha"""
    auth = Objeto(": AutenticacaoService")
    idp = Objeto(": ProvedorIdentidade")
    abaixo(svc, idp, m_idp)
    abaixo(ctrl, auth, M_AUTH)
    auth.y = idp.y = max(auth.y, idp.y)
    return auth, idp, [(ctrl, auth, M_AUTH, 1), (auth, idp, M_IDP, -1),
                       (svc, idp, m_idp, 1)]


# --------------------------------------------------- criar projeto (RF01)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": ProjetoController")
svc = Objeto(": ProjetoService")
projeto = Objeto("projeto : Projeto")
repo = Objeto(": ProjetoRepository")
m_ctrl = ["1: criar(token, titulo, descricao)"]
m_svc = ["1.2: projeto := criar(titulo, descricao, usuario)"]
m_proj = ["1.2.1 [usuario é Professor ou Administrador]:",
          "«create» Projeto(titulo, descricao, coordenador)"]
m_repo = ["1.2.2: salvar(projeto)"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
lado_a_lado(svc, repo, m_repo)
abaixo(svc, projeto, m_proj)
auth, idp, l_auth = autenticacao(ctrl)
objs = [cliente, ctrl, auth, idp, svc, projeto, repo]
desenhar("Criar projeto", "comunicacao/criar_projeto.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, repo, m_repo, 1), (svc, projeto, m_proj, 1)],
         notas=[excecoes(objs, [
             "[usuario não é Professor nem Administrador]: o controller",
             "responde 403 Forbidden e a interação termina"])])

# -------------------------------------------------- vincular aluno (RF03)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": ProjetoController")
svc = Objeto(": ProjetoService")
repo = Objeto(": ProjetoRepository")
projeto = Objeto("projeto : Projeto")
m_ctrl = ["1: vincular(token, id, matricula)"]
m_svc = ["1.2: vincular(id, matricula, usuario)"]
m_repo = ["1.2.1: projeto := buscarPorId(id)", "1.2.5: salvar(projeto)"]
m_idp = ["1.2.3 [pode e projeto ativo]:",
         "aluno := buscarPorMatricula(matricula)"]
m_proj = ["1.2.2: pode := podeGerenciar(usuario)",
          "1.2.4 [aluno é Aluno]: vincular(aluno)"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
lado_a_lado(svc, repo, m_repo)
acima(svc, projeto, m_proj)
auth, idp, l_auth = autenticacao_lado(ctrl, svc, m_idp)
objs = [cliente, ctrl, auth, idp, svc, repo, projeto]
desenhar("Vincular aluno", "comunicacao/vincular_aluno.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, repo, m_repo, 1), (svc, projeto, m_proj, -1)],
         notas=[excecoes(objs, EXC_GERENCIAR + EXC_ALUNO)])

# ---------------------------------------------- registrar presença (RF04)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": FrequenciaController")
svc = Objeto(": FrequenciaService")
repo = Objeto(": ProjetoRepository")
projeto = Objeto("projeto : Projeto")
m_ctrl = ["1: registrarPresenca(token, id, atividadeId, matricula)"]
m_svc = ["1.2: registrarPresenca(id, atividadeId, matricula, usuario)"]
m_repo = ["1.2.1: projeto := buscarPorId(id)", "1.2.6: salvar(projeto)"]
m_idp = ["1.2.4: aluno := buscarPorMatricula(matricula)"]
m_proj = ["1.2.2: pode := podeGerenciar(usuario)",
          "1.2.3 [pode e projeto ativo]:",
          "atividade := atividade(atividadeId)",
          "1.2.5 [aluno é Aluno]: registrarPresenca(atividade, aluno)"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
lado_a_lado(svc, repo, m_repo)
acima(svc, projeto, m_proj)
auth, idp, l_auth = autenticacao_lado(ctrl, svc, m_idp)
objs = [cliente, ctrl, auth, idp, svc, repo, projeto]
desenhar("Registrar presença", "comunicacao/registrar_presenca.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, repo, m_repo, 1), (svc, projeto, m_proj, -1)],
         notas=[excecoes(objs, EXC_GERENCIAR + EXC_ALUNO)])

# ------------------------------------------------ encerrar projeto (RF07)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": ProjetoController")
svc = Objeto(": EncerramentoService")
prepo = Objeto(": ProjetoRepository")
projeto = Objeto("projeto : Projeto")
cert = Objeto("certificado : Certificado")
crepo = Objeto(": CertificadoRepository")
m_ctrl = ["1: encerrar(token, id)"]
m_svc = ["1.2: encerrar(id, usuario)"]
m_prepo = ["1.2.1: projeto := buscarPorId(id)", "1.2.5: salvar(projeto)"]
m_proj = ["1.2.2: pode := podeGerenciar(usuario)",
          "1.2.3 [pode e projeto ativo]: encerrar()",
          "1.2.4: aprovados := aprovados()"]
m_cert = ["1.2.7 *[para cada resumo em aprovados]",
          "[não existe]: «create» Certificado(resumo)"]
m_crepo = ["1.2.6 *[para cada resumo em aprovados]:",
           "existe := existe(projeto, resumo.aluno)",
           "1.2.8 *[para cada resumo em aprovados]",
           "[não existe]: salvar(certificado)"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
# afasta o service para os rótulos do link do certificado (à esquerda) não
# encostarem nos da autenticação (à direita do controller)
svc.x += max(0, ctrl.cx + bloco_mensagens(M_AUTH)[0]
             + bloco_mensagens(m_cert)[0] + 80 - (svc.esq + 25))
lado_a_lado(svc, prepo, m_prepo)
acima(svc, projeto, m_proj)
# certificado e repository abaixo do service, com um link para cada
x_cert, x_crepo = svc.esq + 25, svc.dir - 25
y = svc.base + max(gap_v(m_cert), gap_v(m_crepo))
cert.x, cert.y = x_cert + 25 - cert.w, y
crepo.x, crepo.y = x_crepo - 25, y
auth, idp, l_auth = autenticacao(ctrl)
objs = [cliente, ctrl, auth, idp, svc, prepo, projeto, cert, crepo]
desenhar("Encerrar projeto", "comunicacao/encerrar_projeto.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, prepo, m_prepo, 1), (svc, projeto, m_proj, -1),
          (svc, cert, m_cert, -1, x_cert), (svc, crepo, m_crepo, 1, x_crepo)],
         notas=[excecoes(objs, EXC_GERENCIAR + [
             "1.2.6 a 1.2.8 acontecem na mesma iteração, uma vez para cada",
             "resumo; o certificado só é criado se o aluno ainda não tem um"])])

# ------------------------------------------------- consultar horas (RF05)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": FrequenciaController")
svc = Objeto(": FrequenciaService")
repo = Objeto(": ProjetoRepository")
projeto = Objeto("projeto : Projeto")
m_ctrl = ["1: consultarHoras(token)"]
m_svc = ["1.2: resumos, total := consultarHoras(usuario)"]
m_repo = ["1.2.1 [usuario é Aluno]:",
          "projetos := listarPorAluno(usuario)"]
m_proj = ["1.2.2 *[para cada projeto em projetos]:",
          "resumo := resumoFrequencia(usuario)"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
lado_a_lado(svc, repo, m_repo)
acima(svc, projeto, m_proj)
auth, idp, l_auth = autenticacao(ctrl)
objs = [cliente, ctrl, auth, idp, svc, repo, projeto]
desenhar("Consultar horas", "comunicacao/consultar_horas.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, repo, m_repo, 1), (svc, projeto, m_proj, -1)],
         notas=[excecoes(objs, [
             "[usuario não é Aluno]: o controller responde 403 Forbidden e a",
             "interação termina; o total é a soma das horas dos resumos"])])

# ------------------------- consultar horas dos participantes (RF05, coordenador)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": FrequenciaController")
svc = Objeto(": FrequenciaService")
repo = Objeto(": ProjetoRepository")
projeto = Objeto("projeto : Projeto")
m_ctrl = ["1: consultarHorasProjeto(token, id)"]
m_svc = ["1.2: resumos := consultarHorasProjeto(id, usuario)"]
m_repo = ["1.2.1: projeto := buscarPorId(id)"]
m_proj = ["1.2.2: pode := podeGerenciar(usuario)",
          "1.2.3 [pode]: resumos := resumos()"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
lado_a_lado(svc, repo, m_repo)
acima(svc, projeto, m_proj)
auth, idp, l_auth = autenticacao(ctrl)
objs = [cliente, ctrl, auth, idp, svc, repo, projeto]
desenhar("Consultar horas dos participantes",
         "comunicacao/consultar_horas_projeto.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, repo, m_repo, 1), (svc, projeto, m_proj, -1)],
         notas=[excecoes(objs, EXC_GERENCIAR[:1])])

# ---------------------------------------------- baixar certificado (RF08)

cliente = Objeto(": Cliente web")
ctrl = Objeto(": CertificadoController")
svc = Objeto(": CertificadoService")
repo = Objeto(": CertificadoRepository")
cert = Objeto("certificado : Certificado")
ger = Objeto(": GeradorDocumentoCertificado")
m_ctrl = ["1: baixar(token, id)"]
m_svc = ["1.2: arquivo := gerarArquivo(id, usuario)"]
m_repo = ["1.2.1: certificado := buscarPorId(id)"]
m_cert = ["1.2.2 [certificado encontrado]:",
          "pertence := pertenceA(usuario)"]
m_ger = ["1.2.3 [pertence]: arquivo := gerar(certificado)"]
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, svc, m_svc)
lado_a_lado(svc, repo, m_repo)
acima(svc, cert, m_cert)
abaixo(svc, ger, m_ger)
auth, idp, l_auth = autenticacao(ctrl)
objs = [cliente, ctrl, auth, idp, svc, repo, cert, ger]
desenhar("Baixar certificado", "comunicacao/baixar_certificado.svg", objs,
         [(cliente, ctrl, m_ctrl, 1), *l_auth, (ctrl, svc, m_svc, 1),
          (svc, repo, m_repo, 1), (svc, cert, m_cert, -1),
          (svc, ger, m_ger, 1)],
         notas=[excecoes(objs, [
             "[certificado não encontrado]: o controller responde 404 Not Found",
             "[não pertence]: o controller responde 403 Forbidden",
             "em ambos os casos, a interação termina"])])

# ----------------------------------------------------------------- login
#
# : Login institucional -- : Cliente web -- : AutenticacaoController
#     -- : AutenticacaoService -- : ProvedorIdentidade

ext = Objeto(": Login institucional")
cliente = Objeto(": Cliente web")
ctrl = Objeto(": AutenticacaoController")
auth = Objeto(": AutenticacaoService")
idp = Objeto(": ProvedorIdentidade")
m_ext = ["2: entrar(matricula, senha)"]
m_ctrl = ["1: login()",
          "3: consultarUsuario(token)"]
m_auth = ["1.1: url := urlLogin()",
          "3.1: usuario := identificar(token)"]
m_idp = ["1.1.1: url := urlLogin()",
         "3.1.1: usuario := identificar(token)"]
ext.x, ext.y = 0, 0
lado_a_lado(ext, cliente, m_ext)
lado_a_lado(cliente, ctrl, m_ctrl)
lado_a_lado(ctrl, auth, m_auth)
lado_a_lado(auth, idp, m_idp)
# o provedor consulta o login institucional
m_idp_ext = ["3.1.1.1: matricula := validar(token)"]
desenhar("Login", "comunicacao/login.svg",
         [ext, cliente, ctrl, auth, idp],
         [(cliente, ext, m_ext, 1), (cliente, ctrl, m_ctrl, 1),
          (ctrl, auth, m_auth, 1), (auth, idp, m_idp, 1)],
         rotas=[(por_cima(idp, ext, [m_ext, m_ctrl, m_auth, m_idp]),
                 m_idp_ext, 1)],
         notas=[(idp.dir + 40, idp.y - 10,
                 ["[token inválido]: validar(token) recusa o token,",
                  "consultarUsuario devolve 401 Unauthorized e a",
                  "interação termina"],
                 (idp.dir, idp.cy))])

# ------------------------------------- cenário completo, com autenticação
#
#                   : AutenticacaoController -- : AutenticacaoService -- : ProvedorIdentidade
#                            |                          |                        |
# : Login inst. -- : Cliente web ------------ : ProjetoController -- : ProjetoService -- repo
#                                                                            |
#                                                                     projeto : Projeto

ext = Objeto(": Login institucional")
actrl = Objeto(": AutenticacaoController")
auth = Objeto(": AutenticacaoService")
idp = Objeto(": ProvedorIdentidade")
cliente = Objeto(": Cliente web")
pctrl = Objeto(": ProjetoController")
svc = Objeto(": ProjetoService")
repo = Objeto(": ProjetoRepository")
projeto = Objeto("projeto : Projeto")

m_cli_ext = ["2: entrar(matricula, senha)"]
m_cli_actrl = ["1: login()",
               "3: consultarUsuario(token)"]
m_actrl_auth = ["1.1: url := urlLogin()",
                "3.1: usuario := identificar(token)"]
m_auth_idp = ["1.1.1: url := urlLogin()",
              "3.1.1: usuario := identificar(token)",
              "4.1.1: usuario := identificar(token)",
              "5.1.1: usuario := identificar(token)"]
m_cli_pctrl = ["4: criar(token, titulo, descricao)",
               "5: vincular(token, id, matricula)"]
m_pctrl_auth = ["4.1: usuario := identificar(token)",
                "5.1: usuario := identificar(token)"]
m_pctrl_svc = ["4.2: projeto := criar(titulo, descricao, usuario)",
               "5.2: vincular(id, matricula, usuario)"]
m_svc_idp = ["5.2.3 [pode e projeto ativo]:",
             "aluno := buscarPorMatricula(matricula)"]
m_idp_ext = ["3.1.1.1: matricula := validar(token)",
             "4.1.1.1: matricula := validar(token)",
             "5.1.1.1: matricula := validar(token)"]
m_svc_repo = ["4.2.2: salvar(projeto)",
              "5.2.1: projeto := buscarPorId(id)",
              "5.2.5: salvar(projeto)"]
m_svc_proj = ["4.2.1 [usuario é Professor ou Administrador]:",
              "«create» Projeto(titulo, descricao, coordenador)",
              "5.2.2: pode := podeGerenciar(usuario)",
              "5.2.4 [aluno é Aluno]: vincular(aluno)"]


def lw(msgs):
    return bloco_mensagens(msgs)[0]


# distância entre os centros das colunas: cabe o link mais longo de cada
# linha e os rótulos dos links verticais entre as duas colunas
linhas = [[None, actrl, auth, idp, None],
          [ext, cliente, pctrl, svc, repo]]
msgs_h = [[None, m_actrl_auth, m_auth_idp, None],
          [m_cli_ext, m_cli_pctrl, m_pctrl_svc, m_svc_repo]]
entre_v = [0, lw(m_cli_actrl) + 50, lw(m_pctrl_auth) + lw(m_svc_idp) + 80, 0]
cols = [0]
for i in range(4):
    d = entre_v[i]
    for r in (0, 1):
        a, b, m = linhas[r][i], linhas[r][i + 1], msgs_h[r][i]
        if a and b:
            d = max(d, a.w / 2 + gap_h(m) + b.w / 2)
    cols.append(cols[-1] + d)
GV = max(gap_v(m) for m in (m_cli_actrl, m_pctrl_auth, m_svc_idp))
for r, linha in enumerate(linhas):
    for c, o in zip(cols, linha):
        if o:
            o.x, o.y = c - o.w / 2, r * (36 + GV)
abaixo(svc, projeto, m_svc_proj)

desenhar("Professor cria projeto e vincula aluno", "comunicacao.svg",
         [ext, actrl, auth, idp, cliente, pctrl, svc, repo, projeto],
         [(cliente, ext, m_cli_ext, -1),
          (cliente, actrl, m_cli_actrl, 1),
          (actrl, auth, m_actrl_auth, 1),
          (auth, idp, m_auth_idp, 1),
          (cliente, pctrl, m_cli_pctrl, -1),
          (pctrl, auth, m_pctrl_auth, 1),
          (pctrl, svc, m_pctrl_svc, -1),
          (svc, idp, m_svc_idp, -1),
          (svc, repo, m_svc_repo, 1),
          (svc, projeto, m_svc_proj, 1)],
         rotas=[(por_cima(idp, ext, [m_actrl_auth, m_auth_idp]),
                 m_idp_ext, 1)],
         notas=[(idp.dir + 40, idp.y - 10,
                 ["[token inválido]: validar(token) recusa o token,",
                  "consultarUsuario devolve 401 Unauthorized e a",
                  "interação termina (4 e 5 não ocorrem)"],
                 (idp.dir, idp.cy)),
                excecoes([ext, actrl, auth, idp, cliente, pctrl, svc, repo,
                          projeto], [
                    "[usuario não é Professor nem Administrador], em 4.2: o",
                    "controller responde 403 Forbidden e a interação termina"]
                    + EXC_GERENCIAR + EXC_ALUNO)])
