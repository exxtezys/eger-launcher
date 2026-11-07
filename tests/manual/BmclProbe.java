package test;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/** Диагностика: как Java HttpClient проходит редирект BMCLAPI. */
public class BmclProbe {
    public static void main(String[] args) throws Exception {
        String url = args.length > 0 ? args[0] : "https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json";
        HttpClient noFollow = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1)
                .followRedirects(HttpClient.Redirect.NEVER).connectTimeout(Duration.ofSeconds(15)).build();
        for (int i = 0; i < 3; i++) {
            long t = System.nanoTime();
            try {
                HttpResponse<Void> r = noFollow.send(HttpRequest.newBuilder(URI.create(url))
                        .header("User-Agent", "EliumLauncher").timeout(Duration.ofSeconds(30)).build(),
                        HttpResponse.BodyHandlers.discarding());
                String loc = r.headers().firstValue("location").orElse("-");
                System.out.println("try " + i + ": " + r.statusCode() + " " + (System.nanoTime() - t) / 1_000_000 + "ms -> " + loc);
                if (!"-".equals(loc)) {
                    long t2 = System.nanoTime();
                    try {
                        HttpResponse<Void> r2 = noFollow.send(HttpRequest.newBuilder(URI.create(loc))
                                .header("User-Agent", "EliumLauncher").timeout(Duration.ofSeconds(30)).build(),
                                HttpResponse.BodyHandlers.discarding());
                        System.out.println("   node: " + r2.statusCode() + " " + (System.nanoTime() - t2) / 1_000_000 + "ms");
                    } catch (Exception e) {
                        System.out.println("   node FAIL " + (System.nanoTime() - t2) / 1_000_000 + "ms: " + e);
                    }
                }
            } catch (Exception e) {
                System.out.println("try " + i + " FAIL " + (System.nanoTime() - t) / 1_000_000 + "ms: " + e);
            }
        }
    }
}
