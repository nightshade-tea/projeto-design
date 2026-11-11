package extensao.controllers;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/** GET /  serve a página do cliente web (um arquivo HTML que usa a API). */
public class ClienteController extends Controller {

    private final Path pagina;

    public ClienteController(Path pagina) {
        super(null);
        this.pagina = pagina;
    }

    @Override
    void rotas(Roteador r) {
        r.rota("GET", "/", (troca, p) -> {
            try {
                return Resposta.texto("text/html", Files.readString(pagina, StandardCharsets.UTF_8));
            } catch (IOException e) {
                throw new UncheckedIOException(e);
            }
        });
    }
}
