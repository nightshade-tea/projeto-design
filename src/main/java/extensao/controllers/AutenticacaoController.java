package extensao.controllers;

import extensao.dominio.identidade.Usuario;
import extensao.services.AutenticacaoService;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * GET /login           login(): redireciona para o login institucional
 * GET /sessao?token=   volta do login institucional: guarda o token em um cookie
 * GET /sair            apaga o cookie
 * GET /me              consultarUsuario(token): usuário logado, com nome e papel
 */
public class AutenticacaoController extends Controller {

    public AutenticacaoController(AutenticacaoService autenticacao) {
        super(autenticacao);
    }

    @Override
    void rotas(Roteador r) {
        r.rota("GET", "/login", (troca, p) -> Resposta.redirecionar(autenticacao.urlLogin()));
        r.rota("GET", "/sessao", (troca, p) -> {
            String token = parametro(troca, "token");
            if (token == null || !token.matches("[A-Za-z0-9-]+")) {
                throw new IllegalArgumentException("token ausente");
            }
            // o servidor não guarda sessão: o cookie só leva o token em cada requisição
            return Resposta.redirecionar("/inicio.html")
                    .com("Set-Cookie", "token=" + token + "; Path=/; HttpOnly; SameSite=Lax");
        });
        r.rota("GET", "/sair", (troca, p) -> Resposta.redirecionar("/")
                .com("Set-Cookie", "token=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"));
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
