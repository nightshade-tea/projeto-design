package extensao;

import com.sun.net.httpserver.HttpServer;
import extensao.controllers.AutenticacaoController;
import extensao.controllers.CertificadoController;
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
 * Monta a aplicação e é o único lugar que conhece as implementações. Trocar
 * os repositories em CSV pelo banco de dados, ou o gerador de texto pelo de
 * PDF, muda só este arquivo.
 *
 * O login institucional é um sistema externo, iniciado separadamente
 * (institucional.LoginInstitucional), e o servidor só conhece o endereço
 * dele. O cliente web também é um programa separado (cliente.ClienteExtensao).
 * O servidor só oferece a API, e conhece o endereço do cliente para liberar
 * as chamadas das páginas (CORS) e para voltar a ele depois do login.
 */
public final class ServidorExtensao {

    private ServidorExtensao() {
    }

    public static void main(String[] args) throws IOException {
        int porta = Integer.parseInt(System.getProperty("porta", "7080"));
        String urlLogin = System.getProperty("urlLogin", "http://localhost:9080");
        String urlCliente = System.getProperty("urlCliente", "http://localhost:8080");
        Path dados = Path.of(System.getProperty("dados", "dados"));

        HttpServer servidor = iniciar(porta, urlLogin, urlCliente, dados);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> servidor.stop(0)));

        System.out.println("API: http://localhost:" + porta + "/, login em " + urlLogin
                + ", cliente em " + urlCliente + ", dados em " + dados.toAbsolutePath());
    }

    /** Porta 0 escolhe uma porta livre (usado nos testes). */
    public static HttpServer iniciar(int porta, String urlLogin, String urlCliente, Path dados)
            throws IOException {
        HttpServer servidor = HttpServer.create(new InetSocketAddress(porta), 0);
        // o login institucional volta para cá com o token
        String retorno = "http://localhost:" + servidor.getAddress().getPort() + "/sessao";

        ProvedorIdentidadeInstitucional provedor = new ProvedorIdentidadeInstitucional(
                urlLogin, retorno, dados);
        ProjetoRepositoryCsv projetos = new ProjetoRepositoryCsv(dados);
        CertificadoRepositoryCsv certificados = new CertificadoRepositoryCsv(dados, projetos);

        AutenticacaoService autenticacao = new AutenticacaoService(provedor);
        ProjetoService projetoService = new ProjetoService(projetos, provedor);
        EncerramentoService encerramento = new EncerramentoService(projetos, certificados);
        FrequenciaService frequencia = new FrequenciaService(projetos, provedor);
        CertificadoService certificado = new CertificadoService(certificados, new GeradorTxt());

        servidor.createContext("/", new Roteador(urlCliente,
                new AutenticacaoController(autenticacao, urlCliente),
                new ProjetoController(autenticacao, projetoService, encerramento),
                new FrequenciaController(autenticacao, frequencia),
                new CertificadoController(autenticacao, certificado)));
        servidor.start();
        return servidor;
    }
}
