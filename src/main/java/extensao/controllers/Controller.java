package extensao.controllers;

import com.sun.net.httpserver.HttpExchange;
import extensao.dominio.identidade.Usuario;
import extensao.services.AutenticacaoService;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.Locale;
import java.util.Map;

/** Base dos controllers: identifica o usuário pelo token e lê o corpo das requisições. */
public abstract class Controller {

    protected final AutenticacaoService autenticacao;

    protected Controller(AutenticacaoService autenticacao) {
        this.autenticacao = autenticacao;
    }

    /** Registra as rotas do controller. */
    abstract void rotas(Roteador roteador);

    /** Lê o token do cabeçalho Authorization: Bearer token. */
    protected Usuario identificar(HttpExchange troca) {
        String cabecalho = troca.getRequestHeaders().getFirst("Authorization");
        String token = null;
        if (cabecalho != null && cabecalho.regionMatches(true, 0, "Bearer ", 0, 7)) {
            token = cabecalho.substring(7).trim();
        }
        return autenticacao.identificar(token);
    }

    protected static Map<String, String> corpo(HttpExchange troca) throws IOException {
        return Json.lerObjeto(new String(troca.getRequestBody().readAllBytes(), StandardCharsets.UTF_8));
    }

    protected static String obrigatorio(Map<String, String> dados, String campo) {
        String valor = dados.get(campo);
        if (valor == null || valor.isBlank()) {
            throw new IllegalArgumentException("campo obrigatório: " + campo);
        }
        return valor.trim();
    }

    protected static int inteiro(String texto, String campo) {
        try {
            return Integer.parseInt(texto.trim());
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(campo + " deve ser um número inteiro");
        }
    }

    protected static Integer inteiroOpcional(Map<String, String> dados, String campo) {
        String valor = dados.get(campo);
        return valor == null || valor.isBlank() ? null : inteiro(valor, campo);
    }

    protected static Double numeroOpcional(Map<String, String> dados, String campo) {
        String valor = dados.get(campo);
        if (valor == null || valor.isBlank()) {
            return null;
        }
        try {
            return Double.parseDouble(valor.trim().replace(',', '.'));
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(campo + " deve ser um número");
        }
    }

    protected static LocalDate data(String texto, String campo) {
        try {
            return LocalDate.parse(texto.trim());
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException(campo + " deve estar no formato AAAA-MM-DD");
        }
    }

    protected static String papel(Usuario usuario) {
        return usuario.getClass().getSimpleName().toLowerCase(Locale.ROOT);
    }
}
