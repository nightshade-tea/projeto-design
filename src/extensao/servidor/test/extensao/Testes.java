package extensao;

import extensao.dominio.certificacao.Certificado;
import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Professor;
import extensao.dominio.identidade.Usuario;
import extensao.dominio.projetos.Atividade;
import extensao.dominio.projetos.MinimoHoras;
import extensao.dominio.projetos.PercentualMinimoPresenca;
import extensao.dominio.projetos.Projeto;
import extensao.dominio.projetos.RegraNegocioException;
import extensao.dominio.projetos.ResumoFrequencia;
import extensao.infraestrutura.CertificadoRepositoryCsv;
import extensao.infraestrutura.GeradorTxt;
import extensao.infraestrutura.ProjetoRepositoryCsv;
import extensao.infraestrutura.ProvedorIdentidadeInstitucional;
import extensao.services.CertificadoService;
import extensao.services.EncerramentoService;
import extensao.services.FrequenciaService;
import extensao.services.NaoEncontradoException;
import extensao.services.ProjetoService;
import extensao.services.SemPermissaoException;
import institucional.LoginInstitucional;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Testes do protótipo, sem bibliotecas: cada teste é um método registrado em
 * main. Uso: make test
 */
public final class Testes {

    interface Teste {
        void executar() throws Exception;
    }

    private static final Professor CARLA = new Professor("P001", "Carla Souza");
    private static final Aluno ANA = new Aluno("2021001", "Ana Martins");
    private static final Aluno BRUNO = new Aluno("2021002", "Bruno Alves");
    private static final LocalDate HOJE = LocalDate.now();

    public static void main(String[] args) {
        Map<String, Teste> testes = new LinkedHashMap<>();

        // ------------------------------------------------------------ domínio

        testes.put("presença só de aluno vinculado na data da atividade", () -> {
            Projeto p = new Projeto("Horta", "", CARLA);
            Atividade a = p.adicionarAtividade("Plantio", "", HOJE, 4);
            falha(RegraNegocioException.class, () -> p.registrarPresenca(a, ANA));
            p.vincular(ANA);
            p.registrarPresenca(a, ANA);
            p.registrarPresenca(a, ANA);
            igual(1, a.getPresentes().size());
        });
        testes.put("resumo soma horas e percentual", () -> {
            Projeto p = new Projeto("Horta", "", CARLA);
            p.vincular(ANA);
            Atividade a1 = p.adicionarAtividade("Plantio", "", HOJE, 4);
            p.adicionarAtividade("Colheita", "", HOJE, 2);
            p.registrarPresenca(a1, ANA);
            ResumoFrequencia r = p.resumoFrequencia(ANA);
            igual(4, r.getHorasCumpridas());
            igual(2, r.getQtdAtividades());
            igual(50.0, r.percentualPresenca());
        });
        testes.put("desvincular mantém as horas", () -> {
            Projeto p = new Projeto("Horta", "", CARLA);
            p.vincular(ANA);
            p.registrarPresenca(p.adicionarAtividade("Plantio", "", HOJE, 4), ANA);
            p.desvincular(ANA);
            p.vincular(ANA);
            igual(4, p.resumoFrequencia(ANA).getHorasCumpridas());
            igual(1, p.resumoFrequencia(ANA).getQtdAtividades());
        });
        testes.put("sem critérios ninguém é aprovado", () -> {
            Projeto p = new Projeto("Horta", "", CARLA);
            p.vincular(ANA);
            p.registrarPresenca(p.adicionarAtividade("Plantio", "", HOJE, 4), ANA);
            igual(0, p.aprovados().size());
            p.definirCriterios(List.of(new MinimoHoras(4), new PercentualMinimoPresenca(75)));
            igual(1, p.aprovados().size());
        });
        testes.put("projeto encerrado não aceita alterações", () -> {
            Projeto p = new Projeto("Horta", "", CARLA);
            p.encerrar();
            falha(RegraNegocioException.class, () -> p.vincular(ANA));
            falha(RegraNegocioException.class, () -> p.editar("Outro", ""));
            falha(RegraNegocioException.class, () -> p.adicionarAtividade("X", "", HOJE, 1));
        });
        testes.put("certificado guarda os dados da emissão", () -> {
            Projeto p = new Projeto("Horta", "", CARLA);
            p.vincular(ANA);
            p.registrarPresenca(p.adicionarAtividade("Plantio", "", HOJE, 4), ANA);
            Certificado c = new Certificado(p.resumoFrequencia(ANA));
            p.editar("Outro título", "");
            igual("Horta", c.getTituloProjeto());
            igual(4, c.getCargaHoraria());
            verdade(c.pertenceA(ANA) && !c.pertenceA(BRUNO));
        });

        // --------------------------------------------- services e CSV

        testes.put("só o coordenador ou um administrador gerencia o projeto", () -> {
            Contexto c = new Contexto();
            Projeto p = c.projetos.criar("Horta", "", c.usuario("token-professor"));
            falha(SemPermissaoException.class,
                    () -> c.projetos.vincular(p.getId(), "2021001", c.usuario("token-professor2")));
            falha(SemPermissaoException.class,
                    () -> c.projetos.criar("X", "", c.usuario("token-aluno")));
            c.projetos.vincular(p.getId(), "2021001", c.usuario("token-admin"));
            falha(NaoEncontradoException.class,
                    () -> c.projetos.vincular(p.getId(), "9999999", c.usuario("token-professor")));
            falha(RegraNegocioException.class,
                    () -> c.projetos.vincular(p.getId(), "P002", c.usuario("token-professor")));
            falha(NaoEncontradoException.class,
                    () -> c.projetos.consultar(99, c.usuario("token-professor")));
        });
        testes.put("CSV guarda e recupera o projeto inteiro", () -> {
            Contexto c = new Contexto();
            Usuario carla = c.usuario("token-professor");
            Projeto p = c.projetos.criar("Horta, \"comunitária\"", "linha 1\nlinha 2", carla);
            c.projetos.vincular(p.getId(), "2021001", carla);
            Atividade a = c.projetos.adicionarAtividade(p.getId(), "Plantio", "", HOJE, 4, carla);
            c.frequencia.registrarPresenca(p.getId(), a.getId(), "2021001", carla);
            c.projetos.definirCriterios(p.getId(), 4, 50.0, carla);
            Projeto lido = new ProjetoRepositoryCsv(c.pasta).buscarPorId(p.getId()).orElseThrow();
            igual("Horta, \"comunitária\"", lido.getTitulo());
            igual("linha 1\nlinha 2", lido.getDescricao());
            igual(2, lido.getCriterios().getCriterios().size());
            igual(4, lido.resumoFrequencia(ANA).getHorasCumpridas());
            igual(1, lido.aprovados().size());
        });
        testes.put("encerrar emite certificados e o aluno baixa o seu", () -> {
            Contexto c = new Contexto();
            Usuario carla = c.usuario("token-professor");
            Projeto p = c.projetos.criar("Horta", "", carla);
            c.projetos.vincular(p.getId(), "2021001", carla);
            c.projetos.vincular(p.getId(), "2021002", carla);
            Atividade a = c.projetos.adicionarAtividade(p.getId(), "Plantio", "", HOJE, 4, carla);
            c.frequencia.registrarPresenca(p.getId(), a.getId(), "2021001", carla);
            c.projetos.definirCriterios(p.getId(), 4, null, carla);
            List<Certificado> emitidos = c.encerramento.encerrar(p.getId(), carla);
            igual(1, emitidos.size());
            falha(RegraNegocioException.class, () -> c.encerramento.encerrar(p.getId(), carla));
            Usuario ana = c.usuario("token-aluno");
            igual(4, c.frequencia.consultarHoras(ana).get(0).getHorasCumpridas());
            int id = c.certificados.listar(ana).get(0).getId();
            String texto = new String(c.certificados.gerarArquivo(id, ana), StandardCharsets.UTF_8);
            verdade(texto.contains("Ana Martins") && texto.contains("4 horas"));
            falha(SemPermissaoException.class,
                    () -> c.certificados.gerarArquivo(id, c.usuario("token-aluno2")));
        });

        // ------------------------------------- login institucional e HTTP

        testes.put("login institucional: senha, validar e cópia local", () -> {
            Path pasta = Files.createTempDirectory("teste");
            LoginInstitucional login = new LoginInstitucional(
                    Path.of("src/institucional/resources/usuarios.csv"));
            login.iniciar(0);
            try {
                ProvedorIdentidadeInstitucional provedor = new ProvedorIdentidadeInstitucional(
                        "http://localhost:" + login.porta(), "http://cliente/", pasta);
                igual(null, login.entrar("carla", "errada"));
                Usuario u = provedor.identificar(login.entrar("carla", "sapato")).orElseThrow();
                verdade(u instanceof Professor && u.getNome().equals("Carla Souza"));
                verdade(provedor.identificar("invalido").isEmpty());
                verdade(provedor.buscarPorMatricula("ana").orElseThrow() instanceof Aluno);
                verdade(provedor.buscarPorMatricula("ninguem").isEmpty());
                login.parar();
                // provedor fora do ar: alunos da cópia local ainda são encontrados
                verdade(provedor.buscarPorMatricula("ana").isPresent());
            } finally {
                login.parar();
            }
        });
        testes.put("cenário completo do diagrama de sequência, por HTTP", () -> {
            Cenario.executar(false);
        });

        int falhas = 0;
        for (Map.Entry<String, Teste> t : testes.entrySet()) {
            try {
                t.getValue().executar();
                System.out.println("ok     " + t.getKey());
            } catch (Throwable e) {
                falhas++;
                System.out.println("FALHOU " + t.getKey() + ": " + e);
            }
        }
        System.out.println();
        System.out.println((testes.size() - falhas) + " de " + testes.size() + " testes passaram");
        System.exit(falhas == 0 ? 0 : 1);
    }

    /** Services ligados a repositories CSV em uma pasta temporária e ao provedor em memória. */
    private static final class Contexto {
        final Path pasta;
        final ProvedorIdentidadeTeste provedor = ProvedorIdentidadeTeste.comUsuariosPadrao("");
        final ProjetoService projetos;
        final FrequenciaService frequencia;
        final EncerramentoService encerramento;
        final CertificadoService certificados;

        Contexto() throws Exception {
            pasta = Files.createTempDirectory("teste");
            ProjetoRepositoryCsv repo = new ProjetoRepositoryCsv(pasta);
            CertificadoRepositoryCsv certRepo = new CertificadoRepositoryCsv(pasta, repo);
            projetos = new ProjetoService(repo, provedor);
            frequencia = new FrequenciaService(repo, provedor);
            encerramento = new EncerramentoService(repo, certRepo);
            certificados = new CertificadoService(certRepo, new GeradorTxt());
        }

        Usuario usuario(String token) {
            return provedor.identificar(token).orElseThrow();
        }
    }

    private static void igual(Object esperado, Object atual) {
        if (esperado == null ? atual != null : !esperado.equals(atual)) {
            throw new AssertionError("esperava " + esperado + ", veio " + atual);
        }
    }

    private static void verdade(boolean condicao) {
        if (!condicao) {
            throw new AssertionError("condição falsa");
        }
    }

    private static void falha(Class<? extends Throwable> tipo, Teste acao) throws Exception {
        try {
            acao.executar();
        } catch (Throwable e) {
            if (tipo.isInstance(e)) {
                return;
            }
            throw new AssertionError("esperava " + tipo.getSimpleName() + ", veio " + e);
        }
        throw new AssertionError("esperava " + tipo.getSimpleName() + ", não lançou nada");
    }
}
