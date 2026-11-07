package test;

import com.elium.launcher.Net;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Перебор источников: если официальный хост отказывает, файл берётся с зеркала.
 * Подстановка проверяется на реальных правилах Mirrors через подмену базового
 * адреса на локальный сервер.
 */
public class NetFallbackTest {
    private static int failed = 0;

    static void check(String what, boolean ok) {
        if (!ok) { System.out.println("FAIL " + what); failed++; }
    }

    static String sha1(byte[] data) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-1").digest(data));
    }

    public static void main(String[] args) throws Exception {
        byte[] content = "hello-mirror".getBytes(StandardCharsets.UTF_8);
        String good = sha1(content);

        AtomicInteger deadHits = new AtomicInteger();
        AtomicInteger goodHits = new AtomicInteger();

        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/dead/file.jar", ex -> {
            deadHits.incrementAndGet();
            ex.sendResponseHeaders(503, -1);
            ex.close();
        });
        server.createContext("/good/file.jar", ex -> {
            goodHits.incrementAndGet();
            ex.sendResponseHeaders(200, content.length);
            try (OutputStream o = ex.getResponseBody()) { o.write(content); }
        });
        server.start();
        int port = server.getAddress().getPort();
        String base = "http://127.0.0.1:" + port + "/";

        Path dir = Files.createTempDirectory("netfallback");
        Path target = dir.resolve("file.jar");

        try {
            // Один источник, который всегда отказывает: перебор должен исчерпаться.
            Net.resetHostOverrides();
            Net.addMirrorForTesting(base + "dead/file.jar", base + "good/file.jar");

            Net.download(new Net.Task(base + "dead/file.jar", target, good, content.length), n -> {});
            check("файл скачан", Files.exists(target));
            check("содержимое совпадает", java.util.Arrays.equals(content, Files.readAllBytes(target)));
            check("отказник получил ровно 1 запрос (было " + deadHits.get() + ")", deadHits.get() == 1);
            check("зеркало получило 1 запрос (было " + goodHits.get() + ")", goodHits.get() == 1);
        } finally {
            server.stop(0);
        }

        // Все источники недоступны — исключение с перечнем и без java.net.
        Net.resetHostOverrides();
        Path target2 = dir.resolve("none.jar");
        String message = null;
        try {
            Net.download(new Net.Task("http://127.0.0.1:1/dead/file.jar", target2, null, -1), n -> {});
        } catch (IOException e) {
            message = e.getMessage();
        }
        check("брошено исключение", message != null);
        check("в тексте нет java.net.", message != null && !message.contains("java.net."));

        // Битое зеркало исключается до конца сессии.
        AtomicInteger badHits = new AtomicInteger();
        HttpServer server2 = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server2.createContext("/dead/file.jar", ex -> {
            ex.sendResponseHeaders(503, -1);
            ex.close();
        });
        server2.createContext("/bad/file.jar", ex -> {
            badHits.incrementAndGet();
            byte[] junk = "junk".getBytes(StandardCharsets.UTF_8);
            ex.sendResponseHeaders(200, junk.length);
            try (OutputStream o = ex.getResponseBody()) { o.write(junk); }
        });
        server2.start();
        String base2 = "http://127.0.0.1:" + server2.getAddress().getPort() + "/";
        try {
            Net.resetHostOverrides();
            Net.addMirrorForTesting(base2 + "dead/file.jar", base2 + "bad/file.jar");
            Path t3 = dir.resolve("bad.jar");
            boolean threw = false;
            try {
                Net.download(new Net.Task(base2 + "dead/file.jar", t3, good, content.length), n -> {});
            } catch (IOException e) {
                threw = true;
            }
            check("битое зеркало даёт ошибку", threw);
            for (int i = 1; i < Net.badMirrorLimit(); i++) {
                try {
                    Net.download(new Net.Task(base2 + "dead/file.jar", dir.resolve("bad" + i + ".jar"), good, content.length), n -> {});
                } catch (IOException ignored) {}
            }
            check("до порога зеркало опрашивалось каждый раз (было " + badHits.get() + ")",
                    badHits.get() == Net.badMirrorLimit());
            int afterLimit = badHits.get();
            try {
                Net.download(new Net.Task(base2 + "dead/file.jar", dir.resolve("badX.jar"), good, content.length), n -> {});
            } catch (IOException ignored) {}
            check("после порога битое зеркало больше не опрашивается (было " + afterLimit + ", стало " + badHits.get() + ")",
                    badHits.get() == afterLimit);
        } finally {
            server2.stop(0);
        }

        // Прокси включён — зеркала выключены, остаётся только оригинал.
        Net.resetHostOverrides();
        Net.setMirrorsEnabled(false);
        check("без зеркал только оригинал",
                Net.candidatesForTesting("https://libraries.minecraft.net/a.jar").equals(java.util.List.of("https://libraries.minecraft.net/a.jar")));
        Net.setMirrorsEnabled(true);
        check("с зеркалами — оригинал и BMCLAPI",
                Net.candidatesForTesting("https://libraries.minecraft.net/a.jar").size() == 2);

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
        System.exit(0);
    }
}
