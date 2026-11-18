package extensao;

import extensao.dominio.identidade.Administrador;
import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Professor;
import extensao.dominio.identidade.ProvedorIdentidade;
import extensao.dominio.identidade.Usuario;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

/**
 * Simula o provedor de identidade institucional, com usuários e tokens fixos.
 * Substitui ProvedorIdentidadeInstitucional sem mudar o domínio nem os
 * services (ASR02).
 */
public class ProvedorIdentidadeTeste implements ProvedorIdentidade {

    private final Map<String, Usuario> porToken = new LinkedHashMap<>();
    private final Map<String, Usuario> porMatricula = new LinkedHashMap<>();
    private final String urlLogin;

    public ProvedorIdentidadeTeste(String urlLogin) {
        this.urlLogin = urlLogin;
    }

    /** Usuários usados no protótipo e nos testes. */
    public static ProvedorIdentidadeTeste comUsuariosPadrao(String urlLogin) {
        ProvedorIdentidadeTeste provedor = new ProvedorIdentidadeTeste(urlLogin);
        provedor.adicionar("token-professor", new Professor("P001", "Carla Souza"));
        provedor.adicionar("token-professor2", new Professor("P002", "Diego Lima"));
        provedor.adicionar("token-admin", new Administrador("A001", "Elisa Rocha"));
        provedor.adicionar("token-aluno", new Aluno("2021001", "Ana Martins"));
        provedor.adicionar("token-aluno2", new Aluno("2021002", "Bruno Alves"));
        return provedor;
    }

    public void adicionar(String token, Usuario usuario) {
        porToken.put(token, usuario);
        porMatricula.put(usuario.getMatricula(), usuario);
    }

    @Override
    public Optional<Usuario> identificar(String token) {
        return Optional.ofNullable(porToken.get(token));
    }

    @Override
    public Optional<Usuario> buscarPorMatricula(String matricula) {
        return Optional.ofNullable(porMatricula.get(matricula));
    }

    @Override
    public String urlLogin() {
        return urlLogin;
    }
}
