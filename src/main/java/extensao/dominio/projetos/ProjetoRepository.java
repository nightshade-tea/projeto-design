package extensao.dominio.projetos;

import extensao.dominio.identidade.Aluno;
import java.util.List;
import java.util.Optional;

/** Salva e busca o agregado Projeto; a implementação fica fora do domínio. */
public interface ProjetoRepository {

    /** Salva o projeto inteiro; um projeto sem id recebe um id novo. */
    void salvar(Projeto projeto);

    Optional<Projeto> buscarPorId(int id);

    List<Projeto> listar();

    /** Projetos em que o aluno tem ou teve participação. */
    List<Projeto> listarPorAluno(Aluno aluno);
}
