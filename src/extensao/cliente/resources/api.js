// Funções comuns às páginas do cliente web. As páginas chamam a API do
// servidor (endereço em API, definido por /config.js). O token fica em um
// cookie do servidor, guardado na volta do login e enviado em cada chamada.

var usuario = null;

function el(id) { return document.getElementById(id); }
function v(id) { return el(id).value.trim(); }
function esc(s) {
  return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function parametro(nome) { return new URLSearchParams(location.search).get(nome); }

// chama a API; sem login (401) volta para a página de entrada
async function chamar(metodo, caminho, dados) {
  var opcoes = { method: metodo, headers: {}, credentials: 'include' };
  if (dados) {
    opcoes.headers['Content-Type'] = 'application/json';
    opcoes.body = JSON.stringify(dados);
  }
  var r = await fetch(API + caminho, opcoes);
  if (r.status === 401) {
    location.href = '/';
    throw new Error('não autenticado');
  }
  var texto = await r.text();
  var corpo;
  try { corpo = JSON.parse(texto); } catch (e) { corpo = texto; }
  return { status: r.status, ok: r.ok, corpo: corpo };
}

// escrita: mostra o resultado na página e devolve a resposta
async function escrever(metodo, caminho, dados) {
  var r = await chamar(metodo, caminho, dados);
  if (r.ok) {
    mensagem(r.corpo.mensagem + ' (' + r.status + ')');
  } else {
    mensagem('Erro ' + r.status + ': ' + r.corpo.erro);
  }
  return r;
}

function mensagem(texto) {
  el('mensagem').innerHTML = '<b>' + esc(texto) + '</b>';
}

// tabela com cabeçalho; as células já vêm em HTML
function tabela(colunas, linhas, vazio) {
  if (linhas.length === 0) return '<p><i>' + esc(vazio || 'Nada para mostrar.') + '</i></p>';
  var h = '<table border="1" cellpadding="4" cellspacing="0"><tr>';
  colunas.forEach(function (c) { h += '<th>' + esc(c) + '</th>'; });
  h += '</tr>';
  linhas.forEach(function (l) {
    h += '<tr>';
    l.forEach(function (c) { h += '<td>' + c + '</td>'; });
    h += '</tr>';
  });
  return h + '</table>';
}

// identifica o usuário e monta o menu do topo
async function iniciar() {
  usuario = (await chamar('GET', '/me')).corpo;
  var links = '<a href="/inicio.html">Início</a> | <a href="/projetos.html">Projetos</a>';
  if (usuario.papel === 'aluno') {
    links += ' | <a href="/horas.html">Minhas horas</a> | <a href="/certificados.html">Meus certificados</a>';
  }
  el('topo').innerHTML = '<table width="100%"><tr><td><b>Projetos de Extensão</b> &mdash; ' + links
      + '</td><td align="right">' + esc(usuario.nome) + ' (' + esc(usuario.papel) + ', '
      + esc(usuario.matricula) + ') | <a href="' + API + '/sair">Sair</a></td></tr></table><hr>';
  return usuario;
}
