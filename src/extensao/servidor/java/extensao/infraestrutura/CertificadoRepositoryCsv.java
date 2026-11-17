package extensao.infraestrutura;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.certificacao.CertificadoRepository;
import extensao.dominio.identidade.Aluno;
import extensao.dominio.projetos.ProjetoRepository;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * CertificadoRepository em um arquivo CSV, no lugar do banco de dados
 * (CertificadoRepositorySql em arquitetura.md). O projeto do certificado é
 * buscado pelo ProjetoRepository.
 */
public class CertificadoRepositoryCsv implements CertificadoRepository {

    private static final List<String> CABECALHO = List.of("id", "projetoId", "matriculaAluno",
            "nomeAluno", "tituloProjeto", "nomeCoordenador", "cargaHoraria", "emitidoEm");

    private final Path arquivo;
    private final ProjetoRepository projetos;

    public CertificadoRepositoryCsv(Path pasta, ProjetoRepository projetos) {
        this.arquivo = pasta.resolve("certificados.csv");
        this.projetos = projetos;
    }

    @Override
    public synchronized void salvar(Certificado certificado) {
        Map<Integer, List<String>> linhas = linhas();
        if (certificado.getId() == null) {
            certificado.atribuirId(linhas.keySet().stream().mapToInt(i -> i).max().orElse(0) + 1);
        }
        linhas.put(certificado.getId(), List.of(Csv.texto(certificado.getId()),
                Csv.texto(certificado.getProjeto().getId()), certificado.getAluno().getMatricula(),
                certificado.getNomeAluno(), certificado.getTituloProjeto(),
                certificado.getNomeCoordenador(), Csv.texto(certificado.getCargaHoraria()),
                certificado.getEmitidoEm().toString()));
        Csv.escrever(arquivo, CABECALHO, new ArrayList<>(linhas.values()));
    }

    @Override
    public synchronized Optional<Certificado> buscarPorId(int id) {
        return Optional.ofNullable(linhas().get(id)).map(this::certificado);
    }

    @Override
    public synchronized List<Certificado> listarPorAluno(Aluno aluno) {
        return linhas().values().stream()
                .filter(l -> l.get(2).equals(aluno.getMatricula()))
                .map(this::certificado)
                .toList();
    }

    private Map<Integer, List<String>> linhas() {
        Map<Integer, List<String>> linhas = new LinkedHashMap<>();
        for (List<String> l : Csv.ler(arquivo)) {
            linhas.put(Integer.parseInt(l.get(0)), l);
        }
        return linhas;
    }

    private Certificado certificado(List<String> l) {
        int projetoId = Integer.parseInt(l.get(1));
        return Certificado.restaurar(Integer.parseInt(l.get(0)),
                projetos.buscarPorId(projetoId).orElseThrow(() -> new IllegalStateException(
                        "certificado de um projeto que não existe: " + projetoId)),
                new Aluno(l.get(2), l.get(3)), l.get(3), l.get(4), l.get(5),
                Integer.parseInt(l.get(6)), LocalDateTime.parse(l.get(7)));
    }
}
