package extensao;

import com.sun.net.httpserver.HttpServer;
import extensao.controllers.AutenticacaoController;
import extensao.controllers.CertificadoController;
import extensao.controllers.ClienteController;
import extensao.controllers.FrequenciaController;
import extensao.controllers.ProjetoController;
import extensao.controllers.Roteador;
import extensao.infraestrutura.CertificadoRepositoryCsv;
import extensao.infraestrutura.GeradorTxt;
import extensao.infraestrutura.ProjetoRepositoryCsv;
import extensao.infraestrutura.ProvedorIdentidadeInstitucional;
import extensao.services.AutenticacaoService;
import extensao.services.CertificadoService;
import extensao.services.EncerramentoService;
import extensao.services.FrequenciaService;
import extensao.services.ProjetoService;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.file.Path;

/**
 * Monta a aplicação: é o único lugar que conhece as implementações. Trocar
 * os repositories em CSV pelo banco de dados, ou o gerador de texto pelo de
 * PDF, muda só este arquivo.
 *
 * O login institucional é um sistema externo, iniciado separadamente
 * (institucional.LoginInstitucional); o servidor só conhece o endereço dele.
 */
public final class Main {

    private Main() {
    }

    public static void main(String[] args) throws IOException {
        int porta = Integer.parseInt(System.getProperty("porta", "8080"));
        String urlLogin = System.getProperty("urlLogin", "http://localhost:8081");
        Path dados = Path.of(System.getProperty("dados", "src/dados"));
        Path cliente = Path.of(System.getProperty("cliente", "src/main/resources/cliente"));

        HttpServer servidor = iniciar(porta, urlLogin, dados, cliente);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> servidor.stop(0)));

        System.out.println("Cliente web: http://localhost:" + porta + "/, login em " + urlLogin
                + ", dados em " + dados.toAbsolutePath());
    }

    /** Porta 0 escolhe uma porta livre (usado nos testes). */
    public static HttpServer iniciar(int porta, String urlLogin, Path dados, Path cliente)
            throws IOException {
        HttpServer servidor = HttpServer.create(new InetSocketAddress(porta), 0);
        String urlCliente = "http://localhost:" + servidor.getAddress().getPort() + "/sessao";

        ProvedorIdentidadeInstitucional provedor = new ProvedorIdentidadeInstitucional(
                urlLogin, urlCliente, dados);
        ProjetoRepositoryCsv projetos = new ProjetoRepositoryCsv(dados);
        CertificadoRepositoryCsv certificados = new CertificadoRepositoryCsv(dados, projetos);

        AutenticacaoService autenticacao = new AutenticacaoService(provedor);
        ProjetoService projetoService = new ProjetoService(projetos, provedor);
        EncerramentoService encerramento = new EncerramentoService(projetos, certificados);
        FrequenciaService frequencia = new FrequenciaService(projetos, provedor);
        CertificadoService certificado = new CertificadoService(certificados, new GeradorTxt());

        servidor.createContext("/", new Roteador(
                new ClienteController(cliente),
                new AutenticacaoController(autenticacao),
                new ProjetoController(autenticacao, projetoService, encerramento),
                new FrequenciaController(autenticacao, frequencia),
                new CertificadoController(autenticacao, certificado)));
        servidor.start();
        return servidor;
    }
}
