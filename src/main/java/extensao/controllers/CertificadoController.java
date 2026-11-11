package extensao.controllers;

import extensao.dominio.certificacao.Certificado;
import extensao.services.AutenticacaoService;
import extensao.services.CertificadoService;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * GET /me/certificados            listar os certificados do aluno
 * GET /certificados/{id}/arquivo  baixar o certificado (texto, no lugar do PDF)
 */
public class CertificadoController extends Controller {

    private final CertificadoService service;

    public CertificadoController(AutenticacaoService autenticacao, CertificadoService service) {
        super(autenticacao);
        this.service = service;
    }

    @Override
    void rotas(Roteador r) {
        r.rota("GET", "/me/certificados", (troca, p) -> Resposta.json(200,
                service.listar(identificar(troca)).stream().map(CertificadoController::resumo).toList()));
        r.rota("GET", "/certificados/(\\d+)/arquivo", (troca, p) -> {
            byte[] arquivo = service.gerarArquivo(inteiro(p.get(0), "id"), identificar(troca));
            return Resposta.texto("text/plain", new String(arquivo, StandardCharsets.UTF_8));
        });
    }

    private static Map<String, Object> resumo(Certificado c) {
        Map<String, Object> dados = new LinkedHashMap<>();
        dados.put("id", c.getId());
        dados.put("projeto", c.getTituloProjeto());
        dados.put("cargaHoraria", c.getCargaHoraria());
        dados.put("emitidoEm", c.getEmitidoEm().toLocalDate().toString());
        return dados;
    }
}
