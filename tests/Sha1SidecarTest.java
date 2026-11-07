package test;

import com.elium.launcher.Net;
import com.sun.net.httpserver.HttpServer;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Objects;

/**
 * Контрольная сумма для файла, у которого её нет в метаданных (установщик NeoForge):
 * берём соседний .sha1, с зеркала тоже, если официальный хост молчит.
 */
public class Sha1SidecarTest {
    private static int failed = 0;

    static void eq(String what, Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            System.out.println("FAIL " + what + ": ожидалось " + expected + ", получено " + actual);
            failed++;
        }
    }

    public static void main(String[] args) throws Exception {
        String good = "804b6fe37b75debaa215008b4506d6650dc1b179";

        HttpServer s = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        s.createContext("/ok/installer.jar.sha1", ex -> {
            byte[] b = (good + "  installer.jar\n").getBytes(StandardCharsets.UTF_8);
            ex.sendResponseHeaders(200, b.length);
            try (OutputStream o = ex.getResponseBody()) { o.write(b); }
        });
        s.createContext("/blocked/installer.jar.sha1", ex -> {
            byte[] b = "blocked by provider".getBytes(StandardCharsets.UTF_8);
            ex.sendResponseHeaders(451, b.length);
            try (OutputStream o = ex.getResponseBody()) { o.write(b); }
        });
        s.createContext("/empty/installer.jar.sha1", ex -> { ex.sendResponseHeaders(200, -1); ex.close(); });
        s.start();
        String base = "http://127.0.0.1:" + s.getAddress().getPort() + "/";

        try {
            Net.resetHostOverrides();
            eq("sha1 со своего хоста", good, Net.sha1Sidecar(base + "ok/installer.jar"));

            Net.resetHostOverrides();
            Net.addMirrorForTesting(base + "blocked/installer.jar", base + "ok/installer.jar");
            eq("официальный 451 — берём с зеркала", good, Net.sha1Sidecar(base + "blocked/installer.jar"));

            Net.resetHostOverrides();
            eq("пустой .sha1 — null", null, Net.sha1Sidecar(base + "empty/installer.jar"));

            Net.resetHostOverrides();
            eq("нигде нет — null", null, Net.sha1Sidecar("http://127.0.0.1:1/none/installer.jar"));

            Net.resetHostOverrides();
            String pinned = Net.sha1Sidecar(base + "ok/installer.jar");
            eq("мусор в ответе не проходит", good, pinned);
        } finally {
            s.stop(0);
        }

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
        System.exit(0);
    }
}
