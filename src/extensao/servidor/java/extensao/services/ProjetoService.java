package extensao.services;

import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Professor;
import extensao.dominio.identidade.ProvedorIdentidade;
import extensao.dominio.identidade.Usuario;
import extensao.dominio.projetos.Atividade;
import extensao.dominio.projetos.CriterioCertificacao;
import extensao.dominio.projetos.MinimoHoras;
import extensao.dominio.projetos.PercentualMinimoPresenca;
import extensao.dominio.projetos.Projeto;
import extensao.dominio.projetos.ProjetoRepository;
import extensao.dominio.projetos.RegraNegocioException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.NoSuchElementException;

/** Criar, editar e consultar projetos e gerenciar atividades, participantes e critérios. */
public class ProjetoService {

    private final ProjetoRepository repository;
    private final ProvedorIdentidade provedor;

    public ProjetoService(ProjetoRepository repository, ProvedorIdentidade provedor) {
        this.repository = repository;
        this.provedor = provedor;
    }

    /** RF01 e RN01: só professores criam projetos, e quem cria passa a ser o coordenador. */
    public Projeto criar(String titulo, String descricao, Usuario usuario) {
        if (!(usuario instanceof Professor professor)) {
            throw new SemPermissaoException("só professores criam projetos");
        }
        Projeto projeto = new Projeto(titulo, descricao, professor);
        repository.salvar(projeto);
        return projeto;
    }

    public void editar(int id, String titulo, String descricao, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        projeto.editar(titulo, descricao);
        repository.salvar(projeto);
    }

    /** Qualquer usuário identificado consulta projetos. */
    public Projeto consultar(int id, Usuario usuario) {
        return buscar(id);
    }

    /** O aluno vê os projetos de que participa, e os demais veem todos. */
    public List<Projeto> listar(Usuario usuario) {
        if (usuario instanceof Aluno aluno) {
            return repository.listarPorAluno(aluno);
        }
        return repository.listar();
    }

    public Atividade adicionarAtividade(int id, String titulo, String descricao, LocalDate data,
                                        int cargaHoraria, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        Atividade atividade = projeto.adicionarAtividade(titulo, descricao, data, cargaHoraria);
        repository.salvar(projeto);
        return atividade;
    }

    public void editarAtividade(int id, int atividadeId, String titulo, String descricao,
                                LocalDate data, int cargaHoraria, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        projeto.editarAtividade(buscarAtividade(projeto, atividadeId), titulo, descricao, data,
                cargaHoraria);
        repository.salvar(projeto);
    }

    public void removerAtividade(int id, int atividadeId, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        projeto.removerAtividade(buscarAtividade(projeto, atividadeId));
        repository.salvar(projeto);
    }

    /** RF03: vincula pela matrícula, buscando o aluno no provedor de identidade. */
    public void vincular(int id, String matricula, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        projeto.vincular(buscarAluno(provedor, matricula));
        repository.salvar(projeto);
    }

    public void desvincular(int id, String matricula, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        projeto.desvincular(buscarAluno(provedor, matricula));
        repository.salvar(projeto);
    }

    /** RF06: critérios a partir das opções do sistema. Um valor null deixa a opção de fora. */
    public void definirCriterios(int id, Integer minimoHoras, Double percentualMinimo,
                                 Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        List<CriterioCertificacao> criterios = new ArrayList<>();
        if (minimoHoras != null) {
            criterios.add(new MinimoHoras(minimoHoras));
        }
        if (percentualMinimo != null) {
            criterios.add(new PercentualMinimoPresenca(percentualMinimo));
        }
        projeto.definirCriterios(criterios);
        repository.salvar(projeto);
    }

    private Projeto buscar(int id) {
        return repository.buscarPorId(id)
                .orElseThrow(() -> new NaoEncontradoException("projeto não encontrado: " + id));
    }

    private Projeto buscarGerenciavel(int id, Usuario usuario) {
        Projeto projeto = buscar(id);
        Permissoes.exigirGestor(projeto, usuario);
        return projeto;
    }

    static Atividade buscarAtividade(Projeto projeto, int atividadeId) {
        try {
            return projeto.atividade(atividadeId);
        } catch (NoSuchElementException e) {
            throw new NaoEncontradoException(e.getMessage());
        }
    }

    static Aluno buscarAluno(ProvedorIdentidade provedor, String matricula) {
        Usuario encontrado = provedor.buscarPorMatricula(matricula)
                .orElseThrow(() -> new NaoEncontradoException(
                        "matrícula não encontrada: " + matricula));
        if (!(encontrado instanceof Aluno aluno)) {
            throw new RegraNegocioException("a matrícula não é de um aluno: " + matricula);
        }
        return aluno;
    }
}
