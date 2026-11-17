package institucional;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Simula o serviço de login único da universidade. É um sistema externo,
 * um programa separado do servidor (que não depende deste pacote) e que só
 * conversa com ele por HTTP.
 * Os usuários e as senhas ficam em um arquivo CSV
 * (matricula,senha,nome,vinculo), e os tokens ficam em memória.
 *
 *   GET  /login?retorno=url     página de login
 *   POST /login                 entrar(matricula, senha): 302 para o retorno com o token
 *   GET  /validar?token=...     validar(token): devolve a matrícula, ou 401
 *   GET  /usuarios/{matricula}  devolve "matricula,nome,vinculo", ou 404
 */
public class LoginInstitucional {

    private record Conta(String matricula, String senha, String nome, String vinculo) {
    }

    private final Map<String, Conta> contas = new LinkedHashMap<>();
    private final Map<String, String> tokens = new ConcurrentHashMap<>();
    private HttpServer servidor;

    /** Uso: java -Dporta=9080 -Dusuarios=arquivo.csv institucional.LoginInstitucional */
    public static void main(String[] args) throws IOException {
        int porta = Integer.parseInt(System.getProperty("porta", "9080"));
        Path usuarios = Path.of(System.getProperty("usuarios",
                "src/institucional/resources/usuarios.csv"));
        new LoginInstitucional(usuarios).iniciar(porta);
        System.out.println("Login institucional (simulado): http://localhost:" + porta
                + "/login, usuários em " + usuarios);
    }

    public LoginInstitucional(Path usuarios) {
        try {
            List<String> linhas = Files.readAllLines(usuarios, StandardCharsets.UTF_8);
            for (String linha : linhas.subList(1, linhas.size())) {
                if (linha.isBlank()) {
                    continue;
                }
                String[] c = linha.split(",", -1);
                contas.put(c[0], new Conta(c[0], c[1], c[2], c[3]));
            }
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public void iniciar(int porta) throws IOException {
        servidor = HttpServer.create(new InetSocketAddress(porta), 0);
        servidor.createContext("/login", this::login);
        servidor.createContext("/validar", this::validar);
        servidor.createContext("/usuarios/", this::usuario);
        servidor.start();
    }

    public void parar() {
        if (servidor != null) {
            servidor.stop(0);
        }
    }

    /** Porta em uso (útil quando iniciado na porta 0, nos testes). */
    public int porta() {
        return servidor.getAddress().getPort();
    }

    /** Entrar sem a página, usado nos testes: devolve o token, ou null. */
    public String entrar(String matricula, String senha) {
        Conta conta = contas.get(matricula);
        if (conta == null || !conta.senha().equals(senha)) {
            return null;
        }
        String token = UUID.randomUUID().toString();
        tokens.put(token, matricula);
        return token;
    }

    private void login(HttpExchange troca) throws IOException {
        if (troca.getRequestMethod().equals("GET")) {
            String retorno = parametros(troca.getRequestURI().getRawQuery()).getOrDefault("retorno", "");
            enviar(troca, 200, "text/html", pagina(retorno, ""));
            return;
        }
        Map<String, String> form = parametros(
                new String(troca.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
        String retorno = form.getOrDefault("retorno", "");
        String token = entrar(form.get("matricula"), form.get("senha"));
        if (token == null) {
            enviar(troca, 401, "text/html", pagina(retorno, "Matrícula ou senha inválida."));
        } else if (!retorno.isEmpty()) {
            String separador = retorno.contains("?") ? "&" : "?";
            troca.getResponseHeaders().set("Location", retorno + separador + "token="
                    + URLEncoder.encode(token, StandardCharsets.UTF_8));
            enviar(troca, 302, "text/plain", "");
        } else {
            // sem cliente web no protótipo: mostra o token para usar no cabeçalho Authorization
            enviar(troca, 200, "text/html", "<!doctype html><meta charset=utf-8><p>Token:</p><pre>"
                    + token + "</pre><p>Use no cabeçalho <code>Authorization: Bearer " + token
                    + "</code></p>");
        }
    }

    private void validar(HttpExchange troca) throws IOException {
        String token = parametros(troca.getRequestURI().getRawQuery()).get("token");
        String matricula = token == null ? null : tokens.get(token);
        if (matricula == null) {
            enviar(troca, 401, "text/plain", "token inválido");
        } else {
            enviar(troca, 200, "text/plain", matricula);
        }
    }

    private void usuario(HttpExchange troca) throws IOException {
        String matricula = troca.getRequestURI().getPath().substring("/usuarios/".length());
        Conta conta = contas.get(matricula);
        if (conta == null) {
            enviar(troca, 404, "text/plain", "matrícula não encontrada");
        } else {
            enviar(troca, 200, "text/csv", conta.matricula() + "," + conta.nome() + "," + conta.vinculo());
        }
    }

    private static String pagina(String retorno, String erro) {
        return """
                <!doctype html><meta charset=utf-8><title>Login institucional (simulado)</title>
                <h1>Login institucional (simulado)</h1>
                <p style="color:#b00">%s</p>
                <form method=post action=/login>
                  <input type=hidden name=retorno value="%s">
                  <p><label>Matrícula <input name=matricula></label></p>
                  <p><label>Senha <input name=senha type=password></label></p>
                  <p><button>Entrar</button></p>
                </form>
                """.formatted(erro, html(retorno));
    }

    private static String html(String s) {
        return s.replace("&", "&amp;").replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;");
    }

    private static Map<String, String> parametros(String texto) {
        Map<String, String> parametros = new HashMap<>();
        if (texto == null || texto.isEmpty()) {
            return parametros;
        }
        for (String par : texto.split("&")) {
            int igual = par.indexOf('=');
            String chave = igual < 0 ? par : par.substring(0, igual);
            String valor = igual < 0 ? "" : par.substring(igual + 1);
            parametros.put(URLDecoder.decode(chave, StandardCharsets.UTF_8),
                    URLDecoder.decode(valor, StandardCharsets.UTF_8));
        }
        return parametros;
    }

    private static void enviar(HttpExchange troca, int status, String tipo, String corpo)
            throws IOException {
        byte[] bytes = corpo.getBytes(StandardCharsets.UTF_8);
        troca.getResponseHeaders().set("Content-Type", tipo + "; charset=utf-8");
        troca.sendResponseHeaders(status, bytes.length == 0 ? -1 : bytes.length);
        if (bytes.length > 0) {
            try (OutputStream saida = troca.getResponseBody()) {
                saida.write(bytes);
            }
        }
        troca.close();
    }
}
