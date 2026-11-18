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
        validar(titulo, data, cargaHoraria);
        this.id = id;
        this.titulo = titulo;
        this.descricao = descricao == null ? "" : descricao;
        this.data = data;
        this.cargaHoraria = cargaHoraria;
        this.presentes = presentes;
    }

    /** Recria uma atividade já salva. Usado só pelas implementações dos repositories. */
    public static Atividade restaurar(Integer id, String titulo, String descricao, LocalDate data,
                                      int cargaHoraria, List<Aluno> presentes) {
        return new Atividade(id, titulo, descricao, data, cargaHoraria, new ArrayList<>(presentes));
    }

    /** Altera os dados da atividade e mantém as presenças. */
    void editar(String titulo, String descricao, LocalDate data, int cargaHoraria) {
        validar(titulo, data, cargaHoraria);
        this.titulo = titulo;
        this.descricao = descricao == null ? "" : descricao;
        this.data = data;
        this.cargaHoraria = cargaHoraria;
    }

    /** Registrar uma presença já registrada não cria outra. */
    void registrarPresenca(Aluno aluno) {
        if (!estevePresente(aluno)) {
            presentes.add(aluno);
        }
    }

    void removerPresenca(Aluno aluno) {
        presentes.remove(aluno);
    }

    public boolean estevePresente(Aluno aluno) {
        return presentes.contains(aluno);
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


    public String getDescricao() {
        return descricao;
    }


    public LocalDate getData() {
        return data;
    }


    public int getCargaHoraria() {
        return cargaHoraria;
    }


    public List<Aluno> getPresentes() {
        return Collections.unmodifiableList(presentes);
    }

    private static void validar(String titulo, LocalDate data, int cargaHoraria) {
        if (titulo == null || titulo.isBlank()) {
            throw new IllegalArgumentException("o título da atividade é obrigatório");
        }
        if (data == null) {
            throw new IllegalArgumentException("a data da atividade é obrigatória");
        }
        if (cargaHoraria <= 0) {
            throw new IllegalArgumentException("a carga horária deve ser positiva");
        }
    }
}
