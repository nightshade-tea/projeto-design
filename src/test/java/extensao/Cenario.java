package extensao;

import com.sun.net.httpserver.HttpServer;
import institucional.LoginInstitucional;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Reproduz o cenário completo do diagrama de sequência
 * (docs/diagramas/sequencia.svg), mensagem por mensagem, por HTTP: o
 * professor entra pelo login institucional, consulta o usuário (com o
 * fragmento break do token inválido), cria um projeto e vincula um aluno.
 *
 * Sobe o login institucional e o servidor em portas livres, com os dados em
 * uma pasta temporária. Uso: make cenario
 */
public final class Cenario {

    private final HttpClient http = HttpClient.newHttpClient(); // não segue redirecionamentos
    private final boolean imprimir;

    private Cenario(boolean imprimir) {
        this.imprimir = imprimir;
    }

    public static void main(String[] args) throws Exception {
        executar(true);
    }

    /**
     * Sobe o login institucional e o servidor, executa o cenário e para os
     * dois; lança AssertionError se alguma resposta for diferente do diagrama.
     */
    static void executar(boolean imprimir) throws Exception {
        Path dados = Files.createTempDirectory("cenario");
        LoginInstitucional login = new LoginInstitucional(
                Path.of("src/main/resources/usuarios-institucionais.csv"));
        login.iniciar(0);
        HttpServer servidor = Main.iniciar(0, "http://localhost:" + login.porta(), dados,
                Path.of("src/main/resources/cliente"));
        try {
            new Cenario(imprimir).executar("http://localhost:" + servidor.getAddress().getPort());
            if (imprimir) {
                System.out.println("\nCenário reproduzido. Dados salvos em " + dados);
            }
        } finally {
            servidor.stop(0);
            login.parar();
        }
    }

    private void executar(String servidor) throws Exception {

        passo("Login: o servidor redireciona para o login institucional");
        HttpResponse<String> r = get(servidor + "/login", null);
        esperar(r, 302, "login()");
        String urlLogin = r.headers().firstValue("Location").orElseThrow();
        mostrar("302 Found (" + urlLogin + ")");

        passo("O cliente entra no login institucional (a senha não passa pelo servidor)");
        String retorno = java.net.URLDecoder.decode(urlLogin.replaceAll(".*retorno=", ""),
                StandardCharsets.UTF_8);
        String loginPost = urlLogin.replaceAll("\\?.*", "");
        r = postForm(loginPost, "matricula=P001&senha=senha123&retorno="
                + URLEncoder.encode(retorno, StandardCharsets.UTF_8));
        esperar(r, 302, "entrar(matricula, senha)");
        String volta = r.headers().firstValue("Location").orElseThrow();
        Matcher m = Pattern.compile("token=([^&]+)").matcher(volta);
        if (!m.find()) {
            throw new AssertionError("sem token no redirecionamento: " + volta);
        }
        String token = m.group(1);
        mostrar("302 Found (" + volta + ")");

        passo("consultarUsuario com token inválido: fragmento break");
        r = get(servidor + "/me", "token-que-nao-existe");
        esperar(r, 401, "consultarUsuario(token)");
        mostrar("401 Unauthorized " + r.body());

        passo("consultarUsuario com o token do login: validar(token) no login institucional");
        r = get(servidor + "/me", token);
        esperar(r, 200, "consultarUsuario(token)");
        mostrar("200 OK " + r.body());

        passo("Criar projeto");
        r = postJson(servidor + "/projetos", token,
                "{\"titulo\":\"Horta comunitária\",\"descricao\":\"Horta na escola do bairro\"}");
        esperar(r, 202, "criar(token, titulo, descricao)");
        mostrar("202 Accepted " + r.body());
        Matcher id = Pattern.compile("\"id\":(\\d+)").matcher(r.body());
        if (!id.find()) {
            throw new AssertionError("sem id na resposta: " + r.body());
        }

        passo("Vincular aluno: buscarPorMatricula(matricula) no provedor de identidade");
        String projeto = servidor + "/projetos/" + id.group(1);
        r = postJson(projeto + "/participantes", token, "{\"matricula\":\"2021001\"}");
        esperar(r, 202, "vincular(token, id, matricula)");
        mostrar("202 Accepted " + r.body());

        passo("Conferência: o projeto salvo tem o aluno vinculado");
        r = get(projeto, token);
        esperar(r, 200, "consultar(token, id)");
        if (!r.body().contains("\"matricula\":\"2021001\"")) {
            throw new AssertionError("aluno não vinculado: " + r.body());
        }
        mostrar("200 OK " + r.body());
    }

    private void passo(String texto) {
        if (imprimir) {
            System.out.println("\n== " + texto);
        }
    }

    private void mostrar(String texto) {
        if (imprimir) {
            System.out.println("   <- " + texto);
        }
    }

    private void esperar(HttpResponse<String> r, int status, String mensagem) {
        if (imprimir) {
            System.out.println("   -> " + mensagem + "  [" + r.request().method() + " " + r.uri() + "]");
        }
        if (r.statusCode() != status) {
            throw new AssertionError(mensagem + ": esperava " + status + ", veio " + r.statusCode()
                    + " " + r.body());
        }
    }

    private HttpResponse<String> get(String url, String token) throws IOException, InterruptedException {
        HttpRequest.Builder b = HttpRequest.newBuilder(URI.create(url)).GET();
        if (token != null) {
            b.header("Authorization", "Bearer " + token);
        }
        return http.send(b.build(), HttpResponse.BodyHandlers.ofString());
    }

    private HttpResponse<String> postJson(String url, String token, String json)
            throws IOException, InterruptedException {
        return http.send(HttpRequest.newBuilder(URI.create(url))
                .header("Authorization", "Bearer " + token)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json)).build(),
                HttpResponse.BodyHandlers.ofString());
    }

    private HttpResponse<String> postForm(String url, String form)
            throws IOException, InterruptedException {
        return http.send(HttpRequest.newBuilder(URI.create(url))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(form)).build(),
                HttpResponse.BodyHandlers.ofString());
    }
}
