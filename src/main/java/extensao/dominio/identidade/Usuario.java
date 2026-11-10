package extensao.dominio.identidade;

/** Usuário obtido do provedor de identidade; o papel é a subclasse. */
public abstract class Usuario {

    private String matricula;
    private String nome;

    protected Usuario(String matricula, String nome) {
        this.matricula = matricula;
        this.nome = nome;
    }

    public String getMatricula() {
        return matricula;
    }

    public void setMatricula(String matricula) {
        this.matricula = matricula;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    /** Mesmo usuário se tiver a mesma matrícula (a matrícula é a chave). */
    public boolean mesmoQue(Usuario outro) {
        return outro != null && matricula.equals(outro.matricula);
    }
}
