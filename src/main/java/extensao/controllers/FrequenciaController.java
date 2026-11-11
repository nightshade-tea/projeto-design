package extensao.controllers;

import extensao.dominio.projetos.ResumoFrequencia;
import extensao.services.AutenticacaoService;
import extensao.services.FrequenciaService;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * POST   /projetos/{id}/atividades/{atividadeId}/presencas              registrar {matricula}
 * DELETE /projetos/{id}/atividades/{atividadeId}/presencas/{matricula}  remover
 * GET    /projetos/{id}/horas   horas dos participantes (coordenador ou administrador)
 * GET    /me/horas              horas do próprio aluno
 */
public class FrequenciaController extends Controller {

    private static final String PRESENCAS = "/projetos/(\\d+)/atividades/(\\d+)/presencas";

    private final FrequenciaService service;

    public FrequenciaController(AutenticacaoService autenticacao, FrequenciaService service) {
        super(autenticacao);
        this.service = service;
    }

    @Override
    void rotas(Roteador r) {
        r.rota("POST", PRESENCAS, (troca, p) -> {
            var usuario = identificar(troca);
            service.registrarPresenca(inteiro(p.get(0), "id"), inteiro(p.get(1), "atividadeId"),
                    obrigatorio(corpo(troca), "matricula"), usuario);
            return Resposta.aceita("presença registrada");
        });
        r.rota("DELETE", PRESENCAS + "/([^/]+)", (troca, p) -> {
            service.removerPresenca(inteiro(p.get(0), "id"), inteiro(p.get(1), "atividadeId"),
                    p.get(2), identificar(troca));
            return Resposta.aceita("presença removida");
        });
        r.rota("GET", "/projetos/(\\d+)/horas", (troca, p) -> Resposta.json(200,
                resumos(service.consultarHorasDoProjeto(inteiro(p.get(0), "id"), identificar(troca)))));
        r.rota("GET", "/me/horas", (troca, p) -> Resposta.json(200,
                resumos(service.consultarHoras(identificar(troca)))));
    }

    private static List<Map<String, Object>> resumos(List<ResumoFrequencia> resumos) {
        return resumos.stream().map(FrequenciaController::resumo).toList();
    }

    private static Map<String, Object> resumo(ResumoFrequencia r) {
        Map<String, Object> dados = new LinkedHashMap<>();
        dados.put("projeto", r.getProjeto().getTitulo());
        dados.put("matricula", r.getAluno().getMatricula());
        dados.put("aluno", r.getAluno().getNome());
        dados.put("horasCumpridas", r.getHorasCumpridas());
        dados.put("presencas", r.getQtdPresencas());
        dados.put("atividades", r.getQtdAtividades());
        dados.put("percentualPresenca", Math.round(r.percentualPresenca()));
        return dados;
    }
}
