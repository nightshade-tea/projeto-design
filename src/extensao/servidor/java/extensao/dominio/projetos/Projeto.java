package extensao.dominio.projetos;

import extensao.dominio.identidade.Administrador;
import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Professor;
import extensao.dominio.identidade.Usuario;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;

/**
 * Agregado Projeto: é a entrada para alterar atividades, participantes,
 * presenças e critérios, e garante que um projeto encerrado não seja alterado.
 * Os cálculos ficam em Participacao e CriteriosCertificacao.
 */
public class Projeto {

    private Integer id;
    private String titulo;
    private String descricao;
    private final Professor coordenador;
    private StatusProjeto status;
    private final List<Atividade> atividades;
    private final List<Participacao> participacoes;
    private final CriteriosCertificacao criterios;

    public Projeto(String titulo, String descricao, Professor coordenador) {
        this(null, titulo, descricao, coordenador, StatusProjeto.ATIVO,
                new ArrayList<>(), new ArrayList<>(), List.of());
    }

    private Projeto(Integer id, String titulo, String descricao, Professor coordenador,
                    StatusProjeto status, List<Atividade> atividades,
                    List<Participacao> participacoes, List<CriterioCertificacao> criterios) {
        validar(titulo);
        if (coordenador == null) {
            throw new IllegalArgumentException("o coordenador é obrigatório");
        }
        this.id = id;
        this.titulo = titulo;
        this.descricao = descricao == null ? "" : descricao;
        this.coordenador = coordenador;
        this.status = status;
        this.atividades = atividades;
        this.participacoes = participacoes;
        this.criterios = new CriteriosCertificacao(criterios);
    }

    /** Recria um projeto já salvo. Usado só pelas implementações dos repositories. */
    public static Projeto restaurar(Integer id, String titulo, String descricao,
                                    Professor coordenador, StatusProjeto status,
                                    List<Atividade> atividades, List<Participacao> participacoes,
                                    List<CriterioCertificacao> criterios) {
        return new Projeto(id, titulo, descricao, coordenador, status,
                new ArrayList<>(atividades), new ArrayList<>(participacoes), criterios);
    }

    public void editar(String titulo, String descricao) {
        exigirAtivo();
        validar(titulo);
        this.titulo = titulo;
        this.descricao = descricao == null ? "" : descricao;
    }

    public void encerrar() {
        exigirAtivo();
        status = StatusProjeto.ENCERRADO;
    }

    /** RN02 e RN03: o coordenador gerencia o projeto, e o administrador gerencia qualquer um. */
    public boolean podeGerenciar(Usuario usuario) {
        return coordenador.equals(usuario) || usuario instanceof Administrador;
    }

    public Atividade adicionarAtividade(String titulo, String descricao, LocalDate data,
                                        int cargaHoraria) {
        exigirAtivo();
        Atividade atividade = new Atividade(titulo, descricao, data, cargaHoraria);
        atividades.add(atividade);
        return atividade;
    }

    public void editarAtividade(Atividade atividade, String titulo, String descricao,
                                LocalDate data, int cargaHoraria) {
        exigirAtivo();
        daqui(atividade).editar(titulo, descricao, data, cargaHoraria);
    }

    /** Remover uma atividade remove também as presenças dela. */
    public void removerAtividade(Atividade atividade) {
        exigirAtivo();
        atividades.remove(daqui(atividade));
    }

    /**
     * Vincula o aluno a partir de hoje. Vincular um aluno já vinculado não
     * cria outra participação, então a escrita pode ser repetida pela fila.
     */
    public void vincular(Aluno aluno) {
        exigirAtivo();
        if (participacaoAtual(aluno) == null) {
            participacoes.add(new Participacao(aluno, LocalDate.now(), null));
        }
    }

    /** Desvincular só encerra a participação, e as presenças e horas continuam. */
    public void desvincular(Aluno aluno) {
        exigirAtivo();
        Participacao atual = participacaoAtual(aluno);
        if (atual != null) {
            atual.encerrar();
        }
    }

    public void definirCriterios(List<CriterioCertificacao> criterios) {
        exigirAtivo();
        this.criterios.definir(criterios);
    }

    /** Recusa alunos que não estavam vinculados na data da atividade. */
    public void registrarPresenca(Atividade atividade, Aluno aluno) {
        exigirAtivo();
        Atividade daqui = daqui(atividade);
        if (!vinculado(aluno, daqui.getData())) {
            throw new RegraNegocioException(
                    "o aluno não estava vinculado ao projeto na data da atividade");
        }
        daqui.registrarPresenca(aluno);
    }

    public void removerPresenca(Atividade atividade, Aluno aluno) {
        exigirAtivo();
        daqui(atividade).removerPresenca(aluno);
    }

    public boolean vinculado(Aluno aluno, LocalDate data) {
        return participacoes.stream()
                .anyMatch(p -> p.getAluno().equals(aluno) && p.ativaEm(data));
    }

    /**
     * Soma as participações do aluno (ele pode ter sido desvinculado e
     * vinculado de novo), contando cada atividade uma vez só.
     */
    public ResumoFrequencia resumoFrequencia(Aluno aluno) {
        List<Atividade> restantes = new ArrayList<>(atividades);
        int horas = 0;
        int presencas = 0;
        int total = 0;
        boolean participou = false;
        for (Participacao p : participacoes) {
            if (!p.getAluno().equals(aluno)) {
                continue;
            }
            participou = true;
            ResumoFrequencia parcial = p.resumoFrequencia(this, restantes);
            horas += parcial.getHorasCumpridas();
            presencas += parcial.getQtdPresencas();
            total += parcial.getQtdAtividades();
            restantes.removeIf(a -> p.ativaEm(a.getData()));
        }
        if (!participou) {
            throw new RegraNegocioException("o aluno não participa do projeto");
        }
        return new ResumoFrequencia(aluno, this, horas, presencas, total);
    }

    /** Um resumo por aluno que participa ou participou do projeto. */
    public List<ResumoFrequencia> resumos() {
        Map<String, Aluno> alunos = new LinkedHashMap<>();
        participacoes.forEach(p -> alunos.putIfAbsent(p.getAluno().getMatricula(), p.getAluno()));
        return alunos.values().stream().map(this::resumoFrequencia).toList();
    }

    /** Alunos que atendem aos critérios, incluindo os já desvinculados. */
    public List<ResumoFrequencia> aprovados() {
        return resumos().stream().filter(criterios::atende).toList();
    }

    /** Busca uma atividade do projeto pelo id. */
    public Atividade atividade(int id) {
        return atividades.stream()
                .filter(a -> a.getId() != null && a.getId() == id)
                .findFirst()
                .orElseThrow(() -> new NoSuchElementException("atividade não encontrada: " + id));
    }

    private Participacao participacaoAtual(Aluno aluno) {
        return participacoes.stream()
                .filter(p -> p.getAluno().equals(aluno) && !p.encerrada())
                .findFirst()
                .orElse(null);
    }

    private Atividade daqui(Atividade atividade) {
        if (!atividades.contains(atividade)) {
            throw new IllegalArgumentException("a atividade não é deste projeto");
        }
        return atividade;
    }

    private void exigirAtivo() {
        if (status == StatusProjeto.ENCERRADO) {
            throw new RegraNegocioException("o projeto está encerrado e não aceita alterações");
        }
    }

    private static void validar(String titulo) {
        if (titulo == null || titulo.isBlank()) {
            throw new IllegalArgumentException("o título é obrigatório");
        }
    }

    /** O id é atribuído pelo repository ao salvar um projeto novo. */
    public void atribuirId(int id) {
        if (this.id != null) {
            throw new IllegalStateException("o projeto já tem id");
        }
        this.id = id;
    }

    public Integer getId() {
        return id;
    }

    public String getTitulo() {
        return titulo;
    }

    public String getDescricao() {
        return descricao;
    }

    public Professor getCoordenador() {
        return coordenador;
    }

    public StatusProjeto getStatus() {
        return status;
    }

    public List<Atividade> getAtividades() {
        return Collections.unmodifiableList(atividades);
    }

    public List<Participacao> getParticipacoes() {
        return Collections.unmodifiableList(participacoes);
    }

    public CriteriosCertificacao getCriterios() {
        return criterios;
    }
}
