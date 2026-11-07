package com.elium.launcher;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

/**
 * Разведка источников: один короткий запрос на каждого кандидата, параллельно.
 * Нужна, чтобы игрок с заблокированным хостом не ждал таймаута на каждом из тысяч файлов.
 */
public final class Probe {
    static final Duration TIMEOUT = Duration.ofSeconds(5);

    private Probe() {}

    /**
     * Какой источник использовать: 0 — оригинал, 1..n — номер зеркала, -1 — никто не ответил.
     * Оригинал предпочтительнее: если он ответил, зеркала не ждём.
     */
    public static int pick(String original, List<String> mirrors, Duration timeout) {
        HttpClient http = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .followRedirects(HttpClient.Redirect.ALWAYS)
                .connectTimeout(timeout)
                .build();
        List<String> all = new ArrayList<>();
        all.add(original);
        all.addAll(mirrors);
        List<CompletableFuture<Boolean>> fs = new ArrayList<>();
        for (String u : all) fs.add(ok(http, u, timeout));
        long deadline = System.nanoTime() + timeout.toNanos() + 500_000_000L;
        for (int i = 0; i < fs.size(); i++) {
            long left = Math.max(1, deadline - System.nanoTime());
            try {
                if (fs.get(i).get(left, TimeUnit.NANOSECONDS)) {
                    for (CompletableFuture<Boolean> f : fs) f.cancel(true);
                    return i;
                }
            } catch (Exception e) {
                // не ответил вовремя — следующий
            }
        }
        for (CompletableFuture<Boolean> f : fs) f.cancel(true);
        return -1;
    }

    private static CompletableFuture<Boolean> ok(HttpClient http, String url, Duration timeout) {
        try {
            HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                    .timeout(timeout)
                    .header("User-Agent", "EliumLauncher")
                    .header("Range", "bytes=0-0")
                    .GET()
                    .build();
            return http.sendAsync(req, HttpResponse.BodyHandlers.discarding())
                    .thenApply(r -> r.statusCode() == 200 || r.statusCode() == 206)
                    .exceptionally(e -> false)
                    .orTimeout(timeout.toMillis() + 200, TimeUnit.MILLISECONDS)
                    .exceptionally(e -> false);
        } catch (IllegalArgumentException e) {
            return CompletableFuture.completedFuture(false);
        }
    }

    /** Разведка по всем группам из Mirrors, параллельно. Результат — в Mirrors.prefer. */
    public static void chooseAll() {
        if (!Net.mirrorsEnabled()) return;
        List<Thread> ts = new ArrayList<>();
        for (Mirrors.Group g : Mirrors.groups()) {
            Thread t = new Thread(() -> {
                int i = pick(g.originalProbe, g.mirrorProbes, TIMEOUT);
                Mirrors.prefer(g.name, Math.max(i, 0));
                if (i > 0) System.out.println("загрузка " + g.name + ": зеркало " + g.mirrorProbes.get(i - 1));
                else if (i < 0) System.out.println("загрузка " + g.name + ": ни один источник не ответил при разведке");
            }, "probe-" + g.name);
            t.setDaemon(true);
            t.start();
            ts.add(t);
        }
        for (Thread t : ts) {
            try {
                t.join(TIMEOUT.toMillis() + 2000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }
}
