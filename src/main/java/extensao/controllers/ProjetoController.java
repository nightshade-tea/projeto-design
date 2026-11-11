package extensao.controllers;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.projetos.Atividade;
import extensao.dominio.projetos.CriterioCertificacao;
import extensao.dominio.projetos.MinimoHoras;
import extensao.dominio.projetos.Participacao;
import extensao.dominio.projetos.PercentualMinimoPresenca;
import extensao.dominio.projetos.Projeto;
import extensao.services.AutenticacaoService;
import extensao.services.EncerramentoService;
import extensao.services.ProjetoService;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * GET    /projetos                               listar
 * POST   /projetos                               criar {titulo, descricao}
 * GET    /projetos/{id}                          consultar
 * PUT    /projetos/{id}                          editar {titulo, descricao}
 * POST   /projetos/{id}/encerramento             encerrar e emitir os certificados
 * POST   /projetos/{id}/atividades               adicionar {titulo, descricao, data, cargaHoraria}
 * DELETE /projetos/{id}/atividades/{atividadeId} remover
 * POST   /projetos/{id}/participantes            vincular {matricula}
 * DELETE /projetos/{id}/participantes/{matricula} desvincular
 * PUT    /projetos/{id}/criterios                definir {minimoHoras, percentualMinimo}
 */
public class ProjetoController extends Controller {

    private static final String ID = "/projetos/(\\d+)";

    private final ProjetoService service;
    private final EncerramentoService encerramento;

    public ProjetoController(AutenticacaoService autenticacao, ProjetoService service,
                             EncerramentoService encerramento) {
        super(autenticacao);
        this.service = service;
        this.encerramento = encerramento;
    }

    @Override
    void rotas(Roteador r) {
        r.rota("GET", "/projetos/?", (troca, p) -> Resposta.json(200,
                service.listar(identificar(troca)).stream().map(ProjetoController::resumo).toList()));
        r.rota("POST", "/projetos/?", (troca, p) -> {
            var usuario = identificar(troca);
            var dados = corpo(troca);
            Projeto projeto = service.criar(obrigatorio(dados, "titulo"),
                    dados.getOrDefault("descricao", ""), usuario);
            return Resposta.json(202, Map.of("mensagem", "projeto criado", "id", projeto.getId()));
        });
        r.rota("GET", ID, (troca, p) -> Resposta.json(200,
                detalhe(service.consultar(id(p), identificar(troca)))));
        r.rota("PUT", ID, (troca, p) -> {
            var usuario = identificar(troca);
            var dados = corpo(troca);
            service.editar(id(p), obrigatorio(dados, "titulo"), dados.getOrDefault("descricao", ""),
                    usuario);
            return Resposta.aceita("projeto editado");
        });
        r.rota("POST", ID + "/encerramento", (troca, p) -> {
            List<Certificado> emitidos = encerramento.encerrar(id(p), identificar(troca));
            return Resposta.json(202, Map.of("mensagem", "projeto encerrado",
                    "certificadosEmitidos", emitidos.size()));
        });
        r.rota("POST", ID + "/atividades", (troca, p) -> {
            var usuario = identificar(troca);
            var dados = corpo(troca);
            Atividade atividade = service.adicionarAtividade(id(p), obrigatorio(dados, "titulo"),
                    dados.getOrDefault("descricao", ""), data(obrigatorio(dados, "data"), "data"),
                    inteiro(obrigatorio(dados, "cargaHoraria"), "cargaHoraria"), usuario);
            return Resposta.json(202, Map.of("mensagem", "atividade adicionada",
                    "id", atividade.getId()));
        });
        r.rota("DELETE", ID + "/atividades/(\\d+)", (troca, p) -> {
            service.removerAtividade(id(p), inteiro(p.get(1), "atividadeId"), identificar(troca));
            return Resposta.aceita("atividade removida");
        });
        r.rota("POST", ID + "/participantes", (troca, p) -> {
            var usuario = identificar(troca);
            service.vincular(id(p), obrigatorio(corpo(troca), "matricula"), usuario);
            return Resposta.aceita("aluno vinculado");
        });
        r.rota("DELETE", ID + "/participantes/([^/]+)", (troca, p) -> {
            service.desvincular(id(p), p.get(1), identificar(troca));
            return Resposta.aceita("aluno desvinculado");
        });
        r.rota("PUT", ID + "/criterios", (troca, p) -> {
            var usuario = identificar(troca);
            var dados = corpo(troca);
            service.definirCriterios(id(p), inteiroOpcional(dados, "minimoHoras"),
                    numeroOpcional(dados, "percentualMinimo"), usuario);
            return Resposta.aceita("critérios definidos");
        });
    }

    private static int id(List<String> parametros) {
        return Integer.parseInt(parametros.get(0));
    }

    private static Map<String, Object> resumo(Projeto p) {
        Map<String, Object> dados = new LinkedHashMap<>();
        dados.put("id", p.getId());
        dados.put("titulo", p.getTitulo());
        dados.put("status", p.getStatus().name());
        dados.put("coordenador", p.getCoordenador().getNome());
        return dados;
    }

    private static Map<String, Object> detalhe(Projeto p) {
        Map<String, Object> dados = resumo(p);
        dados.put("descricao", p.getDescricao());
        dados.put("atividades", p.getAtividades().stream().map(ProjetoController::atividade).toList());
        dados.put("participantes", p.getParticipacoes().stream()
                .map(ProjetoController::participante).toList());
        dados.put("criterios", p.getCriterios().getCriterios().stream()
                .map(ProjetoController::criterio).toList());
        return dados;
    }

    private static Map<String, Object> atividade(Atividade a) {
        Map<String, Object> dados = new LinkedHashMap<>();
        dados.put("id", a.getId());
        dados.put("titulo", a.getTitulo());
        dados.put("data", a.getData().toString());
        dados.put("cargaHoraria", a.getCargaHoraria());
        dados.put("presentes", a.getPresentes().stream().map(aluno -> aluno.getMatricula()).toList());
        return dados;
    }

    private static Map<String, Object> participante(Participacao part) {
        Map<String, Object> dados = new LinkedHashMap<>();
        dados.put("matricula", part.getAluno().getMatricula());
        dados.put("nome", part.getAluno().getNome());
        dados.put("inicio", part.getInicio().toString());
        dados.put("fim", part.getFim() == null ? null : part.getFim().toString());
        return dados;
    }

    private static String criterio(CriterioCertificacao c) {
        if (c instanceof MinimoHoras m) {
            return "mínimo de " + m.getCargaHoraria() + " horas";
        }
        if (c instanceof PercentualMinimoPresenca p) {
            return "mínimo de " + p.getPct() + "% de presença";
        }
        return c.getClass().getSimpleName();
    }
}
