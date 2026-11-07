package test;

import com.elium.launcher.Config;
import com.elium.launcher.GameInstaller;
import com.elium.launcher.JavaRuntime;
import com.elium.launcher.Net;
import java.net.InetSocketAddress;
import java.net.Proxy;
import java.net.ProxySelector;
import java.net.SocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Set;

/**
 * Ручная проверка (не входит в test.ps1): полная установка через настоящий код лаунчера,
 * при этом официальные хосты «заблокированы» — запросы к ним уходят в мёртвый прокси.
 * Запуск: java -Delium.dir=<пустая папка> -cp ... test.FullInstallBlocked
 */
public class FullInstallBlocked {
    static final Set<String> BLOCKED = Set.of(
            "piston-meta.mojang.com", "piston-data.mojang.com", "libraries.minecraft.net",
            "resources.download.minecraft.net", "maven.neoforged.net", "api.adoptium.net", "api.github.com");

    public static void main(String[] args) throws Exception {
        ProxySelector block = new ProxySelector() {
            @Override public List<Proxy> select(URI uri) {
                if (BLOCKED.contains(uri.getHost()))
                    return List.of(new Proxy(Proxy.Type.HTTP, new InetSocketAddress("127.0.0.1", 9)));
                return List.of(Proxy.NO_PROXY);
            }
            @Override public void connectFailed(URI uri, SocketAddress sa, java.io.IOException ioe) {}
        };
        ProxySelector.setDefault(block);
        Net.setClient(HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1)
                .followRedirects(HttpClient.Redirect.ALWAYS).connectTimeout(Duration.ofSeconds(15))
                .proxy(block).build());

        Config cfg = new Config();
        Net.Progress p = new Net.Progress() {
            String lastText = "";
            @Override public void update(String text, int done, int total) {
                if (!text.equals(lastText)) { System.out.println("  " + text); lastText = text; }
            }
            @Override public void stage(String key) { System.out.println("== " + key); }
        };
        long start = System.nanoTime();
        Path javaw = JavaRuntime.ensure(cfg.gameDir, p);
        System.out.println("java: " + javaw);
        GameInstaller.Profile prof = new GameInstaller(cfg).install(javaw, p);
        System.out.println("profile: " + prof.id() + " main=" + prof.mainClass() + " cp=" + prof.classpath().size());
        System.out.println("time: " + (System.nanoTime() - start) / 1_000_000_000 + " s");
        System.exit(0);
    }
}
