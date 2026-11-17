package extensao.dominio.projetos;

import extensao.dominio.identidade.Aluno;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** Atividade de um projeto, com a lista de alunos presentes. */
public class Atividade {

    private Integer id;
    private String titulo;
    private String descricao;
    private LocalDate data;
    private int cargaHoraria;
    private final List<Aluno> presentes;

    Atividade(String titulo, String descricao, LocalDate data, int cargaHoraria) {
        this(null, titulo, descricao, data, cargaHoraria, new ArrayList<>());
    }

    private Atividade(Integer id, String titulo, String descricao, LocalDate data,
                      int cargaHoraria, List<Aluno> presentes) {
        if (titulo == null || titulo.isBlank()) {
            throw new IllegalArgumentException("o título da atividade é obrigatório");
        }
        if (data == null) {
            throw new IllegalArgumentException("a data da atividade é obrigatória");
        }
        if (cargaHoraria <= 0) {
            throw new IllegalArgumentException("a carga horária deve ser positiva");
        }
        this.id = id;
        this.titulo = titulo;
        this.descricao = descricao == null ? "" : descricao;
        this.data = data;
        this.cargaHoraria = cargaHoraria;
        this.presentes = presentes;
    }

    /** Recria uma atividade já salva; usado só pelas implementações dos repositories. */
    public static Atividade restaurar(Integer id, String titulo, String descricao, LocalDate data,
                                      int cargaHoraria, List<Aluno> presentes) {
        return new Atividade(id, titulo, descricao, data, cargaHoraria, new ArrayList<>(presentes));
    }

    /** Registrar uma presença já registrada não cria outra. */
    public void registrarPresenca(Aluno aluno) {
        if (!estevePresente(aluno)) {
            presentes.add(aluno);
        }
    }

    public void removerPresenca(Aluno aluno) {
        presentes.removeIf(a -> a.mesmoQue(aluno));
    }

    public boolean estevePresente(Aluno aluno) {
        return presentes.stream().anyMatch(a -> a.mesmoQue(aluno));
    }

    /** O id é atribuído pelo repository ao salvar uma atividade nova. */
    public void atribuirId(int id) {
        if (this.id != null) {
            throw new IllegalStateException("a atividade já tem id");
        }
        this.id = id;
    }

    public Integer getId() {
        return id;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public String getDescricao() {
        return descricao;
    }

    public void setDescricao(String descricao) {
        this.descricao = descricao;
    }

    public LocalDate getData() {
        return data;
    }

    public void setData(LocalDate data) {
        this.data = data;
    }

    public int getCargaHoraria() {
        return cargaHoraria;
    }

    public void setCargaHoraria(int cargaHoraria) {
        this.cargaHoraria = cargaHoraria;
    }

    public List<Aluno> getPresentes() {
        return Collections.unmodifiableList(presentes);
    }
}
