package extensao.controllers;

import extensao.dominio.identidade.Usuario;
import extensao.services.AutenticacaoService;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * GET /login  login(): redireciona para o login institucional
 * GET /me     consultarUsuario(token): usuário logado, com nome e papel
 */
public class AutenticacaoController extends Controller {

    public AutenticacaoController(AutenticacaoService autenticacao) {
        super(autenticacao);
    }

    @Override
    void rotas(Roteador r) {
        r.rota("GET", "/login", (troca, p) -> Resposta.redirecionar(autenticacao.urlLogin()));
        r.rota("GET", "/me", (troca, p) -> Resposta.json(200, consultarUsuario(identificar(troca))));
    }

    private static Map<String, Object> consultarUsuario(Usuario usuario) {
        Map<String, Object> dados = new LinkedHashMap<>();
        dados.put("matricula", usuario.getMatricula());
        dados.put("nome", usuario.getNome());
        dados.put("papel", papel(usuario));
        return dados;
    }
}
