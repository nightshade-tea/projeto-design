package extensao.infraestrutura;

import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Professor;
import extensao.dominio.projetos.Atividade;
import extensao.dominio.projetos.CriterioCertificacao;
import extensao.dominio.projetos.MinimoHoras;
import extensao.dominio.projetos.Participacao;
import extensao.dominio.projetos.PercentualMinimoPresenca;
import extensao.dominio.projetos.Projeto;
import extensao.dominio.projetos.ProjetoRepository;
import extensao.dominio.projetos.StatusProjeto;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * ProjetoRepository em arquivos CSV, um por tabela, no lugar do banco de
 * dados (ProjetoRepositorySql em arquitetura.md). Segue a mesma interface,
 * então trocar pelo banco não muda o domínio nem os services.
 *
 * Cada busca lê os arquivos de novo e devolve objetos novos, como faria um
 * banco. Salvar reescreve as linhas do projeto inteiro (agregado).
 */
public class ProjetoRepositoryCsv implements ProjetoRepository {

    private static final List<String> PROJETOS = List.of(
            "id", "titulo", "descricao", "matriculaCoordenador", "nomeCoordenador", "status");
    private static final List<String> ATIVIDADES = List.of(
            "id", "projetoId", "titulo", "descricao", "data", "cargaHoraria");
    private static final List<String> PRESENCAS = List.of(
            "atividadeId", "matriculaAluno", "nomeAluno");
    private static final List<String> PARTICIPACOES = List.of(
            "projetoId", "matriculaAluno", "nomeAluno", "inicio", "fim");
    private static final List<String> CRITERIOS = List.of("projetoId", "tipo", "valor");

    private final Path projetos;
    private final Path atividades;
    private final Path presencas;
    private final Path participacoes;
    private final Path criterios;

    public ProjetoRepositoryCsv(Path pasta) {
        this.projetos = pasta.resolve("projetos.csv");
        this.atividades = pasta.resolve("atividades.csv");
        this.presencas = pasta.resolve("presencas.csv");
        this.participacoes = pasta.resolve("participacoes.csv");
        this.criterios = pasta.resolve("criterios.csv");
    }

    @Override
    public synchronized void salvar(Projeto projeto) {
        Map<Integer, Projeto> todos = carregar();
        if (projeto.getId() == null) {
            projeto.atribuirId(todos.keySet().stream().mapToInt(i -> i).max().orElse(0) + 1);
        }
        int proximaAtividade = todos.values().stream()
                .flatMap(p -> p.getAtividades().stream())
                .mapToInt(Atividade::getId).max().orElse(0);
        for (Atividade a : projeto.getAtividades()) {
            if (a.getId() == null) {
                a.atribuirId(++proximaAtividade);
            }
        }
        todos.put(projeto.getId(), projeto);
        gravar(todos);
    }

    @Override
    public synchronized Optional<Projeto> buscarPorId(int id) {
        return Optional.ofNullable(carregar().get(id));
    }

    @Override
    public synchronized List<Projeto> listar() {
        return new ArrayList<>(carregar().values());
    }

    @Override
    public synchronized List<Projeto> listarPorAluno(Aluno aluno) {
        return carregar().values().stream()
                .filter(p -> p.getParticipacoes().stream()
                        .anyMatch(part -> part.getAluno().equals(aluno)))
                .toList();
    }

    private Map<Integer, Projeto> carregar() {
        Map<Integer, List<Aluno>> presentes = new LinkedHashMap<>();
        for (List<String> l : Csv.ler(presencas)) {
            presentes.computeIfAbsent(Integer.parseInt(l.get(0)), k -> new ArrayList<>())
                    .add(new Aluno(l.get(1), l.get(2)));
        }
        Map<Integer, List<Atividade>> atividadesPorProjeto = new LinkedHashMap<>();
        for (List<String> l : Csv.ler(atividades)) {
            int id = Integer.parseInt(l.get(0));
            atividadesPorProjeto.computeIfAbsent(Integer.parseInt(l.get(1)), k -> new ArrayList<>())
                    .add(Atividade.restaurar(id, l.get(2), l.get(3), LocalDate.parse(l.get(4)),
                            Integer.parseInt(l.get(5)), presentes.getOrDefault(id, List.of())));
        }
        Map<Integer, List<Participacao>> participacoesPorProjeto = new LinkedHashMap<>();
        for (List<String> l : Csv.ler(participacoes)) {
            participacoesPorProjeto
                    .computeIfAbsent(Integer.parseInt(l.get(0)), k -> new ArrayList<>())
                    .add(new Participacao(new Aluno(l.get(1), l.get(2)), LocalDate.parse(l.get(3)),
                            l.get(4).isEmpty() ? null : LocalDate.parse(l.get(4))));
        }
        Map<Integer, List<CriterioCertificacao>> criteriosPorProjeto = new LinkedHashMap<>();
        for (List<String> l : Csv.ler(criterios)) {
            criteriosPorProjeto.computeIfAbsent(Integer.parseInt(l.get(0)), k -> new ArrayList<>())
                    .add(criterio(l.get(1), l.get(2)));
        }
        Map<Integer, Projeto> todos = new LinkedHashMap<>();
        for (List<String> l : Csv.ler(projetos)) {
            int id = Integer.parseInt(l.get(0));
            todos.put(id, Projeto.restaurar(id, l.get(1), l.get(2),
                    new Professor(l.get(3), l.get(4)),
                    StatusProjeto.valueOf(l.get(5)),
                    atividadesPorProjeto.getOrDefault(id, List.of()),
                    participacoesPorProjeto.getOrDefault(id, List.of()),
                    criteriosPorProjeto.getOrDefault(id, List.of())));
        }
        return todos;
    }

    private void gravar(Map<Integer, Projeto> todos) {
        List<List<String>> linhasProjetos = new ArrayList<>();
        List<List<String>> linhasAtividades = new ArrayList<>();
        List<List<String>> linhasPresencas = new ArrayList<>();
        List<List<String>> linhasParticipacoes = new ArrayList<>();
        List<List<String>> linhasCriterios = new ArrayList<>();
        for (Projeto p : todos.values()) {
            String id = String.valueOf(p.getId());
            linhasProjetos.add(List.of(id, p.getTitulo(), p.getDescricao(),
                    p.getCoordenador().getMatricula(), p.getCoordenador().getNome(),
                    p.getStatus().name()));
            for (Atividade a : p.getAtividades()) {
                linhasAtividades.add(List.of(String.valueOf(a.getId()), id, a.getTitulo(),
                        a.getDescricao(), a.getData().toString(),
                        String.valueOf(a.getCargaHoraria())));
                for (Aluno aluno : a.getPresentes()) {
                    linhasPresencas.add(List.of(String.valueOf(a.getId()), aluno.getMatricula(),
                            aluno.getNome()));
                }
            }
            for (Participacao part : p.getParticipacoes()) {
                linhasParticipacoes.add(List.of(id, part.getAluno().getMatricula(),
                        part.getAluno().getNome(), part.getInicio().toString(),
                        Objects.toString(part.getFim(), "")));
            }
            for (CriterioCertificacao c : p.getCriterios().getCriterios()) {
                linhasCriterios.add(linhaCriterio(id, c));
            }
        }
        Csv.escrever(projetos, PROJETOS, linhasProjetos);
        Csv.escrever(atividades, ATIVIDADES, linhasAtividades);
        Csv.escrever(presencas, PRESENCAS, linhasPresencas);
        Csv.escrever(participacoes, PARTICIPACOES, linhasParticipacoes);
        Csv.escrever(criterios, CRITERIOS, linhasCriterios);
    }

    private static List<String> linhaCriterio(String projetoId, CriterioCertificacao c) {
        return switch (c) {
            case MinimoHoras m ->
                    List.of(projetoId, "MinimoHoras", String.valueOf(m.getCargaHoraria()));
            case PercentualMinimoPresenca p ->
                    List.of(projetoId, "PercentualMinimoPresenca", String.valueOf(p.getPct()));
            default -> throw new IllegalArgumentException(
                    "critério sem formato no CSV: " + c.getClass().getName());
        };
    }

    private static CriterioCertificacao criterio(String tipo, String valor) {
        return switch (tipo) {
            case "MinimoHoras" -> new MinimoHoras(Integer.parseInt(valor));
            case "PercentualMinimoPresenca" ->
                    new PercentualMinimoPresenca(Double.parseDouble(valor));
            default -> throw new IllegalStateException("critério desconhecido no CSV: " + tipo);
        };
    }
}
