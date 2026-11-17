package extensao.infraestrutura;

import extensao.dominio.identidade.Administrador;
import extensao.dominio.identidade.Aluno;
import extensao.dominio.identidade.Professor;
import extensao.dominio.identidade.ProvedorIdentidade;
import extensao.dominio.identidade.Usuario;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * Acessa o login institucional por HTTP e guarda a cópia local dos usuários
 * (usuarios.csv), com a matrícula como chave. O papel é a subclasse de
 * Usuario, definida pelo vínculo informado pelo provedor (RE02).
 *
 * Se o provedor estiver indisponível, não é possível entrar no sistema, mas
 * alunos que já estão na cópia local ainda podem ser buscados.
 */
public class ProvedorIdentidadeInstitucional implements ProvedorIdentidade {

    private static final List<String> CABECALHO = List.of("matricula", "nome", "papel");

    private final String url;
    private final String retorno;
    private final Path copiaLocal;
    private final HttpClient http = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(3)).build();

    /**
     * url: endereço do login institucional; retorno: para onde o login
     * institucional manda o usuário depois de entrar, com o token.
     */
    public ProvedorIdentidadeInstitucional(String url, String retorno, Path pasta) {
        this.url = url.endsWith("/") ? url.substring(0, url.length() - 1) : url;
        this.retorno = retorno;
        this.copiaLocal = pasta.resolve("usuarios.csv");
    }

    @Override
    public Optional<Usuario> identificar(String token) {
        HttpResponse<String> resposta = get("/validar?token="
                + URLEncoder.encode(token, StandardCharsets.UTF_8));
        if (resposta.statusCode() != 200) {
            return Optional.empty();
        }
        String matricula = resposta.body().trim();
        Optional<Usuario> local = buscarLocal(matricula);
        return local.isPresent() ? local : buscarPorMatricula(matricula);
    }

    @Override
    public Optional<Usuario> buscarPorMatricula(String matricula) {
        HttpResponse<String> resposta;
        try {
            resposta = get("/usuarios/" + URLEncoder.encode(matricula, StandardCharsets.UTF_8));
        } catch (UncheckedIOException indisponivel) {
            return buscarLocal(matricula);
        }
        if (resposta.statusCode() != 200) {
            return Optional.empty();
        }
        String[] c = resposta.body().trim().split(",", -1);
        Usuario usuario = criar(c[0], c[1], c[2]);
        guardar(usuario, c[2]);
        return Optional.of(usuario);
    }

    @Override
    public String urlLogin() {
        return url + "/login?retorno=" + URLEncoder.encode(retorno, StandardCharsets.UTF_8);
    }

    private HttpResponse<String> get(String caminho) {
        try {
            HttpRequest pedido = HttpRequest.newBuilder(URI.create(url + caminho))
                    .timeout(Duration.ofSeconds(5)).GET().build();
            return http.send(pedido, HttpResponse.BodyHandlers.ofString());
        } catch (IOException e) {
            throw new UncheckedIOException("provedor de identidade indisponível", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    private static Usuario criar(String matricula, String nome, String papel) {
        return switch (papel) {
            case "aluno" -> new Aluno(matricula, nome);
            case "professor" -> new Professor(matricula, nome);
            case "administrador" -> new Administrador(matricula, nome);
            default -> throw new IllegalStateException("vínculo desconhecido: " + papel);
        };
    }

    private synchronized Optional<Usuario> buscarLocal(String matricula) {
        return Csv.ler(copiaLocal).stream()
                .filter(l -> l.get(0).equals(matricula))
                .findFirst()
                .map(l -> criar(l.get(0), l.get(1), l.get(2)));
    }

    /** Salvar um usuário que já existe atualiza a cópia em vez de criar outra. */
    private synchronized void guardar(Usuario usuario, String papel) {
        Map<String, List<String>> linhas = new LinkedHashMap<>();
        Csv.ler(copiaLocal).forEach(l -> linhas.put(l.get(0), l));
        linhas.put(usuario.getMatricula(), List.of(usuario.getMatricula(), usuario.getNome(), papel));
        Csv.escrever(copiaLocal, CABECALHO, new ArrayList<>(linhas.values()));
    }
}
