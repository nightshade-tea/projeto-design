package extensao.services;

import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.ProvedorIdentidade;
import extensao.dominio.identidade.Usuario;
import extensao.dominio.projetos.Participacao;
import extensao.dominio.projetos.Projeto;
import extensao.dominio.projetos.ProjetoRepository;
import extensao.dominio.projetos.ResumoFrequencia;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** RF04 e RF05: registrar e remover presenças e consultar horas. */
public class FrequenciaService {

    private final ProjetoRepository repository;
    private final ProvedorIdentidade provedor;

    public FrequenciaService(ProjetoRepository repository, ProvedorIdentidade provedor) {
        this.repository = repository;
        this.provedor = provedor;
    }

    public void registrarPresenca(int id, int atividadeId, String matricula, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        Aluno aluno = ProjetoService.buscarAluno(provedor, matricula);
        projeto.registrarPresenca(projeto.atividade(atividadeId), aluno);
        repository.salvar(projeto);
    }

    public void removerPresenca(int id, int atividadeId, String matricula, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        Aluno aluno = ProjetoService.buscarAluno(provedor, matricula);
        projeto.removerPresenca(projeto.atividade(atividadeId), aluno);
        repository.salvar(projeto);
    }

    /** As horas do próprio aluno, um resumo por projeto (o total é a soma). */
    public List<ResumoFrequencia> consultarHoras(Usuario usuario) {
        Aluno aluno = Permissoes.exigirAluno(usuario);
        return repository.listarPorAluno(aluno).stream()
                .map(projeto -> projeto.resumoFrequencia(aluno))
                .toList();
    }

    /** As horas de todos os participantes, para o coordenador ou um administrador. */
    public List<ResumoFrequencia> consultarHorasDoProjeto(int id, Usuario usuario) {
        Projeto projeto = buscarGerenciavel(id, usuario);
        Map<String, Aluno> alunos = new LinkedHashMap<>();
        for (Participacao p : projeto.getParticipacoes()) {
            alunos.putIfAbsent(p.getAluno().getMatricula(), p.getAluno());
        }
        return alunos.values().stream().map(projeto::resumoFrequencia).toList();
    }

    private Projeto buscarGerenciavel(int id, Usuario usuario) {
        Projeto projeto = repository.buscarPorId(id)
                .orElseThrow(() -> new NaoEncontradoException("projeto não encontrado: " + id));
        Permissoes.exigirGestor(projeto, usuario);
        return projeto;
    }
}
