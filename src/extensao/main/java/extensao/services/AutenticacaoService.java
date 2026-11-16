package extensao.services;

import extensao.dominio.identidade.ProvedorIdentidade;
import extensao.dominio.identidade.Usuario;

public class AutenticacaoService {

    private final ProvedorIdentidade provedor;

    public AutenticacaoService(ProvedorIdentidade provedor) {
        this.provedor = provedor;
    }

    public String urlLogin() {
        return provedor.urlLogin();
    }

    /** Identifica o usuário pelo token; recusa tokens ausentes ou inválidos. */
    public Usuario identificar(String token) {
        if (token == null || token.isBlank()) {
            throw new NaoAutenticadoException("token ausente");
        }
        return provedor.identificar(token)
                .orElseThrow(() -> new NaoAutenticadoException("token inválido"));
    }
}
