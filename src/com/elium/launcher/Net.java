package com.elium.launcher;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.time.Duration;
import java.util.HexFormat;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public final class Net {
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .followRedirects(HttpClient.Redirect.ALWAYS)
            .connectTimeout(Duration.ofSeconds(15))
            .build();

    private Net() {}

    /** One file to fetch. sha1/size may be null/-1 when unknown. */
    public record Task(String url, Path target, String sha1, long size) {}

    /** Loading-screen feedback. All methods may be called from worker threads. */
    public interface Progress {
        /** Status line + file counter (total <= 1 = no counter). */
        void update(String text, int done, int total);

        /** A new installation step begins (see LauncherApp.STEPS keys). */
        default void stage(String key) {}

        /** Name of the file currently being processed (null = none). */
        default void file(String name) {}

        /** Downloaded bytes of the current batch (total < 0 = unknown). */
        default void bytes(long done, long total) {}
    }

    /** Receives downloaded byte counts (negative = rollback after a failed attempt). */
    public interface Counter {
        void add(long n);

        default void length(long n) {}
    }

    public static String getText(String url) throws IOException {
        try {
            HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                    .timeout(Duration.ofSeconds(30))
                    .header("User-Agent", "EliumLauncher")
                    .build();
            HttpResponse<String> r = HTTP.send(req, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            if (r.statusCode() != 200) throw new IOException("HTTP " + r.statusCode() + " for " + url);
            return r.body();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("interrupted", e);
        }
    }

    public static boolean isValid(Path file, String sha1, long size) throws IOException {
        if (!Files.isRegularFile(file)) return false;
        if (size >= 0 && Files.size(file) != size) return false;
        return sha1 == null || sha1.equalsIgnoreCase(sha1(file));
    }

    public static String sha1(Path file) throws IOException {
        try (InputStream in = Files.newInputStream(file)) {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) md.update(buf, 0, n);
            return HexFormat.of().formatHex(md.digest());
        } catch (java.security.NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    public static void download(Task t) throws IOException {
        download(t, n -> {});
    }

    /** Streams the file to <target>.part, reporting bytes to the counter, verifies, then moves into place. */
    public static void download(Task t, Counter c) throws IOException {
        IOException last = null;
        for (int attempt = 1; attempt <= 3; attempt++) {
            Path tmp = t.target().resolveSibling(t.target().getFileName() + ".part");
            long got = 0;
            try {
                Files.createDirectories(t.target().getParent());
                HttpRequest req = HttpRequest.newBuilder(URI.create(t.url()))
                        .timeout(Duration.ofMinutes(5))
                        .header("User-Agent", "EliumLauncher")
                        .build();
                HttpResponse<InputStream> r = HTTP.send(req, HttpResponse.BodyHandlers.ofInputStream());
                try (InputStream in = r.body()) {
                    if (r.statusCode() != 200) throw new IOException("HTTP " + r.statusCode() + " for " + t.url());
                    c.length(r.headers().firstValueAsLong("content-length").orElse(-1));
                    try (OutputStream out = Files.newOutputStream(tmp)) {
                        byte[] buf = new byte[65536];
                        int n;
                        while ((n = in.read(buf)) > 0) {
                            out.write(buf, 0, n);
                            got += n;
                            c.add(n);
                        }
                    }
                }
                if (!isValid(tmp, t.sha1(), t.size())) throw new IOException("Checksum mismatch: " + t.url());
                Files.move(tmp, t.target(), StandardCopyOption.REPLACE_EXISTING);
                return;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new IOException("interrupted", e);
            } catch (IOException e) {
                last = e;
                c.add(-got);
                Files.deleteIfExists(tmp);
            }
        }
        throw last;
    }

    /** Single download with live byte progress (size taken from Content-Length). */
    public static void downloadOne(String label, Task t, Progress p) throws IOException {
        p.update(label, 0, 0);
        p.file(t.target().getFileName().toString());
        AtomicLong done = new AtomicLong();
        long[] total = {t.size()};
        p.bytes(0, total[0]);
        download(t, new Counter() {
            @Override public void add(long n) { p.bytes(done.addAndGet(n), total[0]); }
            @Override public void length(long n) { if (n > 0) total[0] = n; }
        });
        p.file(null);
    }

    /** Downloads every task whose target is missing or invalid, in parallel. */
    public static void downloadAll(String label, List<Task> tasks, Progress p) throws IOException {
        downloadAll(label, tasks, p, null);
    }

    public static void downloadAll(String label, List<Task> tasks, Progress p, Path reuseFromLaunchersInto) throws IOException {
        Path gameDir = reuseFromLaunchersInto;
        p.bytes(-1, -1);
        List<Task> todo = new java.util.ArrayList<>();
        int checked = 0, reused = 0;
        for (Task t : tasks) {
            if (!isValid(t.target(), t.sha1(), t.size())) {
                if (gameDir != null && LocalCache.tryCopy(gameDir, t.target(), t.sha1(), t.size())) reused++;
                else todo.add(t);
            }
            checked++;
            if (tasks.size() > 1 && (checked % 50 == 0 || checked == tasks.size())) {
                p.update((reused > 0 ? "Берём с компьютера: " : "Проверка файлов: ") + label.toLowerCase(),
                        checked, tasks.size());
            }
        }
        if (reused > 0) System.out.println(label + ": взято с компьютера " + reused + ", скачать " + todo.size());
        if (todo.isEmpty()) return;

        long known = 0;
        boolean allKnown = true;
        for (Task t : todo) {
            if (t.size() >= 0) known += t.size(); else allKnown = false;
        }
        long total = allKnown ? known : -1;
        AtomicLong bytes = new AtomicLong();
        AtomicInteger done = new AtomicInteger();
        p.update(label + ": скачивание", 0, todo.size());
        p.bytes(0, total);
        Counter counter = n -> p.bytes(bytes.addAndGet(n), total);

        ExecutorService pool = Executors.newFixedThreadPool(12);
        try {
            List<Future<?>> fs = new java.util.ArrayList<>();
            for (Task t : todo) {
                fs.add(pool.submit(() -> {
                    p.file(t.target().getFileName().toString());
                    download(t, counter);
                    p.update(label + ": скачивание", done.incrementAndGet(), todo.size());
                    return null;
                }));
            }
            for (Future<?> f : fs) {
                try {
                    f.get();
                } catch (java.util.concurrent.ExecutionException e) {
                    throw e.getCause() instanceof IOException io ? io : new IOException(e.getCause());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new IOException("interrupted", e);
                }
            }
        } finally {
            pool.shutdownNow();
            p.file(null);
        }
    }
}
