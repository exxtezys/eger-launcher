package test;

import com.elium.launcher.Probe;
import com.sun.net.httpserver.HttpServer;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.time.Duration;
import java.util.List;

/** Разведка: какой источник использовать для группы хостов. */
public class ProbeTest {
    private static int failed = 0;

    static void eq(String what, int expected, int actual) {
        if (expected != actual) {
            System.out.println("FAIL " + what + ": ожидалось " + expected + ", получено " + actual);
            failed++;
        }
    }

    public static void main(String[] args) throws Exception {
        HttpServer s = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        s.setExecutor(java.util.concurrent.Executors.newCachedThreadPool());
        s.createContext("/ok", ex -> {
            byte[] b = "x".getBytes();
            ex.sendResponseHeaders(200, b.length);
            try (OutputStream o = ex.getResponseBody()) { o.write(b); }
        });
        s.createContext("/blocked", ex -> { ex.sendResponseHeaders(403, -1); ex.close(); });
        s.createContext("/hang", ex -> {
            try { Thread.sleep(4000); } catch (InterruptedException ignored) {}
            ex.sendResponseHeaders(200, -1);
            ex.close();
        });
        s.start();
        String b = "http://127.0.0.1:" + s.getAddress().getPort();
        String dead = "http://127.0.0.1:1/x";
        Duration t = Duration.ofSeconds(1);

        try {
            eq("оригинал работает — берём его", 0, Probe.pick(b + "/ok", List.of(b + "/ok?m"), t));
            eq("оригинал 403 — первое зеркало", 1, Probe.pick(b + "/blocked", List.of(b + "/ok?m1", b + "/ok?m2"), t));
            eq("оригинал недоступен, первое зеркало тоже — второе", 2, Probe.pick(dead, List.of(b + "/blocked", b + "/ok"), t));
            eq("оригинал висит дольше таймаута — зеркало", 1, Probe.pick(b + "/hang", List.of(b + "/ok"), t));
            eq("всё мертво — -1", -1, Probe.pick(dead, List.of(b + "/blocked"), t));

            long start = System.nanoTime();
            Probe.pick(b + "/hang", List.of(b + "/hang?m"), t);
            long ms = (System.nanoTime() - start) / 1_000_000;
            if (ms > 2500) { System.out.println("FAIL разведка не уложилась в таймаут: " + ms + " мс"); failed++; }
        } finally {
            s.stop(0);
        }

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
        System.exit(0);
    }
}
