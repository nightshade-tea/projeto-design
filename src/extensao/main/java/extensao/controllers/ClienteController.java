package extensao.controllers;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** Serve as páginas do cliente web (arquivos HTML e JS que usam a API). */
public class ClienteController extends Controller {

    private final Path pasta;

    public ClienteController(Path pasta) {
        super(null);
        this.pasta = pasta;
    }

    @Override
    void rotas(Roteador r) {
        r.rota("GET", "/", (troca, p) -> arquivo("index.html"));
        r.rota("GET", "/([a-z]+\\.(?:html|js))", (troca, p) -> arquivo(p.get(0)));
    }

    private Resposta arquivo(String nome) {
        Path arquivo = pasta.resolve(nome);
        if (!Files.exists(arquivo)) {
            return Resposta.erro(404, "página não encontrada");
        }
        try {
            String tipo = nome.endsWith(".js") ? "text/javascript" : "text/html";
            return Resposta.texto(tipo, Files.readString(arquivo, StandardCharsets.UTF_8));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
