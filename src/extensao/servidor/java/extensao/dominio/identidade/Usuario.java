package extensao.dominio.identidade;

import java.util.Objects;

/** Usuário obtido do provedor de identidade, com o papel definido pela subclasse. */
public abstract class Usuario {

    private final String matricula;
    private final String nome;

    protected Usuario(String matricula, String nome) {
        this.matricula = Objects.requireNonNull(matricula, "matricula");
        this.nome = Objects.requireNonNull(nome, "nome");
    }

    public String getMatricula() {
        return matricula;
    }

    public String getNome() {
        return nome;
    }

    /** Mesmo usuário se tiver a mesma matrícula (a matrícula é a chave). */
    @Override
    public final boolean equals(Object outro) {
        return outro instanceof Usuario u && matricula.equals(u.matricula);
    }

    @Override
    public final int hashCode() {
        return matricula.hashCode();
    }
}
