package com.elium.launcher;

import java.net.Authenticator;
import java.net.InetSocketAddress;
import java.net.PasswordAuthentication;
import java.net.ProxySelector;
import java.net.http.HttpClient;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Прокси лаунчера: SOCKS5 или HTTP, с необязательной авторизацией.
 * Одна настройка применяется к загрузкам лаунчера, пингу сервера и к самой игре (через JVM-аргументы).
 */
public final class ProxyNet {
    private ProxyNet() {}

    public static boolean enabled(Config cfg) {
        return cfg.proxyOn();
    }

    /** HTTP-клиент с учётом прокси из настроек. Если прокси включён, зеркала не нужны и выключаются. */
    public static HttpClient client(Config cfg) {
        HttpClient.Builder b = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .followRedirects(HttpClient.Redirect.ALWAYS)
                .connectTimeout(Duration.ofSeconds(15));
        Net.setMirrorsEnabled(!enabled(cfg));
        if (!enabled(cfg)) return b.build();

        b.proxy(ProxySelector.of(new InetSocketAddress(cfg.proxyHost(), cfg.proxyPort())));

        if (!cfg.proxyUser().isEmpty()) {
            String user = cfg.proxyUser();
            char[] pass = cfg.proxyPass().toCharArray();
            b.authenticator(new Authenticator() {
                @Override protected PasswordAuthentication getPasswordAuthentication() {
                    return new PasswordAuthentication(user, pass);
                }
            });
        }
        return b.build();
    }

    /** JVM-аргументы для игры: System-свойства прокси, которые читает Netty/URL. */
    public static List<String> jvmArgs(Config cfg) {
        List<String> out = new ArrayList<>();
        if (!enabled(cfg)) return out;
        String host = cfg.proxyHost();
        String port = Integer.toString(cfg.proxyPort());
        if ("socks".equalsIgnoreCase(cfg.proxyType())) {
            out.add("-DsocksProxyHost=" + host);
            out.add("-DsocksProxyPort=" + port);
            out.add("-Djava.net.socks.port=" + port);
            if (!cfg.proxyUser().isEmpty()) {
                out.add("-Djava.net.socks.username=" + cfg.proxyUser());
                out.add("-Djava.net.socks.password=" + cfg.proxyPass());
            }
        } else {
            for (String scheme : new String[]{"http", "https", "ftp"}) {
                out.add("-D" + scheme + ".proxyHost=" + host);
                out.add("-D" + scheme + ".proxyPort=" + port);
            }
            out.add("-Dhttp.nonProxyHosts=localhost|127.*|[::1]");
            if (!cfg.proxyUser().isEmpty()) {
                out.add("-Dhttp.proxyUser=" + cfg.proxyUser());
                out.add("-Dhttp.proxyPassword=" + cfg.proxyPass());
            }
        }
        return out;
    }

    /** Прокси для сырых TCP-соединений (пинг сервера). HTTP-прокси тут не годится. */
    public static java.net.Proxy socketProxy(Config cfg) {
        if (!enabled(cfg) || !"socks".equalsIgnoreCase(cfg.proxyType())) return null;
        return new java.net.Proxy(java.net.Proxy.Type.SOCKS,
                new InetSocketAddress(cfg.proxyHost(), cfg.proxyPort()));
    }

    /** Проверка связи через указанный прокси: возвращает текст для интерфейса. */
    public static String test(String type, String host, int port, String user, String pass) {
        try {
            HttpClient.Builder b = HttpClient.newBuilder()
                    .version(HttpClient.Version.HTTP_1_1)
                    .followRedirects(HttpClient.Redirect.ALWAYS)
                    .connectTimeout(Duration.ofSeconds(10))
                    .proxy(ProxySelector.of(new InetSocketAddress(host, port)));
            if (user != null && !user.isBlank()) {
                char[] pw = (pass == null ? "" : pass).toCharArray();
                String u = user;
                b.authenticator(new Authenticator() {
                    @Override protected PasswordAuthentication getPasswordAuthentication() {
                        return new PasswordAuthentication(u, pw);
                    }
                });
            }
            java.net.http.HttpRequest req = java.net.http.HttpRequest
                    .newBuilder(java.net.URI.create("https://api.github.com/"))
                    .timeout(Duration.ofSeconds(10))
                    .header("User-Agent", "EliumLauncher")
                    .GET()
                    .build();
            int code = b.build().send(req, java.net.http.HttpResponse.BodyHandlers.discarding()).statusCode();
            return "Связь есть · ответ " + code;
        } catch (Exception e) {
            return "Прокси не ответил: " + e.getClass().getSimpleName();
        }
    }

    /** Короткое описание для интерфейса. */
    public static String describe(Config cfg) {
        if (!enabled(cfg)) return "Прокси выключен";
        String kind = "socks".equalsIgnoreCase(cfg.proxyType()) ? "SOCKS5" : "HTTP";
        return kind + " · " + cfg.proxyHost() + ":" + cfg.proxyPort();
    }
}
